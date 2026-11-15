---
dataset:
  id: tabela-2-1
  fonte: rtn
  titulo: "Resultado Primário do Governo Central - Anual - Resumida - Valores Correntes"
  resumo: "Resultado primário do Governo Central em versão resumida, em série anual, em valores correntes. Uma linha por conta e período, em formato longo."
  orgao: Secretaria do Tesouro Nacional (STN), Ministério da Fazenda
  pagina_oficial: https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
  licenca: "Open Data Commons Open Database License (ODbL), conforme o conjunto de dados no portal Tesouro Transparente (conferido em 2026-11-15)."
  periodicidade: "anual (anos fechados), atualizada a cada edição mensal do RTN; a série histórica sai inteira em cada planilha"
  cobertura: {inicio: 1997, fim: em-curso}
  unidade: "o valor de uma conta da tabela em um ano"
  granularidade: {espacial: "Brasil (Governo Central)", temporal: ano}
  formato_bruto: "aba 2.1 da planilha XLSX da série histórica do RTN (uma aba por tabela); valores em R$ milhões, períodos nas colunas a partir da linha 5; o código da conta vem embutido no rótulo da primeira coluna"
  lake: {estado: convertido, particoes: [], chave: [year, account], colunas: 3}
  unidades_de_medida:
    value: "R$ (reais correntes)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.7.0
---

# Resultado Primário do Governo Central - Anual - Resumida - Valores Correntes

## Resumo

Aba `2.1` ("Tabela 2.1") da série histórica do Resultado do Tesouro Nacional (RTN). Traz a receita total (com as receitas administradas pela RFB, os incentivos fiscais, a arrecadação líquida para o RGPS e as não administradas), as transferências por repartição de receita, a despesa total (benefícios previdenciários, pessoal e encargos, outras despesas obrigatórias e despesas do Poder Executivo sujeitas à programação financeira), o resultado primário acima da linha, os ajustes metodológicos, a discrepância estatística, o resultado primário abaixo da linha, os juros nominais e o resultado nominal. A tabela cobre o Governo Central (Tesouro Nacional, Previdência Social e Banco Central), com a metodologia "acima da linha" da STN. Cada linha do lake é um valor de uma conta em um ano.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `rtn/tabela-2-1` |
| Órgão | Secretaria do Tesouro Nacional (STN), Ministério da Fazenda |
| Página oficial | https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional |
| Licença | Open Data Commons Open Database License (ODbL), conforme o conjunto de dados no portal Tesouro Transparente (conferido em 2026-11-15). |
| Periodicidade | anual (anos fechados), atualizada a cada edição mensal do RTN; a série histórica sai inteira em cada planilha |
| Cobertura | 1997 a em-curso |
| Unidade (uma linha) | o valor de uma conta da tabela em um ano |
| Granularidade | espacial: Brasil (Governo Central); temporal: ano |
| Formato bruto | aba 2.1 da planilha XLSX da série histórica do RTN (uma aba por tabela); valores em R$ milhões, períodos nas colunas a partir da linha 5; o código da conta vem embutido no rótulo da primeira coluna |
| Estado no lake | convertido |
| Partições | — |
| Chave | `year`, `account` |
| Colunas | 3 |
| Unidades de medida | `value`: R$ (reais correntes) |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.7.0 |

## Origem e coleta

- O fetcher baixa a planilha da série histórica do RTN publicada no portal Tesouro Transparente (conjunto de dados "Resultado do Tesouro Nacional - Série Histórica") e a guarda no bruto como `rtn@AAAAMMDDTHHMMSS.xlsx`, em que o sufixo é o `Last-Modified` do servidor.
- Cada edição traz a série histórica inteira, uma aba por tabela. O conversor lê só a edição mais recente e converte a aba `2.1` em um Parquet de nome fixo (`2-1.parquet`).
- Layout da aba: o título na linha 2, a unidade na linha 3 ("R$ Milhões - Valores Correntes"), o cabeçalho com os períodos na linha 5 (primeira coluna: "Discriminação") e as contas nas linhas seguintes; o código da conta vem embutido no rótulo da primeira coluna. As notas de rodapé ("Obs.", "1/", "2/"...) ficam abaixo da tabela e não entram no lake.
- Conferido em 2026-11-15: edição `seriehistoricajul26.xlsx`, publicada em 27/08/2026 (`Last-Modified` do arquivo), com a aba `2.1` de 1997 a 2025.
- Para o conjunto de dados, a fonte informa frequência de atualização mensal e início em janeiro de 1997 (metadados no portal, conferidos em 2026-11-15); cada aba começa no seu próprio período.

## Conteúdo

- 2.030 linhas: 70 contas × 29 períodos (de 1997 a 2025); cada combinação de `year`, `account` aparece uma vez.
- Unidade de `value`: reais correntes (a fonte publica em R$ milhões e o conversor multiplica por 1.000.000).
- Nenhuma linha tem `value` nulo.
- Os 29 períodos são consecutivos, sem lacunas entre o primeiro e o último.
- Só entram anos fechados: o último ano é 2025, enquanto a série mensal vai até 2026-07.

