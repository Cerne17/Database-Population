# Database Assignment: Vaccine Database

This project is designed to populate a SQL Server database with comprehensive dummy data for a vaccine administration system. It simulates various entities involved in a vaccination process, including geographical data, personal and juridical entities, healthcare facilities, vaccine details, and vaccination records.

## Features

- **Database Interaction**: Connects to a SQL Server database using `pyodbc`.
- **Asynchronous Operations**: Leverages `asyncio` for non-blocking database operations.
- **Data Generation**:
  - Uses the `Faker` library to generate realistic Brazilian Portuguese names, emails, etc.
  - Includes custom functions (`functionalities.py`) to generate valid Brazilian CPFs and CNPJs.
- **External API Integration**:
  - Fetches country data from `restcountries.com`.
  - Fetches state data from `countriesnow.space`.
  - Fetches Brazilian city data from `brasilapi.com.br`.
- **Local Data Files**: Uses JSON files (`neighborhoods.json`, `addresses.json`, `vaccinetypes.json`) as sources for specific data.
- **Comprehensive Data Model**: Populates a wide range of tables, including:
  - Geographical: `Pais` (Country), `Estado` (State), `Cidade` (City), `Bairro` (Neighborhood).
  - Entities: `Pessoa` (Person), `PessoaFisica` (Physical Person), `PessoaJuridica` (Juridical Person).
  - Healthcare: `Paciente` (Patient), `Funcionario` (Worker/Employee), `CentroVacinacao` (Vaccination Center), `Fabrica` (Factory/Manufacturer).
  - Addresses: `Logradouro` (Street Name), `TipoLogradouro` (Street Type), `TipoComplemento` (Complement Type), `Endereco` (Address), `ListaEndereco` (Address List).
  - Vaccine Logistics: `TipoVacina` (Vaccine Type), `Lote` (Batch/Shipment), `Ampola` (Ampoule/Vial).
  - Operational: `Plantao` (Shift), `Vacinacao` (Vaccination Event).
- **Specific Data Scenarios**: Includes logic to ensure specific data conditions, such as `generate_patient_with_all_vaccines` to create a patient record with all available vaccine types.

## Core Scripts

- **`main.py`**: The main executable script that orchestrates the entire data generation and insertion process. It calls various functions to populate different tables in a specific order.
- **`db.py`**: Handles all database connectivity and operations. It provides asynchronous functions for connecting to the SQL Server database, inserting data, and retrieving data.
- **`functionalities.py`**: Contains helper functions for tasks like translating text (using `googletrans`), generating CPFs and CNPJs, and creating random datetime objects.
- **`databasedll.sql`**: This SQL file contains the Data Definition Language (DDL) statements used to create the database schema (tables, relationships, constraints, etc.) for this project. It serves as a reference for the database structure that the Python scripts expect to interact with. **Note:** The Python scripts in this project are designed to _populate_ an existing database; they do not execute this DDL file to create the schema. The schema must be created in your SQL Server instance beforehand, potentially by using the statements in this file.
- **`requirements.txt`**: Lists all Python package dependencies required to run the project. This file can be used with `pip install -r requirements.txt` to easily set up the environment.

## Prerequisites

- Python 3.7+
- A running SQL Server instance.
- The database schema (tables, relationships, etc.) must be pre-created in the SQL Server instance. This script only populates the data.
- Python libraries:
  - `pyodbc`
  - `requests`
  - `Faker`
  - `googletrans`
  - `asyncio` (usually part of the standard library)
    You can typically install these using pip:
  ```bash
  pip install -r requirements.txt
  ```

## Setup

1.  **Configure Database Connection**:
    Open `db.py` and update the following variables with your SQL Server details:

    ```python
    db_server = 'localhost,1433'  # Your SQL Server instance
    db_database = 'master'        # Your target database name
    db_username = 'sa'            # Your SQL Server username
    db_password = 'MyStr0ngP@ss1' # Your SQL Server password
    db_driver = '{ODBC Driver 17 for SQL Server}' # Ensure this matches your installed ODBC driver
    ```

    **Note**: The `TrustServerCertificate=yes;` option is used for development. Review this for production environments.

2.  **Ensure Local JSON Files are Present**:
    Make sure `neighborhoods.json`, `addresses.json`, and `vaccinetypes.json` are in the same directory as `main.py` or update their paths in the script if they are located elsewhere.

