---
dataset:
  id: tabela-4-2
  fonte: rtn
  titulo: "Conciliação do Resultado Primário do RTN e o Resultado de Operações do Governo Central Orçamentário (GCO) - Trimestral - Valores Correntes"
  resumo: "Conciliação entre o resultado primário do RTN e o do Governo Central Orçamentário, em série trimestral, em valores correntes. Uma linha por conta e período, em formato longo."
  orgao: Secretaria do Tesouro Nacional (STN), Ministério da Fazenda
  pagina_oficial: https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
  licenca: "Open Data Commons Open Database License (ODbL), conforme o conjunto de dados no portal Tesouro Transparente (conferido em 2026-11-15)."
  periodicidade: "trimestral; atualizada a cada edição do RTN que traz um trimestre novo"
  cobertura: {inicio: 2020-01, fim: em-curso}
  unidade: "o valor de uma conta da tabela em um trimestre"
  granularidade: {espacial: "Brasil (Governo Central)", temporal: trimestre}
  formato_bruto: "aba 4.2 da planilha XLSX da série histórica do RTN (uma aba por tabela); valores em R$ milhões, períodos nas colunas a partir da linha 5; nas abas 4.x a primeira coluna traz o código da conta e a segunda, o nome"
  lake: {estado: convertido, particoes: [], chave: [year, quarter, account], colunas: 4}
  unidades_de_medida:
    value: "R$ (reais correntes)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.7.0
---

# Conciliação do Resultado Primário do RTN e o Resultado de Operações do Governo Central Orçamentário (GCO) - Trimestral - Valores Correntes

## Resumo

Aba `4.2` ("Tabela 4.2") da série histórica do Resultado do Tesouro Nacional (RTN). Traz o passo a passo que liga a receita, a despesa e o resultado primário do RTN aos do Governo Central Orçamentário (GCO), com os ajustes e as discrepâncias não explicadas. A tabela cobre o Governo Central (Tesouro Nacional, Previdência Social e Banco Central), com a metodologia "acima da linha" da STN. Cada linha do lake é um valor de uma conta em um trimestre.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `rtn/tabela-4-2` |
| Órgão | Secretaria do Tesouro Nacional (STN), Ministério da Fazenda |
| Página oficial | https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional |
| Licença | Open Data Commons Open Database License (ODbL), conforme o conjunto de dados no portal Tesouro Transparente (conferido em 2026-11-15). |
| Periodicidade | trimestral; atualizada a cada edição do RTN que traz um trimestre novo |
| Cobertura | 2020-01 a em-curso |
| Unidade (uma linha) | o valor de uma conta da tabela em um trimestre |
| Granularidade | espacial: Brasil (Governo Central); temporal: trimestre |
| Formato bruto | aba 4.2 da planilha XLSX da série histórica do RTN (uma aba por tabela); valores em R$ milhões, períodos nas colunas a partir da linha 5; nas abas 4.x a primeira coluna traz o código da conta e a segunda, o nome |
| Estado no lake | convertido |
| Partições | — |
| Chave | `year`, `quarter`, `account` |
| Colunas | 4 |
| Unidades de medida | `value`: R$ (reais correntes) |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.7.0 |

## Origem e coleta

- O fetcher baixa a planilha da série histórica do RTN publicada no portal Tesouro Transparente (conjunto de dados "Resultado do Tesouro Nacional - Série Histórica") e a guarda no bruto como `rtn@AAAAMMDDTHHMMSS.xlsx`, em que o sufixo é o `Last-Modified` do servidor.
- Cada edição traz a série histórica inteira, uma aba por tabela. O conversor lê só a edição mais recente e converte a aba `4.2` em um Parquet de nome fixo (`4-2.parquet`).
- Layout da aba: o título na linha 2, a unidade na linha 3 ("R$ Milhões - Valores Correntes"), o cabeçalho com os períodos na linha 5 (primeira coluna: "Discriminação") e as contas nas linhas seguintes; nas abas 4.x a primeira coluna traz o código da conta e a segunda, o nome. As notas de rodapé ("Obs.", "1/", "2/"...) ficam abaixo da tabela e não entram no lake.
- Conferido em 2026-11-15: edição `seriehistoricajul26.xlsx`, publicada em 27/08/2026 (`Last-Modified` do arquivo), com a aba `4.2` de 2020-T1 a 2026-T1.
- Para o conjunto de dados, a fonte informa frequência de atualização mensal e início em janeiro de 1997 (metadados no portal, conferidos em 2026-11-15); cada aba começa no seu próprio período.

## Conteúdo

- 1.275 linhas: 51 contas × 25 períodos (de 2020-T1 a 2026-T1); cada combinação de `year`, `quarter`, `account` aparece uma vez.
- Unidade de `value`: reais correntes (a fonte publica em R$ milhões e o conversor multiplica por 1.000.000).
- Nenhuma linha tem `value` nulo.
- Os 25 períodos são consecutivos, sem lacunas entre o primeiro e o último.
- A tabela parte de uma série trimestral desde 2020-T1 e concilia o RTN, apurado por caixa, com o resultado do Governo Central Orçamentário (tabelas 4.1 e 4.2 dos Demonstrativos GCO).