### Contas

O lake guarda só o código da conta em `account`; o nome não vai para o Parquet. A tabela abaixo é a de contas desta tabela na edição de jul/2026 (código, nível hierárquico e nome como a planilha publica, sem a numeração e as chamadas de nota).

Os códigos usam ponto como separador de níveis (`1.1.01` é filha de `1.1`). Códigos que começam por `auto.` foram gerados pelo conversor para linhas que a planilha não numera (posicionais, com base na indentação); um sufixo `#2` marca a segunda ocorrência de um código repetido na mesma aba.

| Código (`account`) | Nível | Conta |
|---|---|---|
| `1` | 1 | RECEITA TOTAL |
| `1.1` | 2 | &nbsp;&nbsp;Receita Administrada pela RFB |
| `1.1.01` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Imposto sobre a Importação |
| `1.1.02` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;IPI |
| `1.1.03` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Imposto sobre a Renda |
| `1.1.04` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;IOF |
| `1.1.05` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Cofins |
| `1.1.06` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;PIS/Pasep |
| `1.1.07` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;CSLL |
| `1.1.08` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;CPMF |
| `1.1.09` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;CIDE - Combustíveis |
| `1.1.10` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Outras Receitas Administradas pela RFB |
| `1.2` | 2 | &nbsp;&nbsp;Incentivos Fiscais |
| `1.3` | 2 | &nbsp;&nbsp;Arrecadação Líquida para o RGPS |
| `1.4` | 2 | &nbsp;&nbsp;Receitas Não Administradas pela RFB |
| `1.4.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Concessões e Permissões |
| `1.4.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Dividendos e Participações |
| `1.4.3` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Contr. Plano de Seguridade Social do Servidor |
| `1.4.4` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Receitas de Exploração de Recursos Naturais |
| `1.4.5` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Receitas Próprias (fontes 50, 81 e 82) |
| `1.4.6` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Contribuição do Salário Educação |
| `1.4.7` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Complemento para o FGTS (LC nº 110/01) |
| `1.4.8` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Demais Receitas Não Administradas pela RFB |
| `2` | 1 | TRANSF. POR REPARTIÇÃO DE RECEITA |
| `2.1` | 2 | &nbsp;&nbsp;FPM / FPE / IPI-EE |
| `2.2` | 2 | &nbsp;&nbsp;Fundos Constitucionais |
| `2.2.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Repasse Total |
| `2.2.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Superávit dos Fundos |
| `2.3` | 2 | &nbsp;&nbsp;Transferência de Contribuição do Salário Educação |
| `2.4` | 2 | &nbsp;&nbsp;Transferências de Exploração de Recursos Naturais |
| `2.5` | 2 | &nbsp;&nbsp;Transferência da CIDE - Combustíveis |
| `2.6` | 2 | &nbsp;&nbsp;Demais Transferências por Repartição de Receita |
| `3` | 1 | RECEITA LÍQUIDA (1-2) |
| `4` | 1 | DESPESA TOTAL |
| `4.1` | 2 | &nbsp;&nbsp;Benefícios Previdenciários |
| `4.2` | 2 | &nbsp;&nbsp;Pessoal e Encargos Sociais |
| `4.3` | 2 | &nbsp;&nbsp;Outras Despesas Obrigatórias |
| `4.3.01` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Abono e Seguro Desemprego |
| `4.3.02` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Anistiados |
| `4.3.03` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Apoio Fin. EE/MM |
| `4.3.04` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Benefícios de Legislação Especial e Indenizações |
| `4.3.05` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Benefícios de Prestação Continuada da LOAS/RMV |
| `4.3.06` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Complemento para o FGTS (LC nº 110/01) |
| `4.3.07` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Créditos Extraordinários |
| `4.3.08` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Compensação ao RGPS pelas Desonerações da Folha |
| `4.3.09` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Fabricação de Cédulas e Moedas |
| `4.3.10` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;FUNDEB (Complem. União) |
| `4.3.11` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Fundo Constitucional DF (Custeio e Capital) |
| `4.3.12` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Legislativo/Judiciário/MPU/DPU (Custeio e Capital) |
| `4.3.13` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Lei Kandir (LC nº 87/96 e 102/00) e LC nº 176 de 2020 |
| `4.3.14` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Sentenças Judiciais e Precatórios (Custeio e Capital) |
| `4.3.15` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Subsídios, Subvenções e Proagro |
| `4.3.16` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Transferências ANA |
| `4.3.17` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Transferências Multas ANEEL |
| `4.3.18` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Impacto Primário do FIES |
| `4.3.19` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Financiamento de Campanha Eleitoral |
| `4.3.20` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Demais Despesas Obrigatórias |
| `4.4` | 2 | &nbsp;&nbsp;Despesas do Poder Executivo Sujeitas à Programação Financeira |
| `4.4.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Obrigatórias com Controle de Fluxo |
| `4.4.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Despesas Discricionárias |
| `5` | 1 | RESULTADO PRIMÁRIO GOVERNO CENTRAL - ACIMA DA LINHA (3 - 4) |
| `6` | 1 | AJUSTES METODOLÓGICOS |
| `6.1` | 2 | &nbsp;&nbsp;Ajuste Metodológico Itaipu |
| `6.2` | 2 | &nbsp;&nbsp;Ajuste Metodológico Caixa - Competência |
| `6.3` | 2 | &nbsp;&nbsp;Ajuste Metodológico Recursos Não Sacados do PIS/PASEP (EC nº 126/2022) |
| `6.4` | 2 | &nbsp;&nbsp;Ajuste Metodológico Compensações LC nº 194/2022 (pré-Acordo União e Estados/Distrito Federal) |
| `7` | 1 | DISCREPÂNCIA ESTATÍSTICA |
| `8` | 1 | RESULTADO PRIMÁRIO DO GOVERNO CENTRAL - ABAIXO DA LINHA (5 + 6 + 7) |
| `9` | 1 | JUROS NOMINAIS |
| `10` | 1 | RESULTADO NOMINAL DO GOVERNO CENTRAL (8 + 9) |

