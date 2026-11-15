---
dataset:
  id: tabela-1-6
  fonte: rtn
  titulo: "Receita Líquida Ajustada - Lei Complementar 200/2023 - Mensal"
  resumo: "Receita Líquida Ajustada da Lei Complementar 200/2023, em série mensal, em valores correntes. Uma linha por conta e período, em formato longo."
  orgao: Secretaria do Tesouro Nacional (STN), Ministério da Fazenda
  pagina_oficial: https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
  licenca: "Open Data Commons Open Database License (ODbL), conforme o conjunto de dados no portal Tesouro Transparente (conferido em 2026-11-15)."
  periodicidade: "mensal; a STN publica uma planilha nova a cada edição do RTN, com a série histórica inteira"
  cobertura: {inicio: 2021-07, fim: em-curso}
  unidade: "o valor de uma conta da tabela em um mês"
  granularidade: {espacial: "Brasil (Governo Central)", temporal: mês}
  formato_bruto: "aba 1.6 da planilha XLSX da série histórica do RTN (uma aba por tabela); valores em R$ milhões, períodos nas colunas a partir da linha 5; o código da conta vem embutido no rótulo da primeira coluna"
  lake: {estado: convertido, particoes: [], chave: [year, month, account], colunas: 4}
  unidades_de_medida:
    value: "R$ (reais correntes)"
  dados_pessoais: nenhum
  eras: 
    - {desde: 2023-06, mudanca: "as contas auto.2 (variação acumulada do IPCA) e auto.3 (variação real da RLA) passam a ter valores"}
    - {desde: 2023-09, mudanca: "a conta 4.4 (receitas de recursos não sacados do PIS/Pasep) passa a ter valores"}
  revisado_em: 2026-11-15
  versao_fetcher: 0.7.0
---

# Receita Líquida Ajustada - Lei Complementar 200/2023 - Mensal

## Resumo

Aba `1.6` ("Tabela 1.6") da série histórica do Resultado do Tesouro Nacional (RTN). Traz a receita líquida, as receitas primárias e transferências excluídas da base de cálculo da Receita Líquida Ajustada (RLA), a própria RLA e as variações usadas pela lei (IPCA acumulado e variação real). A tabela cobre o Governo Central (Tesouro Nacional, Previdência Social e Banco Central), com a metodologia "acima da linha" da STN. Cada linha do lake é um valor de uma conta em um mês.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `rtn/tabela-1-6` |
| Órgão | Secretaria do Tesouro Nacional (STN), Ministério da Fazenda |
| Página oficial | https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional |
| Licença | Open Data Commons Open Database License (ODbL), conforme o conjunto de dados no portal Tesouro Transparente (conferido em 2026-11-15). |
| Periodicidade | mensal; a STN publica uma planilha nova a cada edição do RTN, com a série histórica inteira |
| Cobertura | 2021-07 a em-curso |
| Unidade (uma linha) | o valor de uma conta da tabela em um mês |
| Granularidade | espacial: Brasil (Governo Central); temporal: mês |
| Formato bruto | aba 1.6 da planilha XLSX da série histórica do RTN (uma aba por tabela); valores em R$ milhões, períodos nas colunas a partir da linha 5; o código da conta vem embutido no rótulo da primeira coluna |
| Estado no lake | convertido |
| Partições | — |
| Chave | `year`, `month`, `account` |
| Colunas | 4 |
| Unidades de medida | `value`: R$ (reais correntes) |
| Dados pessoais | nenhum |
| Eras | 2023-06: as contas auto.2 (variação acumulada do IPCA) e auto.3 (variação real da RLA) passam a ter valores; 2023-09: a conta 4.4 (receitas de recursos não sacados do PIS/Pasep) passa a ter valores |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.7.0 |

## Origem e coleta

- O fetcher baixa a planilha da série histórica do RTN publicada no portal Tesouro Transparente (conjunto de dados "Resultado do Tesouro Nacional - Série Histórica") e a guarda no bruto como `rtn@AAAAMMDDTHHMMSS.xlsx`, em que o sufixo é o `Last-Modified` do servidor.
- Cada edição traz a série histórica inteira, uma aba por tabela. O conversor lê só a edição mais recente e converte a aba `1.6` em um Parquet de nome fixo (`1-6.parquet`).
- Layout da aba: o título na linha 2, a unidade na linha 3 ("R$ Milhões - Valores Correntes"), o cabeçalho com os períodos na linha 5 (primeira coluna: "Discriminação") e as contas nas linhas seguintes; o código da conta vem embutido no rótulo da primeira coluna. As notas de rodapé ("Obs.", "1/", "2/"...) ficam abaixo da tabela e não entram no lake.
- Conferido em 2026-11-15: edição `seriehistoricajul26.xlsx`, publicada em 27/08/2026 (`Last-Modified` do arquivo), com a aba `1.6` de 2021-07 a 2026-07.
- Para o conjunto de dados, a fonte informa frequência de atualização mensal e início em janeiro de 1997 (metadados no portal, conferidos em 2026-11-15); cada aba começa no seu próprio período.

## Conteúdo

- 1.281 linhas: 21 contas × 61 períodos (de 2021-07 a 2026-07); cada combinação de `year`, `month`, `account` aparece uma vez.
- Unidade de `value`: reais correntes (a fonte publica em R$ milhões e o conversor multiplica por 1.000.000).
- 72 linhas têm `value` nulo, em 3 conta(s) (`4.4`, `auto.2`, `auto.3`), entre 2021-07 e 2023-08 (edição de jul/2026).
- Os 61 períodos são consecutivos, sem lacunas entre o primeiro e o último.

### Contas

