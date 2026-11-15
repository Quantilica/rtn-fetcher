---
dataset:
  id: tabela-1-2-a
  fonte: rtn
  titulo: "Resultado Primário do Governo Central - Mensal - Valores Constantes (IPCA)"
  resumo: "Resultado primário do Governo Central em versão detalhada, em série mensal, em valores constantes (IPCA). Uma linha por conta e período, em formato longo."
  orgao: Secretaria do Tesouro Nacional (STN), Ministério da Fazenda
  pagina_oficial: https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
  licenca: "Open Data Commons Open Database License (ODbL), conforme o conjunto de dados no portal Tesouro Transparente (conferido em 2026-11-15)."
  periodicidade: "mensal; a STN publica uma planilha nova a cada edição do RTN, com a série histórica inteira"
  cobertura: {inicio: 1997-01, fim: em-curso}
  unidade: "o valor de uma conta da tabela em um mês"
  granularidade: {espacial: "Brasil (Governo Central)", temporal: mês}
  formato_bruto: "aba 1.2-A da planilha XLSX da série histórica do RTN (uma aba por tabela); valores em R$ milhões, períodos nas colunas a partir da linha 5; o código da conta vem embutido no rótulo da primeira coluna"
  lake: {estado: convertido, particoes: [], chave: [year, month, account], colunas: 4}
  unidades_de_medida:
    value: "R$ de jul/2026 (reais constantes, deflacionados pelo IPCA)"
  dados_pessoais: nenhum
  eras: 
    - {desde: 2020-01, mudanca: "a conta auto.10.4 (PAC, em memorando) fica sem valores"}
    - {desde: 2026-01, mudanca: "a conta auto.10.4.1 (Minha Casa Minha Vida, em memorando) fica sem valores (observado na edição de jul/2026)"}
  revisado_em: 2026-11-15
  versao_fetcher: 0.7.0
---

# Resultado Primário do Governo Central - Mensal - Valores Constantes (IPCA)

## Resumo

Aba `1.2-A` ("Tabela 1.2-A") da série histórica do Resultado do Tesouro Nacional (RTN). Traz as mesmas contas da versão resumida, abertas em mais níveis (por exemplo, as subvenções e os subsídios item a item), mais um bloco de memorando. A tabela cobre o Governo Central (Tesouro Nacional, Previdência Social e Banco Central), com a metodologia "acima da linha" da STN. Cada linha do lake é um valor de uma conta em um mês.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `rtn/tabela-1-2-a` |
| Órgão | Secretaria do Tesouro Nacional (STN), Ministério da Fazenda |
| Página oficial | https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional |
| Licença | Open Data Commons Open Database License (ODbL), conforme o conjunto de dados no portal Tesouro Transparente (conferido em 2026-11-15). |
| Periodicidade | mensal; a STN publica uma planilha nova a cada edição do RTN, com a série histórica inteira |
| Cobertura | 1997-01 a em-curso |
| Unidade (uma linha) | o valor de uma conta da tabela em um mês |
| Granularidade | espacial: Brasil (Governo Central); temporal: mês |
| Formato bruto | aba 1.2-A da planilha XLSX da série histórica do RTN (uma aba por tabela); valores em R$ milhões, períodos nas colunas a partir da linha 5; o código da conta vem embutido no rótulo da primeira coluna |
| Estado no lake | convertido |
| Partições | — |
| Chave | `year`, `month`, `account` |
| Colunas | 4 |
| Unidades de medida | `value`: R$ de jul/2026 (reais constantes, deflacionados pelo IPCA) |
| Dados pessoais | nenhum |
| Eras | 2020-01: a conta auto.10.4 (PAC, em memorando) fica sem valores; 2026-01: a conta auto.10.4.1 (Minha Casa Minha Vida, em memorando) fica sem valores (observado na edição de jul/2026) |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.7.0 |

## Origem e coleta

- O fetcher baixa a planilha da série histórica do RTN publicada no portal Tesouro Transparente (conjunto de dados "Resultado do Tesouro Nacional - Série Histórica") e a guarda no bruto como `rtn@AAAAMMDDTHHMMSS.xlsx`, em que o sufixo é o `Last-Modified` do servidor.
- Cada edição traz a série histórica inteira, uma aba por tabela. O conversor lê só a edição mais recente e converte a aba `1.2-A` em um Parquet de nome fixo (`1-2-A.parquet`).
- Layout da aba: o título na linha 2, a unidade na linha 3 ("R$ Milhões - Valores de Jul/2026 - IPCA"), o cabeçalho com os períodos na linha 5 (primeira coluna: "Discriminação") e as contas nas linhas seguintes; o código da conta vem embutido no rótulo da primeira coluna. As notas de rodapé ("Obs.", "1/", "2/"...) ficam abaixo da tabela e não entram no lake.
- Conferido em 2026-11-15: edição `seriehistoricajul26.xlsx`, publicada em 27/08/2026 (`Last-Modified` do arquivo), com a aba `1.2-A` de 1997-01 a 2026-07.
- Para o conjunto de dados, a fonte informa frequência de atualização mensal e início em janeiro de 1997 (metadados no portal, conferidos em 2026-11-15); cada aba começa no seu próprio período.

