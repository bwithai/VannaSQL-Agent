"""
Authentication interfaces for FastAPI VannaSQL integration.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from fastapi import Request


class AsyncAuthInterface(ABC):
    """
    Abstract base class for authentication in FastAPI.
    """

    @abstractmethod
    async def get_user(self, request: Request) -> Optional[Any]:
        """
        Get user from request.
        """
        pass

    @abstractmethod
    async def is_logged_in(self, user: Optional[Any]) -> bool:
        """
        Check if user is logged in.
        """
        pass

    @abstractmethod
    async def login_form(self) -> str:
        """
        Return login form HTML.
        """
        pass

    @abstractmethod
    async def login_handler(self, request: Request) -> Any:
        """
        Handle login request.
        """
        pass

    @abstractmethod
    async def callback_handler(self, request: Request) -> Any:
        """
        Handle authentication callback.
        """
        pass

    @abstractmethod
    async def logout_handler(self, request: Request) -> Any:
        """
        Handle logout request.
        """
        pass

    @abstractmethod
    async def override_config_for_user(self, user: Optional[Any], config: dict) -> dict:
        """
        Override configuration based on user.
        """
        pass


class AsyncNoAuth(AsyncAuthInterface):
    """
    No authentication implementation for FastAPI.
    """

    async def get_user(self, request: Request) -> Optional[Any]:
        return "anonymous"

    async def is_logged_in(self, user: Optional[Any]) -> bool:
        return True

    async def login_form(self) -> str:
        return ""

    async def login_handler(self, request: Request) -> Any:
        return {"status": "no auth required"}

    async def callback_handler(self, request: Request) -> Any:
        return {"status": "no auth required"}

    async def logout_handler(self, request: Request) -> Any:
        return {"status": "no auth required"}

    async def override_config_for_user(self, user: Optional[Any], config: dict) -> dict:
        return config
