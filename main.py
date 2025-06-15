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
    response = requests.get(url).json()
    for city in response:
      city_info = {}
      city_info['Nm_Cidade'] = city['nome'].strip()
      city_info['Cd_Estado'] = state['Cd_Estado']
      city_info['Cd_IBGE_Cidade'] = city['codigo_ibge'].strip()
      await insert_data(conn, 'Cidade', city_info)

async def insert_neighborhoods(conn):
  response = None
  with open('neighborhoods.json', 'r') as file:
    response = json.load(file)
  cities = await get_brazilian_cities(conn)
  city_codes = {}
  for city in cities:
    city_codes[city['Nm_Cidade'].strip()] = city['Cd_Cidade']
  # for neighborhood in response:
  for city, neighborhoods in response.items():
    for neighborhood in neighborhoods:
      neighborhood_info = {}
      neighborhood_info['Nm_Bairro'] = neighborhood
      neighborhood_info['Cd_Cidade'] = city_codes[city.upper()]
      await insert_data(conn, 'Bairro', neighborhood_info)

async def insert_people(conn):
  for _ in range(200):
    person_info = {}
    person_info['Ds_Email'] = fake.email()
    await insert_data(conn, 'Pessoa', person_info)

async def insert_physical_persons(conn):
  people_db = await get_all_data(conn, 'Pessoa')
  for i in range(150):
    person_info = {}
    nome_completo = fake.name()
    person_info['Nm_PrimeiroNome'] = nome_completo.split(' ')[0]
    person_info['Nm_Sobrenome'] = ' '.join(nome_completo.split(' ')[1:])
    person_info['Cd_CPF'] = generate_cpf()
    person_info['Cd_Pessoa'] = people_db[i]['Cd_Pessoa']
    print(person_info)
    await insert_data(conn, 'PessoaFisica', person_info)

async def insert_juridical_persons(conn):
  people_db = await get_all_data(conn, 'Pessoa')
  for i in range(150, 200):
    person_info = {}
    person_info['Cd_Pessoa'] = people_db[i]['Cd_Pessoa']
    person_info['Cd_cnpj'] = generate_cnpj()
    person_info['Nm_RazaoSocial'] = fake.company()
    await insert_data(conn, 'PessoaJuridica', person_info)

async def insert_patients(conn):
  people_db = await get_all_data(conn, 'PessoaFisica')
  print(people_db)
  for person in people_db:
    patient_info = {}
    patient_info['Cd_PessoaFisica'] = person['Cd_PessoaFisica']
    await insert_data(conn, 'Paciente', patient_info)

async def insert_workers(conn):
  people_db = await get_all_data(conn, 'PessoaFisica')
  for i in range(100, 123):
    worker_info = {}
    worker_info['Cd_PessoaFisica'] = people_db[i]['Cd_PessoaFisica']
    await insert_data(conn, 'Funcionario', worker_info)

async def insert_vaccine_centers(conn):
  companies_db = await get_all_data(conn, 'PessoaJuridica')
  for i in range(0, 40):
    vaccine_center_info = {}
    vaccine_center_info['Nm_CentroVacinacao'] = companies_db[i]['Nm_RazaoSocial']
    vaccine_center_info['Cd_PessoaJuridica'] = companies_db[i]['Cd_PessoaJuridica']
    await insert_data(conn, 'CentroVacinacao', vaccine_center_info)

async def insert_factories(conn):
  companies_db = await get_all_data(conn, 'PessoaJuridica')
  for i in range(40, 50):
    factory_info = {}
    factory_info['Nm_Fabrica'] = companies_db[i]['Nm_RazaoSocial']
    factory_info['Cd_PessoaJuridica'] = companies_db[i]['Cd_PessoaJuridica']
    await insert_data(conn, 'Fabrica', factory_info)

async def insert_vacines(conn):
  pass