O lake guarda só o código da conta em `account`; o nome não vai para o Parquet. A tabela abaixo é a de contas desta tabela na edição de jul/2026 (código, nível hierárquico e nome como a planilha publica, sem a numeração e as chamadas de nota).

Os códigos usam ponto como separador de níveis (`1.1.01` é filha de `1.1`). Códigos que começam por `auto.` foram gerados pelo conversor para linhas que a planilha não numera (posicionais, com base na indentação); um sufixo `#2` marca a segunda ocorrência de um código repetido na mesma aba.

| Código (`account`) | Nível | Conta |
|---|---|---|
| `1` | 1 | RECEITA TOTAL |
| `1.1` | 2 | &nbsp;&nbsp;Receita Administrada pela RFB |
| `1.2` | 2 | &nbsp;&nbsp;Incentivos Fiscais |
| `1.3` | 2 | &nbsp;&nbsp;Arrecadação Líquida para o RGPS |
| `1.4` | 2 | &nbsp;&nbsp;Receitas Não Administradas pela RFB |
| `2` | 1 | TRANSF. POR REPARTIÇÃO DE RECEITA |
| `3` | 1 | RECEITA LÍQUIDA (1-2) |
| `4` | 1 | RECEITAS PRIMÁRIAS NÃO INCLUÍDAS NA BASE DE CÁLCULO DA RLA DA LC Nº 200/2023 (§2º do art. 5º) |
| `4.1` | 2 | &nbsp;&nbsp;Concessões e Permissões (incsiso I do § 2º do art. 5º) |
| `4.2` | 2 | &nbsp;&nbsp;Dividendos e Participações (inciso II do § 2º do art. 5º) |
| `4.3` | 2 | &nbsp;&nbsp;Receita de Exploração de Recursos Naturais (inciso III do § 2º do art. 5º) |
| `4.4` | 2 | &nbsp;&nbsp;Receitas de Recursos não Sacados do Pis Pasep (inciso IV do § 2º do art. 5º) |
| `5` | 1 | TRANSFERÊNCIAS PRIMÁRIAS DECORRENTES DAS RECEITAS PRIMÁRIAS NÃO INCLUÍDAS NA BASE DE CÁLCULO DA RLA DA LC Nº 200/2023 (inciso VI do §2º do art. 5º) |
| `5.1` | 2 | &nbsp;&nbsp;Transferências de Exploração de Recursos Naturais |
| `5.2` | 2 | &nbsp;&nbsp;Superávit dos Fundos |
| `5.3` | 2 | &nbsp;&nbsp;Transferências de Concessões e Permissões |
| `auto.0.5.3.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Cessão Onerosa |
| `auto.0.5.3.2` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Concessão de Recursos Florestais |
| `auto.1` | 1 | Receita Líquida Ajustada ( = 3 - 4 + 5) |
| `auto.2` | 1 | Variação Acumulada do IPCA (§ 4º do art. 5º da LC nº 200/2023) |
| `auto.3` | 1 | Variação real da receita líquida ajustada (art. 5º da LC nº 200/2023) |

## Variáveis

A planilha não traz dicionário de colunas: os dados chegam em formato largo (um período por coluna) e o conversor os passa para o formato longo abaixo. O dicionário de conceitos da STN descreve as contas (não as colunas) em um layout de tabelas anterior ao atual, por isso as descrições de contas não são repetidas aqui linha a linha: as contas ficam na tabela da seção Conteúdo, com o nome como a planilha publica, e a coluna "Descrição" abaixo diz o que cada coluna do lake guarda.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `year` | cabeçalho da coluna de período (data) | inteiro | Ano do mês a que o valor se refere | ano de quatro dígitos | todo |
| `month` | cabeçalho da coluna de período (data) | inteiro | Mês a que o valor se refere | 1 a 12 | todo |
| `account` | rótulo da linha (primeira coluna, com o código embutido) | texto | Código hierárquico da conta, com ponto como separador; ver a tabela de contas na seção Conteúdo | os códigos da tabela de contas | todo |
| `value` | célula da conta no período | decimal | Valor da conta no período; célula vazia, `-`, `n.a.`, `n.d.` e "não disp." na planilha viram nulo | R$ (reais correntes) | todo |

## No lake

- Dataset `rtn/tabela-1-6`, sem partições: um único arquivo `1-6.parquet` com as colunas `year`, `month`, `account`, `value`.
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
- **Série curta e com início posterior.** A tabela começa em 2021-07, mas as contas `auto.2` e `auto.3` (variações do IPCA e real da RLA) só têm valores desde 2023-06, e a conta 4.4 desde 2023-09.
- **As contas `auto.2` e `auto.3` não estão em reais.** A planilha traz a variação acumulada do IPCA e a variação real da RLA como fração (por exemplo, 0,0464 em 2026-06), mas o conversor da versão 0.7.0 multiplica toda a aba por 1.000.000: `value` vem como 46.400, e o valor correto é `value / 1e6`. Todas as demais contas da aba estão em R$.

## Exemplos

Últimos 12 meses da conta `1` (RECEITA TOTAL), em R$ bilhões:

```python
import duckdb

duckdb.sql("""
    SELECT year, month, round(value / 1e9, 1) AS valor_bi
    FROM read_parquet('lake/rtn/tabela-1-6/*.parquet')
    WHERE account = '1' AND value IS NOT NULL
    ORDER BY year DESC, month DESC LIMIT 12
""").show()
```

## Referências

- Conjunto de dados "Resultado do Tesouro Nacional - Série Histórica" (Tesouro Transparente): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Dicionário de Conceitos e Metodologia de Cálculo (planilha do mesmo conjunto): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Metadados da série (PDF do mesmo conjunto): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
