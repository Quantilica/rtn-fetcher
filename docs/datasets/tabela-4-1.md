---
dataset:
  id: tabela-4-1
  fonte: rtn
  titulo: "Demonstrativo de Operações do Governo Central Orçamentário - Metodologia Manual de Estatísticas de Finanças Públicas 2014 - Trimestral - Valores Correntes"
  resumo: "Demonstrativo de Operações do Governo Central Orçamentário, em série trimestral, em valores correntes. Uma linha por conta e período, em formato longo."
  orgao: Secretaria do Tesouro Nacional (STN), Ministério da Fazenda
  pagina_oficial: https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
  licenca: "Open Data Commons Open Database License (ODbL), conforme o conjunto de dados no portal Tesouro Transparente (conferido em 2026-11-15)."
  periodicidade: "trimestral; atualizada a cada edição do RTN que traz um trimestre novo"
  cobertura: {inicio: 2006-01, fim: em-curso}
  unidade: "o valor de uma conta da tabela em um trimestre"
  granularidade: {espacial: "Brasil (Governo Central)", temporal: trimestre}
  formato_bruto: "aba 4.1 da planilha XLSX da série histórica do RTN (uma aba por tabela); valores em R$ milhões, períodos nas colunas a partir da linha 5; nas abas 4.x a primeira coluna traz o código da conta e a segunda, o nome"
  lake: {estado: convertido, particoes: [], chave: [year, quarter, account], colunas: 4}
  unidades_de_medida:
    value: "R$ (reais correntes)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.7.0
---

# Demonstrativo de Operações do Governo Central Orçamentário - Metodologia Manual de Estatísticas de Finanças Públicas 2014 - Trimestral - Valores Correntes

## Resumo

Aba `4.1` ("Tabela 4.1") da série histórica do Resultado do Tesouro Nacional (RTN). Traz receita, gasto, investimento líquido em ativos não financeiros e a capacidade ou necessidade líquida de financiamento, na classificação do Manual de Estatísticas de Finanças Públicas do FMI de 2014 (GFSM 2014), mais itens de memorando. A tabela cobre o Governo Central (Tesouro Nacional, Previdência Social e Banco Central), com a metodologia "acima da linha" da STN. Cada linha do lake é um valor de uma conta em um trimestre.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `rtn/tabela-4-1` |
| Órgão | Secretaria do Tesouro Nacional (STN), Ministério da Fazenda |
| Página oficial | https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional |
| Licença | Open Data Commons Open Database License (ODbL), conforme o conjunto de dados no portal Tesouro Transparente (conferido em 2026-11-15). |
| Periodicidade | trimestral; atualizada a cada edição do RTN que traz um trimestre novo |
| Cobertura | 2006-01 a em-curso |
| Unidade (uma linha) | o valor de uma conta da tabela em um trimestre |
| Granularidade | espacial: Brasil (Governo Central); temporal: trimestre |
| Formato bruto | aba 4.1 da planilha XLSX da série histórica do RTN (uma aba por tabela); valores em R$ milhões, períodos nas colunas a partir da linha 5; nas abas 4.x a primeira coluna traz o código da conta e a segunda, o nome |
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
- Cada edição traz a série histórica inteira, uma aba por tabela. O conversor lê só a edição mais recente e converte a aba `4.1` em um Parquet de nome fixo (`4-1.parquet`).
- Layout da aba: o título na linha 2, a unidade na linha 3 ("R$ Milhões - Valores Correntes"), o cabeçalho com os períodos na linha 5 (primeira coluna: "Governo Central Orçamentário 1/") e as contas nas linhas seguintes; nas abas 4.x a primeira coluna traz o código da conta e a segunda, o nome. As notas de rodapé ("Obs.", "1/", "2/"...) ficam abaixo da tabela e não entram no lake.
- Conferido em 2026-11-15: edição `seriehistoricajul26.xlsx`, publicada em 27/08/2026 (`Last-Modified` do arquivo), com a aba `4.1` de 2006-T1 a 2026-T1.
- Para o conjunto de dados, a fonte informa frequência de atualização mensal e início em janeiro de 1997 (metadados no portal, conferidos em 2026-11-15); cada aba começa no seu próprio período.

## Conteúdo

