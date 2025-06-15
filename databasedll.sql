-- we don't know how to generate root <with-no-name> (class Root) :(

grant connect, execute on database :: master to ##MS_AgentSigningCertificate##
go

grant connect on database :: master to ##MS_PolicyEventProcessingLogin##
go

grant connect on database :: master to dbo
go

grant connect on database :: master to guest
go

grant view any column encryption key definition, view any column master key definition on database :: master to [public]
go

create table Logradouro
(
    Cd_Logradouro int identity
        constraint Logradouro_pk
            primary key,
    Ds_Logradouro char(60) not null
)
go

create table MSreplication_options
(
    optname          sysname not null,
    value            bit     not null,
    major_version    int     not null,
    minor_version    int     not null,
    revision         int     not null,
    install_failures int     not null
)
go

create table Pais
(
    Cd_Pais int identity
        constraint Pais_pk
            primary key,
    Nm_Pais char(255) not null,
    Sg_Pais char(3)   not null
)
go

create table Estado
(
    Cd_Estado int identity
        constraint Estado_pk
            primary key,
    Cd_Pais   int       not null
        constraint Estado_Pais_Cd_Pais_fk
            references Pais
            on update cascade on delete cascade,
    Nm_Estado char(255) not null,
    Sg_Estado char(3)   not null,
    Cd_Area   char(3)   not null
)
go

exec sp_addextendedproperty 'MS_Description', 'Pais do qual o estado faz parte', 'SCHEMA', 'dbo', 'TABLE', 'Estado',
     'COLUMN', 'Cd_Pais'
go

exec sp_addextendedproperty 'MS_Description', 'Codigo de Area para telefones de um determinado estado', 'SCHEMA', 'dbo',
     'TABLE', 'Estado', 'COLUMN', 'Cd_Area'
go

create table Cidade
(
    Cd_Cidade      int identity
        constraint Cidade_pk
            primary key,
    Cd_Estado      int       not null
        constraint Cidade_Estado_Cd_Estado_fk
            references Estado
            on update cascade on delete cascade,
    Nm_Cidade      char(255) not null,
    Cd_IBGE_Cidade char(9)   not null
)
go

create table Bairro
(
    Cd_Bairro int identity
        constraint Bairro_pk
            primary key,
    Cd_Cidade int       not null
        constraint Bairro_Cidade_Cd_Cidade_fk
            references Cidade
            on delete cascade,
    Nm_Bairro char(255) not null
)
go

create table Pessoa
(
    Cd_Pessoa int identity
        constraint Pessoa_pk
            primary key,
    Ds_Email  char(255) not null
)
go

create table PessoaFisica
(
    Cd_PessoaFisica int identity
        constraint PessoaFisica_pk
            primary key,
    Nm_PrimeiroNome char(255) not null,
    Nm_Sobrenome    char(255) not null,
    Cd_CPF          char(11)  not null,
    Cd_Pessoa       int       not null
        constraint PessoaFisica_Pessoa_Cd_Pessoa_fk
            references Pessoa
)
go

exec sp_addextendedproperty 'MS_Description', 'Primeiro nome da pessoa como aparece em documentos', 'SCHEMA', 'dbo',
     'TABLE', 'PessoaFisica', 'COLUMN', 'Nm_PrimeiroNome'
go

exec sp_addextendedproperty 'MS_Description', 'Quaisquer nomes que nao o primeiro nome como em documentos', 'SCHEMA',
     'dbo', 'TABLE', 'PessoaFisica', 'COLUMN', 'Nm_Sobrenome'
go

create table Funcionario
(
    Cd_Funcionario  int identity
        constraint Funcionario_pk
            primary key,
    Cd_PessoaFisica int not null
        constraint Funcionario_Pessoa_Cd_Pessoa_fk
            references PessoaFisica
            on update cascade on delete cascade
)
go

create table Paciente
(
    Cd_Paciente     int identity
        constraint Paciente_pk
            primary key,
    Cd_PessoaFisica int not null
        constraint Paciente_Pessoa_Cd_Pessoa_fk
            references PessoaFisica
            on update cascade on delete cascade
)
go

create table PessoaJuridica
(
    Cd_PessoaJuridica int identity
        constraint PessoaJuridica_pk
            primary key,
    Cd_Pessoa         int       not null
        constraint PessoaJuridica_Pessoa_Cd_Pessoa_fk
            references Pessoa,
    Cd_cnpj           char(14)  not null,
    Nm_RazaoSocial    char(255) not null
)
go