### Contas

O lake guarda só o código da conta em `account`; o nome não vai para o Parquet. A tabela abaixo é a de contas desta tabela na edição de jul/2026 (código, nível hierárquico e nome como a planilha publica, sem a numeração e as chamadas de nota).

Os códigos usam ponto como separador de níveis (`1.1.01` é filha de `1.1`). Códigos que começam por `auto.` foram gerados pelo conversor para linhas que a planilha não numera (posicionais, com base na indentação); um sufixo `#2` marca a segunda ocorrência de um código repetido na mesma aba.

| Código (`account`) | Nível | Conta |
|---|---|---|
| `1.1` | 2 | &nbsp;&nbsp;Receita RTN |
| `1.1.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Ajustes na Receita RTN, dos quais: |
| `auto.2.1` | 2 | &nbsp;&nbsp;(-) Compensação ao RGPS pelas Desonerações da Folha |
| `auto.2.2` | 2 | &nbsp;&nbsp;(-) Venda de ativos não financeiros |
| `auto.2.3` | 2 | &nbsp;&nbsp;(-) Operações financeiras |
| `auto.2.4` | 2 | &nbsp;&nbsp;(+) Contribuição patronal intraorçamentária - RPPS |
| `auto.2.5` | 2 | &nbsp;&nbsp;(+) IRRF Governos Regionais |
| `auto.2.6` | 2 | &nbsp;&nbsp;(+) Registro Siafi x Fluxo de Caixa |
| `auto.2.7` | 2 | &nbsp;&nbsp;(-) Receita do Banco Central |
| `auto.2.8` | 2 | &nbsp;&nbsp;(-) Complemento para o FGTS |
| `auto.3` | 1 | Discrepância não explicada |
| `1.2` | 2 | &nbsp;&nbsp;Receita primária GCO (1.1 + 1.1.1) |
| `1.2.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Receita de juros |
| `1.3` | 2 | &nbsp;&nbsp;Receita (1.2 + 1.2.1) |
| `2.1` | 2 | &nbsp;&nbsp;Transferências e Despesa RTN, dos quais: |
| `auto.8` | 1 | Transferências por repartição de receitas |
| `auto.9` | 1 | Despesa total |
| `2.1.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Ajustes nas Transferências e Despesa RTN, dos quais: |
| `auto.10.1` | 2 | &nbsp;&nbsp;(-) Compensação ao RGPS pelas desonerações da folha |
| `auto.10.2` | 2 | &nbsp;&nbsp;(-) Operações intraorçamentárias |
| `auto.10.3` | 2 | &nbsp;&nbsp;(-) Operações financeiras de subsídios e subvenções |
| `auto.10.4` | 2 | &nbsp;&nbsp;(-) Receitas de retorno de subsídios e subvenções |
| `auto.10.5` | 2 | &nbsp;&nbsp;(-) Aquisição de ativos financeiros |
| `auto.10.6` | 2 | &nbsp;&nbsp;(-) Fundos Constitucionais |
| `auto.10.7` | 2 | &nbsp;&nbsp;(-) Registro FIES |
| `auto.10.8` | 2 | &nbsp;&nbsp;(-) Aquisição de ativos não financeiros |
| `auto.10.9` | 2 | &nbsp;&nbsp;(+) Contribuição patronal intraorçamentária - RPPS |
| `auto.10.10` | 2 | &nbsp;&nbsp;(+) IRRF Governos Regionais |
| `auto.10.11` | 2 | &nbsp;&nbsp;(+) Consumo de capital fixo |
| `auto.10.12` | 2 | &nbsp;&nbsp;(+) Transferência aos Estados referente à compensação de ICMS - LC 194/2022 |
| `auto.10.13` | 2 | &nbsp;&nbsp;(+) Registro FIPEM |
| `auto.10.14` | 2 | &nbsp;&nbsp;(+) Registro contábil - Competência x Pagamento Efetivo |
| `auto.10.15` | 2 | &nbsp;&nbsp;(-) Despesa do Banco Central |
| `auto.10.16` | 2 | &nbsp;&nbsp;(-) Fabricação de Cédulas e Moedas |
| `auto.10.17` | 2 | &nbsp;&nbsp;(-) Complemento para o FGTS |
| `auto.10.18` | 2 | &nbsp;&nbsp;(+) Aquisição de ativos não financeiros |
| `auto.10.19` | 2 | &nbsp;&nbsp;(-) Venda de ativos não financeiros |
| `auto.10.20` | 2 | &nbsp;&nbsp;(-) Consumo de capital fixo |
| `auto.11` | 1 | Discrepância não explicada |
| `2.2` | 2 | &nbsp;&nbsp;Despesa primária GCO (2.1 + 2.1.1) |
| `2.2.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Gasto de juros |
| `2.3` | 2 | &nbsp;&nbsp;Despesa (2.2 + 2.2.1) |
| `3` | 1 | Resultado primário - RTN |
| `3.1` | 2 | &nbsp;&nbsp;Ajuste final (3.1.1 - 3.1.2) |
| `3.1.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Ajuste nas Receitas RTN (+) |
| `3.1.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Ajuste nas Transferências e Despesas RTN (-) |
| `4` | 1 | Capacidade (+)/Necessidade(-) líquida de financiamento primária GCO (3 + 3.1) |
| `4.1` | 2 | &nbsp;&nbsp;Juros Líquidos (4.1.1 - 4.1.2) |
| `4.1.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Receita de juros (+) |
| `4.1.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Gasto de juros (-) |
| `5` | 1 | Capacidade (+)/Necessidade(-) líquida de financiamento GCO (4 + 4.1) |

