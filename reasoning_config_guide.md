# Vanna.AI with Reasoning LLMs (Phi4) - Complete Configuration Guide

## Overview

This guide shows how to leverage **Phi4-reasoning** capabilities with Vanna.AI for enhanced SQL generation through **chain-of-thought reasoning**.

## Key Benefits of Reasoning LLMs with Vanna

### 🧠 **Enhanced Reasoning**
- **Step-by-step analysis** of complex database queries
- **Multi-stage reasoning** for hierarchical data structures  
- **Error detection** through reasoning validation
- **Transparent decision-making** with visible thought processes

### 🎯 **Better SQL Generation**
- **Complex join logic** handled more accurately
- **Business rule interpretation** through reasoning
- **Edge case handling** with systematic thinking
- **Query optimization** through logical analysis

## Configuration Methods

### Method 1: Basic Reasoning Integration

```python
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore

class BasicReasoningVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)
    
    def ask(self, question: str, **kwargs):
        """Enhanced ask with reasoning prompts"""
        reasoning_question = f"""
        Think through this database question step by step:
        
        {question}
        
        Please use the following approach:
        1. Analyze what information is being requested
        2. Identify which tables contain the needed data
        3. Determine the relationships between tables
        4. Plan the query structure
        5. Generate the final SQL
        
        Question: {question}
        """
        return super().ask(reasoning_question, **kwargs)

# Usage
vn = BasicReasoningVanna(config={'model': 'phi4-mini:latest'})
```

### Method 2: Advanced Chain-of-Thought Configuration

```python
class AdvancedReasoningVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        super().__init__(config=config)
        
        # Set reasoning system prompt
        self.reasoning_prompt = """
        You are an expert SQL assistant with chain-of-thought reasoning capabilities.
        
        For each question, structure your response as:
        
        <think>
        Step 1: Understand the question
        - What is being asked?
        - What are the key requirements?
        
        Step 2: Analyze database structure  
        - Which tables are relevant?
        - What are the relationships?
        
        Step 3: Plan the query
        - What joins are needed?
        - What filters should be applied?
        - How should results be ordered/grouped?
        
        Step 4: Validate the approach
        - Does this logic make sense?
        - Are there any edge cases?
        </think>
        
        [Final SQL Query]
        """

    def generate_sql(self, question: str, **kwargs) -> str:
        full_prompt = f"{self.reasoning_prompt}\n\nQuestion: {question}"
        return super().generate_sql(full_prompt, **kwargs)
```

### Method 3: Ollama Thinking Mode Integration

```python
class ThinkingModeVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        super().__init__(config=config)
    
    def ask(self, question: str, **kwargs):
        """Enable Ollama thinking mode"""
        # Enable thinking mode if supported
        kwargs['think'] = True
        kwargs['temperature'] = 0.1  # Lower temperature for reasoning
        kwargs['num_predict'] = 4096  # Allow longer reasoning chains
        
        return super().ask(question, **kwargs)

# Usage with Ollama v0.9.0+
vn = ThinkingModeVanna(config={
    'model': 'phi4-mini:latest',
    'base_url': 'http://localhost:11434'
})
```

## Enhanced Training Strategies

### 1. Reasoning-Based Training Data

```python
def train_with_reasoning_examples():
    # Train with step-by-step explanations
    vn.train(documentation="""
    <think>
    For organizational hierarchy queries in CFMS:
    1. Users have DIRECT foreign keys to all hierarchy levels
    2. No cascading joins needed - use direct relationships
    3. Always filter by is_active = 1 for active users
    4. Order by hierarchy levels for readable output
    </think>
    
    CFMS organizational queries use direct foreign key relationships 
    from users table to corps, divs, brigades, and units tables.
    """)
    
    # Train with reasoning for specific patterns
    vn.train(sql="""
    -- Reasoning: Get active users with full hierarchy
    -- Uses direct JOINs from users to all hierarchy tables
    SELECT usr.username, usr.role, c.name as corps, d.name as division
    FROM users usr
    LEFT JOIN corps c ON usr.corp_id = c.id  
    LEFT JOIN divs d ON usr.div_id = d.id
    WHERE usr.is_active = 1
    """)
```

### 2. Multi-Stage Training Process

```python
def advanced_reasoning_training():
    # Stage 1: Schema understanding with reasoning
    schema_reasoning = """
    <think>
    Analyzing CFMS database structure:
    - Users table: Central entity with direct FK to all hierarchy levels
    - Corps -> Divs -> Brigades -> Units: Hierarchy structure  
    - is_active field: Critical for filtering current users
    - Role field: Stored directly in users table
    </think>
    
    CFMS uses a denormalized approach where users have direct 
    foreign keys to all organizational levels for query efficiency.
    """
    vn.train(documentation=schema_reasoning)
    
    # Stage 2: Query pattern training
    common_patterns = [
        {
            "pattern": "Active user queries",
            "reasoning": "Always include WHERE usr.is_active = 1",
            "example": "SELECT * FROM users usr WHERE usr.is_active = 1"
        },
        {
            "pattern": "Hierarchy queries", 
            "reasoning": "Use LEFT JOINs from users to hierarchy tables",
            "example": """
            SELECT usr.username, c.name, d.name, b.name, u.name
            FROM users usr
            LEFT JOIN corps c ON usr.corp_id = c.id
            LEFT JOIN divs d ON usr.div_id = d.id  
            LEFT JOIN brigades b ON usr.brigade_id = b.id
            LEFT JOIN units u ON usr.unit_id = u.id
            WHERE usr.is_active = 1
            """
        }
    ]
    
    for pattern in common_patterns:
        reasoning_doc = f"""
        <think>
        Pattern: {pattern['pattern']}
        Reasoning: {pattern['reasoning']}
        Implementation approach: {pattern['example']}
        </think>
        
        {pattern['pattern']}: {pattern['reasoning']}
        """
        vn.train(documentation=reasoning_doc)
```

