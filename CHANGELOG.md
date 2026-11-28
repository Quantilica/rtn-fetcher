# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [0.7.6] - 2026-11-28

### Corrigido

- Página de publicações sem nenhum card reconhecido (`div.card-rtn`) passa a ser erro (`ParseError` em `extract_publication_metadata`), em vez de lista vazia. Antes, se o HTML da fonte mudasse, não havia exceção, a reserva do catálogo não agia, a lista vazia ficava no cache e o `sync` saía 0 sem baixar nada. Agora o catálogo cai na lista fixa (entradas `synthetic`) com um WARNING que diz o motivo e uma entrada sentinela de falha de descoberta (ver abaixo); o mesmo vale para uma página com cards mas sem nenhum arquivo listado. O catálogo vazio nunca vai para o cache.
- Falha de descoberta do catálogo (API fora do ar ou página irreconhecível) não some mais atrás da lista fixa. Junto com a reserva, o catálogo traz uma entrada sentinela `rtn-catalogo` (`listing_error`, com `error` e `error_class`). No `check` ela vira um item `skip-unavailable` com motivo `listing-error` (o `check` sai 0 e o `sync --from-plan` conta o item como erro: sai 3 se algo baixou, 1 se nada); no `sync` direto, o download dela levanta `FetchError` e o `sync` sai 3 (reserva baixada ou em dia, mais o erro) ou 1. Antes disso, com o host atual, a página sem cards dava "catálogo vazio" (saída 1) e, com a reserva sozinha, o `sync` sairia 0 sem avisar que a edição nova da fonte não aparecia. `latest_serie_historica_entries` e `download_latest_file` ignoram a sentinela.
- `classify_entry` reconhece a série histórica com `-`, espaço ou `_` entre as palavras, sem diferenciar maiúsculas (ex.: `serie-historica-out26.xlsx`). Antes só o `_` (ou espaço, depois do acento) servia, e um nome com hífen saía do grupo padrão `rtn` e caía em `rtn-anexos`, onde `sync` sem grupo não o baixava.

## [0.7.5] - 2026-11-28

### Corrigido

- `download_latest_file`: quando o link curto da fonte falha (erro HTTP, tempo esgotado, página HTML devolvida com status 200 ou arquivo que não é planilha), a função agora usa o mesmo catálogo do `sync` e baixa a planilha mais recente da série histórica (grupo `rtn`, maior ano/mês de publicação, só XLSX). O log diz por que o link foi abandonado e qual caminho baixou o arquivo. Assinatura e retorno não mudam. O corpo baixado só substitui um arquivo depois de conferir que é um ZIP válido (contêiner do XLSX); as abas não são conferidas no download.
- O link curto não vence mais um catálogo mais novo: quando o link responde, o `Last-Modified` dele é comparado com o da edição mais recente do catálogo (uma leitura de metadados, com o cache que já existe, e um HEAD na planilha do catálogo). Vence a mais nova; empate, o link; catálogo fora do ar, o link. Se o download do escolhido falhar, a função tenta o outro. A comparação é só por `Last-Modified`: o tamanho do arquivo não entra, porque o link não informa o período.
- O catálogo de `download_latest_file` recusa a lista fixa de anexos conhecidos (usada quando a API de metadados está fora do ar), que pode estar atrasada em relação à fonte; antes, com a API fora, o desvio entregava a edição de setembro/2026 mesmo com a de outubro publicada. As entradas dessa lista agora trazem `"synthetic": True` (o `sync` e o `check` continuam usando a lista como antes). Sem catálogo real, o caminho falha com a causa clara e segue para o CKAN ou para o erro final.
- A edição mais recente é a de maior (ano, mês), com mês de 1 a 12. Se o mesmo período tiver mais de uma planilha (ex.: jan/2021 tem a original e a "nova estrutura"), vence a de `Last-Modified` mais recente na fonte.
- Se uma das planilhas empatadas no mesmo período responder erro, só ela é ignorada (com aviso no log); o caminho do catálogo só falha se todas falharem.
- CKAN, último recurso: considera todos os recursos XLSX da série, do mais recente (data de modificação do recurso, normalizada para UTC sem fuso, o que evita erro ao misturar datas com e sem fuso) ao mais antigo, e passa ao próximo se um falhar; sem data nos recursos, segue a ordem da fonte e registra isso no log. O carimbo do arquivo é o `Last-Modified` HTTP do próprio recurso ou, sem ele, o `last_modified` do recurso, em UTC sem fuso; `metadata_modified` e `created` nunca viram carimbo (podem ser posteriores ao arquivo), e recurso sem data confiável do arquivo não serve. Se nenhum caminho funcionar, o erro traz a causa de cada um.