create table CentroVacinacao
(
    Cd_CentroVacinacao int identity
        constraint CentroVacinacao_pk
            primary key,
    Nm_CentroVacinacao char(255) not null,
    Cd_PessoaJuridica  int       not null
        constraint CentroVacinacao_PessoaJuridica_Cd_PessoaJuridica_fk
            references PessoaJuridica
)
go

create table Fabrica
(
    Cd_Fabrica        int identity
        constraint Fabrica_pk
            primary key,
    Nm_Fabrica        char(255) not null,
    Cd_PessoaJuridica int       not null
        constraint Fabrica_PessoaJuridica_Cd_PessoaJuridica_fk
            references PessoaJuridica
)
go

create table Plantao
(
    Cd_Plantao         int identity
        constraint Plantao_pk
            primary key,
    Cd_CentroVacinacao int      not null
        constraint Plantao_CentroVacinacao_Cd_CentroVacinacao_fk
            references CentroVacinacao
            on update cascade on delete cascade,
    Cd_Funcionario     int      not null
        constraint Plantao_Funcionario_Cd_Funcionario_fk
            references Funcionario,
    Dt_Inicio          datetime not null,
    Dt_Termino         datetime
)
go

create table TipoComplemento
(
    Cd_TipoComplemento int identity
        constraint TipoComplemento_pk
            primary key,
    Ds_TipoComplemento char(60) not null
)
go

create table TipoEndereco
(
    Cd_TipoEndereco int identity
        constraint TipoEndereco_pk
            primary key,
    Ds_TipoEndereco char(60) not null
)
go

create table TipoLogradouro
(
    Cd_TipoLogradouro int identity
        constraint TipoLogradouro_pk
            primary key,
    Ds_TipoLogradouro char(255) not null
)
go

create table Endereco
(
    Cd_Endereco        int identity
        constraint Endereco_pk
            primary key,
    Cd_Bairro          int      not null
        constraint Endereco_Bairro_Cd_Bairro_fk
            references Bairro,
    Nu_Local           char(10) not null,
    Ds_Complemento     char(255),
    Cd_TipoLogradouro  int      not null
        constraint Endereco_TipoLogradouro_Cd_TipoLogradouro_fk
            references TipoLogradouro,
    Cd_Logradouro      int      not null
        constraint Endereco_Logradouro_Cd_Logradouro_fk
            references Logradouro,
    Cd_TipoComplemento int      not null
        constraint Endereco_TipoComplemento_Cd_TipoComplemento_fk
            references TipoComplemento,
    Cd_Cep             char(11) not null
)
go

exec sp_addextendedproperty 'MS_Description', 'Numero do local', 'SCHEMA', 'dbo', 'TABLE', 'Endereco', 'COLUMN',
     'Nu_Local'
go

create table ListaEndereco
(
    Cd_ListaEndereco int identity
        constraint ListaEndereco_pk
            primary key,
    Cd_Pessoa        int not null
        constraint ListaEndereco_Pessoa_Cd_Pessoa_fk
            references Pessoa,
    Cd_Endereco      int not null
        constraint ListaEndereco_Endereco_Cd_Endereco_fk
            references Endereco,
    Cd_TipoEndereco  int not null
        constraint ListaEndereco_TipoEndereco_Cd_TipoEndereco_fk
            references TipoEndereco
)
go

create table TipoVacina
(
    Cd_TipoVacina        int identity
        constraint TipoVacina_pk
            primary key,
    Nm_TipoVacina        char(255) not null,
    Pz_Validade          int       not null,
    Pz_ValidadeAposAbrir int       not null
)
go

exec sp_addextendedproperty 'MS_Description', N'Prazo de validade em dias a partir do dia de produção do lote',
     'SCHEMA', 'dbo', 'TABLE', 'TipoVacina', 'COLUMN', 'Pz_Validade'
go

exec sp_addextendedproperty 'MS_Description', 'Prazo de validade reduzido em dias a partir da abertura da ampola',
     'SCHEMA', 'dbo', 'TABLE', 'TipoVacina', 'COLUMN', 'Pz_ValidadeAposAbrir'
go

