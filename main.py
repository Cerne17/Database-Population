from functionalities import *
from db import *
import requests
import asyncio
from faker import Faker
from functools import cache
import json

fake = Faker('pt-BR')

@cache
async def get_countries():
  america_countries = requests.get('https://restcountries.com/v3.1/region/America').json()
  countries = {} # portuguese_name: original_name
  countries_non_official = {}
  for country in america_countries:
    country_name = country['name']['official']
    common_name = country['name']['common']
    portuguese_name = await translate(country_name)
    countries[portuguese_name] = country_name
    countries_non_official[portuguese_name] = common_name
  return countries, countries_non_official

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
  country_data, common_data = await get_countries()
  db_countries = await get_all_data(conn, 'Pais')
  url = "https://countriesnow.space/api/v0.1/countries/states"
  payload = {}
  headers = {}
  response =  requests.request("GET", url, headers=headers, data=payload).json()['data']
  states_data = {}
  for state in response:
    states_data[state['name']] = state['states']
  print(states_data.keys())


  for country in db_countries:
    portuguese_name = country['Nm_Pais'].strip()
    original_name = country_data[portuguese_name].strip()
    common_name = common_data[portuguese_name].strip()

    if common_name in states_data:
      states = states_data[common_name]
      for state in states:
          state_info = {}
          state_info['Cd_Pais'] = country['Cd_Pais']
          state_info['Nm_Estado'] = state['name']
          state_info['Sg_Estado'] = state['state_code']
          state_info['Cd_Area'] = state['state_code']
          await insert_data(conn, 'Estado', state_info)

async def insert_cities(conn):
  for state in await get_brazilian_states(conn):
    print(state)
    state_code = state['Sg_Estado'].strip()
    url = f"https://brasilapi.com.br/api/ibge/municipios/v1/{state_code}?providers=dados-abertos-br,gov,wikipedia"
    print(url)
    response = requests.get(url).json()
    print(response)
    for city in response:
      city_info = {}
      city_info['Nm_Cidade'] = city['nome'].strip()
      city_info['Cd_Estado'] = state['Cd_Estado']
      city_info['Cd_IBGE_Cidade'] = city['codigo_ibge'].strip()
      await insert_data(conn, 'Cidade', city_info)


async def insert_people(conn):
  
  for _ in range(50):
    # print(fake.name())
    # print(fake.address())
    pass


async def main():
  conn = await connect()
  # await insert_countries(conn)
  # await insert_states(conn)
  await insert_cities(conn)

if __name__ == "__main__":
  asyncio.run(main())
