import os
import requests
import re
import sqlparse
from sqlparse import sql, tokens as T
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore
from app.core.config import settings

class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        if not os.path.exists(settings.RAG_LAYER_DIR):
            os.makedirs(settings.RAG_LAYER_DIR)
            print(f"📁 Created directory: {settings.RAG_LAYER_DIR}")

        if config is None:
            config = {"path": settings.RAG_LAYER_DIR}

        ollama_url = settings.OLLAMA_HOST
        config["ollama_host"] = ollama_url

        # Choose model from env var or default
        config["model"] = settings.OLLAMA_MODEL
        self.model = config["model"]

        # Set dialect to MySQL for proper SQL generation
        self.dialect = "mysql"

        # Explicitly set required attribute
        self.ollama_options = {}

        # Call both base classes directly
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

    def get_available_models(self):
        res = requests.get(f"{settings.OLLAMA_HOST}/api/tags")
        return [m["model"] for m in res.json().get("models", [])]
    
    def get_sql_prompt(
        self,
        initial_prompt: str,
        question: str,
        question_sql_list: list,
        ddl_list: list,
        doc_list: list,
        **kwargs,
    ):
        """
        Override the base get_sql_prompt method to include MySQL 8 specific system prompt
        """
        # MySQL 8 specific system prompt
        if initial_prompt is None:
            initial_prompt = """You are a MySQL 8.0 expert SQL assistant and you have only one table 'discipline_data'. Generate SQL queries that are specifically compatible with MySQL 8.0 syntax and features.

Key MySQL 8.0 Guidelines:
- Use MySQL 8.0 specific functions and syntax
- Support for window functions (ROW_NUMBER(), RANK(), DENSE_RANK(), etc.)
- Use Common Table Expressions (CTEs) with WITH clause when appropriate
- Support for JSON functions and operations
- Use proper MySQL 8.0 date/time functions
- Follow MySQL naming conventions (backticks for identifiers if needed)
- Use LIMIT for pagination instead of TOP
- Use proper MySQL data types (INT, VARCHAR, TEXT, DATETIME, etc.)
- Generate only valid, executable MySQL 8.0 SQL without explanations

"""

        # Add DDL context
        initial_prompt = self.add_ddl_to_prompt(
            initial_prompt, ddl_list, max_tokens=self.max_tokens
        )

        # Add documentation context
        if self.static_documentation != "":
            doc_list.append(self.static_documentation)

        initial_prompt = self.add_documentation_to_prompt(
            initial_prompt, doc_list, max_tokens=self.max_tokens
        )

        # Add SQL examples context
        initial_prompt = self.add_sql_to_prompt(
            initial_prompt, [example.get("sql", "") for example in question_sql_list if example and "sql" in example], max_tokens=self.max_tokens
        )

        # Add response guidelines
        initial_prompt += (
            "\n===Response Guidelines===\n"
            "1. If the provided context is sufficient, generate a valid MySQL 8.0 SQL query without explanations.\n"
            "2. If context is almost sufficient but requires column value knowledge, generate an intermediate SQL to find distinct values. Prepend with comment: -- intermediate_sql\n"
            "3. If context is insufficient, explain why the query cannot be generated.\n"
            "4. Use the most relevant table(s) from the provided schema.\n"
            "5. If the question was asked before, repeat the exact previous answer.\n"
            "6. Ensure output SQL is MySQL 8.0-compliant and executable without syntax errors.\n"
            "7. Use proper MySQL 8.0 functions and avoid database-specific syntax from other systems.\n"
        )

        # Build message log
        message_log = [self.system_message(initial_prompt)]

        # Add example conversations
        for example in question_sql_list:
            if example and "question" in example and "sql" in example:
                message_log.append(self.user_message(example["question"]))
                message_log.append(self.assistant_message(example["sql"]))

        # Add current question
        message_log.append(self.user_message(question))

        return message_log
    
    def is_sql_valid(self, sql: str) -> bool:
        """
        Validate SQL syntax for MySQL 8.0 compatibility
        """
        if not sql or not sql.strip():
            return False
            
        try:
            # Parse the SQL using sqlparse
            parsed = sqlparse.parse(sql)
            if not parsed:
                return False
                
            # Check if it's a valid SQL statement
            statement = parsed[0]
            if not statement.tokens:
                return False
            
            # Basic validation - check for common MySQL 8.0 patterns
            sql_lower = sql.lower().strip()
            
            # Check for basic SQL statement types
            valid_statements = ['select', 'insert', 'update', 'delete', 'with', 'show', 'describe', 'explain']
            if not any(sql_lower.startswith(stmt) for stmt in valid_statements):
                return False
            
            # Check for balanced parentheses
            if sql.count('(') != sql.count(')'):
                return False
                
            # Check for balanced quotes
            single_quotes = sql.count("'") - sql.count("\\'")
            double_quotes = sql.count('"') - sql.count('\\"')
            if single_quotes % 2 != 0 or double_quotes % 2 != 0:
                return False
            
            # MySQL specific validations
            # Check for unsupported syntax from other databases
            unsupported_patterns = [
                r'\bTOP\s+\d+\b',  # SQL Server TOP
                r'\bLIMIT\s+\d+\s+OFFSET\s+\d+',  # PostgreSQL style (should be LIMIT offset, count)
                r'\[\w+\]',  # SQL Server bracket notation
                r'\$\d+',    # PostgreSQL parameter style
            ]
            
            for pattern in unsupported_patterns:
                if re.search(pattern, sql, re.IGNORECASE):
                    return False
            
            return True
            
        except Exception as e:
            self.log(title="SQL Validation Error", message=f"Error validating SQL: {str(e)}")
            return False
    
    def generate_sql(self, question: str, allow_llm_to_see_data=False, **kwargs) -> str:
        """
        Override generate_sql to include validation and regeneration logic
        """
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            
            # Generate SQL using parent method
            sql = super().generate_sql(question, allow_llm_to_see_data=allow_llm_to_see_data, **kwargs)
            
            # Clean up the SQL
            sql = sql.replace("\\_", "_").strip()
            
            # Extract SQL from potential markdown formatting
            sql = self._extract_sql_from_response(sql)
            
            # Validate the generated SQL
            if self.is_sql_valid(sql):
                self.log(title="SQL Generation Success", message=f"Valid SQL generated on attempt {attempt}")
                return sql
            else:
                self.log(title="SQL Validation Failed", message=f"Attempt {attempt}: Invalid SQL generated, retrying...")
                
                if attempt < max_attempts:
                    # Modify the question to be more specific about MySQL 8.0 requirements
                    enhanced_question = f"""
{question}

Previous attempt generated invalid SQL. Please ensure the SQL is:
1. Valid MySQL 8.0 syntax
2. Uses proper MySQL functions and keywords
3. Has balanced parentheses and quotes
4. Follows MySQL naming conventions
5. Is executable without syntax errors

Generate a corrected MySQL 8.0 compatible SQL query.
"""
                    kwargs['question'] = enhanced_question
                    question = enhanced_question
        
        # If all attempts failed, return the last generated SQL with a warning
        self.log(title="SQL Generation Warning", message=f"Failed to generate valid SQL after {max_attempts} attempts. Returning last attempt.")
        return sql
    
    def _extract_sql_from_response(self, response: str) -> str:
        """
        Extract SQL query from LLM response that might contain markdown or explanations
        """
        # Remove markdown code blocks
        sql_pattern = r'```(?:sql)?\s*(.*?)\s*```'
        match = re.search(sql_pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Look for SQL statements (basic pattern)
        sql_keywords = r'\b(?:SELECT|INSERT|UPDATE|DELETE|WITH|SHOW|DESCRIBE|EXPLAIN)\b'
        lines = response.split('\n')
        sql_lines = []
        capturing = False
        
        for line in lines:
            line = line.strip()
            if re.search(sql_keywords, line, re.IGNORECASE):
                capturing = True
            
            if capturing:
                sql_lines.append(line)
                # Stop if we hit a semicolon and the next line doesn't look like SQL
                if line.endswith(';'):
                    break
        
        if sql_lines:
            return '\n'.join(sql_lines).strip()
        
        # Fallback: return the original response
        return response.strip()

vn = MyVanna()

# Example usage:
# Generate SQL with MySQL 8.0 specific optimizations and validation
# sql_query = vn.generate_sql("What are the top 10 customers by sales?")
# is_valid = vn.is_sql_valid("SELECT user_name, user_email FROM users WHERE user_id = 123")