create table Lote
(
    Cd_Lote              int identity
        constraint Lote_pk
            primary key,
    Cd_Fabrica           int      not null
        constraint Lote_Fabrica_Cd_Fabrica_fk
            references Fabrica,
    Cd_TipoVacina        int      not null
        constraint Lote_TipoVacina_Cd_TipoVacina_fk
            references TipoVacina,
    Cd_CentroVacinacao   int      not null
        constraint Lote_CentroVacinacao_Cd_CentroVacinacao_fk
            references CentroVacinacao,
    Dt_Fabricacao        datetime not null,
    Nu_QuantidadeAmpolas int      not null,
    Dt_Validade          datetime not null
)
go

create table Ampola
(
    Cd_Ampola   int identity
        constraint Ampola_pk
            primary key,
    Cd_Lote     int not null
        constraint Ampola_Lote_Cd_Lote_fk
            references Lote,
    Dt_Abertura datetime
)
go

create table Vacinacao
(
    Cd_Vacinacao   int identity
        constraint Vacinacao_pk
            primary key,
    Cd_Paciente    int      not null
        constraint Vacinacao_Paciente_Cd_Paciente_fk
            references Paciente,
    Cd_Funcionario int
        constraint Vacinacao_Funcionario_Cd_Funcionario_fk
            references Funcionario,
    Cd_Ampola      int      not null
        constraint Vacinacao_Ampola_Cd_Ampola_fk
            references Ampola,
    Dt_Vacinacao   datetime not null
)
go

create table spt_fallback_db
(
    xserver_name       varchar(30) not null,
    xdttm_ins          datetime    not null,
    xdttm_last_ins_upd datetime    not null,
    xfallback_dbid     smallint,
    name               varchar(30) not null,
    dbid               smallint    not null,
    status             smallint    not null,
    version            smallint    not null
)
go

grant select on spt_fallback_db to [public]
go

create table spt_fallback_dev
(
    xserver_name       varchar(30)  not null,
    xdttm_ins          datetime     not null,
    xdttm_last_ins_upd datetime     not null,
    xfallback_low      int,
    xfallback_drive    char(2),
    low                int          not null,
    high               int          not null,
    status             smallint     not null,
    name               varchar(30)  not null,
    phyname            varchar(127) not null
)
go

grant select on spt_fallback_dev to [public]
go

create table spt_fallback_usg
(
    xserver_name       varchar(30) not null,
    xdttm_ins          datetime    not null,
    xdttm_last_ins_upd datetime    not null,
    xfallback_vstart   int,
    dbid               smallint    not null,
    segmap             int         not null,
    lstart             int         not null,
    sizepg             int         not null,
    vstart             int         not null
)
go

grant select on spt_fallback_usg to [public]
go

create table spt_monitor
(
    lastrun       datetime not null,
    cpu_busy      int      not null,
    io_busy       int      not null,
    idle          int      not null,
    pack_received int      not null,
    pack_sent     int      not null,
    connections   int      not null,
    pack_errors   int      not null,
    total_read    int      not null,
    total_write   int      not null,
    total_errors  int      not null
)
go

grant select on spt_monitor to [public]
go


create view spt_values as
select name collate database_default as name,
	number,
	type collate database_default as type,
	low, high, status
from sys.spt_values
go

grant select on spt_values to [public]
go

create procedure dbo.sp_MScleanupmergepublisher
as
    exec sys.sp_MScleanupmergepublisher_internal
go


create procedure dbo.sp_MSrepl_startup
as
    exec sys.sp_MSrepl_startup_internal
go

grant connect sql to ##MS_AgentSigningCertificate##
go

grant connect sql to ##MS_PolicyEventProcessingLogin##
go

grant control server, view any definition to ##MS_PolicySigningCertificate##
go

grant connect sql, view any definition, view server state to ##MS_PolicyTsqlExecutionLogin##
go

grant authenticate server to ##MS_SQLAuthenticatorCertificate##
go

grant authenticate server, view any definition, view server state to ##MS_SQLReplicationSigningCertificate##
go

grant view any definition to ##MS_SQLResourceSigningCertificate##
go

grant view any definition to ##MS_SmoExtendedSigningCertificate##
go

grant connect sql to [BUILTIN\Administrators]
go

grant connect sql to [NT AUTHORITY\NETWORK SERVICE]
go

grant alter any event session, connect any database, connect sql, view any definition, view server state to [NT AUTHORITY\SYSTEM]
go

grant view any database to [public]
go

grant connect sql to sa
go