## [0.7.4] - 2026-11-25

### Corrigido

- Anexos PDF: o endereço de publicação/anexo do Tesouro devolve uma página HTML "Visualização de PDF" com o arquivo num iframe, e era essa página (cerca de 400 bytes) que ficava salva no lugar do PDF. `sync` e `check` agora leem o `src` do iframe, aceitam só `https` em `tesouro.gov.br` ou subdomínio (sem credenciais nem porta atípica) e baixam o PDF real, com carimbo da versão vindo do `Last-Modified` dele. O nome do arquivo não muda. Corpo que não começa com `%PDF` é recusado antes de substituir qualquer arquivo existente; página sem iframe ou com iframe para outro host é recusada.

## [0.7.3] - 2026-11-19

### Corrigido

- A descoberta das edições pela API de metadados usava uma rota com barra dupla (`aria//v1`), que a origem passou a recusar com HTTP 403; o catálogo caía na lista fixa de anexos e não via edições novas. A rota agora é `aria/v1`.

## [0.7.2] - 2026-11-19

### Alterado

- Infraestrutura de CI e de repositório alinhada ao template de fetchers da Quantilica (`fetcher-template`): workflows `public-hygiene` e `publish`, `dependabot.yml`, `.gitignore` e `pytest` com `pythonpath = ["src"]`. O `.copier-answers.yml` passa a registrar as respostas do template, para receber as melhorias dele por `copier update`.

### Corrigido

- `lake`: o build sem mudança não abre mais a planilha. Com `datasets` alvo, as abas são conhecidas sem abri-la: se todas já estão no lake com o mesmo bruto (sidecar e rodapé do Parquet), conta `skipped` sem abrir o XLSX; sem alvo, ou com abas ainda por converter, a planilha é aberta mas cada aba em dia é pulada antes de ser lida e convertida. Mesma contagem de `converted`/`skipped`/`errors`; `force` e bruto novo seguem convertendo. Exige `quantilica-analytics>=0.14.0` (o sha256 do bruto sai do sidecar, sem lê-lo). Os testes usam sidecar e espiam as leituras do bruto.

## [0.7.1] - 2026-11-15
### Adicionado
- Testes: identidade do registro conferida.
- Documentação dos dados em `docs/`, conforme a norma de documentação dos dados: página da fonte, página e esquema de referência para cada um dos 24 datasets, com o dicionário de todas as variáveis e a tabela de contas de cada aba. Um teste a verifica. O `.gitignore` passa a aceitar os `*.schema.json` de `docs/datasets/`.

### Corrigido
- CI: o pyproject declara o PyPI antes do índice Quantilica (`[[tool.uv.index]]`), e o workflow perde `--index` e `--index-strategy`. Com a estratégia padrão `first-index`, o `uv sync` só consulta o índice para o que não está no PyPI (`quantilica-analytics`) e deixa de receber o 503 intermitente que o GitHub Pages devolve a caminhos inexistentes.

## [0.7.0] - 2026-11-14

### Adicionado
- O fetcher declara os fatos da fonte (`FetcherInfo`: id canônico, órgão, página e cadência) para o registro de fetchers da Quantilica.
- `stn-rtn` declarado como apelido do id `rtn` (nome antigo da fonte no catálogo).

### Alterado
- Requer `quantilica-core>=0.19.0` (e `quantilica-cli>=0.17.0` como host).
- Grupo `dev` passa a incluir `typer` e `rich`, como nos demais fetchers (os testes exercitam o plugin Typer do host).
- `FetcherInfo.licenca` passa a declarar a licença da fonte: ODbL (evidência: https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional).

### Removido
- Módulo `rtn_fetcher.writer` e a função `write_table_to_parquet`: a conversão para Parquet é feita pelo comando `convert` (lake particionado), que já substituía esse caminho. Os arquivos já gravados no lake não mudam de nome nem de formato.

## [0.6.4] - 2026-11-04

### Corrigido
- Sem o extra `analysis`, o comando `convert` termina com código 1 e a instrução de instalação (`quantilica install rtn --extra analysis`), sem traceback.

