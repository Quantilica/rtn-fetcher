---
dataset:
  id: tabela-2-3
  fonte: rtn
  titulo: "Investimento do Governo Central - Anual - Valores Correntes"
  resumo: "Investimento do Governo Central, em série anual, em valores correntes. Uma linha por conta e período, em formato longo."
  orgao: Secretaria do Tesouro Nacional (STN), Ministério da Fazenda
  pagina_oficial: https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
  licenca: "Open Data Commons Open Database License (ODbL), conforme o conjunto de dados no portal Tesouro Transparente (conferido em 2026-11-15)."
  periodicidade: "anual (anos fechados), atualizada a cada edição mensal do RTN; a série histórica sai inteira em cada planilha"
  cobertura: {inicio: 2008, fim: em-curso}
  unidade: "o valor de uma conta da tabela em um ano"
  granularidade: {espacial: "Brasil (Governo Central)", temporal: ano}
  formato_bruto: "aba 2.3 da planilha XLSX da série histórica do RTN (uma aba por tabela); valores em R$ milhões, períodos nas colunas a partir da linha 5; o código da conta vem embutido no rótulo da primeira coluna"
  lake: {estado: convertido, particoes: [], chave: [year, account], colunas: 3}
  unidades_de_medida:
    value: "R$ (reais correntes)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.7.0
---

# Investimento do Governo Central - Anual - Valores Correntes

## Resumo

Aba `2.3` ("Tabela 2.3") da série histórica do Resultado do Tesouro Nacional (RTN). Traz o investimento total por grupo de despesa (GND 4, investimentos, e GND 5, inversões financeiras) e por função orçamentária, e, em um bloco de memorando, o investimento por natureza da despesa. A tabela cobre o Governo Central (Tesouro Nacional, Previdência Social e Banco Central), com a metodologia "acima da linha" da STN. Cada linha do lake é um valor de uma conta em um ano.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `rtn/tabela-2-3` |
| Órgão | Secretaria do Tesouro Nacional (STN), Ministério da Fazenda |
| Página oficial | https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional |
| Licença | Open Data Commons Open Database License (ODbL), conforme o conjunto de dados no portal Tesouro Transparente (conferido em 2026-11-15). |
| Periodicidade | anual (anos fechados), atualizada a cada edição mensal do RTN; a série histórica sai inteira em cada planilha |
| Cobertura | 2008 a em-curso |
| Unidade (uma linha) | o valor de uma conta da tabela em um ano |
| Granularidade | espacial: Brasil (Governo Central); temporal: ano |
| Formato bruto | aba 2.3 da planilha XLSX da série histórica do RTN (uma aba por tabela); valores em R$ milhões, períodos nas colunas a partir da linha 5; o código da conta vem embutido no rótulo da primeira coluna |
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
- Cada edição traz a série histórica inteira, uma aba por tabela. O conversor lê só a edição mais recente e converte a aba `2.3` em um Parquet de nome fixo (`2-3.parquet`).
- Layout da aba: o título na linha 2, a unidade na linha 3 ("R$ Milhões - Valores Correntes"), o cabeçalho com os períodos na linha 5 (primeira coluna: "Investimento por Grupo de Despesa (GND) e Função") e as contas nas linhas seguintes; o código da conta vem embutido no rótulo da primeira coluna. As notas de rodapé ("Obs.", "1/", "2/"...) ficam abaixo da tabela e não entram no lake.
- Conferido em 2026-11-15: edição `seriehistoricajul26.xlsx`, publicada em 27/08/2026 (`Last-Modified` do arquivo), com a aba `2.3` de 2008 a 2025.
- Para o conjunto de dados, a fonte informa frequência de atualização mensal e início em janeiro de 1997 (metadados no portal, conferidos em 2026-11-15); cada aba começa no seu próprio período.

## Conteúdo

- 1.404 linhas: 78 contas × 18 períodos (de 2008 a 2025); cada combinação de `year`, `account` aparece uma vez.
- Unidade de `value`: reais correntes (a fonte publica em R$ milhões e o conversor multiplica por 1.000.000).
- Nenhuma linha tem `value` nulo.
- Os 18 períodos são consecutivos, sem lacunas entre o primeiro e o último.
- Só entram anos fechados: o último ano é 2025, enquanto a série mensal vai até 2026-07.

### Contas

O lake guarda só o código da conta em `account`; o nome não vai para o Parquet. A tabela abaixo é a de contas desta tabela na edição de jul/2026 (código, nível hierárquico e nome como a planilha publica, sem a numeração e as chamadas de nota).

Os códigos usam ponto como separador de níveis (`1.1.01` é filha de `1.1`). Códigos que começam por `auto.` foram gerados pelo conversor para linhas que a planilha não numera (posicionais, com base na indentação); um sufixo `#2` marca a segunda ocorrência de um código repetido na mesma aba.

