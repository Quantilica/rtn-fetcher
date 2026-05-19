# rtn-fetcher: Download e análise do Resultado do Tesouro Nacional

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square) ![Python](https://img.shields.io/badge/python-3.13+-blue.svg?style=flat-square)

**rtn-fetcher** é uma biblioteca Python para download, extração e transformação de dados do Resultado do Tesouro Nacional (RTN).

## Sobre

O Resultado do Tesouro Nacional (RTN) contém informações fiscais consolidadas do Governo Federal brasileiro, incluindo receitas, despesas e resultado primário. Esta biblioteca facilita o acesso programático a esses dados.

**Fonte dos dados:** [Tesouro Nacional - RTN](https://www.gov.br/tesouronacional/pt-br/estatisticas-fiscais-e-planejamento/resultado-do-tesouro-nacional-rtn)

## Instalação

### Usando uv (recomendado)

```bash
uv add "git+https://github.com/Quantilica/rtn-fetcher.git"
```

### Usando pip

```bash
pip install git+https://github.com/Quantilica/rtn-fetcher.git
```

### Requisitos

- Python 3.13+
- openpyxl
- httpx
- beautifulsoup4

### Extras Opcionais

Para análise de dados com pandas ou polars:

```bash
pip install "rtn-fetcher[pandas] @ git+https://github.com/Quantilica/rtn-fetcher.git"
pip install "rtn-fetcher[polars] @ git+https://github.com/Quantilica/rtn-fetcher.git"
```

## Uso Rápido

### Download de Dados

```python
from pathlib import Path
from rtn_fetcher import download_latest_file

# Download da planilha mais recente
data_dir = Path("data")
filepath = download_latest_file(data_dir)
print(f"Arquivo baixado: {filepath}")
```

### Leitura de Dados

```python
from rtn_fetcher import read_sheet, write_table_to_csv
from pathlib import Path

# Ler aba específica
filepath = Path("data/rtn_202412301200.xlsx")
data, accounts = read_sheet(filepath, "1.2")

# Examinar dados
print(data)
print(f"Dados: {data.nrows} linhas × {data.ncols} colunas")
print(f"Contas: {accounts.nrows} linhas × {accounts.ncols} colunas")

# Exportar para CSV
write_table_to_csv(data, Path("output/rtn_1_2_data.csv"))
write_table_to_csv(accounts, Path("output/rtn_1_2_accounts.csv"))
```

### Ler Todas as Abas

```python
from rtn_fetcher import read_all_sheets

results = read_all_sheets(filepath)

for sheet_name, (data, accounts) in results.items():
    print(f"{sheet_name}: {data.nrows} linhas de dados")
```

### Conversão para pandas/polars

Converta dados para DataFrames nativos para análise avançada:

#### Usando pandas

```python
from rtn_fetcher import read_sheet, to_pandas

data, accounts = read_sheet(filepath, "1.2")

# Método 1: Usar função
df = to_pandas(data)

# Método 2: Usar método direto
df = data.to_pandas()

# Agora use operações pandas
df_filtered = df[df["year"] >= 2023]
df_pivot = df.pivot_table(values="value", index="account", columns="month")
```

#### Usando polars

```python
from rtn_fetcher import read_sheet, to_polars

data, accounts = read_sheet(filepath, "1.2")

# Método 1: Usar função
df = to_polars(data)

# Método 2: Usar método direto
df = data.to_polars()

# Agora use operações polars (mais rápido para dados grandes)
df_filtered = df.filter(df["year"] >= 2023)
df_pivot = df.pivot(on="month", index="account", values="value")
```

### Exportar para Excel ou SQLite

Use o comando `rtn-fetcher export` com subcomandos:

```bash
# Exportar para arquivo Excel formatado
rtn-fetcher export excel

# Exportar para banco de dados SQLite
rtn-fetcher export sqlite

# Customizar caminho de saída
rtn-fetcher export excel --save-as meus_dados.xlsx
rtn-fetcher export sqlite --save-as meus_dados.db

# Usar arquivo local já baixado (sem nova requisição de rede)
rtn-fetcher export excel --file rtn@20250101T120000.xlsx --save-as meus_dados.xlsx
```

Ambos os comandos baixam automaticamente a planilha mais recente se nenhum `--file` for especificado.

## Funcionalidades

### Download de Dados

- Download automático da planilha RTN mais recente
- Detecção de arquivos já baixados (evita downloads duplicados)
- Nomenclatura baseada em timestamp do arquivo
- Acesso à API de metadados das publicações

### Processamento de Dados

- Leitura de múltiplas abas da planilha RTN
- Detecção dinâmica de cabeçalhos e linhas de dados nas abas suportadas
- Extração de hierarquia de contas contábeis
- Transformação de formato wide para long (unpivot)
- Expansão automática de códigos hierárquicos
- Conversão de valores em R$ milhões para reais
- Preservação de indicadores em % do PIB como frações
- Separação de períodos em ano/mês ou ano/trimestre

### Análise de Dados

- Conversão para pandas DataFrame (análise flexível)
- Conversão para polars DataFrame (análise de alto desempenho)
- Integração com ecossistema de data science Python

### Abas Suportadas

| Abas | Descrição | Período | Unidade |
|------|-----------|---------|---------|
| 1.1, 1.2, 1.3, 1.4, 1.5, 1.6 | Séries mensais em valores correntes | Mensal | R$ |
| 1.1-A, 1.2-A, 1.3-A, 1.4-A, 1.5-A | Séries mensais em valores constantes | Mensal | R$ |
| 1.2-B | Série mensal acumulada em 12 meses, IPCA | Mensal | R$ |
| 2.1, 2.2, 2.3, 2.4, 2.5 | Séries anuais em valores correntes | Anual | R$ |
| 2.1-A, 2.2-A, 2.3-A, 2.4-A, 2.5-A | Séries anuais em % do PIB | Anual | Fração do PIB |
| 4.1, 4.2 | Séries trimestrais do Governo Central Orçamentário | Trimestral | R$ |

As abas 3.1 e 3.2 têm layout comparativo de publicação corrente, com cabeçalhos
multinível, e ainda não são normalizadas pelo leitor de séries históricas.

## Estrutura de Dados

### Tabela de Dados (Long Format)

Após processamento, os dados ficam em formato long com as seguintes colunas:

| Coluna  | Tipo | Descrição                           |
|---------|------|-------------------------------------|
| year    | int  | Ano de referência                   |
| month   | int  | Mês de referência (dados mensais)   |
| quarter | int  | Trimestre de referência (dados trimestrais) |
| account | str  | Código hierárquico da conta         |
| value   | int/float | Valores monetários em reais; % do PIB como fração |

### Tabela de Hierarquia de Contas

| Coluna        | Tipo | Descrição                              |
|---------------|------|----------------------------------------|
| account_code  | str  | Código hierárquico (ex: "1.2.3")       |
| account_name  | str  | Nome completo da conta                 |
| account_level | int  | Nível hierárquico                      |
| P_1, P_2, ... | str  | Nome de cada parte da hierarquia       |

### Exemplo de Dados

```python
# Dados
year  month  account  value
2024  1      1.1      1500000000
2024  1      1.2      2300000000
2024  2      1.1      1600000000

# Hierarquia
account_code  account_name                account_level  P_1       P_2
1.1           1.1 Receitas Correntes     2              Receitas  Receitas Correntes
1.2           1.2 Receitas de Capital    2              Receitas  Receitas de Capital
```

## Interface de Linha de Comando (CLI)

Use o comando `rtn-fetcher` para operações de sincronização e exportação:

```bash
rtn-fetcher --help
rtn-fetcher --version

# Sincronizar todas as publicações RTN (metadados + arquivos)
rtn-fetcher sync

# Baixar apenas o arquivo da série histórica mais recente
rtn-fetcher latest

# Exportar dados para outros formatos
rtn-fetcher export excel
rtn-fetcher export sqlite
```

### Opções do `sync`

O comando `sync` busca metadados da página de publicações do Tesouro Nacional, identifica os links de download e baixa todos os arquivos ainda não presentes no diretório local. Os metadados são cacheados localmente; use `--force` para atualizá-los.

```bash
rtn-fetcher sync -o /data/rtn              # Diretório de destino
rtn-fetcher sync --force                   # Refaz o fetch de metadados mesmo se já existe
rtn-fetcher sync --concurrency 8           # Até 8 downloads simultâneos
rtn-fetcher sync --dry-run                 # Lista os arquivos sem baixar
rtn-fetcher sync --metadata metadata.json  # Usa JSON de metadados existente
rtn-fetcher --verbose sync                 # Exibe logs detalhados
```

### Opções do `export`

```bash
rtn-fetcher export excel --save-as rtn_dados.xlsx
rtn-fetcher export sqlite --save-as rtn_dados.db

# Usar arquivo local já baixado (sem nova requisição de rede)
rtn-fetcher export excel --file rtn@20250101T120000.xlsx --save-as rtn_dados.xlsx
rtn-fetcher export sqlite --file rtn@20250101T120000.xlsx --save-as rtn_dados.db

# Sobrescrever banco SQLite existente sem confirmação
rtn-fetcher export sqlite --save-as rtn_dados.db --force
```

### Integração com `quantilica-cli`

Quando instalado junto com `quantilica-cli`, o rtn-fetcher é descoberto automaticamente via entry point e montado no hub unificado:

```bash
quantilica fetch rtn sync
quantilica fetch rtn latest
quantilica fetch rtn export excel
quantilica fetch rtn export sqlite
```

## API Reference

### Funções Principais

#### `download_latest_file(destination_dir: Path) -> Path | None`

Baixa a planilha RTN mais recente do servidor do Tesouro Nacional.

**Parâmetros:**
- `destination_dir`: Diretório onde salvar o arquivo

**Retorna:**
- `Path` do arquivo baixado, ou `None` se arquivo já existe

#### `fetch_publications_metadata() -> list[dict]`

Busca metadados de todas as publicações RTN disponíveis.

**Retorna:**
- Lista de dicionários com informações das publicações

#### `read_sheet(filepath: Path, sheet_name: str) -> tuple[Tbl, Tbl]`

Lê e normaliza uma aba específica da planilha RTN.

**Parâmetros:**
- `filepath`: Caminho para o arquivo Excel
- `sheet_name`: Nome da aba ("1.2", "1.3", "1.6", "2.2-A", etc.)

**Retorna:**
- Tupla de `(dados, hierarquia_contas)` em formato long normalizado

**Exceções:**
- `ValueError`: Se a aba não estiver configurada
- `KeyError`: Se a aba não existir no arquivo

#### `read_all_sheets(filepath: Path) -> dict[str, tuple[Tbl, Tbl]]`

Lê e normaliza todas as abas configuradas.

**Parâmetros:**
- `filepath`: Caminho para o arquivo Excel

**Retorna:**
- Dicionário mapeando nomes de abas para tuplas `(dados, hierarquia)`

#### `write_table_to_csv(data: Tbl, filepath: Path) -> None`

Exporta tabela para arquivo CSV.

**Parâmetros:**
- `data`: Tabela a exportar
- `filepath`: Caminho do arquivo CSV de destino

### Classe Tbl

Estrutura de dados tabular orientada a colunas (dados armazenados por coluna, não por linha).

```python
from rtn_fetcher import Tbl

# Criar tabela
data = Tbl([
    ["nome", "Alice", "Bob"],
    ["idade", 25, 30]
])

# Acessar colunas
names = data["nome"]  # ["nome", "Alice", "Bob"]

# Propriedades
print(f"Dimensões: {data.nrows} linhas × {data.ncols} colunas")

# Operações
data_subset = data.select("nome")
data_with_city = data.assign(cidade=["SP", "RJ"])
long_data = data.melt(id_cols=["nome"])
renamed = data.rename(nome="name", idade="age")

# Iterar por linhas
for row in data.iter_rows():
    print(row)
```

**Métodos principais:**
- `select(*columns)`: Seleciona colunas específicas
- `assign(**columns)`: Adiciona/atualiza colunas
- `melt(id_cols, var_name, value_name)`: Transforma wide → long (unpivot)
- `transpose()`: Transpõe tabela
- `insert(table, index)`: Insere colunas de outra tabela
- `drop_rows(rows)`: Remove linhas por índice
- `drop_cols(cols)`: Remove colunas por índice
- `rename(**names)`: Renomeia colunas
- `iter_rows()`: Itera sobre linhas
- `get_header()`: Retorna nomes de colunas

**Atributos:**
- `data`: Matriz de colunas (lista de listas)
- `nrows`: Número de linhas (incluindo cabeçalho)
- `ncols`: Número de colunas

### Funções Avançadas

#### `extract_sheet_rows(sheet: Sheet) -> list[list[Any]]`

Extrai linhas brutos de uma aba Excel sem normalização.

#### `extract_publication_metadata(html: str) -> dict[str, Any]`

Extrai metadados de publicação de HTML.

#### `build_account_data(table: Tbl) -> Tbl`

Constrói hierarquia de contas a partir de tabela de dados.

#### `parse_account_name(name: str) -> tuple[str, str]`

Extrai código e nome de uma string combinada (ex: "1.2.3 Descrição").

#### `expand_account_hierarchy(code: str, name: str, level: int) -> tuple[str, list[str]]`

Expande código hierárquico com os nomes de cada nível.

## Arquitetura

### Módulos

```
src/rtn_fetcher/
├── __init__.py       # API pública
├── cli.py            # Interface de linha de comando
├── constants.py      # Configurações centralizadas
├── table.py          # Estrutura de dados Tbl
├── excel.py          # Leitura de arquivos Excel
├── fetcher.py        # Download de dados
├── extract.py        # Extração de dados brutos
├── account.py        # Processamento de hierarquia
└── reader.py         # Pipeline de leitura completo
```

### Fluxo de Dados

```
Excel File → extract_data_rows() → build_account_data()
    ↓
convert_cells_to_values() → melt() → split period columns
    ↓
(data, account_hierarchy)
```

### Princípios de Design

1. **Orientado a colunas**: Dados armazenados como lista de colunas para eficiência
2. **Transformações imutáveis**: Operações retornam novas tabelas
3. **Type hints completos**: Melhor IDE support e validação
4. **Docstrings detalhadas**: Documentação em cada função
5. **Separação de responsabilidades**: Cada módulo tem função clara

## Desenvolvimento

```bash
git clone https://github.com/Quantilica/rtn-fetcher.git
cd rtn-fetcher
uv sync --dev
uv run pytest
```

## Licença

MIT — veja [LICENSE](LICENSE).

## Links

- [Tesouro Nacional - RTN](https://www.gov.br/tesouronacional/pt-br/estatisticas-fiscais-e-planejamento/resultado-do-tesouro-nacional-rtn)
- [API do Tesouro](https://apiapex.tesouro.gov.br/)
- [Documentação oficial das séries históricas](http://sisweb.tesouro.gov.br/apex/cosis/thot/link/rtn/serie-historica)