async def insert_logradouro(conn, description):
  logradouro_info = {}
  logradouro_info['Ds_Logradouro'] = description
  await insert_data(conn, 'Logradouro', logradouro_info)

async def insert_addresses(conn):
  total_neighborhood_not_found = 0
  neighborhood_not_found = []

  logradouros = await get_all_data(conn, 'Logradouro')
  logradouros = {logradouro['Ds_Logradouro'].strip(): logradouro['Cd_Logradouro'] for logradouro in logradouros}
  neighborhoods = await get_all_data(conn, 'Bairro')
  neighborhoods = {neighborhood['Nm_Bairro'].strip(): neighborhood['Cd_Bairro'] for neighborhood in neighborhoods}
  logradouros_types = await get_all_data(conn, 'TipoLogradouro')
  logradouros_types = {logradouro_type['Ds_TipoLogradouro'].strip(): logradouro_type['Cd_TipoLogradouro'] for logradouro_type in logradouros_types}
  complement_type = await get_all_data(conn, 'TipoComplemento')
  complement_type = {complement['Ds_TipoComplemento'].strip(): complement['Cd_TipoComplemento'] for complement in complement_type}

  response = None
  with open('addresses.json', 'r') as file:
    response = json.load(file)['enderecos']
  
  for address in response:

    address['TipoComplemento'] = address['Complemento'].split()[0] if address['Complemento'] else ''
    address['Complemento'] = ' '.join(address['Complemento'].split()[1:]) if address['Complemento'] else ''

    if address['Logradouro'] not in logradouros.keys():
      await insert_data(conn, 'Logradouro', {'Ds_Logradouro': address['Logradouro']})
      logradouros = await get_all_data(conn, 'Logradouro')
      logradouros = {logradouro['Ds_Logradouro'].strip(): logradouro['Cd_Logradouro'] for logradouro in logradouros}

    if address['Bairro'] not in neighborhoods.keys():
      print('Warning! Neighborhood not found, register it manually.')
      total_neighborhood_not_found += 1
      neighborhood_not_found.append(address['Bairro'])
      continue
    if address['TipoLogradouro'] not in logradouros_types.keys():
      await insert_data(conn, 'TipoLogradouro', {'Ds_TipoLogradouro': address['TipoLogradouro']})
      logradouros_types = await get_all_data(conn, 'TipoLogradouro')
      logradouros_types = {logradouro_type['Ds_TipoLogradouro'].strip(): logradouro_type['Cd_TipoLogradouro'] for logradouro_type in logradouros_types}

    if address['TipoComplemento'] not in complement_type.keys():
      await insert_data(conn, 'TipoComplemento', {'Ds_TipoComplemento': address['TipoComplemento']})
      complement_type = await get_all_data(conn, 'TipoComplemento')
      complement_type = {complement['Ds_TipoComplemento'].strip(): complement['Cd_TipoComplemento'] for complement in complement_type}

    address_info = {}
    address_info['Cd_Logradouro'] = logradouros[address['Logradouro']]
    address_info['Cd_Bairro'] = neighborhoods[address['Bairro']]
    address_info['Cd_TipoLogradouro'] = logradouros_types[address['TipoLogradouro']]
    address_info['Cd_TipoComplemento'] = complement_type[address['TipoComplemento']]
    address_info['Ds_Complemento'] = address['Complemento']
    address_info['Nu_Local'] = address['Numero']
    address_info['Cd_Cep'] = address['CEP']
    await insert_data(conn, 'Endereco', address_info)
  print(f'Total neighborhoods not found: {total_neighborhood_not_found}')
  print(f'Neighborhoods not found: {neighborhood_not_found}')

