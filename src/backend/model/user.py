import uuid
from enum import Enum
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import UUID as SQLAUUID
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utils.dbconnection import SqlDataTableBase


class UserType(str, Enum):
    """
    Enum representing different types of users.

    Attributes:
        employee (str): Represents an employee user.
        employer (str): Represents an employer user.
    """

    employee = "Employee"
    employer = "Employer"


class User(SqlDataTableBase):
    """
    Represents a user in the system.

    Attributes:
        id (UUID): The unique identifier for the user.
        username (str): The unique username of the user.
        hashed_password (str): The hashed password of the user.
        role (str): The role of the user in the system.
        tasks_assigned (list[Task]): The list of tasks assigned to the user.
        tasks_created (list[Task]): The list of tasks created by the user.
    """

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        SQLAUUID,
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    role: Mapped[UserType] = mapped_column(SQLAEnum(UserType, name="role_enum"),
                                           default=UserType.employee,
                                           nullable=False)

    tasks_assigned: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="assignee",
        foreign_keys='Task.assignee_id',
    )
    tasks_created: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="creator",
        foreign_keys="Task.creator_id",
    )

    tasks_updated: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="updater",
        foreign_keys="Task.updated_by",
    )


class LoggedInUser(BaseModel):
    id: UUID
    username: str
    role: UserType