### Alterado
- O diretório de saída padrão (`/data/rtn`) passa a ser declarado explicitamente no plugin; o valor não muda.
- Os tipos das chaves de partição vêm de `partition_types_for` do `quantilica-core`, com resultado idêntico no lake.

## [0.6.3] - 2026-11-04

### Corrigido
- Política de frescor volta a F2 (`HEAD_FALLBACK_GET`): `REMOTE_ONLY` (F3, para fontes sem validadores) causava re-download diário de fontes com Last-Modified/ETag, porque descartava o Last-Modified e o nome do arquivo caía em `@hoje`.

### Alterado
- Exige `quantilica-core>=0.16.0`.

## [0.6.2] - 2026-10-30

### Adicionado
- `inventory()` no conversor do lake: para cada arquivo bruto da árvore, informa
  o dataset que ele alimenta ou o motivo de ser ignorado (gêmeo em outro formato,
  arquivo não tabular ou versão anterior). Uma planilha com várias abas aparece
  uma vez por dataset que `convert` escreveria. Permite que a auditoria do lake
  confira a cobertura da fonte sem falsos positivos.

## [0.6.1] - 2026-10-29

### Corrigido
- `convert` lê só a série histórica mais recente. Cada série traz o histórico inteiro e
  cada aba vira um Parquet de chave fixa; percorrer todas as pastas mensais refazia o
  trabalho e gerava ~290 erros nos layouts de anexos antigos (1995–2022).

## [0.6.0] - 2026-10-27

### Adicionado
- Módulo `rtn_fetcher.lake` e entry point `quantilica.lake`: conversão direta das planilhas da Série Histórica do RTN para o lake Parquet (tabelas estatísticas em formato longo unpartitioned com substituição atômica).
- Comandos CLI `convert` e `pipeline` integrados via SDK do `FetcherApp`, com suporte a `--lake`, `--dataset` e `--force`.
- Extra `analysis` atualizado para `quantilica-analytics>=0.5.0`.
- Dependência de base `quantilica-core` atualizada para `>=0.13.0` para conformidade com o contrato de layout Hive.

## [0.5.1] - 2026-10-20

### Corrigido
- Sem o extra `analysis`, importar `rtn_fetcher.schema` ou `rtn_fetcher.writer` levantava `ModuleNotFoundError` cru de `polars`/`quantilica.analytics`; agora levanta `ImportError` com a instrução `uv add 'rtn-fetcher[analysis]' --index https://index.quantilica.com/simple/`. `Tbl.to_polars()` e `dataframe.to_polars()` dão a mesma orientação. `reader`, `fetcher` e `constants` continuam sem exigir o extra.

## [0.5.0] - 2026-10-20

### Alterado
- Catálogo dividido em três grupos: `rtn` (planilhas `serie_historica_*` `.xlsx`/`.csv`), `rtn-anexos` (demais planilhas: Anexos RTN e tabelas `.xls` de 1996 a 2014) e `rtn-publicacoes` (PDF, GIF, DOC, PPT e links), com os aliases `planilhas` (`rtn` + `rtn-anexos`) e `todos`. `sync` e `check` sem grupo usam só `rtn` (87 arquivos em 2026-10-20, contra 2.074 antes); para baixar o resto, passe o grupo ou alias (`quantilica rtn sync todos`). `list_datasets("rtn")` passa a devolver só a série histórica; `list_datasets()` continua devolvendo tudo.
- A página de publicações é baixada uma vez por processo (cache de 5 minutos; `catalog.clear_cache()` força nova leitura): `rtn list` fazia o download duas vezes por grupo.

### Corrigido
- A conta "10. RESULTADO NOMINAL DO GOVERNO CENTRAL" das abas 1.1, 1.1-A, 1.2, 1.2-A, 1.2-B, 2.1, 2.1-A, 2.2 e 2.2-A era lida com código `1.0`, nível 2, filha de "9 JUROS NOMINAIS". Códigos embutidos no rótulo não são mais quebrados dígito a dígito (`normalize_account_code(..., compact=False)`), então ela passa a ter código `10` e nível 1. Os códigos compactos da coluna de código das abas 4.1/4.2 (`111` -> `1.1.1`, `2M` -> `2.M`) não mudam. Consumidores que guardam contas pelo código (ex.: importadores que guardam o código da conta) passam a ver `10` no lugar de `1.0`.
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
