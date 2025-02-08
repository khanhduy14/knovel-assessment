from backend.model.task import Task
from backend.model.user import User
from settings import AppSettings
from utils.dbconnection import DbConnection, SqlDataTableBase

_APP_MANAGED_MODELS: list[type[SqlDataTableBase]] = [Task, User]

_APP_MANAGED_TABLES = [model.__table__ for model in _APP_MANAGED_MODELS]


def drop_app_managed_tables(db_connection: DbConnection):
    """
    Drops all tables that are managed by the application.
    :param db_connection: The database connection to use.
    """
    with db_connection.create_session() as session:
        SqlDataTableBase.metadata.drop_all(db_connection.engine, tables=_APP_MANAGED_TABLES, checkfirst=True)
        session.commit()


def create_app_managed_tables(db_connection: DbConnection):
    """
    Creates all tables that are managed by the application.
    :param db_connection: The database connection to use.
    """
    with db_connection.create_session() as session:
        SqlDataTableBase.metadata.create_all(db_connection.engine, tables=_APP_MANAGED_TABLES, checkfirst=True)
        session.commit()


def main():
    """
    Main function for executing this file directly, which creates the app managed tables.
    """
    config = AppSettings.get_config()
    db_connection = config.db.create()
    create_app_managed_tables(db_connection)


if __name__ == "__main__":
    main()
