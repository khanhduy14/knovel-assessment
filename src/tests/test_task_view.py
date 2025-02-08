import unittest
from datetime import datetime
from typing import Any
from unittest.mock import patch
from uuid import uuid4

from fastapi import HTTPException
from pydantic import ValidationError

from backend.model.task import Task, TaskStatus
from backend.model.user import LoggedInUser, User, UserType
from backend.viewdata.task import TaskCreate, TaskUpdate, ViewTask


class TestTaskView(unittest.TestCase):

    def setUp(self):
        self._db_patcher = patch('backend.viewdata.task.DbConnection')
        self._mock_db_connection = self._db_patcher.start()
        self.addCleanup(self._db_patcher.stop)

    def test_task_create_valid(self):
        task_data: dict[str, Any] = {
            "title": "Test Task",
            "description": "This is a test task",
            "due_date": datetime.now(),
            "assignee_id": uuid4()
        }
        task = TaskCreate(**task_data)
        self.assertEqual(task.title, task_data["title"])
        self.assertEqual(task.description, task_data["description"])
        self.assertEqual(task.due_date, task_data["due_date"])
        self.assertEqual(task.assignee_id, task_data["assignee_id"])

    def test_task_create_invalid(self):
        task_data: dict[str, Any] = {
            "title": "Test Task",
            "description": "This is a test task",
            "due_date": "invalid date",
            "assignee_id": "invalid uuid"
        }
        with self.assertRaises(ValidationError):
            TaskCreate(**task_data)

    def test_task_update_valid(self):
        task_data: dict[str, Any] = {"status": "Completed"}
        task = TaskUpdate(**task_data)
        self.assertEqual(task.status, task_data["status"])

    def test_task_update_invalid(self):
        task_data: dict[str, Any] = {"status": "invalid status"}
        with self.assertRaises(ValidationError):
            TaskUpdate(**task_data)

    def test_create_task(self):
        mock_session = self._mock_db_connection.return_value.create_session.return_value.__enter__.return_value
        mock_user = User(id=uuid4(), role=UserType.employee)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user

        db_connection = self._mock_db_connection()
        view_task = ViewTask(db_connection)
        task_data = TaskCreate(title="Test Task",
                               description="This is a test task",
                               due_date=datetime.now(),
                               assignee_id=mock_user.id)
        current_user = LoggedInUser(id=uuid4(), username="testuser", role=UserType.employer)
        created_task = view_task.create_task(task_data, current_user)

        self.assertEqual(created_task.title, task_data.title)
        self.assertEqual(created_task.description, task_data.description)
        self.assertEqual(created_task.assignee_id, task_data.assignee_id)
        self.assertEqual(created_task.creator_id, current_user.id)

    def test_create_task_invalid_assignee(self):
        mock_session = self._mock_db_connection.return_value.create_session.return_value.__enter__.return_value
        mock_session.query.return_value.filter.return_value.first.return_value = None

        db_connection = self._mock_db_connection()
        view_task = ViewTask(db_connection)
        task_data = TaskCreate(title="Test Task",
                               description="This is a test task",
                               due_date=datetime.now(),
                               assignee_id=uuid4())
        current_user = LoggedInUser(id=uuid4(), username="testuser", role=UserType.employer)

        with self.assertRaises(HTTPException):
            view_task.create_task(task_data, current_user)

    def test_update_task(self):
        mock_session = self._mock_db_connection.return_value.create_session.return_value.__enter__.return_value
        mock_task = Task(id=uuid4(), title="Test Task", description="This is a test task", status=TaskStatus.pending)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_task

        db_connection = self._mock_db_connection()
        view_task = ViewTask(db_connection)
        task_update = TaskUpdate(status=TaskStatus.completed)
        current_user = LoggedInUser(id=uuid4(), username="testuser", role=UserType.employer)
        updated_task = view_task.update_task(mock_task.id, task_update, current_user)

        self.assertEqual(updated_task.status, task_update.status)
        self.assertEqual(updated_task.updated_by, current_user.id)

    def test_update_task_not_found(self):
        mock_session = self._mock_db_connection.return_value.create_session.return_value.__enter__.return_value
        mock_session.query.return_value.filter.return_value.first.return_value = None

        db_connection = self._mock_db_connection()
        view_task = ViewTask(db_connection)
        task_update = TaskUpdate(status=TaskStatus.completed)
        current_user = LoggedInUser(id=uuid4(), username="testuser", role=UserType.employer)

        with self.assertRaises(HTTPException):
            view_task.update_task(uuid4(), task_update, current_user)

    def test_delete_task(self):
        mock_session = self._mock_db_connection.return_value.create_session.return_value.__enter__.return_value
        mock_task = Task(id=uuid4(), title="Test Task", description="This is a test task", status=TaskStatus.pending)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_task

        db_connection = self._mock_db_connection()
        view_task = ViewTask(db_connection)
        view_task.delete_task(mock_task.id)

        mock_session.delete.assert_called_once_with(mock_task)
        mock_session.commit.assert_called_once()

    def test_delete_task_not_found(self):
        mock_session = self._mock_db_connection.return_value.create_session.return_value.__enter__.return_value
        mock_session.query.return_value.filter.return_value.first.return_value = None

        db_connection = self._mock_db_connection()
        view_task = ViewTask(db_connection)

        with self.assertRaises(HTTPException):
            view_task.delete_task(uuid4())

    def test_get_tasks(self):
        mock_session = self._mock_db_connection.return_value.create_session.return_value.__enter__.return_value
        mock_task = Task(id=uuid4(), title="Test Task", description="This is a test task", status=TaskStatus.pending)
        mock_session.query.return_value.all.return_value = [mock_task]

        db_connection = self._mock_db_connection()
        view_task = ViewTask(db_connection)
        tasks = view_task.get_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, mock_task.title)

    def test_get_employee_task_summary(self):
        mock_session = self._mock_db_connection.return_value.create_session.return_value.__enter__.return_value
        mock_user = User(id=uuid4(), username="testuser", role=UserType.employee)

        mock_session.query.return_value.filter.return_value.all.return_value = [mock_user]
        mock_session.query.return_value.filter.return_value.count.side_effect = [1, 1]

        db_connection = self._mock_db_connection()
        view_task = ViewTask(db_connection)
        summary = view_task.get_employee_task_summary()

        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0].username, mock_user.username)
        self.assertEqual(summary[0].total_tasks, 1)
        self.assertEqual(summary[0].completed_tasks, 1)

    def test_get_task_by_authenticated_user(self):
        mock_session = self._mock_db_connection.return_value.create_session.return_value.__enter__.return_value
        mock_task = Task(id=uuid4(), title="Test Task", description="This is a test task", status=TaskStatus.pending)
        mock_session.query.return_value.filter.return_value.all.return_value = [mock_task]

        db_connection = self._mock_db_connection()
        view_task = ViewTask(db_connection)
        current_user = LoggedInUser(id=uuid4(), username="testuser", role=UserType.employee)
        tasks = view_task.get_task_by_authenticated_user(current_user)

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, mock_task.title)
