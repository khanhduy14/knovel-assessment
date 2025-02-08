import uuid
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID

from sqlalchemy import UUID as SQLAUUID
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utils.dbconnection import SqlDataTableBase


class TaskStatus(str, Enum):
    """
    Enum representing the status of a task.

    Attributes:
        pending (str): The task is pending and has not started yet.
        in_progress (str): The task is currently in progress.
        completed (str): The task has been completed.
    """

    pending = "Pending"
    in_progress = "In Progress"
    completed = "Completed"


class Task(SqlDataTableBase):
    """
    Represents a task in the system.

    Attributes:
        id (UUID): The unique identifier for the task.
        title (str): The title of the task.
        description (str): A detailed description of the task.
        status (TaskStatus): The current status of the task. Defaults to TaskStatus.pending.
        created_at (datetime): The timestamp when the task was created. Defaults to the current UTC time.
        due_date (datetime | None): The due date for the task. Can be None if not specified.
        assignee_id (UUID): The ID of the user to whom the task is assigned.
        creator_id (UUID): The ID of the user who created the task.
        assignee (User): The user to whom the task is assigned.
        creator (User): The user who created the task.
    """
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(
        SQLAUUID,
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

    status: Mapped[TaskStatus] = mapped_column(SQLAEnum(TaskStatus, name="task_status_enum"),
                                               default=TaskStatus.pending,
                                               nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    assignee_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    creator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=datetime.now(timezone.utc), nullable=True)
    updated_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    assignee = relationship("User", back_populates="tasks_assigned", foreign_keys=[assignee_id])
    creator = relationship("User", back_populates="tasks_created", foreign_keys=[creator_id])
    updater = relationship("User", foreign_keys=[updated_by], back_populates="tasks_updated")