## How to Run

1.  Ensure all prerequisites and setup steps are completed.
2.  Navigate to the project directory in your terminal.
3.  Execute the main script:

    ```bash
    python main.py
    ```

    The script will print success, warning, and error messages to the console as it processes and inserts data.

    **Optional: Redirecting Output to a File**

    If you want to save the script's output to a file instead of displaying it in the console, you can use shell redirection. For example, to save all output (both standard messages and errors) to `application_output.txt`:

    ```bash
    python main.py > application_output.txt 2>&1
    ```

    This will create or overwrite `application_output.txt` with the script's full output. To append to the file instead, use `>>`:

    ```bash
    python main.py >> application_output.txt 2>&1
    ```

    In my case, as I use a macbook, I need to specify the version of python that has all packages properly installed:

    ```bash
    python3.12 main.py >> application_output.txt 2>&1
    ```

## Data Generation Flow

The `main.py` script populates the database in a sequence designed to respect foreign key constraints. This generally involves:

1.  Inserting geographical data (countries, states, cities, neighborhoods).
2.  Inserting base person and company data.
3.  Creating specific roles like patients, workers, vaccine centers, and factories.
4.  Populating address-related tables and linking addresses to entities.
5.  Inserting vaccine types, batches (lots), and ampoules.
6.  Creating work shifts for employees.
7.  Simulating vaccination events.
8.  Running specific scripts like `generate_patient_with_all_vaccines` to fulfill particular data requirements.

---

## (Versão em Português)

# Trabalho de Banco de Dados: Banco de Dados de Vacinas

Este projeto foi desenvolvido para popular um banco de dados SQL Server com dados fictícios abrangentes para um sistema de administração de vacinas. Ele simula várias entidades envolvidas em um processo de vacinação, incluindo dados geográficos, entidades físicas e jurídicas, instalações de saúde, detalhes de vacinas e registros de vacinação.

## Funcionalidades

- **Interação com Banco de Dados**: Conecta-se a um banco de dados SQL Server usando `pyodbc`.
- **Operações Assíncronas**: Utiliza `asyncio` para operações de banco de dados não bloqueantes.
- **Geração de Dados**:
  - Usa a biblioteca `Faker` para gerar nomes, e-mails, etc., realistas em português do Brasil.
  - Inclui funções personalizadas (`functionalities.py`) para gerar CPFs e CNPJs brasileiros válidos.
- **Integração com APIs Externas**:
  - Busca dados de países em `restcountries.com`.
  - Busca dados de estados em `countriesnow.space`.
  - Busca dados de cidades brasileiras em `brasilapi.com.br`.
- **Arquivos de Dados Locais**: Usa arquivos JSON (`neighborhoods.json`, `addresses.json`, `vaccinetypes.json`) como fontes para dados específicos.
- **Modelo de Dados Abrangente**: Popula uma vasta gama de tabelas, incluindo:
  - Geográficas: `Pais`, `Estado`, `Cidade`, `Bairro`.
  - Entidades: `Pessoa`, `PessoaFisica`, `PessoaJuridica`.
  - Saúde: `Paciente`, `Funcionario`, `CentroVacinacao`, `Fabrica`.
  - Endereços: `Logradouro`, `TipoLogradouro`, `TipoComplemento`, `Endereco`, `ListaEndereco`.
  - Logística de Vacinas: `TipoVacina`, `Lote`, `Ampola`.
  - Operacional: `Plantao`, `Vacinacao`.
- **Cenários de Dados Específicos**: Inclui lógica para garantir condições de dados específicas, como `generate_patient_with_all_vaccines` para criar um registro de paciente com todos os tipos de vacina disponíveis.

## Scripts Principais