## Conteúdo

- 59.285 linhas: 167 contas × 355 períodos (de 1997-01 a 2026-07); cada combinação de `year`, `month`, `account` aparece uma vez.
- Unidade de `value`: reais constantes da data-base do cabeçalho da aba (nesta edição, Jul/2026), deflacionados pelo IPCA (a fonte publica em R$ milhões e o conversor multiplica por 1.000.000).
- 95 linhas têm `value` nulo, em 11 conta(s) (`10`, `6`, `6.1`, `6.2`, `6.3`, `6.4`, `7`, `8`, `9`, `auto.10.4`, `auto.10.4.1`), entre 2020-01 e 2026-07 (edição de jul/2026).
- Os 355 períodos são consecutivos, sem lacunas entre o primeiro e o último.
- As contas 6 a 10 (ajustes metodológicos, discrepância estatística, resultado abaixo da linha, juros nominais e resultado nominal) ficam nulas no último mês da planilha (2026-07). A fonte não explica o motivo; as notas atribuem ao Banco Central o resultado abaixo da linha e os juros nominais.

### Contas

O lake guarda só o código da conta em `account`; o nome não vai para o Parquet. A tabela abaixo é a de contas desta tabela na edição de jul/2026 (código, nível hierárquico e nome como a planilha publica, sem a numeração e as chamadas de nota).

Os códigos usam ponto como separador de níveis (`1.1.01` é filha de `1.1`). Códigos que começam por `auto.` foram gerados pelo conversor para linhas que a planilha não numera (posicionais, com base na indentação); um sufixo `#2` marca a segunda ocorrência de um código repetido na mesma aba.