async def insert_addresses_list(conn):
  address_types = await get_all_data(conn, 'TipoEndereco')
  address_types = {address_type['Ds_TipoEndereco'].strip(): address_type['Cd_TipoEndereco'] for address_type in address_types}

  used_addresses = 0

  addresses = await get_all_data(conn, 'Endereco')
  addresses = [address['Cd_Endereco'] for address in addresses]

  factories = await get_all_data(conn, 'Fabrica')
  factories = [factory['Cd_PessoaJuridica'] for factory in factories]
  print(factories)
  factories_persons = [await get_by_id(conn, 'PessoaJuridica', factory_id) for factory_id in factories]
  print(factories_persons)
  factories_persons = [factory_person['Cd_Pessoa'] for factory_person in factories_persons]

  for i in range(len(factories_persons)):
    address_list_info = {}
    address_list_info['Cd_Pessoa'] = factories_persons[i]
    address_list_info['Cd_Endereco'] = addresses[i%2]
    address_list_info['Cd_TipoEndereco'] = address_types['Matriz']
    await insert_data(conn, 'ListaEndereco', address_list_info)
    used_addresses = (i+used_addresses)%2
    

  vaccine_centers = await get_all_data(conn, 'CentroVacinacao')
  vaccine_centers = [vaccine_center['Cd_PessoaJuridica'] for vaccine_center in vaccine_centers]
  vaccine_centers_persons = [await get_by_id(conn, 'PessoaJuridica', vaccine_center_id) for vaccine_center_id in vaccine_centers]
  vaccine_centers_persons = [vaccine_center_person['Cd_Pessoa'] for vaccine_center_person in vaccine_centers_persons]

  for i in range(len(vaccine_centers_persons)):
    address_list_info = {}
    address_list_info['Cd_Pessoa'] = vaccine_centers_persons[i]
    address_list_info['Cd_Endereco'] = addresses[(i+used_addresses)%4]
    address_list_info['Cd_TipoEndereco'] = address_types['Filial']
    await insert_data(conn, 'ListaEndereco', address_list_info)

    used_addresses = (i+used_addresses)%4 # 15

  patients = await get_all_data(conn, 'Paciente')
  patients = [patient['Cd_PessoaFisica'] for patient in patients]
  patients_persons = [await get_by_id(conn, 'PessoaFisica', patient_id) for patient_id in patients]
  patients_persons = [patient_person['Cd_Pessoa'] for patient_person in patients_persons]

  for i in range(len(patients_persons)):
    address_list_info = {}
    address_list_info['Cd_Pessoa'] = patients_persons[i]
    address_list_info['Cd_Endereco'] = addresses[(used_addresses+i)%12]
    address_list_info['Cd_TipoEndereco'] = address_types['Residencia']
    await insert_data(conn, 'ListaEndereco', address_list_info)

    used_addresses = (i+used_addresses)%15 # ~28

  workers = await get_all_data(conn, 'Funcionario')
  workers = [worker['Cd_PessoaFisica'] for worker in workers]
  workers_persons = [await get_by_id(conn, 'PessoaFisica', worker_id) for worker_id in workers]
  workers_persons = [worker_person['Cd_Pessoa'] for worker_person in workers_persons]

  for i in range(len(workers_persons)):
    address_list_info = {}
    address_list_info['Cd_Pessoa'] = workers_persons[i]
    address_list_info['Cd_Endereco'] = addresses[(used_addresses+i)%3]
    address_list_info['Cd_TipoEndereco'] = address_types['Residencia']
    await insert_data(conn, 'ListaEndereco', address_list_info)

async def main():
  conn = await connect()
  # await insert_countries(conn)
  # await insert_states(conn)
  # await insert_cities(conn)
  # await insert_neighborhoods(conn)
  # await insert_people(conn)
  # await insert_physical_persons(conn)
  # await insert_juridical_persons(conn)
  # await insert_patients(conn)
  # await insert_workers(conn)
  # await insert_vaccine_centers(conn)
  # await insert_factories(conn)
  # await insert_addresses(conn)
  await insert_addresses_list(conn)
  conn.close()


if __name__ == "__main__":
  asyncio.run(main())