## Variáveis

A planilha não traz dicionário de colunas: os dados chegam em formato largo (um período por coluna) e o conversor os passa para o formato longo abaixo. O dicionário de conceitos da STN descreve as contas (não as colunas) em um layout de tabelas anterior ao atual, por isso as descrições de contas não são repetidas aqui linha a linha: as contas ficam na tabela da seção Conteúdo, com o nome como a planilha publica, e a coluna "Descrição" abaixo diz o que cada coluna do lake guarda.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `year` | cabeçalho da coluna de período ("AAAA-T", algarismos romanos) | inteiro | Ano do trimestre | ano de quatro dígitos | todo |
| `quarter` | cabeçalho da coluna de período ("AAAA-T", algarismos romanos) | inteiro | Trimestre a que o valor se refere | 1 a 4 (`I` a `IV` na fonte) | todo |
| `account` | rótulo da linha (código na primeira coluna e nome na segunda) | texto | Código hierárquico da conta, com ponto como separador; ver a tabela de contas na seção Conteúdo | os códigos da tabela de contas | todo |
| `value` | célula da conta no período | decimal | Valor da conta no período; célula vazia, `-`, `n.a.`, `n.d.` e "não disp." na planilha viram nulo | R$ (reais correntes) | todo |

## No lake

- Dataset `rtn/tabela-4-2`, sem partições: um único arquivo `4-2.parquet` com as colunas `year`, `quarter`, `account`, `value`.
- O conversor lê a planilha mais recente do bruto, passa a aba do formato largo para o longo (uma linha por conta e período), identifica o código da conta pelo rótulo e aplica o contrato de tipos (`year`, `month` e `quarter` inteiros; `account` texto; `value` decimal de 64 bits).
- O valor é multiplicado por 1.000.000 (a fonte publica em R$ milhões), então `value` está em reais.
- Linhas de notas ("Obs.", "Fonte:", "Memorando" e chamadas "1/"), de deflator e de PIB nominal não viram dados (ver Cuidados de uso).
- Como o nome do arquivo é fixo, converter uma edição nova refaz o arquivo; o lake guarda só a edição convertida mais recente.

## Cuidados de uso

- **O nome da conta não está no lake.** Una `account` à tabela de contas da seção Conteúdo (ou à planilha). O mesmo código significa coisas diferentes em tabelas diferentes: `1.1` é "Receita Administrada pela RFB" na tabela 1.1 e "Investimentos (GND 4)" na 1.3.
- **Há totais e componentes na mesma tabela.** Contas de nível 1 resumem as de nível 2, e assim por diante; some só contas do mesmo nível sob o mesmo pai, ou use só a conta que quer, para não contar duas vezes. Os blocos de memorando (`auto.…`, `m.…`) são recortes ou reclassificações dos totais principais, não parcelas adicionais.
- **Códigos `auto.` são posicionais.** Eles vêm da ordem e da indentação das linhas sem número na planilha; se a STN reordenar a tabela, o mesmo código pode passar a apontar outra linha. Prefira os códigos numéricos da própria planilha.
- **Dados revisáveis.** A fonte avisa "Dados sujeitos à alteração" e diz que a série pode ser revista até o início do exercício corrente (metadados do conjunto de dados); o lake guarda só a edição mais recente, sem a versão anterior.
- **Itens de ajuste sem número.** As linhas de ajuste e de discrepância não têm código na planilha e entram com códigos `auto.…`, que dependem da ordem das linhas.
- **Sinais.** Os ajustes vêm com sinal: "(-)" e "(+)" no nome da conta dizem como o ajuste entra no cálculo, e o valor já é negativo quando a operação subtrai (por exemplo, "(-) Compensação ao RGPS pelas Desonerações da Folha" em 2020-T1).

## Exemplos

Últimos 8 trimestres da conta `1.1` (Receita RTN), em R$ bilhões:

```python
import duckdb

duckdb.sql("""
    SELECT year, quarter, round(value / 1e9, 1) AS valor_bi
    FROM read_parquet('lake/rtn/tabela-4-2/*.parquet')
    WHERE account = '1.1' AND value IS NOT NULL
    ORDER BY year DESC, quarter DESC LIMIT 8
""").show()
```

## Referências

- Conjunto de dados "Resultado do Tesouro Nacional - Série Histórica" (Tesouro Transparente): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Dicionário de Conceitos e Metodologia de Cálculo (planilha do mesmo conjunto): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Metadados da série (PDF do mesmo conjunto): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
