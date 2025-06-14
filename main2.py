from faker import Faker
import requests
import json
from googletrans import Translator
import asyncio
import pyodbc

async def translate(text):
  translator = Translator()
  translation = await translator.translate(text, dest='pt')
  return translation.text

async def insert_data(conn: pyodbc.Connection, table_name: str, data: dict) -> None:
  """
  Inserts data in a specified table.

  :param conn: The database connection.
  :param table_name: The name of the table to insert data into, directly injected in the SQL Query.
  :param data: A dictionary containing the data to be inserted.
  :return: None
  """
  if not data:
    print("No data was provided. Exiting...")
    return
  
  columns = ', '.join(data.keys())
  placeholders = ', '.join(['?'] * len(data))
  sql_insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

  values = tuple(data.values())

  try:
    def _db_operation():
      with conn.cursor() as cursor:
        cursor.execute(sql_insert_query, values)
      conn.commit()

    await asyncio.to_thread(_db_operation)
    print(f'Successfully inserted data into {table_name}: {data}')

  except pyodbc.Error as er:
    print(f'Error inserting data into {table_name}: {er}')
    try:
      conn.rollback()
      print(f'Operation canceled at {table_name}. Rollback performed.')
    except pyodbc.Error as rer:
      print(f'Error performing rollback: {rer}')

async def main():
  america_countries = requests.get('https://restcountries.com/v3.1/region/America').json()
  # south_america_contries = requests.get('https://restcountries.com/v3.1/subregion/South%20America').json()

  db_server = 'localhost,1433' 
  db_database = 'master' # Substitua pelo nome do seu banco
  db_username = 'sa' 
  db_password = 'MyStr0ngP@ss1' # Substitua pela sua senha
  db_driver = '{ODBC Driver 17 for SQL Server}' 

  conn_str = (
    f'DRIVER={db_driver};'
    f'SERVER={db_server};'
    f'DATABASE={db_database};'
    f'UID={db_username};'
    f'PWD={db_password};'  # Adicionado ponto e vírgula
    f'TrustServerCertificate=yes;' # Use isto para certificados autoassinados/desenvolvimento, remova Trusted_Connection se usar UID/PWD
  )

  conn = None
  try: 
    conn = pyodbc.connect(conn_str)
    print('Successfully connected to the database.')
  except pyodbc.Error as er:
    print(f'Error connecting to the database: {er}')

  country_data: dict = {}

  for country in america_countries:
    country_name = country['name']['official']

    print(f"Original: {country_name}")
    portuguese_name = await translate(country_name)
    print(f"Traduzido: {portuguese_name}")
    country_code = country['cca2']
    print(country_code)

    country_data['Nm_Pais'] = portuguese_name
    country_data['Sg_Pais'] = country_code

    await insert_data(conn, 'Pais', country_data)
    country_data.clear()

  fake = Faker('pt-BR')
  for _ in range(50):
    # print(fake.name())
    # print(fake.address())
    pass

if __name__ == "__main__":
  asyncio.run(main())