- **`main.py`**: O script executável principal que orquestra todo o processo de geração e inserção de dados. Ele chama várias funções para popular diferentes tabelas em uma ordem específica.
- **`db.py`**: Lida com toda a conectividade e operações de banco de dados. Fornece funções assíncronas para conectar ao banco de dados SQL Server, inserir dados e recuperar dados.
- **`functionalities.py`**: Contém funções auxiliares para tarefas como traduzir texto (usando `googletrans`), gerar CPFs e CNPJs, e criar objetos datetime aleatórios.
- **`databasedll.sql`**: Este arquivo SQL contém as instruções DDL (Data Definition Language - Linguagem de Definição de Dados) usadas para criar o esquema do banco de dados (tabelas, relacionamentos, restrições, etc.) para este projeto. Ele serve como referência para a estrutura do banco de dados com a qual os scripts Python esperam interagir. **Nota:** Os scripts Python neste projeto são projetados para _popular_ um banco de dados existente; eles não executam este arquivo DDL para criar o esquema. O esquema deve ser criado em sua instância do SQL Server antecipadamente, potencialmente usando as instruções contidas neste arquivo.
- **`requirements.txt`**: Lista todas as dependências de pacotes Python necessárias para executar o projeto. Este arquivo pode ser usado com `pip install -r requirements.txt` para configurar facilmente o ambiente.

## Pré-requisitos

- Python 3.7+
- Uma instância do SQL Server em execução.
- O esquema do banco de dados (tabelas, relacionamentos, etc.) deve ser pré-criado na instância do SQL Server. Este script apenas popula os dados.
- Bibliotecas Python:
  - `pyodbc`
  - `requests`
  - `Faker`
  - `googletrans`
  - `asyncio` (geralmente parte da biblioteca padrão)
    Você pode instalá-las usando pip:
  ```bash
  pip install -r requirements.txt
  ```

## Configuração

1.  **Configurar Conexão com o Banco de Dados**:
    Abra `db.py` e atualize as seguintes variáveis com os detalhes do seu SQL Server:

    ```python
    db_server = 'localhost,1433'  # Sua instância do SQL Server
    db_database = 'master'        # O nome do seu banco de dados alvo
    db_username = 'sa'            # Seu nome de usuário do SQL Server
    db_password = 'MyStr0ngP@ss1' # Sua senha do SQL Server
    db_driver = '{ODBC Driver 17 for SQL Server}' # Certifique-se de que corresponde ao seu driver ODBC instalado
    ```

    **Nota**: A opção `TrustServerCertificate=yes;` é usada para desenvolvimento. Revise isso para ambientes de produção.

2.  **Garantir que os Arquivos JSON Locais Estejam Presentes**:
    Certifique-se de que `neighborhoods.json`, `addresses.json`, e `vaccinetypes.json` estão no mesmo diretório que `main.py` ou atualize seus caminhos no script se estiverem localizados em outro lugar.

## Como Executar

1.  Certifique-se de que todos os pré-requisitos e etapas de configuração foram concluídos.
2.  Navegue até o diretório do projeto no seu terminal.
3.  Execute o script principal:

    ```bash
    python main.py
    ```

    O script imprimirá mensagens de sucesso, aviso e erro no console enquanto processa e insere os dados.

    **Opcional: Redirecionando a Saída para um Arquivo**

    Se você deseja salvar a saída do script em um arquivo em vez de exibi-la no console, pode usar o redirecionamento de shell. Por exemplo, para salvar toda a saída (mensagens padrão e erros) em `application_output.txt`:

    ```bash
    python main.py > application_output.txt 2>&1
    ```

    Isso criará ou substituirá o arquivo `application_output.txt` com a saída completa do script. Para anexar ao arquivo em vez de substituí-lo, use `>>`:

    ```bash
    python main.py >> application_output.txt 2>&1
    ```

    No meu caso, como utilizo um macbook, eu preciso explicitar a versão do python que tenha todos pacotes devidamente instalados:

    ```bash
    python3.12 main.py >> application_output.txt 2>&1
    ```

## Fluxo de Geração de Dados

O script `main.py` popula o banco de dados em uma sequência projetada para respeitar as restrições de chave estrangeira. Isso geralmente envolve:

1.  Inserir dados geográficos (países, estados, cidades, bairros).
2.  Inserir dados base de pessoas e empresas.
3.  Criar papéis específicos como pacientes, funcionários, centros de vacinação e fábricas.
4.  Popular tabelas relacionadas a endereços e vincular endereços a entidades.
5.  Inserir tipos de vacina, lotes e ampolas.
6.  Criar turnos de trabalho para funcionários.
7.  Simular eventos de vacinação.
8.  Executar scripts específicos como `generate_patient_with_all_vaccines` para atender a requisitos de dados particulares.
