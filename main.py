from functionalities import *
from db import *
import requests
import asyncio
from faker import Faker
from functools import cache
import json
from random import choice
from datetime import datetime, timedelta

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

    portuguese_name = await translate(country_name)
    country_code = country['cca2']

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
  print(f'Warning! Total neighborhoods not found: {total_neighborhood_not_found}')
  print(f'Warning! Neighborhoods not found: {neighborhood_not_found}')

async def insert_addresses_list(conn):
  address_types = await get_all_data(conn, 'TipoEndereco')
  address_types = {address_type['Ds_TipoEndereco'].strip(): address_type['Cd_TipoEndereco'] for address_type in address_types}

  used_addresses = 0

  addresses = await get_all_data(conn, 'Endereco')
  addresses = [address['Cd_Endereco'] for address in addresses]

  factories = await get_all_data(conn, 'Fabrica')
  factories = [factory['Cd_PessoaJuridica'] for factory in factories]
  factories_persons = [await get_by_id(conn, 'PessoaJuridica', factory_id) for factory_id in factories]
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
    address_list_info['Cd_Endereco'] = addresses[(used_addresses+i)%5]
    address_list_info['Cd_TipoEndereco'] = address_types['Residencia']
    await insert_data(conn, 'ListaEndereco', address_list_info)

    used_addresses = (i+used_addresses)%5 # ~28

async def insert_vaccine_types(conn):
  vaccine_types = None
  with open('vaccinetypes.json', 'r') as file:
    vaccine_types = json.load(file)['TipoVacina']
  for vaccine_type in vaccine_types:
    vaccine_type_info = {}
    vaccine_type_info['Nm_TipoVacina'] = vaccine_type['Nm_TipoVacina']
    vaccine_type_info['Pz_Validade'] = vaccine_type['Pz_Validade']
    vaccine_type_info['Pz_ValidadeAposAbrir'] = vaccine_type['Pz_ValidadeAposAbrir']
    await insert_data(conn, 'TipoVacina', vaccine_type_info)

async def insert_ships(conn):
  ship_sizes = [30, 50, 100]
  factories = await get_all_data(conn, 'Fabrica')
  factories = [factory['Cd_Fabrica'] for factory in factories]
  vaccine_centers = await get_all_data(conn, 'CentroVacinacao')
  vaccine_centers = [vaccine_center['Cd_CentroVacinacao'] for vaccine_center in vaccine_centers]
  vaccine_types = await get_all_data(conn, 'TipoVacina')
  vaccine_types = {vaccine_type['Cd_TipoVacina']: vaccine_type['Pz_Validade'] for vaccine_type in vaccine_types}
  vaccine_types_id = list(vaccine_types.keys())

  for _ in range(150):
    factory = choice(factories)
    vaccine_type = choice(vaccine_types_id)
    vaccine_center = choice(vaccine_centers)
    size = choice(ship_sizes)
    manufactured_date = fake.date_time_between(start_date='-1y')
    expiration_date = manufactured_date + timedelta(days=vaccine_types[vaccine_type])

    ship_info = {}
    ship_info['Cd_Fabrica'] = factory
    ship_info['Cd_TipoVacina'] = vaccine_type
    ship_info['Cd_CentroVacinacao'] = vaccine_center
    ship_info['Dt_Fabricacao'] = manufactured_date
    ship_info['Dt_Validade'] = expiration_date
    ship_info['Nu_QuantidadeAmpolas'] = size
    await insert_data(conn, 'Lote', ship_info)

async def insert_shifts(conn):
  shifts_durations_in_hours = [8, 12, 16, 24, 48]
  workers = await get_all_data(conn, 'Funcionario')
  workers = [worker['Cd_Funcionario'] for worker in workers]
  vaccination_centers = await get_all_data(conn, 'CentroVacinacao')
  vaccination_centers = [vaccination_center['Cd_CentroVacinacao'] for vaccination_center in vaccination_centers]

  for i in range(2500):
    worker = choice(workers)
    vaccination_center = choice(vaccination_centers)
    shift_duration = choice(shifts_durations_in_hours)
    shift_start = fake.date_time_between(start_date='-5y', end_date='-3y')
    shift_end = shift_start + timedelta(hours=shift_duration)

    shift_info = {}
    shift_info['Cd_Funcionario'] = worker
    shift_info['Cd_CentroVacinacao'] = vaccination_center
    shift_info['Dt_Inicio'] = shift_start
    shift_info['Dt_Termino'] = shift_end
    await insert_data(conn, 'Plantao', shift_info)

