from pydantic.dataclasses import dataclass as pd_dataclass
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from utils.dbconnection import DbConnection, DbConnectionFactory


@pd_dataclass
class PostgresqlDbConnectionFactory(DbConnectionFactory):
    connection_string: str

    def create(self) -> DbConnection:
        return PostgresqlDbConnection(self.connection_string)


class PostgresqlDbConnection(DbConnection):
    """
    A database connection class for PostgreSQL databases.

    This class provides a concrete implementation of the `DbConnection` abstract base class
    for PostgreSQL databases. It provides methods for creating a SQLAlchemy Engine instance
    and a SQLAlchemy Session instance for interacting with the database.

    Attributes:
        connection_string (str): The connection string for the PostgreSQL database.

    Methods:
        create_session() -> Session: Creates and returns a new SQLAlchemy Session instance.
    """

    def __init__(self, connection_string: str):
        """
        Initialize the PostgreSQL database connection with the given connection string.

        Args:
            connection_string (str): The connection string for the PostgreSQL database.

        Returns:
            None
        """
        self._connection_string = connection_string

    @property
    def engine(self) -> Engine:
        """
        Get the SQLAlchemy Engine instance for the PostgreSQL database.

        This method creates and returns a new SQLAlchemy Engine instance for the PostgreSQL
        database using the connection string provided during initialization.

        Args:
            None

        Returns:
            Engine: A SQLAlchemy Engine instance for the PostgreSQL database.
        """
        return create_engine(self._connection_string)

    def create_session(self) -> Session:
        """
        Create a new SQLAlchemy Session instance for the PostgreSQL database.

        This method creates and returns a new SQLAlchemy Session instance for the PostgreSQL
        database using the Engine instance obtained from the `engine` property.

        Args:
            None

        Returns:
            Session: A new SQLAlchemy Session instance for the PostgreSQL database.
        """
        engine = self.engine
        return sessionmaker(autocommit=False, bind=engine)()
