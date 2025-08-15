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
    ):
        self.app = FastAPI(title="Vanna API", description="AI-powered SQL generation API")
        self.vn = vn
        self.cache = cache or AsyncMemoryCache()
        self.auth = auth or AsyncNoAuth()
        self.allow_llm_to_see_data = allow_llm_to_see_data
        self.chart = chart
        
        self.config = {
            "allow_llm_to_see_data": allow_llm_to_see_data,
            "chart": chart,
        }

        # Setup logging
        logging.getLogger("uvicorn.access").setLevel(logging.ERROR)

        # Register routes
        self._register_routes()

    async def get_current_user(self, request: Request):
        """Dependency to get current user."""
        user = await self.auth.get_user(request)
        if not await self.auth.is_logged_in(user):
            raise HTTPException(status_code=401, detail="Not authenticated")
        return user

    async def requires_cache_fields(
        self, 
        request: Request, 
        required_fields: List[str], 
        optional_fields: Optional[List[str]] = None
    ):
        """Dependency to check cache requirements."""
        optional_fields = optional_fields or []
        
        # Get ID from query params or JSON body
        cache_id = request.query_params.get("id")
        if not cache_id and request.method == "POST":
            try:
                body = await request.json()
                cache_id = body.get("id")
            except:
                pass
                
        if not cache_id:
            raise HTTPException(status_code=400, detail="No id provided")

        # Check required fields
        field_values = {}
        for field in required_fields:
            value = await self.cache.get(id=cache_id, field=field)
            if value is None:
                raise HTTPException(status_code=400, detail=f"No {field} found")
            field_values[field] = value

        # Get optional fields
        for field in optional_fields:
            field_values[field] = await self.cache.get(id=cache_id, field=field)

        field_values["id"] = cache_id
        return field_values

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
            request: Request,
            cache_data=Depends(lambda r: self.requires_cache_fields(r, ["sql"])),
            user=Depends(self.get_current_user)
        ):
            """Execute SQL query and return results."""
            cache_id = cache_data["id"]
            sql = cache_data["sql"]

            if not self.vn.run_sql_is_set:
                raise HTTPException(
                    status_code=400,
                    detail="Please connect to a database using vn.connect_to_... in order to run SQL queries."
                )

            try:
                # Run SQL asynchronously
                df = await asyncio.get_event_loop().run_in_executor(
                    None, self.vn.run_sql, sql
                )

                await self.cache.set(id=cache_id, field="df", value=df)

                # Check if chart should be generated
                should_generate_chart = self.chart and await asyncio.get_event_loop().run_in_executor(
                    None, self.vn.should_generate_chart, df
                )

                return {
                    "type": "df",
                    "id": cache_id,
                    "df": df.head(10).to_json(orient='records', date_format='iso'),
                    "should_generate_chart": should_generate_chart,
                }

            except Exception as e:
                return {"type": "sql_error", "error": str(e)}

        @self.app.post("/api/v0/fix_sql")
        async def fix_sql(
            fix_request: FixSQLRequest,
            request: Request,
            user=Depends(self.get_current_user)
        ):
            """Fix SQL based on error message."""
            cache_data = await self.requires_cache_fields(
                request, ["question", "sql"]
            )
            cache_id = fix_request.id
            question = cache_data["question"]
            sql = cache_data["sql"]
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
            request: Request,
            cache_data=Depends(lambda r: self.requires_cache_fields(r, ["df"])),
            user=Depends(self.get_current_user)
        ):
            """Download query results as CSV."""
            cache_id = cache_data["id"]
            df = cache_data["df"]

            csv_content = df.to_csv()
            
            return StreamingResponse(
                iter([csv_content]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={cache_id}.csv"}
            )

        @self.app.get("/api/v0/generate_plotly_figure")
        async def generate_plotly_figure(
            request: Request,
            chart_instructions: Optional[str] = None,
            cache_data=Depends(lambda r: self.requires_cache_fields(r, ["df", "question", "sql"])),
            user=Depends(self.get_current_user)
        ):
            """Generate Plotly visualization."""
            cache_id = cache_data["id"]
            df = cache_data["df"]
            question = cache_data["question"]
            sql = cache_data["sql"]

            try:
                if chart_instructions is None or len(chart_instructions) == 0:
                    code = await self.cache.get(id=cache_id, field="plotly_code")
                else:
                    enhanced_question = f"{question}. When generating the chart, use these special instructions: {chart_instructions}"
                    code = await asyncio.get_event_loop().run_in_executor(
                        None,
                        self.vn.generate_plotly_code,
                        enhanced_question,
                        sql,
                        f"Running df.dtypes gives:\n {df.dtypes}"
                    )
                    await self.cache.set(id=cache_id, field="plotly_code", value=code)

                fig = await asyncio.get_event_loop().run_in_executor(
                    None, self.vn.get_plotly_figure, code, df, False
                )
                fig_json = fig.to_json()

                await self.cache.set(id=cache_id, field="fig_json", value=fig_json)

                return {
                    "type": "plotly_figure",
                    "id": cache_id,
                    "fig": fig_json,
                }
            except Exception as e:
                return {"type": "error", "error": str(e)}

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
            request: Request,
            cache_data=Depends(lambda r: self.requires_cache_fields(r, ["df", "question", "sql"])),
            user=Depends(self.get_current_user)
        ):
            """Generate followup questions."""
            cache_id = cache_data["id"]
            df = cache_data["df"]
            question = cache_data["question"]
            sql = cache_data["sql"]

            if self.allow_llm_to_see_data:
                followup_questions = await asyncio.get_event_loop().run_in_executor(
                    None, self.vn.generate_followup_questions, question, sql, df
                )
                if followup_questions is not None and len(followup_questions) > 5:
                    followup_questions = followup_questions[:5]

                await self.cache.set(id=cache_id, field="followup_questions", value=followup_questions)

                return {
                    "type": "question_list",
                    "id": cache_id,
                    "questions": followup_questions,
                    "header": "Here are some potential followup questions:",
                }
            else:
                await self.cache.set(id=cache_id, field="followup_questions", value=[])
                return {
                    "type": "question_list",
                    "id": cache_id,
                    "questions": [],
                    "header": "Followup Questions can be enabled if you set allow_llm_to_see_data=True",
                }

        @self.app.get("/api/v0/generate_summary")
        async def generate_summary(
            request: Request,
            cache_data=Depends(lambda r: self.requires_cache_fields(r, ["df", "question"])),
            user=Depends(self.get_current_user)
        ):
            """Generate summary of results."""
            cache_id = cache_data["id"]
            df = cache_data["df"]
            question = cache_data["question"]

            if self.allow_llm_to_see_data:
                summary = await asyncio.get_event_loop().run_in_executor(
                    None, self.vn.generate_summary, question, df
                )

                await self.cache.set(id=cache_id, field="summary", value=summary)

                return {
                    "type": "text",
                    "id": cache_id,
                    "text": summary,
                }
            else:
                return {
                    "type": "text",
                    "id": cache_id,
                    "text": "Summarization can be enabled if you set allow_llm_to_see_data=True",
                }

        @self.app.get("/api/v0/get_question_history")
        async def get_question_history(user=Depends(self.get_current_user)):
            """Get question history from cache."""
            questions = await self.cache.get_all(field_list=["question"])
            return {
                "type": "question_history",
                "questions": questions,
            }

    def run(self, host: str = "0.0.0.0", port: int = 8000, **kwargs):
        """Run the FastAPI app."""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port, **kwargs)