async def insert_ampoules(conn):
  ships = await get_all_data(conn, 'Lote')
  ships = {ship['Cd_Lote']: [ship['Nu_QuantidadeAmpolas'], ship['Dt_Fabricacao'], ship['Dt_Validade']] for ship in ships}

  for ship in ships.keys():
    for _ in range(int(ships[ship][0])):
      ampoule_info = {}
      ampoule_info['Cd_Lote'] = ship
      ampoule_info['Dt_Abertura'] = fake.date_time_between(start_date=ships[ship][1], end_date=ships[ship][2])
      await insert_data(conn, 'Ampola', ampoule_info)

async def insert_vaccines(conn):
  shifts = await get_all_data(conn, 'Plantao')
  shifts = {shift['Cd_Plantao']: [shift['Cd_Funcionario'], shift['Cd_CentroVacinacao'], shift['Dt_Inicio'], shift['Dt_Termino']] for shift in shifts}
  patients = await get_all_data(conn, 'Paciente')
  patients = [patient['Cd_Paciente'] for patient in patients]
  ampoules = await get_all_data(conn, 'Ampola')
  ampoules = {ampoule['Cd_Ampola']: [ampoule['Cd_Lote'], ampoule['Dt_Abertura']] for ampoule in ampoules}
  for _ in range(1000):
    vaccine_info = {}
    shift = choice(list(shifts.keys()))
    vaccine_worker = shifts[shift][0]
    vaccine_date = fake.date_time_between(start_date=shifts[shift][2], end_date=shifts[shift][3])
    
    vaccine_info['Cd_Paciente'] = choice(patients)
    vaccine_info['Cd_Funcionario'] = vaccine_worker
    vaccine_info['Cd_Ampola'] = choice(list(ampoules.keys()))
    vaccine_info['Dt_Vacinacao'] = vaccine_date
    await insert_data(conn, 'Vacinacao', vaccine_info)

async def generate_patient_with_all_vaccines(conn):
  patient_id = 200 # Chosen manually
  shifts = await get_all_data(conn, 'Plantao')
  shifts = {shift['Cd_Plantao']: [shift['Cd_Funcionario'], shift['Cd_CentroVacinacao'], shift['Dt_Inicio'], shift['Dt_Termino']] for shift in shifts}
  ampoules = await get_all_data(conn, 'Ampola')
  ampoules = {ampoule['Cd_Ampola']: [ampoule['Cd_Lote'], ampoule['Dt_Abertura']] for ampoule in ampoules}
  ships = [await get_by_id(conn, 'Lote', ampoules[ampoule_id][0]) for ampoule_id in ampoules.keys()]
  ships = {ship['Cd_Lote']: [ship['Cd_TipoVacina'], ship['Cd_CentroVacinacao']] for ship in ships}
  vaccine_types = await get_all_data(conn, 'TipoVacina')
  vaccine_types = [vaccine_type['Cd_TipoVacina'] for vaccine_type in vaccine_types]
  for type in vaccine_types:
    ship_id = None
    vaccine_center_id = None
    for ship in ships.keys():
      if ships[ship][0] == type:
        ship_id = ship
        vaccine_center_id = ships[ship][1]
        break
    if ship_id is None:
      print(f'Warning! Vaccine Type {type} has no ship available. Add manually. Skipping...')
      continue

    ampoule_id = None
    ampoule_open_date = None
    for ampoule in ampoules.keys():
      if ampoules[ampoule][0] == ship_id:
        ampoule_id = ampoule
        ampoule_open_date = ampoules[ampoule][1]
        break
    if ampoule_id is None:
        print(f'Warning! Ship {ship_id} has no ampoules available. Add manually. Skipping...')
        continue
    
    shift_id = None
    worker_id = None
    shift_start = None
    shift_end = None
    for shift in shifts.keys():
      if shifts[shift][1] == vaccine_center_id and shifts[shift][2] > ampoule_open_date:
        shift_id = shift
        worker_id = shifts[shift][0]
        shift_start = shifts[shift][2]
        shift_end = shifts[shift][3]
        break
    if shift_id is None:
      print(f'Warning! Vaccine center {vaccine_center_id} has no shifts available. Add manually. Skipping...')
      continue

    vaccine_info ={}
    vaccine_info['Cd_Paciente'] = patient_id
    vaccine_info['Cd_Funcionario'] = worker_id
    vaccine_info['Cd_Ampola'] = ampoule_id
    vaccine_info['Dt_Vacinacao'] = fake.date_time_between(start_date=shift_start, end_date=shift_end)
    await insert_data(conn, 'Vacinacao', vaccine_info)

