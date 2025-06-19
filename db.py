import asyncio
import logging
import os

import pyodbc
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def connect() -> pyodbc.Connection:

    load_dotenv()

    db_server = os.getenv("DB_SERVER", "localhost,1433")
    db_database = os.getenv("DB_DATABASE", "master")
    db_username = os.getenv("DB_USERNAME", "sa")
    db_password = os.getenv("DB_PASSWORD", "MyStr0ngP@ss1")
    db_driver = os.getenv("DB_DRIVER", "{ODBC Driver 17 for SQL Server}")

    conn_str = (
        f"DRIVER={db_driver};"
        f"SERVER={db_server};"
        f"DATABASE={db_database};"
        f"UID={db_username};"
        f"PWD={db_password};"
        # Used in development, remove if in production
        f"TrustServerCertificate=yes;"
    )

    conn = None
    try:
        conn = pyodbc.connect(conn_str)
        logging.info("Success! Successfully connected to the database.")
    except pyodbc.Error as er:
        logging.warning(f"Warning! Error connecting to the database: {er}")

    return conn


async def insert_data(conn: pyodbc.Connection, table_name: str, data: dict) -> None:
    """
    Inserts data in a specified table.

    :param conn: The database connection.
    :param table_name: The name of the table to insert data into,
    directly injected in the SQL Query.
    :param data: A dictionary containing the data to be inserted.
    :return: None
    """
    if not data:
        logging.warning("Warning! No data was provided. Exiting...")
        return

    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    sql_insert_query = f"""
        INSERT INTO {table_name} ({columns})
        VALUES ({placeholders})
    """

    values = tuple(data.values())

    try:

        def _db_operation():
            with conn.cursor() as cursor:
                cursor.execute(sql_insert_query, values)
            conn.commit()

        await asyncio.to_thread(_db_operation)
        logging.info(f"""Success! Inserted data into {table_name}: {data}""")

    except pyodbc.Error as er:
        logging.warning(f"Warning! Error inserting data into {table_name}: {er}")
        try:
            conn.rollback()
            logging.warning(
                f"Warning! Operation canceled at {table_name}. Rollback performed."
            )
        except pyodbc.Error as rer:
            logging.warning(f"Warning! Error performing rollback: {rer}")


async def get_all_data(conn: pyodbc.Connection, table_name: str) -> list:
    """
    Retrieves all data from a specified table.

    :param conn: The database connection.
    :param table_name: The name of the table to retrieve data from.
                       This name is directly injected into the SQL query,
                       so it should come from a trusted source.
    :return: A list of dictionaries, where each dictionary represents a row,
             or an empty list if an error occurs or no data is found.
    """
    if not table_name:
        print("Warning! No table name was provided. Exiting...")
        return []

    # Warning! No safety checks, SQL-Injection is possible
    sql_select_query = f"SELECT * FROM {table_name}"

    try:

        def _db_operation():
            with conn.cursor() as cursor:
                cursor.execute(sql_select_query)
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]

        return await asyncio.to_thread(_db_operation)
    except pyodbc.Error as er:
        logging.warning(f"Warning! Error retrieving data from {table_name}: {er}")
        return []


async def get_brazilian_states(conn: pyodbc.Connection) -> list:
    query = """
  SELECT Estado.Cd_Estado, Estado.Nm_Estado, Estado.Sg_Estado
  FROM Pais
  JOIN Estado
  On Pais.Cd_Pais = Estado.Cd_Pais
  WHERE Pais.Sg_Pais = 'BR';
  """
    try:

        def _db_operation():
            with conn.cursor() as cursor:
                cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]

        return await asyncio.to_thread(_db_operation)
    except pyodbc.Error as er:
        logging.warning(f"Warning! Error retrieving data from Brazil: {er}")
        return []


async def get_brazilian_cities(conn: pyodbc.Connection) -> list:
    query = """
  SELECT Cidade.Cd_Cidade, Cidade.Nm_Cidade, Cidade.Cd_IBGE_Cidade
  FROM Estado
  JOIN Cidade
  ON Estado.Cd_Estado = Cidade.Cd_Estado;
  """
    try:

        def _db_operation():
            with conn.cursor() as cursor:
                cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]

        return await asyncio.to_thread(_db_operation)
    except pyodbc.Error as er:
        logging.warning(f"Warning! Error retrieving data from States: {er}")
        return []


async def get_by_id(
    conn: pyodbc.Connection, table_name: str, id_value: int
) -> dict | None:
    """
    Retrieves a single record from a table by its ID.
    Assumes the ID column is named 'Cd_TableName'.
    """
    query = f"SELECT * FROM {table_name} WHERE Cd_{table_name} = ?;"
    try:

        def _db_operation():
            with conn.cursor() as cursor:
                cursor.execute(query, id_value)
                row = cursor.fetchone()
                if row:
                    columns = [column[0] for column in cursor.description]
                    return dict(zip(columns, row))
            return None  # Return None if no row is found

        return await asyncio.to_thread(_db_operation)
    except pyodbc.Error as er:
        logging.warning(f"Warning! Error retrieving data from {table_name}: {er}")
        return None


async def get_where(
    conn: pyodbc.Connection, table_name: str, where_clause: str
) -> list:
    query = f"SELECT * FROM {table_name} WHERE {where_clause};"
    try:

        def _db_operation():
            with conn.cursor() as cursor:
                cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            return None

        return await asyncio.to_thread(_db_operation)
    except pyodbc.Error as er:
        logging.warning(f"Warning! Error retrieving data from {table_name}: {er}")
        return []


async def main():
    conn = await connect()
    test_where = await get_where(conn, "Paciente", "Cd_Paciente = 200")
    logging.debug(test_where)
    conn.close()


if __name__ == "__main__":
    asyncio.run(main())
