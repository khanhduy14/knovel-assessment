import logging
from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from backend.model.user import LoggedInUser, User, UserType
from utils.dbconnection import DbConnection


class Authenticator(ABC):

    @abstractmethod
    async def authenticate(self, request: Request) -> LoggedInUser:
        pass

    @abstractmethod
    def get_current_user(self) -> LoggedInUser:
        pass


class DebugAuthenticator(Authenticator):

    def __init__(self, user_config: dict[str, Any] | None = None) -> None:
        """
        Sets the static user, which gets returned in all __call__ executions.
        """
        if user_config:
            self._user = LoggedInUser(**user_config)
        else:
            self._user = LoggedInUser(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                role=UserType.employer,
                username="test",
            )

    async def authenticate(self, request: Request) -> LoggedInUser:
        return self._user

    def get_current_user(self) -> LoggedInUser:

        return self._user


class JwtAuthenticator(Authenticator):

    def __init__(self, secret_key: str, db_connection: DbConnection) -> None:
        self._oauth = OAuth2PasswordBearer(tokenUrl="token")
        self._secret_key = secret_key
        self._logger = logging.getLogger(__name__)
        self._db_connection = db_connection
        self._user: LoggedInUser | None = None

    async def authenticate(self, request: Request) -> LoggedInUser:
        """
        Extends call to also validate the token.
        """
        access_token = await self._get_access_token(request)
        _, claims = self._extract_token_info(access_token)

        self._user = self._validate_and_decode_token(access_token, self._secret_key, claims)
        return self._user

    async def _get_access_token(self, request: Request) -> str:
        """
        Asynchronously retrieves the access token from the OAuth provider.

        Args:
            request (Request): The incoming HTTP request containing the OAuth credentials.

        Returns:
            str: The access token as a string.

        Raises:
            HTTPException: If the access token retrieval fails, an HTTP 401 Unauthorized error is raised.
        """

        try:
            return str(await self._oauth(request=request))
        except Exception as error:
            self._logger.warning("Failed to retrieve access token. Error: %s", error, exc_info=True)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    def _extract_token_info(self, access_token: str) -> tuple[dict[str, str], dict[str, Any]]:
        """
        Extracts header and claims information from a given access token.

        Args:
            access_token (str): The JWT access token from which to extract information.

        Returns:
            tuple[dict[str, str], dict[str, Any]]: A tuple containing two dictionaries:
                - The first dictionary contains the header information.
                - The second dictionary contains the claims information.

        Raises:
            HTTPException: If the token is malformed or invalid, an HTTP 401 Unauthorized exception is raised.
        """

        try:
            header = jwt.get_unverified_header(token=access_token) or {}
            claims = jwt.get_unverified_claims(token=access_token) or {}
            return header, claims
        except Exception as error:
            self._logger.warning("Malformed token received. %s. Error: %s", access_token, error, exc_info=True)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    def _validate_and_decode_token(self, access_token: str, key: str, claims: dict[str, Any]):
        """
        Validates and decodes a JWT access token.

        Args:
            access_token (str): The JWT access token to be validated and decoded.
            key (str): The secret key used to decode the JWT.
            claims (dict[str, Any]): The claims extracted from the JWT.

        Returns:
            LoggedInUser: An instance of LoggedInUser containing the username, role, and id of the authenticated user.

        Raises:
            HTTPException: If the token is invalid or the credentials could not be validated.
        """

        try:
            jwt.decode(access_token, key=key, algorithms=["HS256"])
            username = claims.get("sub")
            if username is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
            db_user = self._get_db_user(username)
            return LoggedInUser(username=db_user.username, role=db_user.role, id=db_user.id)

        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    def _get_db_user(self, username: str) -> User:
        """
        Retrieve a user from the database by username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User: The user object corresponding to the given username.

        Raises:
            HTTPException: If no user is found with the given username, an HTTP 401 Unauthorized exception is raised.
        """

        with self._db_connection.create_session() as session:
            user = session.query(User).filter(User.username == username).first()
            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
            return user

    def get_current_user(self) -> LoggedInUser:
        """
        Retrieve the currently authenticated user.

        Returns:
            LoggedInUser: The currently authenticated user.

        Raises:
            HTTPException: If no user is authenticated, raises an HTTP 401 Unauthorized error.
        """

        if self._user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        return self._user
