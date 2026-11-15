---
dataset:
  id: tabela-1-4-a
  fonte: rtn
  titulo: "Custeio Administrativo do Governo Central - Mensal - Valores Constantes (IPCA)"
  resumo: "Custeio administrativo do Governo Central, em série mensal, em valores constantes (IPCA). Uma linha por conta e período, em formato longo."
  orgao: Secretaria do Tesouro Nacional (STN), Ministério da Fazenda
  pagina_oficial: https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
  licenca: "Open Data Commons Open Database License (ODbL), conforme o conjunto de dados no portal Tesouro Transparente (conferido em 2026-11-15)."
  periodicidade: "mensal; a STN publica uma planilha nova a cada edição do RTN, com a série histórica inteira"
  cobertura: {inicio: 2011-01, fim: em-curso}
  unidade: "o valor de uma conta da tabela em um mês"
  granularidade: {espacial: "Brasil (Governo Central)", temporal: mês}
  formato_bruto: "aba 1.4-A da planilha XLSX da série histórica do RTN (uma aba por tabela); valores em R$ milhões, períodos nas colunas a partir da linha 5; o código da conta vem embutido no rótulo da primeira coluna"
  lake: {estado: convertido, particoes: [], chave: [year, month, account], colunas: 4}
  unidades_de_medida:
    value: "R$ de jul/2026 (reais constantes, deflacionados pelo IPCA)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.7.0
---

# Custeio Administrativo do Governo Central - Mensal - Valores Constantes (IPCA)

## Resumo

Aba `1.4-A` ("Tabela 1.4-A") da série histórica do Resultado do Tesouro Nacional (RTN). Traz o custeio administrativo por grupo e item de despesa e, em um bloco de memorando, o custeio administrativo por função orçamentária. A tabela cobre o Governo Central (Tesouro Nacional, Previdência Social e Banco Central), com a metodologia "acima da linha" da STN. Cada linha do lake é um valor de uma conta em um mês.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `rtn/tabela-1-4-a` |
| Órgão | Secretaria do Tesouro Nacional (STN), Ministério da Fazenda |
| Página oficial | https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional |
| Licença | Open Data Commons Open Database License (ODbL), conforme o conjunto de dados no portal Tesouro Transparente (conferido em 2026-11-15). |
| Periodicidade | mensal; a STN publica uma planilha nova a cada edição do RTN, com a série histórica inteira |
| Cobertura | 2011-01 a em-curso |
| Unidade (uma linha) | o valor de uma conta da tabela em um mês |
| Granularidade | espacial: Brasil (Governo Central); temporal: mês |
| Formato bruto | aba 1.4-A da planilha XLSX da série histórica do RTN (uma aba por tabela); valores em R$ milhões, períodos nas colunas a partir da linha 5; o código da conta vem embutido no rótulo da primeira coluna |
| Estado no lake | convertido |
| Partições | — |
| Chave | `year`, `month`, `account` |
| Colunas | 4 |
| Unidades de medida | `value`: R$ de jul/2026 (reais constantes, deflacionados pelo IPCA) |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.7.0 |

## Origem e coleta

- O fetcher baixa a planilha da série histórica do RTN publicada no portal Tesouro Transparente (conjunto de dados "Resultado do Tesouro Nacional - Série Histórica") e a guarda no bruto como `rtn@AAAAMMDDTHHMMSS.xlsx`, em que o sufixo é o `Last-Modified` do servidor.
- Cada edição traz a série histórica inteira, uma aba por tabela. O conversor lê só a edição mais recente e converte a aba `1.4-A` em um Parquet de nome fixo (`1-4-A.parquet`).
- Layout da aba: o título na linha 2, a unidade na linha 3 ("R$ Milhões - Valores de Jul/2026 - IPCA"), o cabeçalho com os períodos na linha 5 (primeira coluna: "Custeio Administrativo por Grupo e Item") e as contas nas linhas seguintes; o código da conta vem embutido no rótulo da primeira coluna. As notas de rodapé ("Obs.", "1/", "2/"...) ficam abaixo da tabela e não entram no lake.
- Conferido em 2026-11-15: edição `seriehistoricajul26.xlsx`, publicada em 27/08/2026 (`Last-Modified` do arquivo), com a aba `1.4-A` de 2011-01 a 2026-07.
- Para o conjunto de dados, a fonte informa frequência de atualização mensal e início em janeiro de 1997 (metadados no portal, conferidos em 2026-11-15); cada aba começa no seu próprio período.

