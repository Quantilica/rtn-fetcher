# Resultado do Tesouro Nacional — RTN (`rtn`)

O `rtn-fetcher` coleta a série histórica do Resultado do Tesouro Nacional (RTN), que a Secretaria do Tesouro Nacional (STN) publica todo mês e que mede o resultado fiscal do Governo Central (Tesouro Nacional, Previdência Social e Banco Central) pela metodologia "acima da linha": receitas, transferências, despesas e resultado primário. A planilha da série histórica tem uma aba por tabela; o conversor transforma 24 delas em datasets do lake, um por aba, em formato longo (uma linha por conta e período).

| Dataset | O que é | Origem | Período | Unidade | Página |
|---|---|---|---|---|---|
| `tabela-1-1` | Resultado Primário do Governo Central - Mensal - Resumida - Valores Correntes | aba `1.1` | 1997-01 a 2026-07 | R$ correntes | [tabela-1-1](datasets/tabela-1-1.md) |
| `tabela-1-1-a` | Resultado Primário do Governo Central - Mensal - Resumida - Valores Constantes (IPCA) | aba `1.1-A` | 1997-01 a 2026-07 | R$ constantes (IPCA) | [tabela-1-1-a](datasets/tabela-1-1-a.md) |
| `tabela-1-2` | Resultado Primário do Governo Central - Mensal - Valores Correntes | aba `1.2` | 1997-01 a 2026-07 | R$ correntes | [tabela-1-2](datasets/tabela-1-2.md) |
| `tabela-1-2-a` | Resultado Primário do Governo Central - Mensal - Valores Constantes (IPCA) | aba `1.2-A` | 1997-01 a 2026-07 | R$ constantes (IPCA) | [tabela-1-2-a](datasets/tabela-1-2-a.md) |
| `tabela-1-2-b` | Resultado Primário do Governo Central - Mensal - Valores Constantes (IPCA) - Acumulado em 12 meses | aba `1.2-B` | 1997-12 a 2026-07 | R$ constantes, acumulado em 12 meses | [tabela-1-2-b](datasets/tabela-1-2-b.md) |
| `tabela-1-3` | Investimento do Governo Central - Mensal - Valores Correntes | aba `1.3` | 2008-01 a 2026-07 | R$ correntes | [tabela-1-3](datasets/tabela-1-3.md) |
| `tabela-1-3-a` | Investimento do Governo Central - Mensal - Valores Constantes (IPCA) | aba `1.3-A` | 2008-01 a 2026-07 | R$ constantes (IPCA) | [tabela-1-3-a](datasets/tabela-1-3-a.md) |
| `tabela-1-4` | Custeio Administrativo do Governo Central - Mensal - Valores Correntes | aba `1.4` | 2011-01 a 2026-07 | R$ correntes | [tabela-1-4](datasets/tabela-1-4.md) |
| `tabela-1-4-a` | Custeio Administrativo do Governo Central - Mensal - Valores Constantes (IPCA) | aba `1.4-A` | 2011-01 a 2026-07 | R$ constantes (IPCA) | [tabela-1-4-a](datasets/tabela-1-4-a.md) |
| `tabela-1-5` | Transferências e despesas primárias do Governo Central apuradas pelo critério de "valor pago" - Mensal - Valores Correntes | aba `1.5` | 2008-01 a 2026-07 | R$ correntes | [tabela-1-5](datasets/tabela-1-5.md) |
| `tabela-1-5-a` | Transferências e despesas primárias do Governo Central apuradas pelo critério de "valor pago" - Mensal - Valores Constantes (IPCA) | aba `1.5-A` | 2008-01 a 2026-07 | R$ constantes (IPCA) | [tabela-1-5-a](datasets/tabela-1-5-a.md) |
| `tabela-1-6` | Receita Líquida Ajustada - Lei Complementar 200/2023 - Mensal | aba `1.6` | 2021-07 a 2026-07 | R$ correntes | [tabela-1-6](datasets/tabela-1-6.md) |
| `tabela-2-1` | Resultado Primário do Governo Central - Anual - Resumida - Valores Correntes | aba `2.1` | 1997 a 2025 | R$ correntes | [tabela-2-1](datasets/tabela-2-1.md) |
| `tabela-2-1-a` | Resultado Primário do Governo Central - Anual - Resumida - % do PIB | aba `2.1-A` | 1997 a 2025 | fração do PIB | [tabela-2-1-a](datasets/tabela-2-1-a.md) |
| `tabela-2-2` | Resultado Primário do Governo Central - Anual - Valores Correntes | aba `2.2` | 1997 a 2025 | R$ correntes | [tabela-2-2](datasets/tabela-2-2.md) |
| `tabela-2-2-a` | Resultado Primário do Governo Central - Anual - % do PIB | aba `2.2-A` | 1997 a 2025 | fração do PIB | [tabela-2-2-a](datasets/tabela-2-2-a.md) |
| `tabela-2-3` | Investimento do Governo Central - Anual - Valores Correntes | aba `2.3` | 2008 a 2025 | R$ correntes | [tabela-2-3](datasets/tabela-2-3.md) |
| `tabela-2-3-a` | Investimento do Governo Central - Anual - % do PIB | aba `2.3-A` | 2008 a 2025 | fração do PIB | [tabela-2-3-a](datasets/tabela-2-3-a.md) |
| `tabela-2-4` | Custeio Administrativo do Governo Central - Anual - Valores Correntes | aba `2.4` | 2011 a 2025 | R$ correntes | [tabela-2-4](datasets/tabela-2-4.md) |
| `tabela-2-4-a` | Custeio Administrativo do Governo Central - Anual - % do PIB | aba `2.4-A` | 2011 a 2025 | fração do PIB | [tabela-2-4-a](datasets/tabela-2-4-a.md) |
| `tabela-2-5` | Transferências e despesas primárias do Governo Central apuradas pelo critério de "valor pago" - Anual - Valores Correntes | aba `2.5` | 2008 a 2025 | R$ correntes | [tabela-2-5](datasets/tabela-2-5.md) |
| `tabela-2-5-a` | Transferências e despesas primárias do Governo Central apuradas pelo critério de "valor pago" - Anual - % do PIB | aba `2.5-A` | 2008 a 2025 | fração do PIB | [tabela-2-5-a](datasets/tabela-2-5-a.md) |
| `tabela-4-1` | Demonstrativo de Operações do Governo Central Orçamentário - Metodologia Manual de Estatísticas de Finanças Públicas 2014 - Trimestral - Valores Correntes | aba `4.1` | 2006-T1 a 2026-T1 | R$ correntes | [tabela-4-1](datasets/tabela-4-1.md) |
| `tabela-4-2` | Conciliação do Resultado Primário do RTN e o Resultado de Operações do Governo Central Orçamentário (GCO) - Trimestral - Valores Correntes | aba `4.2` | 2020-T1 a 2026-T1 | R$ correntes | [tabela-4-2](datasets/tabela-4-2.md) |

