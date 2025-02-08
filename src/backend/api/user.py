from fastapi import APIRouter, FastAPI

from backend.viewdata.user import (
    ApiCreateUserReq,
    ApiLoginReq,
    ApiTokenResponse,
    ViewUser,
)


def register_user_api(app: FastAPI, user_view: ViewUser):
    """
    Registers the user-related API endpoints with the given FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance to register the routes with.
        user_view (ViewUser): An instance of ViewUser that handles the user-related operations.

    Endpoints:
        POST /v1/users/login: Logs in a user and returns an API token.
            - Request Body: ApiLoginReq
            - Response: ApiTokenResponse

        POST /v1/users/: Creates a new user.
            - Request Body: ApiCreateUserReq
            - Response: The result of the user creation operation.
    """

    router = APIRouter(prefix="/v1/users")

    @router.post("/login", response_model=ApiTokenResponse)
    def login(login_req: ApiLoginReq):
        return user_view.login(login_req.username, login_req.password)

    @router.post("/")
    def create_user(create_user_req: ApiCreateUserReq):
        return user_view.create_user(create_user_req.username, create_user_req.password, create_user_req.role)

    app.include_router(router)