## Variáveis

A planilha não traz dicionário de colunas: os dados chegam em formato largo (um período por coluna) e o conversor os passa para o formato longo abaixo. O dicionário de conceitos da STN descreve as contas (não as colunas) em um layout de tabelas anterior ao atual, por isso as descrições de contas não são repetidas aqui linha a linha: as contas ficam na tabela da seção Conteúdo, com o nome como a planilha publica, e a coluna "Descrição" abaixo diz o que cada coluna do lake guarda.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `year` | cabeçalho da coluna de período (ano) | inteiro | Ano a que o valor se refere | ano de quatro dígitos | todo |
| `account` | rótulo da linha (primeira coluna, com o código embutido) | texto | Código hierárquico da conta, com ponto como separador; ver a tabela de contas na seção Conteúdo | os códigos da tabela de contas | todo |
| `value` | célula da conta no período | decimal | Valor da conta no período; célula vazia, `-`, `n.a.`, `n.d.` e "não disp." na planilha viram nulo | R$ (reais correntes) | todo |

## No lake

- Dataset `rtn/tabela-2-1`, sem partições: um único arquivo `2-1.parquet` com as colunas `year`, `account`, `value`.
- O conversor lê a planilha mais recente do bruto, passa a aba do formato largo para o longo (uma linha por conta e período), identifica o código da conta pelo rótulo e aplica o contrato de tipos (`year`, `month` e `quarter` inteiros; `account` texto; `value` decimal de 64 bits).
- O valor é multiplicado por 1.000.000 (a fonte publica em R$ milhões), então `value` está em reais.
- Linhas de notas ("Obs.", "Fonte:", "Memorando" e chamadas "1/"), de deflator e de PIB nominal não viram dados (ver Cuidados de uso).
- Como o nome do arquivo é fixo, converter uma edição nova refaz o arquivo; o lake guarda só a edição convertida mais recente.

## Cuidados de uso

- **O nome da conta não está no lake.** Una `account` à tabela de contas da seção Conteúdo (ou à planilha). O mesmo código significa coisas diferentes em tabelas diferentes: `1.1` é "Receita Administrada pela RFB" na tabela 1.1 e "Investimentos (GND 4)" na 1.3.
- **Há totais e componentes na mesma tabela.** Contas de nível 1 resumem as de nível 2, e assim por diante; some só contas do mesmo nível sob o mesmo pai, ou use só a conta que quer, para não contar duas vezes. Os blocos de memorando (`auto.…`, `m.…`) são recortes ou reclassificações dos totais principais, não parcelas adicionais.
- **Códigos `auto.` são posicionais.** Eles vêm da ordem e da indentação das linhas sem número na planilha; se a STN reordenar a tabela, o mesmo código pode passar a apontar outra linha. Prefira os códigos numéricos da própria planilha.
- **Dados revisáveis.** A fonte avisa "Dados sujeitos à alteração" e diz que a série pode ser revista até o início do exercício corrente (metadados do conjunto de dados); o lake guarda só a edição mais recente, sem a versão anterior.
- **Critério de apuração das despesas.** Veja as notas da própria aba na planilha: a fonte registra por caixa e apura as despesas ora por "pagamento efetivo" (saque na Conta Única), ora por "valor pago" (ordens bancárias emitidas), conforme a tabela (metadados do conjunto de dados).

## Exemplos

Últimos 10 anos da conta `1` (RECEITA TOTAL):

```python
import duckdb

duckdb.sql("""
    SELECT year, round(value / 1e9, 1) AS valor_bi
    FROM read_parquet('lake/rtn/tabela-2-1/*.parquet')
    WHERE account = '1' AND value IS NOT NULL
    ORDER BY year DESC LIMIT 10
""").show()
```

## Referências

- Conjunto de dados "Resultado do Tesouro Nacional - Série Histórica" (Tesouro Transparente): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Dicionário de Conceitos e Metodologia de Cálculo (planilha do mesmo conjunto): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Metadados da série (PDF do mesmo conjunto): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