## Como a STN publica

- A série histórica sai em uma planilha XLSX única no conjunto de dados "Resultado do Tesouro Nacional - Série Histórica" do portal Tesouro Transparente, com a série inteira a cada edição mensal. O nome do arquivo muda por edição (`seriehistoricajul26.xlsx` na de jul/2026); o fetcher guarda cada versão com o `Last-Modified` no nome (`rtn@AAAAMMDDTHHMMSS.xlsx`) e o lake converte só a mais recente.
- O conjunto de dados traz ainda o "Dicionário de Conceitos e Metodologia de Cálculo" (planilha), um PDF de metadados e a indicação de uma API de séries temporais. O dicionário descreve as contas num layout de tabelas anterior ao atual (numeração e blocos diferentes), então as descrições não casam linha a linha com as abas de hoje.
- A licença do conjunto de dados, informada no portal, é a ODbL (conferido em 2026-11-15). A fonte informa início em janeiro de 1997 e atualização mensal.
- Os dados são revisados a cada edição: a STN avisa "Dados sujeitos à alteração", e os valores podem retroceder até o início do exercício. O lake guarda só a edição mais recente.
- O fetcher também sabe baixar os anexos e as publicações em PDF do RTN (grupos `rtn-anexos` e `rtn-publicacoes`), mas só a planilha da série histórica vira dataset.

## Como as abas se relacionam

- **Mensais (`1.x`) e anuais (`2.x`).** As tabelas `2.1` a `2.5` repetem as `1.1` a `1.5` com período anual, em ano fechado (o último ano é 2025, quando a série mensal vai a 2026-07). A `1.6` e as `4.x` não têm par anual.
- **Variantes `-A` e `-B`.** Nas tabelas mensais, `-A` repete a tabela em reais constantes deflacionados pelo IPCA, com a data-base do mês da edição, e a `1.2-B` traz o resultado detalhado em reais constantes acumulado em 12 meses. Nas tabelas anuais, `-A` repete a tabela em fração do PIB.
- **Mesma árvore de contas.** Uma tabela e sua variante `-A` têm as mesmas contas; as famílias são: resultado primário resumido (`1.1`, `2.1`), resultado primário detalhado (`1.2`, `2.2`), investimento (`1.3`, `2.3`), custeio administrativo (`1.4`, `2.4`) e transferências e despesas por valor pago (`1.5`, `2.5`).
- **Trimestrais (`4.x`).** A `4.1` é o Demonstrativo de Operações do Governo Central Orçamentário no padrão do manual do FMI (GFSM 2014), e a `4.2` concilia o resultado primário do RTN com o do Governo Central Orçamentário.
- **Não convertidas.** As abas `3.1` e `3.2` (valores e variações selecionadas) existem na planilha, mas o conversor não as lê; não há dataset para elas.

## Contas e códigos

O lake guarda o código da conta em `account`, não o nome. Cada página de dataset traz a tabela de contas da edição de jul/2026. Os códigos têm ponto como separador de níveis e **mudam de significado de uma tabela para outra**. Códigos que começam por `auto.` foram gerados pelo conversor para linhas sem numeração na planilha e dependem da ordem das linhas. Um sufixo `#2` marca a segunda ocorrência de um código repetido na mesma aba.

## Dados pessoais

Nenhum dos datasets tem dados pessoais: são agregados fiscais do Governo Central.

## Quebras que valem para mais de um dataset

| Desde | Mudança | Afeta |
|---|---|---|
| 2022 | As contas `2.1.1` a `2.1.3` (benefícios previdenciários por clientela) ficam sem valores e, nas tabelas mensais, as contas `2.3.1.1` e `2.3.1.2` (abono e seguro-desemprego, benefícios e sentenças) passam a ter valores (observado na edição de jul/2026) | `tabela-1-5`, `tabela-1-5-a`, `tabela-2-5`, `tabela-2-5-a` |
| 2020-01 | A conta `auto.10.4` (PAC, em memorando) fica sem valores | `tabela-1-2`, `tabela-1-2-a`, `tabela-1-2-b` |
