from datetime import timedelta

from fastapi import HTTPException, status
from pydantic import BaseModel

from backend.model.user import User, UserType
from utils.dbconnection import DbConnection
from utils.jwt_token import JWTUtils


class ApiTokenResponse(BaseModel):
    access_token: str
    token_type: str


class ApiCreateUserReq(BaseModel):
    username: str
    password: str
    role: UserType


class ApiLoginReq(BaseModel):
    username: str
    password: str


class ViewUser:

    def __init__(self, db_connection: DbConnection, jwt_utils: JWTUtils, token_expire_mins: int) -> None:
        self._db_connection = db_connection
        self._jwt_utils = jwt_utils
        self._token_expire_mins = token_expire_mins

    def login(self, username: str, password: str) -> ApiTokenResponse:
        with self._db_connection.create_session() as session:
            user = self._jwt_utils.authenticate_user(session, username, password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                )
            access_token_expires = timedelta(minutes=self._token_expire_mins)
            access_token = self._jwt_utils.create_access_token(data={"sub": user.username},
                                                               expires_delta=access_token_expires)
            return ApiTokenResponse(access_token=access_token, token_type="bearer")

    def create_user(self, username: str, password: str, role: UserType) -> None:
        with self._db_connection.create_session() as session:
            hashed_password = self._jwt_utils.get_password_hash(password)
            user = User(username=username, hashed_password=hashed_password, role=role)
            session.add(user)
            session.commit()