- 2.835 linhas: 35 contas × 81 períodos (de 2006-T1 a 2026-T1); cada combinação de `year`, `quarter`, `account` aparece uma vez.
- Unidade de `value`: reais correntes (a fonte publica em R$ milhões e o conversor multiplica por 1.000.000).
- Nenhuma linha tem `value` nulo.
- Os 81 períodos são consecutivos, sem lacunas entre o primeiro e o último.
- O Demonstrativo segue o GFSM 2014 do FMI; a receita é apurada por caixa, exceto os juros, que são por competência, e o gasto é apurado por competência (despesa liquidada), segundo as notas da fonte.

### Contas

O lake guarda só o código da conta em `account`; o nome não vai para o Parquet. A tabela abaixo é a de contas desta tabela na edição de jul/2026 (código, nível hierárquico e nome como a planilha publica, sem a numeração e as chamadas de nota).

Os códigos usam ponto como separador de níveis (`1.1.01` é filha de `1.1`). Códigos que começam por `auto.` foram gerados pelo conversor para linhas que a planilha não numera (posicionais, com base na indentação); um sufixo `#2` marca a segunda ocorrência de um código repetido na mesma aba.

Nesta aba os códigos vêm da primeira coluna e seguem a codificação do GFSM compacta, em que cada dígito é um nível (`1411` vira `1.4.1.1`, `2M` vira `2.M`); `1#2` e `2#2` são as linhas de memorando "1." e "2." (ROB e ROL), cujos códigos repetem os de Receita e Gasto.

| Código (`account`) | Nível | Conta |
|---|---|---|
| `1` | 1 | Receita |
| `1.1` | 2 | &nbsp;&nbsp;Impostos |
| `1.1.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Impostos sobre renda, lucros e ganhos de capital |
| `1.1.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Impostos sobre a folha de pagamento e a mão de obra |
| `1.1.3` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Impostos sobre a propriedade |
| `1.1.4` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Impostos sobre bens e serviços |
| `1.1.5` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Impostos sobre o comércio e transações internacionais |
| `1.1.6` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Outros impostos |
| `1.2` | 2 | &nbsp;&nbsp;Contribuições sociais |
| `1.3` | 2 | &nbsp;&nbsp;Transferências / Doações |
| `1.4` | 2 | &nbsp;&nbsp;Outras receitas |
| `1.4.1.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Juros |
| `1.4.x` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Demais |
| `2.M` | 2 | &nbsp;&nbsp;Despesa (2+31) |
| `2` | 1 | Gasto |
| `2.1` | 2 | &nbsp;&nbsp;Remuneração de empregados |
| `2.2` | 2 | &nbsp;&nbsp;Uso de bens e serviços |
| `2.3` | 2 | &nbsp;&nbsp;Consumo de capital fixo |
| `2.4` | 2 | &nbsp;&nbsp;Juros |
| `2.5` | 2 | &nbsp;&nbsp;Subsídios |
| `2.6` | 2 | &nbsp;&nbsp;Transferências / Doações |
| `2.7` | 2 | &nbsp;&nbsp;Benefícios previdenciários e assistenciais |
| `2.8` | 2 | &nbsp;&nbsp;Outros gastos |
| `3.1` | 2 | &nbsp;&nbsp;Investimento líquido |
| `3.1.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Ativos fixos |
| `3.1.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Estoques |
| `3.1.3` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Objetos de valor |
| `3.1.4` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Ativos não produzidos |
| `auto.29` | 1 | Capacidade (+)/Necessidade(-) líquida de financiamento (1-2M) |
| `auto.30` | 1 | Capacidade (+)/Necessidade(-) líquida de financiamento primária ((1-1411)-(2M-24)) |
| `1#2` | 1 | Resultado operacional bruto - ROB (1-2+23) |
| `2#2` | 1 | Resultado operacional líquido - ROL (1-2) |
| `31.1` | 2 | &nbsp;&nbsp;Aquisição de ativos não financeiros |
| `31.2` | 2 | &nbsp;&nbsp;Venda de ativos não financeiros |
| `31.3` | 2 | &nbsp;&nbsp;Consumo de Capital Fixo |

## Variáveis

