from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, Query

from backend.auth.authenticator import Authenticator
from backend.auth.role_checker import RoleChecker
from backend.model.user import UserType
from backend.viewdata.task import (
    EmployeeTaskSummary,
    TaskCreate,
    TaskOut,
    TaskUpdate,
    ViewTask,
)


def register_task_api(app: FastAPI, task_view: ViewTask, auth: Authenticator):
    """
    Register task-related API endpoints with the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance.
        task_view (ViewTask): The view handling task-related operations.
        auth (Authenticator): The authentication handler.
    """
    router = APIRouter(prefix="/v1/tasks")

    @router.post(
        "/",
        dependencies=[Depends(RoleChecker(auth, allowed_roles=[UserType.employer]))],
        response_model=TaskOut,
    )
    def create_task(task_create: TaskCreate):
        """
        Create a new task.

        Dependencies:
            RoleChecker(auth, allowed_roles=[UserType.employer])
        Request Body:
            TaskCreate
        Response:
            TaskOut
        """
        current_user = auth.get_current_user()
        return TaskOut.model_validate(task_view.create_task(task_create, current_user))

    @router.get(
        "/",
        dependencies=[Depends(RoleChecker(auth, allowed_roles=[UserType.employer]))],
        response_model=list[TaskOut],
    )
    def get_tasks(
            assignee_id: Optional[int] = Query(None),
            status_filter: Optional[str] = Query(None),
            sort_by: Optional[str] = Query("created_at", regex="^(created_at|due_date|status)$"),
            order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    ):
        """
        Retrieve a list of tasks.

        Dependencies:
            RoleChecker(auth, allowed_roles=[UserType.employer])
        Query Parameters:
            assignee_id (Optional[int]): Filter tasks by assignee ID.
            status_filter (Optional[str]): Filter tasks by status.
            sort_by (Optional[str]): Sort tasks by 'created_at', 'due_date', or 'status'.
            order (Optional[str]): Order of sorting, 'asc' or 'desc'.
        Response:
            List[TaskOut]
        """
        tasks = task_view.get_tasks(assignee_id, status_filter, sort_by, order)
        return [TaskOut.model_validate(task) for task in tasks]

    @router.put(
        "/{task_id}",
        dependencies=[Depends(RoleChecker(auth, allowed_roles=[UserType.employee]))],
        response_model=TaskOut,
    )
    def update_task(task_id: UUID, task_update: TaskUpdate):
        """
        Update an existing task.

        Dependencies:
            RoleChecker(auth, allowed_roles=[UserType.employee])
        Path Parameters:
            task_id (UUID)
        Request Body:
            TaskUpdate
        Response:
            TaskOut
        """
        current_user = auth.get_current_user()
        return TaskOut.model_validate(task_view.update_task(task_id, task_update, current_user))

    @router.get(
        "/my-tasks",
        dependencies=[Depends(RoleChecker(auth, allowed_roles=[UserType.employee]))],
        response_model=list[TaskOut],
    )
    def get_my_tasks():
        """
        Retrieve tasks assigned to the authenticated user.

        Dependencies:
            RoleChecker(auth, allowed_roles=[UserType.employee])
        Response:
            List[TaskOut]
        """
        current_user = auth.get_current_user()
        tasks = task_view.get_task_by_authenticated_user(current_user)
        return [TaskOut.model_validate(task) for task in tasks]

    @router.get(
        "/task-summary",
        response_model=list[EmployeeTaskSummary],
        dependencies=[Depends(RoleChecker(auth, allowed_roles=[UserType.employer]))],
    )
    def get_task_summary():
        """
        Retrieve a summary of tasks for employees.

        Dependencies:
            RoleChecker(auth, allowed_roles=[UserType.employer])
        Response:
            List[EmployeeTaskSummary]
        """
        task_summary = task_view.get_employee_task_summary()
        return [EmployeeTaskSummary.model_validate(summary) for summary in task_summary]

    app.include_router(router)