| Código (`account`) | Nível | Conta |
|---|---|---|
| `1` | 1 | RECEITA TOTAL |
| `1.1` | 2 | &nbsp;&nbsp;Receita Administrada pela RFB |
| `1.1.01` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Imposto sobre a Importação |
| `1.1.02` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;IPI |
| `1.1.02.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IPI - Fumo |
| `1.1.02.2` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IPI - Bebidas |
| `1.1.02.3` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IPI - Automóveis |
| `1.1.02.4` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IPI - Vinculado à importação |
| `1.1.02.5` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IPI - Outros |
| `1.1.03` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Imposto sobre a Renda |
| `1.1.03.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;I.R. - Pessoa Física |
| `1.1.03.2` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;I.R. - Pessoa Jurídica |
| `1.1.03.3` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;I.R. - Retido na fonte |
| `1.1.03.3.1` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IRRF - Rendimentos do Trabalho |
| `1.1.03.3.2` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IRRF - Rendimentos do Capital |
| `1.1.03.3.3` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IRRF - Rendimentos de Residentes no Exterior |
| `1.1.03.3.4` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IRRF - Outros Rendimentos |
| `1.1.04` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;IOF |
| `1.1.05` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Cofins |
| `1.1.06` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;PIS/Pasep |
| `1.1.07` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;CSLL |
| `1.1.08` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;CPMF |
| `1.1.09` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;CIDE - Combustíveis |
| `1.1.10` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Outras Receitas Administradas pela RFB |
| `1.2` | 2 | &nbsp;&nbsp;Incentivos Fiscais |
| `1.3` | 2 | &nbsp;&nbsp;Arrecadação Líquida para o RGPS |
| `1.3.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Arrecadação Líquida para o RGPS - Urbana |
| `1.3.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Arrecadação Líquida para o RGPS - Rural |
| `1.4` | 2 | &nbsp;&nbsp;Receitas Não Administradas pela RFB |
| `1.4.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Concessões e Permissões |
| `1.4.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Dividendos e Participações |
| `1.4.2.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Banco do Brasil |
| `1.4.2.2` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BNB |
| `1.4.2.3` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;BNDES |
| `1.4.2.4` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Caixa Econômica Federal |
| `1.4.2.5` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Empresa Brasileira de Correios e Telégrafos (Correios) |
| `1.4.2.6` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Eletrobrás |
| `1.4.2.7` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;IRB |
| `1.4.2.8` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Petrobras |
| `1.4.2.9` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demais Dividendos e Participações |
| `1.4.3` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Contr. Plano de Seguridade Social do Servidor |
| `1.4.4` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Receitas de Exploração de Recursos Naturais |
| `1.4.5` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Receitas Próprias (fontes 50, 81 e 82) |
| `1.4.6` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Contribuição do Salário Educação |
| `1.4.7` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Complemento para o FGTS (LC nº 110/01) |
| `1.4.8` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Demais Receitas Não Administradas pela RFB |
| `1.4.8.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;d/q Receitas de Operações com Ativos |
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
| `4.1.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Benefícios Previdenciários - Urbano |
| `4.1.1.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Sent. Judiciais e Precatórios de Benefícios Previdenciários - Urbano |
| `4.1.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Benefícios Previdenciários - Rural |
| `4.1.2.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Sent. Judiciais e Precatórios de Benefícios Previdenciários - Rural |
| `4.2` | 2 | &nbsp;&nbsp;Pessoal e Encargos Sociais |
| `4.2.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Sent. Judiciais e Precatórios de Pessoal e Encargos |
| `4.3` | 2 | &nbsp;&nbsp;Outras Despesas Obrigatórias |
| `4.3.01` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Abono e Seguro Desemprego |
| `4.3.01.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Abono |
| `4.3.01.2` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Seguro Desemprego |
| `4.3.01.2.1` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;d/q Seguro Defeso |
| `4.3.02` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Anistiados |
| `4.3.03` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Apoio Fin. EE/MM |
| `4.3.04` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Benefícios de Legislação Especial e Indenizações |
| `4.3.05` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Benefícios de Prestação Continuada da LOAS/RMV |
| `4.3.05.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Sentenças Judiciais e Precatórios de BPC/LOAS |
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
| `4.3.15.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Operações Oficiais de Crédito e Reordenamento de Passivos |
| `4.3.15.1.1` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Equalização de custeio agropecuário |
| `4.1.15.1.2` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Equalização de invest. rural e agroindustrial |
| `4.3.15.1.3` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Política de preços agrícolas |
| `4.3.15.1.3.1` | 6 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Equalização Empréstimo do Governo Federal |
| `4.3.15.1.3.2` | 6 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Equalização Aquisições do Governo Federal |
| `4.3.15.1.3.3` | 6 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Garantia à Sustentação de Preços |
| `4.3.15.1.4` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Pronaf |
| `4.3.15.1.4.1` | 6 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Equalização Empréstimo do Governo Federal |
| `4.3.15.1.4.2` | 6 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Concessão de Financiamento |
| `4.3.15.1.4.3` | 6 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Aquisição |
| `4.3.15.1.5` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Proex |
| `4.3.15.1.5.1` | 6 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Equalização Empréstimo do Governo Federal |
| `4.3.15.1.5.2` | 6 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Concessão de Financiamento |
| `4.3.15.1.6` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Programa especial de saneamento de ativos (PESA) |
| `4.3.15.1.7` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Álcool |
| `4.3.15.1.8` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Cacau |
| `4.3.15.1.9` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Programa de subsídio à habitação de interesse social (PSH) |
| `4.3.15.1.10` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Securitização da dívida agrícola (LEI 9.138/1995) |
| `4.3.15.1.11` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Fundo da terra/ INCRA |
| `4.3.15.1.12` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Funcafé |
| `4.3.15.1.13` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Revitaliza |
| `4.3.15.1.14` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Programa de Sustentação ao Investimento - PSI |
| `4.3.15.1.15` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Operações de Microcredito Produtivo Orientado (EQMPO) |
| `4.3.15.1.16` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Operações de crédito destinadas a Pessoas com deficiência (EQPCD) |
| `4.3.15.1.17` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Fundo nacional de desenvolvimento (FND) |
| `4.3.15.1.18` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Fundo Setorial Audiovisual (FSA) |
| `4.3.15.1.19` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Capitalização à Emgea |
| `4.3.15.1.20` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Subv. Parcial à Remuneração por Cessão de Energia Elétrica de Itaipu |
| `4.3.15.1.21` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Subvenções Econômicas |
| `4.3.15.1.22` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Equalização dos Fundos FDA/FDNE/FDCO |
| `4.3.15.1.23` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Sudene |
| `4.3.15.1.24` | 5 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Receitas de Recuperação de Subvenções |
| `4.3.15.2` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Proagro |
| `4.3.15.3` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;PNAFE |
| `4.3.15.4` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demais Subsídios e Subvenções |
| `4.3.16` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Transferências ANA |
| `4.3.17` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Transferências Multas ANEEL |
| `4.3.18` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Impacto Primário do FIES |
| `4.3.19` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Financiamento de Campanha Eleitoral |
| `4.3.20` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Demais Despesas Obrigatórias |
| `4.3.20.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Auxílio CDE |
| `4.3.20.2` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Convênios |
| `4.3.20.3` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Doações |
| `4.3.20.4` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;FDA/FDNE |
| `4.3.20.5` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Reserva de Contingência |
| `4.3.20.6` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ressarc. Est/Mun. Comb. Fósseis |
| `4.4` | 2 | &nbsp;&nbsp;Despesas do Poder Executivo Sujeitas à Programação Financeira |
| `4.4.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Obrigatórias com Controle de Fluxo |
| `4.4.1.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Benefícios a servidores públicos |
| `4.4.1.2` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Bolsa Família e Auxílio Brasil |
| `4.4.1.3` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Saúde |
| `4.4.1.4` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Educação |
| `4.4.1.5` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demais |
| `4.4.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Despesas Discricionárias |
| `4.4.2.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Saúde |
| `4.4.2.2` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Educação |
| `4.4.2.3` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Defesa |
| `4.4.2.4` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Transporte |
| `4.4.2.5` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Administração |
| `4.4.2.6` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ciência e Tecnologia |
| `4.4.2.7` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Segurança Pública |
| `4.4.2.8` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Assistência Social |
| `4.4.2.9` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demais |
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
| `auto.10.1` | 2 | &nbsp;&nbsp;Arrecadação Líquida para o RGPS |
| `auto.10.1.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Arrecadação Ordinária |
| `auto.10.1.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Compensação ao RGPS pelas Desonerações da Folha |
| `auto.10.2` | 2 | &nbsp;&nbsp;Custeio Administrativo |
| `auto.10.3` | 2 | &nbsp;&nbsp;Investimento |
| `auto.10.4` | 2 | &nbsp;&nbsp;PAC |
| `auto.10.4.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Minha Casa Minha Vida |
| `auto.10.5` | 2 | &nbsp;&nbsp;Fundo Soberano do Brasil |

