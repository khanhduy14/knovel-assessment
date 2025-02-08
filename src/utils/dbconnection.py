"""
This module provides utility classes for database connection management.

Classes:
    Base: A base class for SQLAlchemy declarative models.
    DbConnection: An abstract base class for database connection management.

Classes:
    Base:
        A base class for SQLAlchemy declarative models.

    DbConnection:
        An abstract base class for database connection management.

        Properties:
            engine (Engine): An abstract property that should return a SQLAlchemy Engine instance.

        Methods:
            create_session() -> Session: An abstract method that should create and return a new
            SQLAlchemy Session instance.
"""
from abc import ABC, abstractmethod

from sqlalchemy import Engine, Table
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.session import Session


class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy declarative models.

    This class serves as the base class for all SQLAlchemy ORM models in the application.
    It inherits from `DeclarativeBase`, which is a base class provided by SQLAlchemy for
    declarative class definitions.

    Attributes:
        None

    Methods:
        None
    """


class SqlDataTableBase(Base):
    __abstract__ = True
    __tablename__: str
    __table__: Table  # type: ignore


class DbConnection(ABC):
    """
    Abstract base class for database connections.

    This class defines the interface for database connections, including methods
    for obtaining the database engine and creating sessions.

    Attributes:
        engine (Engine): Abstract property that should return the database engine.

    Methods:
        create_session() -> Session: Abstract method that should create and return
        a new database session.
    """

    @property
    @abstractmethod
    def engine(self) -> Engine:
        """
        Establishes and returns a connection to the database engine.

        Returns:
            Engine: An SQLAlchemy Engine instance connected to the database.
        """

    @abstractmethod
    def create_session(self) -> Session:
        """
        Creates and returns a new database session.

        Returns:
            Session: A new database session object.
        """


class DbConnectionFactory(ABC):

    @abstractmethod
    def create(self) -> DbConnection:
        pass
