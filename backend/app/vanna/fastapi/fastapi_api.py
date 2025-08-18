"""
FastAPI implementation for VannaSQL with async support.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from ..base import VannaBase
from .auth import AsyncAuthInterface, AsyncNoAuth
from .cache import AsyncCache, AsyncMemoryCache


# Pydantic models for request/response
class QuestionRequest(BaseModel):
    question: str


class SQLUpdateRequest(BaseModel):
    id: str
    sql: str


class TrainingRequest(BaseModel):
    question: Optional[str] = None
    sql: Optional[str] = None
    ddl: Optional[str] = None
    documentation: Optional[str] = None


class RemoveTrainingRequest(BaseModel):
    id: str


class FixSQLRequest(BaseModel):
    id: str
    error: str


class FunctionUpdateRequest(BaseModel):
    old_function_name: str
    updated_function: Dict[str, Any]


class DeleteFunctionRequest(BaseModel):
    function_name: str


class RewrittenQuestionRequest(BaseModel):
    last_question: str
    new_question: str


class VannaFastAPI:
    """
    Async FastAPI implementation for Vanna.
    """

    def __init__(
        self,
        vn: VannaBase,
        cache: Optional[AsyncCache] = None,
        auth: Optional[AsyncAuthInterface] = None,
        allow_llm_to_see_data: bool = False,
        chart: bool = True,
        redraw_chart: bool = True,
        auto_fix_sql: bool = True,
        ask_results_correct: bool = True,
        followup_questions: bool = True,
        summarization: bool = True,
        function_generation: bool = True,
    ):
        self.app = FastAPI(title="Vanna API", description="AI-powered SQL generation API")
        self.vn = vn
        self.cache = cache or AsyncMemoryCache()
        self.auth = auth or AsyncNoAuth()
        self.allow_llm_to_see_data = allow_llm_to_see_data
        self.chart = chart
        self.redraw_chart = redraw_chart
        self.auto_fix_sql = auto_fix_sql
        self.ask_results_correct = ask_results_correct
        self.followup_questions = followup_questions
        self.summarization = summarization
        self.function_generation = function_generation and hasattr(vn, "get_function")
        
        self.config = {
            "allow_llm_to_see_data": allow_llm_to_see_data,
            "chart": chart,
            "redraw_chart": redraw_chart,
            "auto_fix_sql": auto_fix_sql,
            "ask_results_correct": ask_results_correct,
            "followup_questions": followup_questions,
            "summarization": summarization,
            "function_generation": self.function_generation,
        }

        # Setup logging
        logging.getLogger("uvicorn.access").setLevel(logging.ERROR)

        # Register routes
        self._register_routes()





    def _generate_enhanced_question(self, prompt: str) -> str:
        """
        Generate an enhanced question using LLM (synchronous method for thread executor).
        """
        try:
            # Use the VannaBase's LLM to generate enhanced question
            if hasattr(self.vn, 'submit_prompt'):
                # For models that support direct prompt submission
                messages = [
                    self.vn.system_message("You are a helpful AI assistant that rewrites questions to be more specific and clear based on additional context. Always respond with just the rewritten question."),
                    self.vn.user_message(prompt)
                ]
                response = self.vn.submit_prompt(messages)
                return response.strip()
            else:
                # Fallback: use generate_sql method but adapt the prompt
                question_request = f"Rewrite this question based on additional context (respond with question only, no SQL):\n\n{prompt}"
                response = self.vn.generate_sql(question_request, allow_llm_to_see_data=False)
                
                # Clean up any SQL code blocks that might be in the response
                import re
                response = re.sub(r'```sql.*?```', '', response, flags=re.DOTALL)
                response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
                
                return response.strip()
                
        except Exception as e:
            raise Exception(f"LLM enhanced question generation failed: {str(e)}")

    async def get_current_user(self, request: Request):
        """Dependency to get current user."""
        user = await self.auth.get_user(request)
        if not await self.auth.is_logged_in(user):
            raise HTTPException(status_code=401, detail="Not authenticated")
        return user

    def _register_routes(self):
        """Register all API routes."""

        @self.app.get("/api/v0/get_config")
        async def get_config(user=Depends(self.get_current_user)):
            """Get configuration for the current user."""
            config = await self.auth.override_config_for_user(user, self.config)
            return {"type": "config", "config": config}

        @self.app.get("/api/v0/generate_questions")
        async def generate_questions(user=Depends(self.get_current_user)):
            """Generate sample questions based on training data."""
            # Check for hardcoded chinook model
            if hasattr(self.vn, "_model") and self.vn._model == "chinook":
                return {
                    "type": "question_list",
                    "questions": [
                        "What are the top 10 artists by sales?",
                        "What are the total sales per year by country?",
                        "Who is the top selling artist in each genre? Show the sales numbers.",
                        "How do the employees rank in terms of sales performance?",
                        "Which 5 cities have the most customers?",
                    ],
                    "header": "Here are some questions you can ask:",
                }

            # Get training data asynchronously
            training_data = await asyncio.get_event_loop().run_in_executor(
                None, self.vn.get_training_data
            )

            if training_data is None or len(training_data) == 0:
                return {
                    "type": "error",
                    "error": "No training data found. Please add some training data first.",
                }

            try:
                # Filter and sample questions
                questions = (
                    training_data[training_data["question"].notnull()]
                    .sample(5)["question"]
                    .tolist()
                )
                return {
                    "type": "question_list",
                    "questions": questions,
                    "header": "Here are some questions you can ask",
                }
            except Exception:
                return {
                    "type": "question_list",
                    "questions": [],
                    "header": "Go ahead and ask a question",
                }

        @self.app.get("/api/v0/generate_sql")
        async def generate_sql(
            question: str, 
            user=Depends(self.get_current_user)
        ):
            """Generate SQL from a natural language question."""
            if not question:
                raise HTTPException(status_code=400, detail="No question provided")

            cache_id = await self.cache.generate_id(question=question)
            
            # Generate SQL asynchronously
            sql = await asyncio.get_event_loop().run_in_executor(
                None, 
                self.vn.generate_sql, 
                question, 
                self.allow_llm_to_see_data
            )

            await self.cache.set(id=cache_id, field="question", value=question)
            await self.cache.set(id=cache_id, field="sql", value=sql)

            # Check if SQL is valid
            is_valid = await asyncio.get_event_loop().run_in_executor(
                None, self.vn.is_sql_valid, sql
            )

            return {
                "type": "sql" if is_valid else "text",
                "id": cache_id,
                "text": sql,
            }

        @self.app.get("/api/v0/run_sql")
        async def run_sql(
            id: str,
            user=Depends(self.get_current_user)
        ):
            """Execute SQL query and return results."""
            # Get SQL from cache
            sql = await self.cache.get(id=id, field="sql")
            if sql is None:
                raise HTTPException(status_code=400, detail="No SQL found for this ID")

            if not self.vn.run_sql_is_set:
                raise HTTPException(
                    status_code=400,
                    detail="Please connect to a database using vn.connect_to_... in order to run SQL queries."
                )

            try:
                # Log the start of SQL execution
                self.vn.log(f"🏁 Starting SQL execution for query ID: {id}", "SQL Execution")
                self.vn.log(f"📄 SQL to execute: {sql}", "SQL Execution")
                
                # Try to run SQL with auto-retry on error using shared base method
                original_question = await self.cache.get(id=id, field="question") or "Query execution"
                df, final_sql, error_history = await asyncio.get_event_loop().run_in_executor(
                    None, self.vn.run_sql_with_retry, sql, 2, original_question
                )
                
                if df is not None:
                    # Success - log and store results
                    self.vn.log(f"🎉 SQL execution completed successfully!", "SQL Execution")
                    if final_sql != sql:
                        self.vn.log(f"🔧 SQL was auto-corrected during execution", "SQL Execution")
                    
                    await self.cache.set(id=id, field="df", value=df)
                    await self.cache.set(id=id, field="sql", value=final_sql)  # Store the corrected SQL
                    
                    # Store error history for debugging
                    if error_history:
                        await self.cache.set(id=id, field="error_history", value=error_history)
                        self.vn.log(f"📚 Stored error history with {len(error_history)} correction attempts", "SQL Execution")

                    # Check if chart should be generated
                    should_generate_chart = self.chart and await asyncio.get_event_loop().run_in_executor(
                        None, self.vn.should_generate_chart, df
                    )

                    return {
                        "type": "df",
                        "id": id,
                        "df": df.head(10).to_json(orient='records', date_format='iso'),
                        "should_generate_chart": should_generate_chart,
                        "sql_corrected": final_sql != sql,  # Indicate if SQL was auto-corrected
                        "correction_attempts": len(error_history) if error_history else 0
                    }
                else:
                    # Failed after retries - return conversation questions to gather more context
                    self.vn.log(f"💔 SQL execution failed after all retry attempts", "SQL Execution")
                    self.vn.log(f"📊 Total error attempts: {len(error_history)}", "SQL Execution")
                    
                    # Create a more human response asking for clarification
                    original_question = await self.cache.get(id=id, field="question") or "your question"
                    
                    return f"I'm having trouble generating the right SQL for '{original_question}'. Could you provide more context or clarify what specific information you're looking for? This will help me understand your request better."

            except Exception as e:
                return {"type": "sql_error", "error": f"Unexpected error: {str(e)}"}

        @self.app.post("/api/v0/fix_sql")
        async def fix_sql(
            fix_request: FixSQLRequest,
            user=Depends(self.get_current_user)
        ):
            """Fix SQL based on error message."""
            # Get required data from cache
            question = await self.cache.get(id=fix_request.id, field="question")
            sql = await self.cache.get(id=fix_request.id, field="sql")
            
            # Check if required data exists
            if question is None:
                raise HTTPException(status_code=400, detail="No question found for this ID")
            if sql is None:
                raise HTTPException(status_code=400, detail="No SQL found for this ID")
            
            cache_id = fix_request.id
            error = fix_request.error

            fix_question = f"I have an error: {error}\n\nHere is the SQL I tried to run: {sql}\n\nThis is the question I was trying to answer: {question}\n\nCan you rewrite the SQL to fix the error?"

            # Generate fixed SQL
            fixed_sql = await asyncio.get_event_loop().run_in_executor(
                None, self.vn.generate_sql, fix_question
            )

            await self.cache.set(id=cache_id, field="sql", value=fixed_sql)

            return {
                "type": "sql",
                "id": cache_id,
                "text": fixed_sql,
            }

        @self.app.post("/api/v0/update_sql")
        async def update_sql(
            update_request: SQLUpdateRequest,
            user=Depends(self.get_current_user)
        ):
            """Update SQL in cache."""
            await self.cache.set(
                id=update_request.id, 
                field="sql", 
                value=update_request.sql
            )

            return {
                "type": "sql",
                "id": update_request.id,
                "text": update_request.sql,
            }

        @self.app.get("/api/v0/download_csv")
        async def download_csv(
            id: str,
            user=Depends(self.get_current_user)
        ):
            """Download query results as CSV."""
            # Get dataframe from cache
            df = await self.cache.get(id=id, field="df")
            if df is None:
                raise HTTPException(status_code=400, detail="No dataframe found for this ID")

            csv_content = df.to_csv()
            
            return StreamingResponse(
                iter([csv_content]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={id}.csv"}
            )

        @self.app.get("/api/v0/generate_plotly_figure")
        async def generate_plotly_figure(
            id: str,
            chart_instructions: Optional[str] = None,
            user=Depends(self.get_current_user)
        ):
            """Generate Plotly visualization."""
            # Get required data from cache
            df = await self.cache.get(id=id, field="df")
            question = await self.cache.get(id=id, field="question")
            sql = await self.cache.get(id=id, field="sql")
            
            # Check if required data exists
            if df is None:
                raise HTTPException(status_code=400, detail="No dataframe found for this ID")
            if question is None:
                raise HTTPException(status_code=400, detail="No question found for this ID")
            if sql is None:
                raise HTTPException(status_code=400, detail="No SQL found for this ID")

            try:
                if chart_instructions is None or len(chart_instructions.strip()) == 0:
                    # No instructions - try to get from cache
                    code = await self.cache.get(id=id, field="plotly_code")
                    if code is None:
                        # Generate default chart if no cache exists
                        self.vn.log(f"🎨 Generating default chart for query {id}", "Chart Generation")
                        code = await asyncio.get_event_loop().run_in_executor(
                            None,
                            self.vn.generate_plotly_code,
                            question,
                            sql,
                            f"Running df.dtypes gives:\n {df.dtypes}"
                        )
                        await self.cache.set(id=id, field="plotly_code", value=code)
                else:
                    # Chart instructions provided - always regenerate
                    self.vn.log(f"🎨 Regenerating chart with custom instructions: {chart_instructions[:50]}...", "Chart Generation")
                    enhanced_question = f"{question}. When generating the chart, use these special instructions: {chart_instructions}"
                    code = await asyncio.get_event_loop().run_in_executor(
                        None,
                        self.vn.generate_plotly_code,
                        enhanced_question,
                        sql,
                        f"Running df.dtypes gives:\n {df.dtypes}"
                    )
                    # Store the custom chart code (this will overwrite default)
                    await self.cache.set(id=id, field="plotly_code", value=code)
                    # Also store the instructions used for debugging
                    await self.cache.set(id=id, field="chart_instructions", value=chart_instructions)

                self.vn.log(f"📊 Generating figure from code: {code[:100]}...", "Chart Generation")
                fig = await asyncio.get_event_loop().run_in_executor(
                    None, self.vn.get_plotly_figure, code, df, False
                )
                fig_json = fig.to_json()

                await self.cache.set(id=id, field="fig_json", value=fig_json)

                return {
                    "type": "plotly_figure",
                    "id": id,
                    "fig": fig_json,
                    "chart_instructions_applied": chart_instructions is not None and len(chart_instructions.strip()) > 0
                }
            except Exception as e:
                self.vn.log(f"❌ Chart generation failed: {str(e)}", "Chart Generation")
                return {"type": "error", "error": str(e)}

        @self.app.get("/api/v0/generate_rewritten_question")
        async def generate_rewritten_question(
            last_question: str,
            new_question: str,
            user=Depends(self.get_current_user)
        ):
            """Generate a rewritten question by combining last and new questions if related."""
            rewritten_question = await asyncio.get_event_loop().run_in_executor(
                None, self.vn.generate_rewritten_question, last_question, new_question
            )

            return {
                "type": "rewritten_question", 
                "question": rewritten_question
            }

        @self.app.post("/api/v0/answer_conversation")
        async def answer_conversation(
            request: Dict[str, Any],
            user=Depends(self.get_current_user)
        ):
            """Handle user's answers to conversation questions and generate a better question."""
            cache_id = request.get("id")
            answers = request.get("answers", {})  # Dict of question -> answer
            
            if not cache_id:
                raise HTTPException(status_code=400, detail="No cache ID provided")
            
            # Get original question
            original_question = await self.cache.get(id=cache_id, field="question")
            if not original_question:
                raise HTTPException(status_code=400, detail="No original question found for this ID")
            
            # Create context from user answers
            context_parts = []
            for question, answer in answers.items():
                if answer and answer.strip():
                    context_parts.append(f"Q: {question}\nA: {answer}")
            
            context_text = "\n\n".join(context_parts)
            
            # Generate a better question with the new context
            enhanced_prompt = f"""
Based on the user's original question and their additional context, generate a more specific and clear question that better captures what they want.

Original Question: {original_question}

Additional Context from User:
{context_text}

Generate a rewritten question that:
1. Incorporates the additional context provided
2. Is more specific about what data they want
3. Includes relevant filters, timeframes, or conditions mentioned
4. Is clear enough to generate accurate SQL

Return only the rewritten question, nothing else.
"""

            try:
                rewritten_question = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._generate_enhanced_question,
                    enhanced_prompt
                )
                
                # Store the enhanced question for potential new SQL generation
                await self.cache.set(id=cache_id, field="enhanced_question", value=rewritten_question)
                await self.cache.set(id=cache_id, field="conversation_context", value=answers)
                
                return {
                    "type": "enhanced_question",
                    "original_question": original_question,
                    "enhanced_question": rewritten_question,
                    "id": cache_id,
                    "message": "Based on your answers, here's a more specific version of your question:"
                }
                
            except Exception as e:
                return {
                    "type": "error", 
                    "error": f"Failed to enhance question: {str(e)}"
                }

        @self.app.get("/api/v0/get_training_data")
        async def get_training_data(user=Depends(self.get_current_user)):
            """Get all training data."""
            df = await asyncio.get_event_loop().run_in_executor(
                None, self.vn.get_training_data
            )

            if df is None or len(df) == 0:
                return {
                    "type": "error",
                    "error": "No training data found. Please add some training data first.",
                }

            return {
                "type": "df",
                "id": "training_data",
                "df": df.to_json(orient="records"),
            }

        @self.app.post("/api/v0/remove_training_data")
        async def remove_training_data(
            remove_request: RemoveTrainingRequest,
            user=Depends(self.get_current_user)
        ):
            """Remove training data by ID."""
            success = await asyncio.get_event_loop().run_in_executor(
                None, self.vn.remove_training_data, remove_request.id
            )

            if success:
                return {"success": True}
            else:
                return {"type": "error", "error": "Couldn't remove training data"}

        @self.app.post("/api/v0/train")
        async def add_training_data(
            training_request: TrainingRequest,
            user=Depends(self.get_current_user)
        ):
            """Add training data."""
            try:
                train_id = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.vn.train,
                    training_request.question,
                    training_request.sql,
                    training_request.ddl,
                    training_request.documentation
                )
                return {"id": train_id}
            except Exception as e:
                return {"type": "error", "error": str(e)}

        @self.app.get("/api/v0/generate_followup_questions")
        async def generate_followup_questions(
            id: str,
            user=Depends(self.get_current_user)
        ):
            """Generate followup questions."""
            # Get required data from cache
            df = await self.cache.get(id=id, field="df")
            question = await self.cache.get(id=id, field="question")
            sql = await self.cache.get(id=id, field="sql")
            
            # Check if required data exists
            if df is None:
                raise HTTPException(status_code=400, detail="No dataframe found for this ID")
            if question is None:
                raise HTTPException(status_code=400, detail="No question found for this ID")
            if sql is None:
                raise HTTPException(status_code=400, detail="No SQL found for this ID")

            if self.allow_llm_to_see_data:
                followup_questions = await asyncio.get_event_loop().run_in_executor(
                    None, self.vn.generate_followup_questions, question, sql, df
                )
                if followup_questions is not None and len(followup_questions) > 5:
                    followup_questions = followup_questions[:5]

                await self.cache.set(id=id, field="followup_questions", value=followup_questions)

                return {
                    "type": "question_list",
                    "id": id,
                    "questions": followup_questions,
                    "header": "Here are some potential followup questions:",
                }
            else:
                await self.cache.set(id=id, field="followup_questions", value=[])
                return {
                    "type": "question_list",
                    "id": id,
                    "questions": [],
                    "header": "Followup Questions can be enabled if you set allow_llm_to_see_data=True",
                }

        @self.app.get("/api/v0/generate_summary")
        async def generate_summary(
            id: str,
            user=Depends(self.get_current_user)
        ):
            """Generate summary of results."""
            # Get required data from cache
            df = await self.cache.get(id=id, field="df")
            question = await self.cache.get(id=id, field="question")
            
            # Check if required data exists
            if df is None:
                raise HTTPException(status_code=400, detail="No dataframe found for this ID")
            if question is None:
                raise HTTPException(status_code=400, detail="No question found for this ID")

            if self.allow_llm_to_see_data:
                summary = await asyncio.get_event_loop().run_in_executor(
                    None, self.vn.generate_summary, question, df
                )

                await self.cache.set(id=id, field="summary", value=summary)

                return {
                    "type": "text",
                    "id": id,
                    "text": summary,
                }
            else:
                return {
                    "type": "text",
                    "id": id,
                    "text": "Summarization can be enabled if you set allow_llm_to_see_data=True",
                }

        @self.app.get("/api/v0/load_question")
        async def load_question(
            id: str,
            user=Depends(self.get_current_user)
        ):
            """Load a previously cached question with all its data."""
            self.vn.log(f"🔍 Loading question data for ID: {id}", "Load Question")
            
            # Get required data from cache
            question = await self.cache.get(id=id, field="question")
            sql = await self.cache.get(id=id, field="sql")
            df = await self.cache.get(id=id, field="df")
            
            # Log what we found
            self.vn.log(f"📋 Found question: {'✅' if question else '❌'}", "Load Question")
            self.vn.log(f"📋 Found SQL: {'✅' if sql else '❌'}", "Load Question")
            self.vn.log(f"📋 Found dataframe: {'✅' if df is not None else '❌'}", "Load Question")
            
            # Be more lenient - only require question and SQL, make df optional
            if question is None:
                self.vn.log(f"❌ Missing question for ID: {id}", "Load Question")
                raise HTTPException(status_code=400, detail="No question found for this ID")
            if sql is None:
                self.vn.log(f"❌ Missing SQL for ID: {id}", "Load Question")
                raise HTTPException(status_code=400, detail="No SQL found for this ID")
            
            # Get optional data from cache
            fig_json = await self.cache.get(id=id, field="fig_json")
            summary = await self.cache.get(id=id, field="summary")
            
            self.vn.log(f"📋 Found chart: {'✅' if fig_json else '❌'}", "Load Question")
            self.vn.log(f"📋 Found summary: {'✅' if summary else '❌'}", "Load Question")
            
            try:
                response_data = {
                    "type": "question_cache",
                    "id": id,
                    "question": question,
                    "sql": sql,
                    "df": None,  # Will be set below if df exists
                    "fig": fig_json,
                    "summary": summary,
                }
                
                # Handle dataframe - if it exists, convert to JSON, otherwise return empty array
                if df is not None:
                    try:
                        response_data["df"] = df.head(10).to_json(orient="records", date_format="iso")
                        self.vn.log(f"✅ Successfully converted dataframe to JSON", "Load Question")
                    except Exception as df_error:
                        self.vn.log(f"⚠️ Error converting dataframe: {str(df_error)}", "Load Question")
                        response_data["df"] = "[]"  # Empty array as fallback
                else:
                    response_data["df"] = "[]"  # Empty array if no dataframe
                    self.vn.log(f"⚠️ No dataframe found, returning empty array", "Load Question")
                
                self.vn.log(f"✅ Successfully loaded question data for ID: {id}", "Load Question")
                return response_data
                
            except Exception as e:
                self.vn.log(f"❌ Error preparing response: {str(e)}", "Load Question")
                return {"type": "error", "error": str(e)}

        @self.app.get("/api/v0/get_question_history")
        async def get_question_history(user=Depends(self.get_current_user)):
            """Get question history from cache."""
            questions = await self.cache.get_all(field_list=["question"])
            return {
                "type": "question_history",
                "questions": questions,
            }

        @self.app.get("/api/v0/get_error_history")
        async def get_error_history(
            id: str,
            user=Depends(self.get_current_user)
        ):
            """Get error history and correction attempts for a specific query."""
            error_history = await self.cache.get(id=id, field="error_history")
            
            if error_history is None:
                return {
                    "type": "error_history",
                    "id": id,
                    "error_history": [],
                    "message": "No error history found for this query."
                }
            
            return {
                "type": "error_history",
                "id": id,
                "error_history": error_history,
                "total_attempts": len(error_history)
            }

        @self.app.get("/api/v0/debug_cache")
        async def debug_cache(
            id: str,
            user=Depends(self.get_current_user)
        ):
            """Debug endpoint to see what's actually cached for a given ID."""
            fields_to_check = ["question", "sql", "df", "fig_json", "summary", "error_history"]
            cache_status = {}
            
            for field in fields_to_check:
                value = await self.cache.get(id=id, field=field)
                cache_status[field] = {
                    "exists": value is not None,
                    "type": type(value).__name__ if value is not None else "None",
                    "preview": str(value)[:100] + "..." if value is not None and len(str(value)) > 100 else str(value)
                }
            
            return {
                "type": "cache_debug",
                "id": id,
                "cache_status": cache_status,
                "total_fields": len([f for f in cache_status.values() if f["exists"]])
            }

        @self.app.get("/api/v0/get_function")
        async def get_function(
            question: str,
            user=Depends(self.get_current_user)
        ):
            """Get a function from a question."""
            if not question:
                raise HTTPException(status_code=400, detail="No question provided")

            if not hasattr(self.vn, "get_function"):
                return {"type": "error", "error": "This setup does not support function generation."}

            cache_id = await self.cache.generate_id(question=question)
            function = await asyncio.get_event_loop().run_in_executor(
                None, self.vn.get_function, question
            )

            if function is None:
                return {"type": "error", "error": "No function found"}

            if 'instantiated_sql' not in function:
                self.vn.log(f"No instantiated SQL found for {question} in {function}")
                return {"type": "error", "error": "No instantiated SQL found"}

            await self.cache.set(id=cache_id, field="question", value=question)
            await self.cache.set(id=cache_id, field="sql", value=function['instantiated_sql'])

            if 'instantiated_post_processing_code' in function and function['instantiated_post_processing_code'] is not None and len(function['instantiated_post_processing_code']) > 0:
                await self.cache.set(id=cache_id, field="plotly_code", value=function['instantiated_post_processing_code'])

            return {
                "type": "function",
                "id": cache_id,
                "function": function,
            }

        @self.app.get("/api/v0/get_function_with_execution")
        async def get_function_with_execution(
            question: str,
            user=Depends(self.get_current_user)
        ):
            """Get a function from a question and execute its SQL with retry logic."""
            if not question:
                raise HTTPException(status_code=400, detail="No question provided")

            if not hasattr(self.vn, "get_function"):
                return {"type": "error", "error": "This setup does not support function generation."}

            # Check if database connection is set
            if not self.vn.run_sql_is_set:
                return {"type": "error", "error": "Please connect to a database using vn.connect_to_... in order to run SQL queries."}

            cache_id = await self.cache.generate_id(question=question)
            function = await asyncio.get_event_loop().run_in_executor(
                None, self.vn.get_function, question
            )

            if function is None:
                return {"type": "error", "error": "No function found"}

            if 'instantiated_sql' not in function:
                self.vn.log(f"No instantiated SQL found for {question} in {function}")
                return {"type": "error", "error": "No instantiated SQL found"}

            # Cache function data
            await self.cache.set(id=cache_id, field="question", value=question)
            await self.cache.set(id=cache_id, field="sql", value=function['instantiated_sql'])

            if 'instantiated_post_processing_code' in function and function['instantiated_post_processing_code'] is not None and len(function['instantiated_post_processing_code']) > 0:
                await self.cache.set(id=cache_id, field="plotly_code", value=function['instantiated_post_processing_code'])

            # Execute the SQL with retry logic
            self.vn.log(f"🏁 Starting function SQL execution with retry for: {question}", "Function Execution")
            self.vn.log(f"📄 Function SQL to execute: {function['instantiated_sql']}", "Function Execution")
            
            try:
                # Use the same retry logic as normal SQL execution
                df, final_sql, error_history = await self._run_sql_with_retry(cache_id, function['instantiated_sql'])
                
                if df is not None:
                    # Success - return function data with results
                    self.vn.log(f"🎉 Function SQL executed successfully!", "Function Execution")
                    
                    await self.cache.set(id=cache_id, field="df", value=df)
                    await self.cache.set(id=cache_id, field="sql", value=final_sql)  # Store corrected SQL
                    
                    # Store error history for debugging
                    if error_history:
                        await self.cache.set(id=cache_id, field="error_history", value=error_history)
                    
                    # Check if chart should be generated
                    should_generate_chart = self.chart and await asyncio.get_event_loop().run_in_executor(
                        None, self.vn.should_generate_chart, df
                    )

                    return {
                        "type": "function_with_results",
                        "id": cache_id,
                        "function": function,
                        "df": df.head(10).to_json(orient='records', date_format='iso'),
                        "should_generate_chart": should_generate_chart,
                        "sql_corrected": final_sql != function['instantiated_sql'],
                        "correction_attempts": len(error_history) if error_history else 0
                    }
                else:
                    # Failed after retries - return conversation questions 
                    self.vn.log(f"💔 Function SQL execution failed after all retry attempts", "Function Execution")
                    
                    return {
                        "type": "function_conversation_needed",
                        "id": cache_id,
                        "function": function,
                        "message": f"I'm having trouble executing the SQL for '{question}'. Could you provide more context or clarify what specific information you're looking for? This will help me generate the correct query.",
                        "conversation_questions": [],  # Remove confusing auto-generated questions
                        "error_history": error_history,
                        "max_retries_reached": True,
                        "original_question": question
                    }
                    
            except Exception as e:
                return {"type": "error", "error": f"Unexpected error executing function SQL: {str(e)}"}

        @self.app.get("/api/v0/get_all_functions")
        async def get_all_functions(user=Depends(self.get_current_user)):
            """Get all the functions."""
            if not hasattr(self.vn, "get_all_functions"):
                return {"type": "error", "error": "This setup does not support function generation."}

            functions = await asyncio.get_event_loop().run_in_executor(
                None, self.vn.get_all_functions
            )

            return {
                "type": "functions",
                "functions": functions,
            }

        @self.app.get("/api/v0/create_function")
        async def create_function(
            id: str,
            user=Depends(self.get_current_user)
        ):
            """Create function from cached question and SQL."""
            # Get required data from cache
            question = await self.cache.get(id=id, field="question")
            sql = await self.cache.get(id=id, field="sql")
            
            if question is None:
                raise HTTPException(status_code=400, detail="No question found for this ID")
            if sql is None:
                raise HTTPException(status_code=400, detail="No SQL found for this ID")

            plotly_code = await self.cache.get(id=id, field="plotly_code")
            if plotly_code is None:
                plotly_code = ""

            function_data = await asyncio.get_event_loop().run_in_executor(
                None, self.vn.create_function, question, sql, plotly_code
            )

            return {
                "type": "function_template",
                "id": id,
                "function_template": function_data,
            }

        @self.app.post("/api/v0/update_function")
        async def update_function(
            update_request: FunctionUpdateRequest,
            user=Depends(self.get_current_user)
        ):
            """Update function."""
            updated = await asyncio.get_event_loop().run_in_executor(
                None, self.vn.update_function, update_request.old_function_name, update_request.updated_function
            )

            return {"success": updated}

        @self.app.post("/api/v0/delete_function")
        async def delete_function(
            delete_request: DeleteFunctionRequest,
            user=Depends(self.get_current_user)
        ):
            """Delete function."""
            success = await asyncio.get_event_loop().run_in_executor(
                None, self.vn.delete_function, delete_request.function_name
            )

            return {"success": success}

    def run(self, host: str = "0.0.0.0", port: int = 8000, **kwargs):
        """Run the FastAPI app."""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port, **kwargs)