| Código (`account`) | Nível | Conta |
|---|---|---|
| `1` | 1 | INVESTIMENTO TOTAL (1 + 2 + 3) |
| `1.1` | 2 | &nbsp;&nbsp;Investimentos (GND 4) |
| `1.1.01` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Legislativa |
| `1.1.02` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Judiciária |
| `1.1.03` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Essencial à Justiça |
| `1.1.04` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Administração |
| `1.1.05` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Defesa Nacional |
| `1.1.06` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Segurança Pública |
| `1.1.07` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Relações Exteriores |
| `1.1.08` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Assistência Social |
| `1.1.09` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Previdência Social |
| `1.1.10` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Saúde |
| `1.1.11` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Trabalho |
| `1.1.12` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Educação |
| `1.1.13` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Cultura |
| `1.1.14` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Direitos da Cidadania |
| `1.1.15` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Urbanismo |
| `1.1.16` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Habitação |
| `1.1.17` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Saneamento |
| `1.1.18` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Gestão Ambiental |
| `1.1.19` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Ciência e Tecnologia |
| `1.1.20` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Agricultura |
| `1.1.21` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Organização Agrária |
| `1.1.22` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Indústria |
| `1.1.23` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Comércio e Serviços |
| `1.1.24` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Comunicações |
| `1.1.25` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Energia |
| `1.1.26` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Transporte |
| `1.1.27` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Desporto e Lazer |
| `1.1.28` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Encargos Especiais |
| `1.2` | 2 | &nbsp;&nbsp;Inversões Financeiras (GND 5) |
| `1.2.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Legislativa |
| `1.2.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Judiciária |
| `1.2.3` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Essencial à Justiça |
| `1.2.4` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Administração |
| `1.2.5` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Defesa Nacional |
| `1.2.6` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Segurança Pública |
| `1.2.7` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Relações Exteriores |
| `1.2.8` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Assistência Social |
| `1.2.9` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Previdência Social |
| `1.2.10` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Saúde |
| `1.2.11` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Trabalho |
| `1.2.12` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Educação |
| `1.2.13` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Cultura |
| `1.2.14` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Direitos da Cidadania |
| `1.2.15` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Urbanismo |
| `1.2.16` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Habitação |
| `1.2.17` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Saneamento |
| `1.2.18` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Gestão Ambiental |
| `1.2.19` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Ciência e Tecnologia |
| `1.2.20` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Agricultura |
| `1.2.21` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Organização Agrária |
| `1.2.22` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Indústria |
| `1.2.23` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Comércio e Serviços |
| `1.2.24` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Comunicações |
| `1.2.25` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Energia |
| `1.2.26` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Transporte |
| `1.2.27` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Desporto e Lazer |
| `1.2.28` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Encargos Especiais |
| `1.3` | 2 | &nbsp;&nbsp;Ajuste de Ordem Bancária |
| `2` | 1 | INVESTIMENTO TOTAL (1 + 2 + 3) |
| `2.1` | 2 | &nbsp;&nbsp;Investimentos (GND 4) |
| `2.1.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Aplicações Diretas da União |
| `2.1.1.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Obras e instalações |
| `2.1.1.2` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Equipamentos e material permanente |
| `2.1.1.3` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Serviços |
| `2.1.1.4` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demais aplicações diretas da União |
| `2.1.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Transferências a Estados/DF |
| `2.1.3` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Transferências a Municípios |
| `2.1.4` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Outras transferências |
| `2.2` | 2 | &nbsp;&nbsp;Inversões Financeiras (GND 5) 2/ por Ação |
| `2.2.1` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Despesas com aumento de capital de empresas estatais não dependentes (Participação da União no Capital) |
| `2.2.2` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Integralização de Cotas |
| `2.2.2.1` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Fundos garantidores |
| `2.2.2.2` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Organismos internacionais |
| `2.2.2.3` | 4 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Outras |
| `2.2.3` | 3 | &nbsp;&nbsp;&nbsp;&nbsp;Demais |
| `2.3` | 2 | &nbsp;&nbsp;Ajuste de Ordem Bancária |

## Variáveis

A planilha não traz dicionário de colunas: os dados chegam em formato largo (um período por coluna) e o conversor os passa para o formato longo abaixo. O dicionário de conceitos da STN descreve as contas (não as colunas) em um layout de tabelas anterior ao atual, por isso as descrições de contas não são repetidas aqui linha a linha: as contas ficam na tabela da seção Conteúdo, com o nome como a planilha publica, e a coluna "Descrição" abaixo diz o que cada coluna do lake guarda.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `year` | cabeçalho da coluna de período (ano) | inteiro | Ano a que o valor se refere | ano de quatro dígitos | todo |
| `account` | rótulo da linha (primeira coluna, com o código embutido) | texto | Código hierárquico da conta, com ponto como separador; ver a tabela de contas na seção Conteúdo | os códigos da tabela de contas | todo |
| `value` | célula da conta no período | decimal | Valor da conta no período; célula vazia, `-`, `n.a.`, `n.d.` e "não disp." na planilha viram nulo | R$ (reais correntes) | todo |

## No lake

- Dataset `rtn/tabela-2-3`, sem partições: um único arquivo `2-3.parquet` com as colunas `year`, `account`, `value`.
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
- **Dois blocos com a mesma raiz.** Os códigos `1…` (investimento por função) e `2…` (memorando, por natureza da despesa) trazem o mesmo "Investimento total", com aberturas diferentes; o total não se soma entre os blocos.

## Exemplos

Últimos 10 anos da conta `1` (INVESTIMENTO TOTAL (1 + 2 + 3)):

```python
import duckdb

duckdb.sql("""
    SELECT year, round(value / 1e9, 1) AS valor_bi
    FROM read_parquet('lake/rtn/tabela-2-3/*.parquet')
    WHERE account = '1' AND value IS NOT NULL
    ORDER BY year DESC LIMIT 10
""").show()
```

## Referências

- Conjunto de dados "Resultado do Tesouro Nacional - Série Histórica" (Tesouro Transparente): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Dicionário de Conceitos e Metodologia de Cálculo (planilha do mesmo conjunto): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
- Metadados da série (PDF do mesmo conjunto): https://www.tesourotransparente.gov.br/ckan/dataset/resultado-do-tesouro-nacional