## Conteúdo

- 11.407 linhas: 61 contas × 187 períodos (de 2011-01 a 2026-07); cada combinação de `year`, `month`, `account` aparece uma vez.
- Unidade de `value`: reais constantes da data-base do cabeçalho da aba (nesta edição, Jul/2026), deflacionados pelo IPCA (a fonte publica em R$ milhões e o conversor multiplica por 1.000.000).
- Nenhuma linha tem `value` nulo.
- Os 187 períodos são consecutivos, sem lacunas entre o primeiro e o último.

### Contas

O lake guarda só o código da conta em `account`; o nome não vai para o Parquet. A tabela abaixo é a de contas desta tabela na edição de jul/2026 (código, nível hierárquico e nome como a planilha publica, sem a numeração e as chamadas de nota).

Os códigos usam ponto como separador de níveis (`1.1.01` é filha de `1.1`). Códigos que começam por `auto.` foram gerados pelo conversor para linhas que a planilha não numera (posicionais, com base na indentação); um sufixo `#2` marca a segunda ocorrência de um código repetido na mesma aba.

| Código (`account`) | Nível | Conta |
|---|---|---|
| `auto.1` | 1 | CUSTEIO ADMINISTRATIVO (1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9) |
| `1` | 1 | Serviços de Apoio |
| `1.1` | 2 | &nbsp;&nbsp;Contratação Temporária |
| `1.2` | 2 | &nbsp;&nbsp;Locações de Mão-de-Obra e Terceirização |
| `1.3` | 2 | &nbsp;&nbsp;Serviços de Limpeza e Conservação |
| `1.4` | 2 | &nbsp;&nbsp;Vigilância Ostensiva |
| `1.5` | 2 | &nbsp;&nbsp;Apoio Administrativo, Técnico e Operacional |
| `2` | 1 | Material de Consumo |
| `2.1` | 2 | &nbsp;&nbsp;Combustíveis e Lubrificantes |
| `2.2` | 2 | &nbsp;&nbsp;Outros Materiais de Consumo |
| `3` | 1 | Tecnologia da Informação e Comunicação |
| `3.1` | 2 | &nbsp;&nbsp;Tecnologia da Informação e Comunicação |
| `4` | 1 | Serviços de Comunicação em Geral e Telecomunicações |
| `4.1` | 2 | &nbsp;&nbsp;Serviços de Comunicação em Geral |
| `4.2` | 2 | &nbsp;&nbsp;Serviços de Telecomunicações |
| `5` | 1 | Locação e Conservação de Bens Imóveis |
| `5.1` | 2 | &nbsp;&nbsp;Locação de Imóveis |
| `5.2` | 2 | &nbsp;&nbsp;Manutenção e Conservação de Bens Imóveis |
| `6` | 1 | Energia Elétrica e Água |
| `6.1` | 2 | &nbsp;&nbsp;Serviços de Água e Esgoto |
| `6.2` | 2 | &nbsp;&nbsp;Serviços de Energia Elétrica |
| `7` | 1 | Locação e Conservação de Bens Móveis |
| `7.1` | 2 | &nbsp;&nbsp;Locação de Máquinas e Equipamentos |
| `7.2` | 2 | &nbsp;&nbsp;Manutenção e Conservação de Equipamentos |
| `7.3` | 2 | &nbsp;&nbsp;Locação de Veículos |
| `8` | 1 | Diárias e Passagens |
| `8.1` | 2 | &nbsp;&nbsp;Diárias |
| `8.2` | 2 | &nbsp;&nbsp;Passagens e Despesas com Locomoção |
| `9` | 1 | Outros Serviços |
| `9.1` | 2 | &nbsp;&nbsp;Serviços Bancários |
| `9.2` | 2 | &nbsp;&nbsp;Serviços de Cópias e Reproduções de Documentos |
| `9.3` | 2 | &nbsp;&nbsp;Serviços de Consultoria |
| `auto.11` | 1 | CUSTEIO ADMINISTRATIVO |
| `auto.11.1` | 2 | &nbsp;&nbsp;Legislativa |
| `auto.11.2` | 2 | &nbsp;&nbsp;Judiciária |
| `auto.11.3` | 2 | &nbsp;&nbsp;Essencial à Justiça |
| `auto.11.4` | 2 | &nbsp;&nbsp;Administração |
| `auto.11.5` | 2 | &nbsp;&nbsp;Defesa Nacional |
| `auto.11.6` | 2 | &nbsp;&nbsp;Segurança Pública |
| `auto.11.7` | 2 | &nbsp;&nbsp;Relações Exteriores |
| `auto.11.8` | 2 | &nbsp;&nbsp;Assistência Social |
| `auto.11.9` | 2 | &nbsp;&nbsp;Previdência Social |
| `auto.11.10` | 2 | &nbsp;&nbsp;Saúde |
| `auto.11.11` | 2 | &nbsp;&nbsp;Trabalho |
| `auto.11.12` | 2 | &nbsp;&nbsp;Educação |
| `auto.11.13` | 2 | &nbsp;&nbsp;Cultura |
| `auto.11.14` | 2 | &nbsp;&nbsp;Direitos da Cidadania |
| `auto.11.15` | 2 | &nbsp;&nbsp;Urbanismo |
| `auto.11.16` | 2 | &nbsp;&nbsp;Habitação |
| `auto.11.17` | 2 | &nbsp;&nbsp;Saneamento |
| `auto.11.18` | 2 | &nbsp;&nbsp;Gestão Ambiental |
| `auto.11.19` | 2 | &nbsp;&nbsp;Ciência e Tecnologia |
| `auto.11.20` | 2 | &nbsp;&nbsp;Agricultura |
| `auto.11.21` | 2 | &nbsp;&nbsp;Organização Agrária |
| `auto.11.22` | 2 | &nbsp;&nbsp;Indústria |
| `auto.11.23` | 2 | &nbsp;&nbsp;Comércio e Serviços |
| `auto.11.24` | 2 | &nbsp;&nbsp;Comunicações |
| `auto.11.25` | 2 | &nbsp;&nbsp;Energia |
| `auto.11.26` | 2 | &nbsp;&nbsp;Transporte |
| `auto.11.27` | 2 | &nbsp;&nbsp;Desporto e Lazer |
| `auto.11.28` | 2 | &nbsp;&nbsp;Encargos Especiais |