## Variáveis

A planilha não traz dicionário de colunas: os dados chegam em formato largo (um período por coluna) e o conversor os passa para o formato longo abaixo. O dicionário de conceitos da STN descreve as contas (não as colunas) em um layout de tabelas anterior ao atual, por isso as descrições de contas não são repetidas aqui linha a linha: as contas ficam na tabela da seção Conteúdo, com o nome como a planilha publica, e a coluna "Descrição" abaixo diz o que cada coluna do lake guarda.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `year` | cabeçalho da coluna de período (data) | inteiro | Ano do mês a que o valor se refere | ano de quatro dígitos | todo |
| `month` | cabeçalho da coluna de período (data) | inteiro | Mês a que o valor se refere | 1 a 12 | todo |
| `account` | rótulo da linha (primeira coluna, com o código embutido) | texto | Código hierárquico da conta, com ponto como separador; ver a tabela de contas na seção Conteúdo | os códigos da tabela de contas | todo |
| `value` | célula da conta no período | decimal | Valor da conta no período; célula vazia, `-`, `n.a.`, `n.d.` e "não disp." na planilha viram nulo | R$ de jul/2026 (reais constantes, deflacionados pelo IPCA) | todo |

## No lake

- Dataset `rtn/tabela-1-2-a`, sem partições: um único arquivo `1-2-A.parquet` com as colunas `year`, `month`, `account`, `value`.
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
- **Valores constantes mudam de base a cada edição.** O deflator é o IPCA com base no mês da edição (nesta, Jul/2026). Não junte `value` de edições diferentes e não compare com a aba de valores correntes sem deflacionar de novo.
- **Linha de deflator descartada.** A planilha traz o deflator do IPCA (razão por mês, de 1 a ~6) em uma linha "Deflator - IPCA base Jul/2026"; o conversor a descarta, então o lake não permite reverter o ajuste.
- **Último mês incompleto.** As contas 6 a 10 (ajustes, discrepância, abaixo da linha, juros e resultado nominal) ficam nulas em 2026-07 (edição de jul/2026); use 2026-06 como último mês completo ou trate o nulo.
- **PAC e Minha Casa Minha Vida em memorando.** `auto.10.4` (PAC) só tem valores até 2019-12 e `auto.10.4.1` (Minha Casa Minha Vida) até 2025-12 (edição de jul/2026); depois disso os valores são nulos.

## Exemplos

Últimos 12 meses da conta `1` (RECEITA TOTAL), em R$ bilhões:

```python
import duckdb

duckdb.sql("""
    SELECT year, month, round(value / 1e9, 1) AS valor_bi
    FROM read_parquet('lake/rtn/tabela-1-2-a/*.parquet')
    WHERE account = '1' AND value IS NOT NULL
    ORDER BY year DESC, month DESC LIMIT 12
""").show()
```

## Referências

- Conjunto de dados "Resultado do Tesouro Nacional - Série Histórica" (Tesouro Transparente): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Dicionário de Conceitos e Metodologia de Cálculo (planilha do mesmo conjunto): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Metadados da série (PDF do mesmo conjunto): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
