from functionalities import *
from db import *
import requests
import asyncio
from faker import Faker

fake = Faker('pt-BR')

async def get_countries():
  america_countries = requests.get('https://restcountries.com/v3.1/region/America').json()
  countries = {} # portuguese_name: original_name
  for country in america_countries:
    country_name = country['name']['official']
    portuguese_name = await translate(country_name)
    countries[portuguese_name] = country_name
  return countries

async def insert_countries(conn):
  america_countries = requests.get('https://restcountries.com/v3.1/region/America').json()

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

async def insert_states(conn):
  country_data: dict = await get_countries()
  db_countries = await get_all_data(conn, 'Pais')
  for country in db_countries:
    

async def insert_people(conn):
  
  for _ in range(50):
    # print(fake.name())
    # print(fake.address())
    pass


async def main():
  conn = await connect()
  await insert_states(conn)

if __name__ == "__main__":
  asyncio.run(main())
