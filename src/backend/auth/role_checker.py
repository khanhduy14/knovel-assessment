from fastapi import HTTPException, Request

from backend.auth.authenticator import Authenticator
from backend.model.user import LoggedInUser, UserType


class RoleChecker:
    """
    User Role Checker. Default all roles are allowed.
    """

    def __init__(self, user_authenticator: Authenticator, allowed_roles: list[UserType] | None = None):

        self._allowed_roles = allowed_roles or list(UserType)
        self._user_authenticator = user_authenticator

    async def __call__(self, request: Request) -> LoggedInUser:
        """
        Asynchronously handles the request to authenticate and authorize a user.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            LoggedInUser: The authenticated and authorized user.

        Raises:
            HTTPException: If the user is not authorized to access the resource.
        """

        user: LoggedInUser = await self._user_authenticator.authenticate(request)
        if self._is_user_authorized(user):
            return user

        raise HTTPException(status_code=403, detail="User is not authorized to access this resource")

    def _is_user_authorized(self, user: LoggedInUser) -> bool:
        return any(allowed_role in user.role for allowed_role in self._allowed_roles)