A planilha não traz dicionário de colunas: os dados chegam em formato largo (um período por coluna) e o conversor os passa para o formato longo abaixo. O dicionário de conceitos da STN descreve as contas (não as colunas) em um layout de tabelas anterior ao atual, por isso as descrições de contas não são repetidas aqui linha a linha: as contas ficam na tabela da seção Conteúdo, com o nome como a planilha publica, e a coluna "Descrição" abaixo diz o que cada coluna do lake guarda.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `year` | cabeçalho da coluna de período ("AAAA-T", algarismos romanos) | inteiro | Ano do trimestre | ano de quatro dígitos | todo |
| `quarter` | cabeçalho da coluna de período ("AAAA-T", algarismos romanos) | inteiro | Trimestre a que o valor se refere | 1 a 4 (`I` a `IV` na fonte) | todo |
| `account` | rótulo da linha (código na primeira coluna e nome na segunda) | texto | Código hierárquico da conta, com ponto como separador; ver a tabela de contas na seção Conteúdo | os códigos da tabela de contas | todo |
| `value` | célula da conta no período | decimal | Valor da conta no período; célula vazia, `-`, `n.a.`, `n.d.` e "não disp." na planilha viram nulo | R$ (reais correntes) | todo |

## No lake

- Dataset `rtn/tabela-4-1`, sem partições: um único arquivo `4-1.parquet` com as colunas `year`, `quarter`, `account`, `value`.
- O conversor lê a planilha mais recente do bruto, passa a aba do formato largo para o longo (uma linha por conta e período), identifica o código da conta pelo rótulo e aplica o contrato de tipos (`year`, `month` e `quarter` inteiros; `account` texto; `value` decimal de 64 bits).
- O valor é multiplicado por 1.000.000 (a fonte publica em R$ milhões), então `value` está em reais.
- Linhas de notas ("Obs.", "Fonte:", "Memorando" e chamadas "1/"), de deflator e de PIB nominal não viram dados (ver Cuidados de uso).
- Como o nome do arquivo é fixo, converter uma edição nova refaz o arquivo; o lake guarda só a edição convertida mais recente.

## Cuidados de uso

- **O nome da conta não está no lake.** Una `account` à tabela de contas da seção Conteúdo (ou à planilha). O mesmo código significa coisas diferentes em tabelas diferentes: `1.1` é "Receita Administrada pela RFB" na tabela 1.1 e "Investimentos (GND 4)" na 1.3.
- **Há totais e componentes na mesma tabela.** Contas de nível 1 resumem as de nível 2, e assim por diante; some só contas do mesmo nível sob o mesmo pai, ou use só a conta que quer, para não contar duas vezes. Os blocos de memorando (`auto.…`, `m.…`) são recortes ou reclassificações dos totais principais, não parcelas adicionais.
- **Códigos `auto.` são posicionais.** Eles vêm da ordem e da indentação das linhas sem número na planilha; se a STN reordenar a tabela, o mesmo código pode passar a apontar outra linha. Prefira os códigos numéricos da própria planilha.
- **Dados revisáveis.** A fonte avisa "Dados sujeitos à alteração" e diz que a série pode ser revista até o início do exercício corrente (metadados do conjunto de dados); o lake guarda só a edição mais recente, sem a versão anterior.
- **Códigos repetidos.** `1#2` e `2#2` são os itens de memorando ROB e ROL (códigos "1." e "2." na planilha) e não são os mesmos que `1` (Receita) e `2` (Gasto).
- **`31` e `31.1`.** `3.1` é "Investimento líquido" (código `31` da planilha); `31.1`, `31.2` e `31.3` são itens de memorando (aquisição, venda e consumo de capital fixo) e não são filhos de `3.1` (cujos filhos são `3.1.1` a `3.1.4`).
- **Fontes mistas.** As notas da fonte atribuem partes da tabela ao SIAFI, ao Banco Central (juros) e ao IBGE (consumo de capital fixo).

## Exemplos

Últimos 8 trimestres da conta `1` (Receita), em R$ bilhões:

```python
import duckdb

duckdb.sql("""
    SELECT year, quarter, round(value / 1e9, 1) AS valor_bi
    FROM read_parquet('lake/rtn/tabela-4-1/*.parquet')
    WHERE account = '1' AND value IS NOT NULL
    ORDER BY year DESC, quarter DESC LIMIT 8
""").show()
```

## Referências

- Conjunto de dados "Resultado do Tesouro Nacional - Série Histórica" (Tesouro Transparente): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Dicionário de Conceitos e Metodologia de Cálculo (planilha do mesmo conjunto): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Metadados da série (PDF do mesmo conjunto): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
