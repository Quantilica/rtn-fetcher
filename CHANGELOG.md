# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [0.5.1] - 2026-10-20

### Corrigido
- Sem o extra `analysis`, importar `rtn_fetcher.schema` ou `rtn_fetcher.writer` levantava `ModuleNotFoundError` cru de `polars`/`quantilica.analytics`; agora levanta `ImportError` com a instrução `uv add 'rtn-fetcher[analysis]' --index https://index.quantilica.com/simple/`. `Tbl.to_polars()` e `dataframe.to_polars()` dão a mesma orientação. `reader`, `fetcher` e `constants` continuam sem exigir o extra.

## [0.5.0] - 2026-10-20

### Alterado
- Catálogo dividido em três grupos: `rtn` (planilhas `serie_historica_*` `.xlsx`/`.csv`), `rtn-anexos` (demais planilhas: Anexos RTN e tabelas `.xls` de 1996 a 2014) e `rtn-publicacoes` (PDF, GIF, DOC, PPT e links), com os aliases `planilhas` (`rtn` + `rtn-anexos`) e `todos`. `sync` e `check` sem grupo usam só `rtn` (87 arquivos em 2026-10-20, contra 2.074 antes); para baixar o resto, passe o grupo ou alias (`quantilica rtn sync todos`). `list_datasets("rtn")` passa a devolver só a série histórica; `list_datasets()` continua devolvendo tudo.
- A página de publicações é baixada uma vez por processo (cache de 5 minutos; `catalog.clear_cache()` força nova leitura): `rtn list` fazia o download duas vezes por grupo.

### Corrigido
- A conta "10. RESULTADO NOMINAL DO GOVERNO CENTRAL" das abas 1.1, 1.1-A, 1.2, 1.2-A, 1.2-B, 2.1, 2.1-A, 2.2 e 2.2-A era lida com código `1.0`, nível 2, filha de "9 JUROS NOMINAIS". Códigos embutidos no rótulo não são mais quebrados dígito a dígito (`normalize_account_code(..., compact=False)`), então ela passa a ter código `10` e nível 1. Os códigos compactos da coluna de código das abas 4.1/4.2 (`111` -> `1.1.1`, `2M` -> `2.M`) não mudam. Consumidores que guardam contas pelo código (ex.: importador do `quantilica-workers`) passam a ver `10` no lugar de `1.0`.
- Links sem extensão na página de publicações (ex.: "API pública") recebiam `ext` `xlsx`; agora ficam em `rtn-publicacoes` com `ext` `html`.

## [0.4.3] - 2026-10-20

### Corrigido
- `src/rtn_fetcher/py.typed` esvaziado conforme PEP 561.
- `pyproject.toml`: extra `analysis` declara `polars>=1.0.0` explicitamente.

### Alterado
- `cli.py` protege o import do plugin; sem o host a CLI standalone sai com código 1 e orienta `quantilica install rtn`.
- Substituição da instância global de `HttpClient` em `fetcher.py` por factory lazy `_get_client()`, evitando inicialização antecipada de sockets.

## [0.4.2] - 2026-10-02

### Corrigido
- `src/rtn_fetcher/py.typed` esvaziado conforme PEP 561.
- `pyproject.toml`: extra `analysis` declara `polars>=1.0.0` explicitamente.

### Alterado
- Alinhamento com as dependências canônicas do ecossistema: `quantilica-core` atualizada para `>=0.8.0` e `quantilica-analytics` (extra `analysis`) para `>=0.3.0`.
- Gravação Parquet (`write_table_to_parquet`) operando com escrita atômica (arquivo temporário seguido de `os.replace`) e proveniência de manifest persistida em metadados `quantilica.*` do arquivo e em sidecar JSON padronizado (`<target>.manifest.json`) fornecidos por `quantilica.analytics.writer.to_parquet`.

## [0.4.1] - 2026-10-02

### Corrigido
- Remoção da diretiva legada `[tool.hatch.metadata] allow-direct-references = true` em `pyproject.toml` para conformidade estrita com o padrão de publicação PEP 503.

## [0.4.0] - 2026-08-07
### Corrigido
- `src/rtn_fetcher/py.typed` esvaziado conforme PEP 561.
- `pyproject.toml`: extra `analysis` declara `polars>=1.0.0` explicitamente.

### Alterado
- Refatoração arquitetural: Remoção de dependências (`quantilica-cli` e `quantilica-catalog`) e limpeza de imports. Os fetchers agora são pacotes de extração puros, dependendo estritamente do `quantilica-core`.

## [0.2.1] - 2026-07-24

### Corrigido

- `cli.py` usava `logging.getLogger(...)` em `main()` sem importar o módulo
  `logging` — `NameError` sempre que a CLI rodasse sem `--verbose`. Também
  padronizado nos demais fetchers do ecossistema que ainda não tinham a
  supressão de logs verbosos de terceiros (`anac-fetcher`, `anp-fetcher`,
  `inep-fetcher`).
- A linha de rodapé `Deflator - IPCA base <mês/ano>`, presente ao final das
  abas de valores constantes (`1.1-A`, `1.2-A`, `1.2-B`, `1.3-A`, `1.4-A`,
  `1.5-A`), não tinha código hierárquico e virava uma pseudo-conta de
  primeiro nível na árvore de contas — com valores de razão de deflação
  (~1-6), não R$. Adicionado o prefixo `"deflator"` ao filtro de linhas de
  metadado (`is_metadata_row`, junto com `"obs."`, `"fonte:"`,
  `"memorando"`), que já excluía notas de rodapé equivalentes; a linha
  deixa de ser extraída como dado e como conta.

## [0.2.0] - 2026-05-19

Primeira entrada em formato Keep a Changelog; documenta o estado do pacote nesta
versão.

### Adicionado

- Download, extração e transformação de dados do Resultado do Tesouro Nacional
  (RTN) a partir da fonte oficial do Tesouro Nacional.
- Extras opcionais `[pandas]` e `[polars]` para análise.
- CLI standalone e plugin Typer para o `quantilica-cli` (`quantilica rtn`).