async def generate_patient_with_all_factories(conn):
  patient_id = 200 # Chosen manually
  
  # Fetch all necessary data once to minimize DB calls
  all_shifts_raw = await get_all_data(conn, 'Plantao')
  all_ampoules_raw = await get_all_data(conn, 'Ampola')
  all_factories_raw = await get_all_data(conn, 'Fabrica')

  # Prepare data for easier lookup
  shifts = {
      shift['Cd_Plantao']: {
          'worker_id': shift['Cd_Funcionario'],
          'center_id': shift['Cd_CentroVacinacao'],
          'start_time': shift['Dt_Inicio'],
          'end_time': shift['Dt_Termino']
      } for shift in all_shifts_raw
  }

  ampoules = {
      ampoule['Cd_Ampola']: {
          'ship_id': ampoule['Cd_Lote'],
          'open_date': ampoule['Dt_Abertura']
      } for ampoule in all_ampoules_raw
  }

  # We'll need to fetch ship details individually as they are linked to ampoules
  # and then to factories.

  factories = [factory['Cd_Fabrica'] for factory in all_factories_raw]

  for factory_id in factories:
    print(f"Processing factory ID: {factory_id}")
    ship_from_factory_id = None
    vaccine_center_for_ship = None
    
    # Find a ship (Lote) that came from the current factory
    # This requires iterating through ampoules to find their ships, then checking ship's factory
    # This is inefficient if done repeatedly. A better approach would be to get all ships
    # and map them to factories if possible, or accept the current lookup strategy.
    # For this example, we'll find the first suitable ship.

    found_ship_for_factory = False
    target_ship_id = None
    target_ampoule_id = None
    target_ampoule_open_date = None

    # Find an ampoule whose ship (Lote) is from the current factory
    for amp_id, amp_data in ampoules.items():
        ship_details = await get_by_id(conn, 'Lote', amp_data['ship_id'])
        if ship_details and ship_details['Cd_Fabrica'] == factory_id:
            target_ship_id = amp_data['ship_id']
            vaccine_center_for_ship = ship_details['Cd_CentroVacinacao']
            target_ampoule_id = amp_id
            target_ampoule_open_date = amp_data['open_date']
            found_ship_for_factory = True
            print(f"  Found ship ID: {target_ship_id} from factory {factory_id} via ampoule {target_ampoule_id}")
            break # Found a suitable ampoule/ship for this factory

    if not found_ship_for_factory:
      print(f"Warning! No ship/ampoule found originating from factory {factory_id}. Skipping this factory.")
      continue

    # Find a suitable shift for vaccination
    found_shift = False
    target_shift_id = None
    target_worker_id = None
    target_shift_start = None
    target_shift_end = None

    for shift_id, shift_data in shifts.items():
      # Check if shift is at the correct vaccination center
      # and if the shift starts after the ampoule was opened (or on the same day)
      if shift_data['center_id'] == vaccine_center_for_ship and \
         shift_data['start_time'] >= target_ampoule_open_date:
        target_shift_id = shift_id
        target_worker_id = shift_data['worker_id']
        target_shift_start = shift_data['start_time']
        target_shift_end = shift_data['end_time']
        found_shift = True
        print(f"  Found shift ID: {target_shift_id} at center {vaccine_center_for_ship}")
        break

    if not found_shift:
      print(f"Warning! No suitable shift found for ampoule {target_ampoule_id} (from factory {factory_id}) at vaccine center {vaccine_center_for_ship}. Skipping this factory.")
      continue

    # All conditions met, prepare and insert vaccination record
    vaccine_info = {}
    vaccine_info['Cd_Paciente'] = patient_id
    vaccine_info['Cd_Funcionario'] = target_worker_id
    vaccine_info['Cd_Ampola'] = target_ampoule_id
    # Ensure vaccination date is within the shift and after ampoule opening
    # For simplicity, using a date within the shift. A more precise logic might be needed
    # if fake.date_time_between needs to consider target_ampoule_open_date as well.
    # Current fake.date_time_between might pick a date before ampoule was opened if shift started earlier.
    
    # Ensure vaccination date is after ampoule opening and within shift
    possible_vaccination_start_date = max(target_shift_start, target_ampoule_open_date)
    if possible_vaccination_start_date > target_shift_end:
        print(f"Warning! Ampoule {target_ampoule_id} opened after shift {target_shift_id} ended. Skipping this factory.")
        continue

    vaccine_info['Dt_Vacinacao'] = fake.date_time_between(start_date=possible_vaccination_start_date, end_date=target_shift_end)
    
    await insert_data(conn, 'Vacinacao', vaccine_info)
    print(f"  Successfully recorded vaccination for patient {patient_id} from factory {factory_id} using ampoule {target_ampoule_id}.")

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
  # await insert_addresses_list(conn)
  # await insert_vaccine_types(conn)
  # await insert_ships(conn)
  # await insert_shifts(conn)
  # await insert_ampoules(conn)
  # await insert_vaccines(conn)

  # Other scripts to ensure that all data necessary for the assignement are present
  # await generate_patient_with_all_vaccines(conn)
  await generate_patient_with_all_factories(conn)
  conn.close()


if __name__ == "__main__":
  asyncio.run(main())