## Optimal Model Parameters for Reasoning

### Phi4-reasoning Configuration

```python
reasoning_config = {
    'model': 'phi4-mini:latest',
    'temperature': 0.1,        # Low for focused reasoning
    'top_p': 0.95,            # Balanced creativity
    'num_predict': 4096,      # Allow long reasoning chains
    'repeat_penalty': 1.1,    # Reduce repetition
    'system': """You are an expert SQL assistant with advanced reasoning capabilities.
    Always think through problems step-by-step before generating SQL."""
}

vn = ReasoningVanna(config=reasoning_config)
```

### System Prompt Templates

```python
# Template 1: Structured Reasoning
STRUCTURED_REASONING = """
Structure your SQL generation process as:

<think>
1. ANALYZE: What is the question asking for?
2. IDENTIFY: Which tables and columns are needed?
3. PLAN: What joins and filters are required?
4. VALIDATE: Does the logic handle edge cases?
5. OPTIMIZE: Can the query be improved?
</think>

[Generate SQL based on reasoning above]
"""

# Template 2: Domain-Specific Reasoning  
CFMS_REASONING = """
For CFMS database queries, always consider:

<think>
- CFMS Structure: Users have direct FKs to all hierarchy levels
- Active Filter: Always check is_active = 1 for current users
- Hierarchy Order: Corps -> Divisions -> Brigades -> Units
- Role Access: Roles stored directly in users table
- Join Strategy: Use LEFT JOINs for optional hierarchy levels
</think>

Apply CFMS-specific reasoning to generate accurate SQL.
"""
```

## Testing Reasoning Capabilities

### Test Suite for Reasoning

```python
def test_reasoning_capabilities():
    test_cases = [
        {
            "question": "Get all active users with complete organizational hierarchy",
            "expected_reasoning": [
                "Identify active users (is_active = 1)",
                "Join with hierarchy tables using direct FKs", 
                "Include all hierarchy levels",
                "Order by organizational structure"
            ]
        },
        {
            "question": "Count users by role in each division",
            "expected_reasoning": [
                "Filter active users",
                "Group by division and role",
                "Use COUNT aggregation",
                "Join with divs table for division names"
            ]
        }
    ]
    
    for test in test_cases:
        print(f"Testing: {test['question']}")
        result = vn.ask(test['question'])
        
        # Check if reasoning elements are present
        for reasoning_element in test['expected_reasoning']:
            if reasoning_element.lower() in result.lower():
                print(f"✅ Found reasoning: {reasoning_element}")
            else:
                print(f"❌ Missing reasoning: {reasoning_element}")
```

## Best Practices

### 1. **Progressive Training**
```python
# Start with simple reasoning, build complexity
vn.train(documentation="Simple active user query reasoning...")
vn.train(documentation="Complex hierarchy query reasoning...")  
vn.train(documentation="Advanced aggregation reasoning...")
```

### 2. **Reasoning Validation**  
```python
def validate_reasoning(question: str, generated_sql: str):
    validation_prompt = f"""
    <think>
    Validate this SQL for the question:
    Question: {question}
    SQL: {generated_sql}
    
    Check:
    1. Does SQL answer the question?
    2. Are joins correct?
    3. Are filters appropriate?
    4. Is syntax valid?
    </think>
    
    Provide validation feedback.
    """
    return vn.generate_sql(validation_prompt)
```

### 3. **Error Recovery with Reasoning**
```python
def reasoning_error_recovery(question: str, error: str):
    recovery_prompt = f"""
    <think>
    The previous query failed with error: {error}
    Original question: {question}
    
    Let me analyze:
    1. What caused the error?
    2. What needs to be corrected?
    3. How should I fix the approach?
    </think>
    
    Generate a corrected SQL query.
    """
    return vn.generate_sql(recovery_prompt)
```

## Performance Optimization

### Memory Management
```python
# Configure for reasoning workloads
reasoning_vn = ReasoningVanna(config={
    'model': 'phi4-mini:latest',
    'num_ctx': 8192,          # Larger context for reasoning
    'num_predict': 4096,      # Allow detailed reasoning  
    'num_thread': 8,          # Parallel processing
    'repeat_last_n': 256,     # Reduce repetition
})
```

### Batch Processing for Training
```python
def batch_reasoning_training(examples: list):
    """Process multiple training examples with reasoning"""
    for batch in chunks(examples, 10):  # Process in batches
        for example in batch:
            vn.train_with_reasoning(
                example['question'], 
                example['sql']
            )
        # Allow model to process batch
        time.sleep(1)
```

## Conclusion

Leveraging Phi4's reasoning capabilities with Vanna.AI provides:

- **🎯 Higher accuracy** through step-by-step analysis
- **🔍 Better debugging** with visible reasoning processes  
- **🚀 Enhanced learning** from reasoning-based training
- **💡 Improved edge case handling** through systematic thinking

The combination of chain-of-thought reasoning with Vanna's RAG approach creates a powerful system for intelligent SQL generation that can handle complex database scenarios with greater reliability and transparency. 