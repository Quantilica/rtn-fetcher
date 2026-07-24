# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

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
