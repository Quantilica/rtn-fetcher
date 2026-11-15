---
dataset:
  id: tabela-2-5-a
  fonte: rtn
  titulo: "Transferências e despesas primárias do Governo Central apuradas pelo critério de \"valor pago\" - Anual - % do PIB"
  resumo: "Transferências e despesas primárias do Governo Central pelo critério de valor pago, em série anual, em proporção do PIB. Uma linha por conta e período, em formato longo."
  orgao: Secretaria do Tesouro Nacional (STN), Ministério da Fazenda
  pagina_oficial: https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
  licenca: "Open Data Commons Open Database License (ODbL), conforme o conjunto de dados no portal Tesouro Transparente (conferido em 2026-11-15)."
  periodicidade: "anual (anos fechados), atualizada a cada edição mensal do RTN; a série histórica sai inteira em cada planilha"
  cobertura: {inicio: 2008, fim: em-curso}
  unidade: "o valor de uma conta da tabela em um ano"
  granularidade: {espacial: "Brasil (Governo Central)", temporal: ano}
  formato_bruto: "aba 2.5-A da planilha XLSX da série histórica do RTN (uma aba por tabela); valores em % do PIB, períodos nas colunas a partir da linha 5; o código da conta vem embutido no rótulo da primeira coluna"
  lake: {estado: convertido, particoes: [], chave: [year, account], colunas: 3}
  unidades_de_medida:
    value: "fração do PIB nominal do ano (0,167 = 16,7% do PIB)"
  dados_pessoais: nenhum
  eras: 
    - {desde: 2022, mudanca: "as contas 2.1.1 a 2.1.3 (benefícios previdenciários urbano, rural e sentenças) ficam sem valores (observado na edição de jul/2026)"}
  revisado_em: 2026-11-15
  versao_fetcher: 0.7.0
---

# Transferências e despesas primárias do Governo Central apuradas pelo critério de "valor pago" - Anual - % do PIB

## Resumo

Aba `2.5-A` ("Tabela 2.5-A") da série histórica do Resultado do Tesouro Nacional (RTN). Traz as transferências por repartição de receita e a despesa total detalhada (benefícios previdenciários, pessoal, outras despesas obrigatórias, despesas sujeitas à programação financeira), mais um bloco de memorando com os créditos extraordinários. A tabela cobre o Governo Central (Tesouro Nacional, Previdência Social e Banco Central), com a metodologia "acima da linha" da STN. Cada linha do lake é um valor de uma conta em um ano.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `rtn/tabela-2-5-a` |
| Órgão | Secretaria do Tesouro Nacional (STN), Ministério da Fazenda |
| Página oficial | https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional |
| Licença | Open Data Commons Open Database License (ODbL), conforme o conjunto de dados no portal Tesouro Transparente (conferido em 2026-11-15). |
| Periodicidade | anual (anos fechados), atualizada a cada edição mensal do RTN; a série histórica sai inteira em cada planilha |
| Cobertura | 2008 a em-curso |
| Unidade (uma linha) | o valor de uma conta da tabela em um ano |
| Granularidade | espacial: Brasil (Governo Central); temporal: ano |
| Formato bruto | aba 2.5-A da planilha XLSX da série histórica do RTN (uma aba por tabela); valores em % do PIB, períodos nas colunas a partir da linha 5; o código da conta vem embutido no rótulo da primeira coluna |
| Estado no lake | convertido |
| Partições | — |
| Chave | `year`, `account` |
| Colunas | 3 |
| Unidades de medida | `value`: fração do PIB nominal do ano (0,167 = 16,7% do PIB) |
| Dados pessoais | nenhum |
| Eras | 2022: as contas 2.1.1 a 2.1.3 (benefícios previdenciários urbano, rural e sentenças) ficam sem valores (observado na edição de jul/2026) |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.7.0 |

## Origem e coleta

- O fetcher baixa a planilha da série histórica do RTN publicada no portal Tesouro Transparente (conjunto de dados "Resultado do Tesouro Nacional - Série Histórica") e a guarda no bruto como `rtn@AAAAMMDDTHHMMSS.xlsx`, em que o sufixo é o `Last-Modified` do servidor.
- Cada edição traz a série histórica inteira, uma aba por tabela. O conversor lê só a edição mais recente e converte a aba `2.5-A` em um Parquet de nome fixo (`2-5-A.parquet`).
- Layout da aba: o título na linha 2, a unidade na linha 3 ("% do PIB"), o cabeçalho com os períodos na linha 5 (primeira coluna: "Discriminação") e as contas nas linhas seguintes; o código da conta vem embutido no rótulo da primeira coluna. As notas de rodapé ("Obs.", "1/", "2/"...) ficam abaixo da tabela e não entram no lake.
- Conferido em 2026-11-15: edição `seriehistoricajul26.xlsx`, publicada em 27/08/2026 (`Last-Modified` do arquivo), com a aba `2.5-A` de 2008 a 2025.
- Para o conjunto de dados, a fonte informa frequência de atualização mensal e início em janeiro de 1997 (metadados no portal, conferidos em 2026-11-15); cada aba começa no seu próprio período.