## Variáveis

A planilha não traz dicionário de colunas: os dados chegam em formato largo (um período por coluna) e o conversor os passa para o formato longo abaixo. O dicionário de conceitos da STN descreve as contas (não as colunas) em um layout de tabelas anterior ao atual, por isso as descrições de contas não são repetidas aqui linha a linha: as contas ficam na tabela da seção Conteúdo, com o nome como a planilha publica, e a coluna "Descrição" abaixo diz o que cada coluna do lake guarda.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `year` | cabeçalho da coluna de período (data) | inteiro | Ano do mês a que o valor se refere | ano de quatro dígitos | todo |
| `month` | cabeçalho da coluna de período (data) | inteiro | Mês a que o valor se refere | 1 a 12 | todo |
| `account` | rótulo da linha (primeira coluna, com o código embutido) | texto | Código hierárquico da conta, com ponto como separador; ver a tabela de contas na seção Conteúdo | os códigos da tabela de contas | todo |
| `value` | célula da conta no período | decimal | Valor da conta no período; célula vazia, `-`, `n.a.`, `n.d.` e "não disp." na planilha viram nulo | R$ de jul/2026 (reais constantes, deflacionados pelo IPCA) | todo |

## No lake

- Dataset `rtn/tabela-1-4-a`, sem partições: um único arquivo `1-4-A.parquet` com as colunas `year`, `month`, `account`, `value`.
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
- **Linha de deflator descartada.** A planilha traz o deflator do IPCA em uma linha "Deflator - IPCA base Jul/2026"; o conversor a descarta.
- **Dois blocos.** `auto.1` e os códigos `1` a `9` são o custeio administrativo por grupo e item; `auto.11…` é o memorando por função orçamentária. Os dois blocos têm o mesmo total, com aberturas diferentes.

## Exemplos

Últimos 12 meses da conta `1` (Serviços de Apoio), em R$ bilhões:

```python
import duckdb

duckdb.sql("""
    SELECT year, month, round(value / 1e9, 1) AS valor_bi
    FROM read_parquet('lake/rtn/tabela-1-4-a/*.parquet')
    WHERE account = '1' AND value IS NOT NULL
    ORDER BY year DESC, month DESC LIMIT 12
""").show()
```

## Referências

- Conjunto de dados "Resultado do Tesouro Nacional - Série Histórica" (Tesouro Transparente): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Dicionário de Conceitos e Metodologia de Cálculo (planilha do mesmo conjunto): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Metadados da série (PDF do mesmo conjunto): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
