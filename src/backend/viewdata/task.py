from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict

from backend.model.task import Task, TaskStatus
from backend.model.user import LoggedInUser, User, UserType
from utils.dbconnection import DbConnection


class TaskBase(BaseModel):
    title: str
    description: str
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    assignee_id: UUID


class TaskUpdate(BaseModel):
    status: TaskStatus


class TaskOut(BaseModel):
    id: UUID
    title: str
    description: str
    status: str
    created_at: datetime
    due_date: Optional[datetime]
    assignee_id: UUID
    creator_id: UUID

    model_config = ConfigDict(from_attributes=True)


class EmployeeTaskSummary(BaseModel):
    employee_id: UUID
    username: str
    total_tasks: int
    completed_tasks: int


class ViewTask:

    def __init__(self, db_connection: DbConnection) -> None:
        self._db_connection = db_connection

    def create_task(self, task: TaskCreate, current_user: LoggedInUser) -> Task:
        """
        Creates a new task and assigns it to an employee.

        Args:
            task (TaskCreate): The task details to be created.
            current_user (LoggedInUser): The user who is creating the task.

        Returns:
            Task: The created task object.

        Raises:
            HTTPException: If the assignee is not found or is not an employee.
        """

        with self._db_connection.create_session() as session:
            assignee = session.query(User).filter(User.id == task.assignee_id, User.role == UserType.employee).first()
            if not assignee:
                raise HTTPException(status_code=404, detail="Assignee not found or not an employee")
            db_task = Task(title=task.title,
                           description=task.description,
                           due_date=task.due_date,
                           assignee_id=task.assignee_id,
                           creator_id=current_user.id,
                           status="Pending")
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
            return db_task

    def get_tasks(
        self,
        assignee_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = None,
    ) -> list[Task]:
        """
        Retrieve a list of tasks based on optional filters and sorting criteria.

        Args:
            assignee_id (Optional[int]): The ID of the assignee to filter tasks by.
            status_filter (Optional[str]): The status to filter tasks by.
            sort_by (Optional[str]): The field to sort tasks by.
            order (Optional[str]): The order of sorting, either 'asc' for ascending or 'desc' for descending.

        Returns:
            list[Task]: A list of tasks that match the given filters and sorting criteria.
        """
        with self._db_connection.create_session() as session:
            query = session.query(Task)
            if assignee_id:
                query = query.filter(Task.assignee_id == assignee_id)
            if status_filter:
                query = query.filter(Task.status == status_filter)
            if sort_by:
                sort_column = getattr(Task, sort_by)
                sort_column = sort_column.desc() if order == "desc" else sort_column.asc()
                query = query.order_by(sort_column)
            return query.all()

    def update_task(self, task_id: UUID, task_update: TaskUpdate, current_user: LoggedInUser) -> Task:
        """
        Updates the status of an existing task.

        Args:
            task_id (UUID): The unique identifier of the task to be updated.
            task_update (TaskUpdate): An object containing the updated task information.
            current_user (LoggedInUser): The user performing the update.

        Returns:
            Task: The updated task object.

        Raises:
            HTTPException: If the task with the given ID is not found.
        """

        with self._db_connection.create_session() as session:
            db_task = session.query(Task).filter(Task.id == task_id).first()
            if not db_task:
                raise HTTPException(status_code=404, detail="Task not found")
            db_task.status = task_update.status
            db_task.updated_by = current_user.id
            session.commit()
            session.refresh(db_task)
            return db_task

    def delete_task(self, task_id: UUID) -> None:
        """
        Deletes a task from the database.

        Args:
            task_id (UUID): The ID of the task to be deleted.

        Raises:
            HTTPException: If the task with the given ID is not found.
        """

        with self._db_connection.create_session() as session:
            db_task = session.query(Task).filter(Task.id == task_id).first()
            if not db_task:
                raise HTTPException(status_code=404, detail="Task not found")
            session.delete(db_task)
            session.commit()

    def get_employee_task_summary(self) -> list[EmployeeTaskSummary]:
        """
        Retrieves a summary of tasks for each employee.

        This method queries the database to get a list of all users with the role "employee".
        For each employee, it calculates the total number of tasks assigned to them and the number of tasks they have completed.
        It then returns a list of EmployeeTaskSummary objects containing this information.

        Returns:
            list[EmployeeTaskSummary]: A list of summaries, each containing the employee's ID, username, total tasks, and completed tasks.
        """

        with self._db_connection.create_session() as session:
            employees = session.query(User).filter(User.role == "employee").all()
            summary: list[EmployeeTaskSummary] = []
            for emp in employees:
                total_tasks = session.query(Task).filter(Task.assignee_id == emp.id).count()
                completed_tasks = session.query(Task).filter(Task.assignee_id == emp.id,
                                                             Task.status == TaskStatus.completed).count()
                summary.append(
                    EmployeeTaskSummary(employee_id=emp.id,
                                        username=emp.username,
                                        total_tasks=total_tasks,
                                        completed_tasks=completed_tasks))
            return summary

    def get_task_by_authenticated_user(self, current_user: LoggedInUser) -> list[Task]:
        with self._db_connection.create_session() as session:
            return session.query(Task).filter(Task.assignee_id == current_user.id).all()
