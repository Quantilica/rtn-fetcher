# rtnpy

**rtnpy** é uma biblioteca Python para download, extração e transformação de dados do Resultado do Tesouro Nacional (RTN).

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📋 Índice

- [Sobre](#sobre)
- [Instalação](#instalação)
- [Uso Rápido](#uso-rápido)
- [Funcionalidades](#funcionalidades)
- [Estrutura de Dados](#estrutura-de-dados)
- [API Reference](#api-reference)
- [Arquitetura](#arquitetura)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

## 🎯 Sobre

O Resultado do Tesouro Nacional (RTN) contém informações fiscais consolidadas do Governo Federal brasileiro, incluindo receitas, despesas e resultado primário. Esta biblioteca facilita o acesso programático a esses dados.

**Fonte dos dados:** [Tesouro Nacional - RTN](https://www.gov.br/tesouronacional/pt-br/estatisticas-fiscais-e-planejamento/resultado-do-tesouro-nacional-rtn)

## 📦 Instalação

### Usando uv (recomendado)

```bash
uv add rtnpy
```

### Usando pip

```bash
pip install rtnpy
```

### Requisitos

- Python 3.13+
- openpyxl
- httpx
- beautifulsoup4

## 🚀 Uso Rápido

### Download de Dados

```python
from pathlib import Path
from rtnpy import download_latest_file

# Download da planilha mais recente
data_dir = Path("data")
filepath = download_latest_file(data_dir)
print(f"Arquivo baixado: {filepath}")
```

### Leitura de Dados

```python
from rtnpy import read_sheet, write_table_to_csv
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
from rtnpy import read_all_sheets

results = read_all_sheets(filepath)

for sheet_name, (data, accounts) in results.items():
    print(f"{sheet_name}: {data.nrows} linhas de dados")
```

## 🔧 Funcionalidades

### Download de Dados

- ✅ Download automático da planilha RTN mais recente
- ✅ Detecção de arquivos já baixados (evita downloads duplicados)
- ✅ Nomenclatura baseada em timestamp do arquivo
- ✅ Acesso à API de metadados das publicações

### Processamento de Dados

- ✅ Leitura de múltiplas abas da planilha RTN
- ✅ Detecção dinâmica de cabeçalhos e linhas de dados nas abas suportadas
- ✅ Extração de hierarquia de contas contábeis
- ✅ Transformação de formato wide para long (unpivot)
- ✅ Expansão automática de códigos hierárquicos
- ✅ Conversão de valores em R$ milhões para reais
- ✅ Preservação de indicadores em % do PIB como frações
- ✅ Separação de períodos em ano/mês ou ano/trimestre

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

## 📊 Estrutura de Dados

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
| account_code  | str  | Código hierárquico (ex: "1=>2=>3")     |
| account_name  | str  | Nome completo da conta                 |
| account_level | int  | Nível hierárquico                      |
| P_1, P_2, ... | str  | Nome de cada parte da hierarquia       |

### Exemplo de Dados

```python
# Dados
year  month  account  value
2024  1      1=>1     1500000000
2024  1      1=>2     2300000000
2024  2      1=>1     1600000000

# Hierarquia
account_code  account_name                account_level  P_1       P_2
1=>1          1.1 Receitas Correntes     2              Receitas  Receitas Correntes
1=>2          1.2 Receitas de Capital    2              Receitas  Receitas de Capital
```

## 📚 API Reference

### Funções Principais

#### `download_latest_file(destination_dir: Path) -> Path | None`

Baixa a planilha RTN mais recente.

**Parâmetros:**
- `destination_dir`: Diretório onde salvar o arquivo

**Retorna:**
- `Path` do arquivo baixado, ou `None` se já existe

#### `read_sheet(filepath: Path, sheet_name: str) -> tuple[Tbl, Tbl]`

Lê uma aba específica da planilha RTN.

**Parâmetros:**
- `filepath`: Caminho para o arquivo Excel
- `sheet_name`: Nome da aba ("1.2", "1.3", "1.6", "2.2-A")

**Retorna:**
- Tupla de `(dados, hierarquia_contas)`

**Exceções:**
- `ValueError`: Se a aba não estiver configurada
- `KeyError`: Se a aba não existir no arquivo

#### `read_all_sheets(filepath: Path) -> dict[str, tuple[Tbl, Tbl]]`

Lê todas as abas configuradas.

**Parâmetros:**
- `filepath`: Caminho para o arquivo Excel

**Retorna:**
- Dicionário mapeando nomes de abas para tuplas `(dados, hierarquia)`

#### `write_table_to_csv(data: Tbl, filepath: Path) -> None`

Exporta tabela para CSV.

**Parâmetros:**
- `data`: Tabela a exportar
- `filepath`: Caminho do arquivo CSV de destino

### Classe Tbl

Estrutura de dados tabular orientada a colunas.

```python
from rtnpy import Tbl

# Criar tabela
data = Tbl([
    ["nome", "Alice", "Bob"],
    ["idade", 25, 30]
])

# Acessar colunas
names = data["nome"]  # ["nome", "Alice", "Bob"]

# Operações
data_subset = data.select("nome")
data_with_city = data.assign(cidade=["SP", "RJ"])
long_data = data.melt(id_cols=["nome"])

# Iterar por linhas
for row in data.iter_rows():
    print(row)
```

**Métodos principais:**
- `select(*columns)`: Seleciona colunas
- `assign(**columns)`: Adiciona/atualiza colunas
- `melt(id_cols, var_name, value_name)`: Transforma wide → long
- `transpose()`: Transpõe tabela
- `drop_rows(rows)`: Remove linhas
- `drop_cols(cols)`: Remove colunas
- `rename(**names)`: Renomeia colunas

## 🏗️ Arquitetura

### Módulos

```
rtnpy/
├── __init__.py       # API pública
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

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🔗 Links

- [Tesouro Nacional - RTN](https://www.gov.br/tesouronacional/pt-br/estatisticas-fiscais-e-planejamento/resultado-do-tesouro-nacional-rtn)
- [API do Tesouro](https://apiapex.tesouro.gov.br/)
- [Documentação oficial das séries históricas](http://sisweb.tesouro.gov.br/apex/cosis/thot/link/rtn/serie-historica)