## Conteúdo

- 2.070 linhas: 115 contas × 18 períodos (de 2008 a 2025); cada combinação de `year`, `account` aparece uma vez.
- Unidade de `value`: fração do PIB nominal do ano (0,167 = 16,7% do PIB); o conversor não altera o valor da planilha.
- 12 linhas têm `value` nulo, em 3 conta(s) (`2.1.1`, `2.1.2`, `2.1.3`), entre 2022 e 2025 (edição de jul/2026).
- Os 18 períodos são consecutivos, sem lacunas entre o primeiro e o último.
- Só entram anos fechados: o último ano é 2025, enquanto a série mensal vai até 2026-07.

### Contas

O lake guarda só o código da conta em `account`; o nome não vai para o Parquet. A tabela abaixo é a de contas desta tabela na edição de jul/2026 (código, nível hierárquico e nome como a planilha publica, sem a numeração e as chamadas de nota).

Os códigos usam ponto como separador de níveis (`1.1.01` é filha de `1.1`). Códigos que começam por `auto.` foram gerados pelo conversor para linhas que a planilha não numera (posicionais, com base na indentação); um sufixo `#2` marca a segunda ocorrência de um código repetido na mesma aba.

| Código (`account`) | Nível | Conta |
|---|---|---|
| `1` | 1 | TRANSF. POR REPARTIÇÃO DE RECEITA |
| `1.1` | 2 | &nbsp;&nbsp;FPM / FPE / IPI-EE |
| `1.2` | 2 | &nbsp;&nbsp;Fundos Constitucionais |
| `1.2.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Repasse Total |
| `1.2.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Superávit dos Fundos |
| `1.3` | 2 | &nbsp;&nbsp;Contribuição do Salário Educação |
| `1.4` | 2 | &nbsp;&nbsp;Transferências de Exploração de Recursos Naturais (Compensações Financeiras) |
| `1.5` | 2 | &nbsp;&nbsp;CIDE - Combustíveis |
| `1.6` | 2 | &nbsp;&nbsp;Demais |
| `1.6.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Concessão de Recursos Florestais |
| `1.6.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Concurso de Prognóstico |
| `1.6.3` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;IOF Ouro |
| `1.6.4` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;ITR |
| `1.6.5` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Taxa de ocupação, foro e laudêmio |
| `1.6.6` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Outras |
| `2` | 1 | DESPESA TOTAL |
| `2.1` | 2 | &nbsp;&nbsp;Benefícios Previdenciários |
| `2.1.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Benefícios Previdenciários - Urbano |
| `2.1.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Benefícios Previdenciários - Rural |
| `2.1.3` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Benefícios Previdenciários - Sentenças e precatórios |
| `2.2` | 2 | &nbsp;&nbsp;Pessoal e Encargos Sociais |
| `2.2.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Ativo Civil |
| `2.2.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Ativo Militar |
| `2.2.3` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Aposentadorias e pensões civis |
| `2.2.4` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Reformas e pensões militares |
| `2.2.5` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Sentenças e Precatórios |
| `2.2.6` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Outros |
| `2.3` | 2 | &nbsp;&nbsp;Outras Despesas Obrigatórias |
| `2.3.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Abono e seguro desemprego |
| `2.3.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Anistiados |
| `2.3.3` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Apoio Fin. Municípios / Estados |
| `2.3.4` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Benefícios de Legislação Especial e Indenizações |
| `2.3.5` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Benefícios de Prestação Continuada da LOAS/RMV |
| `2.3.5.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Benefícios de Prestação Continuada da LOAS/RMV - Benefícios |
| `2.3.5.2` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Benefícios de Prestação Continuada da LOAS/RMV - Sentenças e Precatórios |
| `2.3.6` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Complemento do FGTS (LC nº 110/01) |
| `2.3.7` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Créditos Extraordinários |
| `2.3.8` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Compensação ao RGPS pelas Desonerações da Folha |
| `2.3.9` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Fabricação de Cédulas e Moedas |
| `2.3.10` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;FUNDEB (Complem. União) |
| `2.3.11` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Fundo Constitucional DF |
| `2.3.12` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Legislativo, Judiciário, MPU e DPU |
| `2.3.13` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Lei Kandir (LC nº 87/96 e 102/00) e LC nº 176 de 2020 |
| `2.3.14` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Sentenças Judiciais e Precatórios - OCC |
| `2.3.15` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Subsídios, Subvenções e Proagro |
| `2.3.15.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Equalização de custeio agropecuário |
| `2.3.15.2` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Equalização de invest. rural e agroindustrial |
| `2.3.15.3` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Equalização Empréstimo do Governo Federal |
| `2.3.15.4` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Equalização Aquisições do Governo Federal |
| `2.3.15.5` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Garantia à Sustentação de Preços |
| `2.3.15.6` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Pronaf |
| `2.3.15.7` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Proex |
| `2.3.15.8` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Programa especial de saneamento de ativos (PESA) |
| `2.3.15.9` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Álcool |
| `2.3.15.10` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Fundo da terra/ INCRA |
| `2.3.15.11` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Funcafé |
| `2.3.15.12` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Revitaliza |
| `2.3.15.13` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Programa de Sustentação ao Investimento - PSI |
| `2.3.15.14` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Operações de crédito destinadas a Pessoas com deficiência (EQPCD) |
| `2.3.15.15` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Fundo Setorial Audiovisual (FSA) |
| `2.3.15.16` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Subv. Parcial à Remuneração por Cessão de Energia Elétrica de Itaipu |
| `2.3.15.17` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Equalização dos Fundos FDA/FDNE/FDCO |
| `2.3.15.18` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Receitas de Recuperação de Subvenções |
| `2.3.15.19` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Proagro |
| `2.3.15.20` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;PNAFE |
| `2.3.15.21` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Fundo Nacional do Desenvolvimento |
| `2.3.15.22` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Sudene (Microcrédito Produtivo Orientado) |
| `2.3.15.23` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Subvenções Econômicas |
| `2.3.15.24` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Securitização da dívida agrícola (Lei 9.318/1595) |
| `2.3.15.25` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Capitalização à Emgea |
| `2.3.15.26` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Cacau |
| `2.3.15.27` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demais Subsídios e Subvenções |
| `2.3.16` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Transferências ANA |
| `2.3.17` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Transferências Multas ANEEL |
| `2.3.18` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Impacto Primário do FIES |
| `2.3.19` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Financiamento de Campanha Eleitoral |
| `2.3.20` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Demais |
| `2.3.20.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Auxílio CDE |
| `2.3.20.2` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Fundos de Desenvolvimento Regional |
| `2.3.20.3` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Reserva de Contingência |
| `2.3.20.4` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ressarc. Est/Mun. Comb. Fósseis |
| `2.4` | 2 | &nbsp;&nbsp;Despesas do Poder Executivo Sujeitas à Programação Financeira |
| `2.4.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Obrigatórias com Controle de Fluxo |
| `2.4.1.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Benefícios a servidores públicos |
| `2.4.1.2` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Bolsa Família e Auxílio Brasil |
| `2.4.1.3` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Saúde |
| `2.4.1.4` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Educação |
| `2.4.1.5` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demais |
| `2.4.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Discricionárias |
| `2.4.2.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Saúde |
| `2.4.2.2` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Educação |
| `2.4.2.3` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Defesa |
| `2.4.2.4` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Transporte |
| `2.4.2.5` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Administração |
| `2.4.2.6` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ciência e Tecnologia |
| `2.4.2.7` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Segurança Pública |
| `2.4.2.8` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Assistência Social |
| `2.4.2.9` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demais |
| `auto.44` | 1 | m. Créditos Extraordinários |
| `m.1` | 2 | &nbsp;&nbsp;Obrigatórias com Controle de Fluxo (Créditos Extraordinários) |
| `m.1.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Obrigatórias com Controle de Fluxo - Benefícios a servidores públicos (Créditos Extraordinários) |
| `m.1.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Obrigatórias com Controle de Fluxo - Bolsa Família e Auxílio Brasil (Créditos Extraordinários) |
| `m.1.3` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Obrigatórias com Controle de Fluxo - Saúde (Créditos Extraordinários) |
| `m.1.4` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Obrigatórias com Controle de Fluxo - Educação (Créditos Extraordinários) |
| `m.1.5` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Obrigatórias com Controle de Fluxo - Demais (Créditos Extraordinários) |
| `m.2` | 2 | &nbsp;&nbsp;Discricionárias (Créditos Extraordinários) |
| `m.2.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Discricionárias - Saúde (Créditos Extraordinários) |
| `m.2.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Discricionárias - Educação (Créditos Extraordinários) |
| `m.2.3` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Discricionárias - Defesa (Créditos Extraordinários) |
| `m.2.4` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Discricionárias - Transporte (Créditos Extraordinários) |
| `m.2.5` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Discricionárias - Administração (Créditos Extraordinários) |
| `m.2.6` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Discricionárias - Ciência e Tecnologia (Créditos Extraordinários) |
| `m.2.7` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Discricionárias - Segurança Pública (Créditos Extraordinários) |
| `m.2.8` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Discricionárias - Assistência Social (Créditos Extraordinários) |
| `m.2.9` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Discricionárias - Demais (Créditos Extraordinários) |

## Variáveis

A planilha não traz dicionário de colunas: os dados chegam em formato largo (um período por coluna) e o conversor os passa para o formato longo abaixo. O dicionário de conceitos da STN descreve as contas (não as colunas) em um layout de tabelas anterior ao atual, por isso as descrições de contas não são repetidas aqui linha a linha: as contas ficam na tabela da seção Conteúdo, com o nome como a planilha publica, e a coluna "Descrição" abaixo diz o que cada coluna do lake guarda.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `year` | cabeçalho da coluna de período (ano) | inteiro | Ano a que o valor se refere | ano de quatro dígitos | todo |
| `account` | rótulo da linha (primeira coluna, com o código embutido) | texto | Código hierárquico da conta, com ponto como separador; ver a tabela de contas na seção Conteúdo | os códigos da tabela de contas | todo |
| `value` | célula da conta no período | decimal | Valor da conta no período; célula vazia, `-`, `n.a.`, `n.d.` e "não disp." na planilha viram nulo | fração do PIB nominal do ano (0,167 = 16,7% do PIB) | todo |

## No lake

- Dataset `rtn/tabela-2-5-a`, sem partições: um único arquivo `2-5-A.parquet` com as colunas `year`, `account`, `value`.
- O conversor lê a planilha mais recente do bruto, passa a aba do formato largo para o longo (uma linha por conta e período), identifica o código da conta pelo rótulo e aplica o contrato de tipos (`year`, `month` e `quarter` inteiros; `account` texto; `value` decimal de 64 bits).
- A planilha não está em R$ milhões: `value` é a proporção do PIB como a fonte publica, sem multiplicação.
- Linhas de notas ("Obs.", "Fonte:", "Memorando" e chamadas "1/"), de deflator e de PIB nominal não viram dados (ver Cuidados de uso).
- Como o nome do arquivo é fixo, converter uma edição nova refaz o arquivo; o lake guarda só a edição convertida mais recente.

## Cuidados de uso

- **O nome da conta não está no lake.** Una `account` à tabela de contas da seção Conteúdo (ou à planilha). O mesmo código significa coisas diferentes em tabelas diferentes: `1.1` é "Receita Administrada pela RFB" na tabela 1.1 e "Investimentos (GND 4)" na 1.3.
- **Há totais e componentes na mesma tabela.** Contas de nível 1 resumem as de nível 2, e assim por diante; some só contas do mesmo nível sob o mesmo pai, ou use só a conta que quer, para não contar duas vezes. Os blocos de memorando (`auto.…`, `m.…`) são recortes ou reclassificações dos totais principais, não parcelas adicionais.
- **Códigos `auto.` são posicionais.** Eles vêm da ordem e da indentação das linhas sem número na planilha; se a STN reordenar a tabela, o mesmo código pode passar a apontar outra linha. Prefira os códigos numéricos da própria planilha.
- **Dados revisáveis.** A fonte avisa "Dados sujeitos à alteração" e diz que a série pode ser revista até o início do exercício corrente (metadados do conjunto de dados); o lake guarda só a edição mais recente, sem a versão anterior.
- **Critério de apuração das despesas.** Veja as notas da própria aba na planilha: a fonte registra por caixa e apura as despesas ora por "pagamento efetivo" (saque na Conta Única), ora por "valor pago" (ordens bancárias emitidas), conforme a tabela (metadados do conjunto de dados).
- **Proporção, não percentual.** `0,167` é 16,7% do PIB. O PIB nominal usado (R$ milhões, por ano) está numa linha de memorando da planilha, que o conversor não leva para o lake; se precisar dele, leia a planilha.
- **Mudança de abertura em 2022.** As contas 2.1.1 a 2.1.3 (benefícios previdenciários urbano, rural e sentenças) só têm valores até 2021, e Para séries longas, use a conta pai (`2.1`, `2.3.1`).
- **Memorando de créditos extraordinários.** O bloco `auto.44` e `m.…` traz os créditos extraordinários por tipo de despesa; é um memorando e não deve ser somado às contas principais.

## Exemplos

Últimos 10 anos da conta `1` (TRANSF. POR REPARTIÇÃO DE RECEITA), em % do PIB:

```python
import duckdb

duckdb.sql("""
    SELECT year, round(value * 100, 2) AS pct_do_pib
    FROM read_parquet('lake/rtn/tabela-2-5-a/*.parquet')
    WHERE account = '1' AND value IS NOT NULL
    ORDER BY year DESC LIMIT 10
""").show()
```

## Referências

- Conjunto de dados "Resultado do Tesouro Nacional - Série Histórica" (Tesouro Transparente): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Dicionário de Conceitos e Metodologia de Cálculo (planilha do mesmo conjunto): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Metadados da série (PDF do mesmo conjunto): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
