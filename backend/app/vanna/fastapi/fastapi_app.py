"""
FastAPI App with UI integration for VannaSQL.
"""

import importlib.metadata
import os
from typing import Optional

import requests
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from ..base import VannaBase
from ..flask.assets import css_content, html_content, js_content
from .auth import AsyncAuthInterface, AsyncNoAuth
from .cache import AsyncCache, AsyncMemoryCache
from .fastapi_api import VannaFastAPI


class VannaFastAPIApp(VannaFastAPI):
    """
    FastAPI app with UI integration for Vanna.
    """

    def __init__(
        self,
        vn: VannaBase,
        cache: Optional[AsyncCache] = None,
        auth: Optional[AsyncAuthInterface] = None,
        allow_llm_to_see_data: bool = False,
        logo: str = "https://img.vanna.ai/vanna-flask.svg",
        title: str = "Welcome to Vanna.AI",
        subtitle: str = "Your AI-powered copilot for SQL queries.",
        show_training_data: bool = True,
        suggested_questions: bool = True,
        sql: bool = True,
        table: bool = True,
        csv_download: bool = True,
        chart: bool = True,
        redraw_chart: bool = True,
        auto_fix_sql: bool = True,
        ask_results_correct: bool = True,
        followup_questions: bool = True,
        summarization: bool = True,
        function_generation: bool = True,
        index_html_path: Optional[str] = None,
        assets_folder: Optional[str] = None,
    ):
        """
        Initialize FastAPI app with UI configuration.

        Args:
            vn: The Vanna instance to interact with.
            cache: The cache to use. Defaults to AsyncMemoryCache.
            auth: The authentication method to use. Defaults to AsyncNoAuth.
            allow_llm_to_see_data: Whether to allow the LLM to see data.
            logo: The logo to display in the UI.
            title: The title to display in the UI.
            subtitle: The subtitle to display in the UI.
            show_training_data: Whether to show the training data in the UI.
            suggested_questions: Whether to show suggested questions in the UI.
            sql: Whether to show the SQL input in the UI.
            table: Whether to show the table output in the UI.
            csv_download: Whether to allow downloading the table output as a CSV file.
            chart: Whether to show the chart output in the UI.
            redraw_chart: Whether to allow redrawing the chart.
            auto_fix_sql: Whether to allow auto-fixing SQL errors.
            ask_results_correct: Whether to ask the user if the results are correct.
            followup_questions: Whether to show followup questions.
            summarization: Whether to show summarization.
            function_generation: Whether to enable function generation.
            index_html_path: Path to the index.html file.
            assets_folder: The location where you'd like to serve the static assets from.
        """
        super().__init__(
            vn=vn,
            cache=cache or AsyncMemoryCache(),
            auth=auth or AsyncNoAuth(),
            allow_llm_to_see_data=allow_llm_to_see_data,
            chart=chart,
        )

        # Update config with UI settings
        self.config.update({
            "logo": logo,
            "title": title,
            "subtitle": subtitle,
            "show_training_data": show_training_data,
            "suggested_questions": suggested_questions,
            "sql": sql,
            "table": table,
            "csv_download": csv_download,
            "chart": chart,
            "redraw_chart": redraw_chart,
            "auto_fix_sql": auto_fix_sql,
            "ask_results_correct": ask_results_correct,
            "followup_questions": followup_questions,
            "summarization": summarization,
            "function_generation": function_generation and hasattr(vn, "get_function"),
        })

        try:
            self.config["version"] = importlib.metadata.version('vanna')
        except importlib.metadata.PackageNotFoundError:
            self.config["version"] = "local"

        self.index_html_path = index_html_path
        self.assets_folder = assets_folder

        # Register UI routes
        self._register_ui_routes()

    def _register_ui_routes(self):
        """Register UI-specific routes."""

        @self.app.post("/auth/login")
        async def login(request):
            """Handle login requests."""
            return await self.auth.login_handler(request)

        @self.app.get("/auth/callback")
        async def callback(request):
            """Handle authentication callback."""
            return await self.auth.callback_handler(request)

        @self.app.get("/auth/logout")
        async def logout(request):
            """Handle logout requests."""
            return await self.auth.logout_handler(request)

        @self.app.get("/assets/{filename:path}")
        async def proxy_assets(filename: str):
            """Serve static assets."""
            if self.assets_folder:
                file_path = os.path.join(self.assets_folder, filename)
                if os.path.exists(file_path):
                    return FileResponse(file_path)

            if ".css" in filename:
                return Response(content=css_content, media_type="text/css")

            if ".js" in filename:
                return Response(content=js_content, media_type="text/javascript")

            # Return 404
            return Response(content="File not found", status_code=404)

        @self.app.get("/vanna.svg")
        async def proxy_vanna_svg():
            """Proxy the vanna.svg file to the remote server."""
            try:
                remote_url = "https://vanna.ai/img/vanna.svg"
                response = requests.get(remote_url, stream=True, timeout=10)

                if response.status_code == 200:
                    return Response(
                        content=response.content,
                        status_code=response.status_code,
                        headers={
                            name: value
                            for name, value in response.headers.items()
                            if name.lower() not in [
                                "content-encoding",
                                "content-length", 
                                "transfer-encoding",
                                "connection"
                            ]
                        }
                    )
                else:
                    return Response(
                        content="Error fetching file from remote server",
                        status_code=response.status_code
                    )
            except Exception:
                return Response(
                    content="Error fetching file from remote server",
                    status_code=500
                )

        @self.app.get("/")
        @self.app.get("/{path:path}")
        async def serve_ui(path: str = ""):
            """Serve the main UI."""
            if self.index_html_path and os.path.exists(self.index_html_path):
                return FileResponse(self.index_html_path)
            return HTMLResponse(content=html_content)

    async def run_async(self, host: str = "0.0.0.0", port: int = 8000, **kwargs):
        """Run the FastAPI app asynchronously."""
        import uvicorn
        config = uvicorn.Config(self.app, host=host, port=port, **kwargs)
        server = uvicorn.Server(config)
        await server.serve()

    def run(self, host: str = "0.0.0.0", port: int = 8000, **kwargs):
        """Run the FastAPI app."""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port, **kwargs)
