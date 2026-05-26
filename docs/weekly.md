# Status do Projeto — Modelo de Risco Jurídico / Jurimetria

## 1. Objetivo do projeto

Estamos construindo uma solução de jurimetria para apoiar o time jurídico na priorização de processos, com foco inicial em prever o risco de perda do banco em ações judiciais encerradas e, futuramente, usar esse score para priorização de casos em aberto.

O objetivo de negócio é responder:

1. Quais processos têm maior probabilidade de perda?
2. Quais temas, produtos, ações, comarcas e carteiras concentram maior risco?
3. Quais processos devem ser priorizados para revisão humana, tese jurídica, negociação ou acordo?
4. Como transformar os dados do Benner e DeepLegal em uma base analítica confiável para modelos de Machine Learning?

---

## 2. Bases utilizadas

Até o momento foram utilizadas três fontes principais:

| Base | Descrição |
|---|---|
| Benner Processos | Base interna de gestão jurídica, com dados cadastrais, carteira, produto, assunto, ação, valor ajuizado, situação, motivo de encerramento e estimativa de perda. |
| DeepLegal Processos | Base externa/processual enriquecida, com dados do processo, classe, assunto, fase, comarca, órgão julgador, status e informações extraídas do processo. |
| DeepLegal Eventos | Base de eventos/movimentações processuais, ainda não utilizada no modelo principal early-stage, mas mapeada como fonte futura para features temporais e sequenciais. |

O foco atual está no cruzamento entre **Benner Processos + DeepLegal Processos**.

---

## 3. Principais decisões metodológicas

### 3.1 Target

Foi definido o target binário:

```text
0 = banco ganhou
1 = banco perdeu
```

A modelagem está focada em prever a classe **1**, ou seja, **risco de perda do banco**.

A regra de target foi construída a partir dos campos de situação e motivo de encerramento, com tratamento específico para casos como procedência, improcedência, extinção, prescrição e acordos.

Ponto importante: ainda é necessário validar formalmente com o jurídico se a regra de classificação de acordos, extinções e baixas administrativas está aderente à visão de negócio.

---

### 3.2 Restrição early-stage

Foi adotada uma premissa importante: o modelo deve simular uma predição no início do processo.

Por isso, foram bloqueadas variáveis que só existem depois do andamento ou encerramento do processo, como:

```text
Motivo_Encerramento
Situacao
Dataencerramento
Estimativa_De_Perde
Fasedoprocesso
Passiveldeacordo
Processorelevante
campos de sentença, condenação, acordo e resultado
predições externas da DeepLegal
```

Isso evita **data leakage** e aproxima o modelo de um cenário real de uso em produção.

---

## 4. EDA realizada

Foi feita uma EDA forense com foco em:

1. Qualidade dos dados.
2. Nulos e colunas pouco úteis.
3. Cruzamento Benner + DeepLegal.
4. Distribuição do valor ajuizado.
5. Relação entre valor ajuizado, assunto, produto, ação, carteira, UF e desfecho.
6. Identificação de temas com maior risco financeiro.
7. Identificação de variáveis candidatas para feature engineering.

Principais achados:

| Tema | Leitura |
|---|---|
| Valor ajuizado | Há forte assimetria, com poucos processos concentrando muito valor. |
| Risco por assunto | Alguns assuntos apresentam taxa de perda e exposição financeira significativamente maiores. |
| Risco por produto/ação | Combinações de produto, ação e assunto geram sinal relevante para priorização. |
| Drift temporal | A taxa de perda muda bastante ao longo do tempo, então o split aleatório foi descartado. |
| Top-k financeiro | O modelo deve ser avaliado não só por métrica estatística, mas também pela capacidade de capturar perdas financeiras no topo do ranking. |

---

## 5. Feature engineering concluído

Foram criadas features early-stage sem leakage, incluindo:

### 5.1 Features de valor

```text
Valorajuizado bruto
log do valor ajuizado
valor winsorizado
faixas de valor
flags de valor acima de determinados cortes
```

### 5.2 Features temporais

```text
ano inicial
mês inicial
trimestre inicial
semestre inicial
dia da semana
coortes temporais
```

### 5.3 Features categóricas normalizadas

```text
produto
assunto
ação
UF
comarca
carteira
empresa
tipo de processo
```

### 5.4 Interações

```text
produto x assunto
produto x ação
ação x assunto
produto x ação x assunto
UF x comarca
carteira x assunto
```

### 5.5 Features históricas sem leakage

Foram criadas features históricas usando apenas processos anteriores à data inicial do caso, evitando vazamento temporal.

Exemplos:

```text
taxa histórica de perda por assunto
taxa histórica de perda por produto
taxa histórica de perda por ação
taxa histórica de perda por UF/comarca
contagem histórica por grupo
flags de categoria rara
média histórica de valor por grupo
```

Após essa etapa, a base passou a ter aproximadamente **190 features** no cenário early-stage.

---

## 6. Validação e split

A validação foi feita com split temporal, não aleatório.

A divisão atual é:

| Conjunto | Quantidade | Taxa de perda |
|---|---:|---:|
| Dev / treino | 37.311 | ~38,0% |
| Holdout temporal | 9.317 | ~21,1% |

Esse comportamento mostra um **drift temporal relevante**, pois a taxa de perda no holdout é bem menor que no treino.

Por isso, as métricas do holdout são tratadas como a avaliação mais próxima de produção.

---

## 7. Modelos testados

### 7.1 07_03A — Baseline com Random Forest / Regressão Logística

Modelos com:

```text
OneHotEncoder
TF-IDF
Random Forest
Logistic Regression
HistGradientBoosting
```

Melhor resultado geral até agora:

```text
Random Forest + OneHot + TF-IDF
```

Resultado no holdout:

```text
PR-AUC perda: ~0,4668
ROC-AUC perda: ~0,7786
Top 5% precisão perda: ~60,3%
```

Esse segue sendo o melhor baseline até o momento.

---

### 7.2 07_03B — Encoders avançados + Feature-engine

Foram testados:

```text
CatBoostEncoder
JamesSteinEncoder
MEstimateEncoder
HistGradientBoosting
Logistic Regression
```

Resultado:

```text
PR-AUC perda no holdout: ~0,4348
ROC-AUC perda no holdout: ~0,7697
```

Apesar de tecnicamente válido, não superou o baseline 3A.

---

### 7.3 07_03C — LightGBM/XGBoost sem texto

Como havia restrição de compliance para instalar CatBoost, foi criada uma alternativa com:

```text
LightGBM
XGBoost
Category Encoders
OrdinalEncoder
CatBoostEncoder do category_encoders
```

Melhor modelo:

```text
XGBoost + OrdinalEncoder
```

Resultado no holdout:

```text
PR-AUC perda: ~0,4345
ROC-AUC perda: ~0,7649
Top 5% precisão perda: ~53,4%
```

Também não superou o baseline 3A.

---

### 7.4 07_03D — LightGBM/XGBoost com texto

Foi gerado o notebook 07_03D para testar XGBoost e LightGBM com features textuais via TF-IDF, de forma mais comparável ao baseline 3A.

Status atual:

```text
Notebook gerado, mas ainda não executado.
Resultados pendentes.
```

---

## 8. Resultado atual consolidado

Até o momento, o ranking é:

| Cenário | Melhor modelo | PR-AUC perda holdout | ROC-AUC perda holdout | Status |
|---|---|---:|---:|---|
| 07_03A | Random Forest + OneHot + TF-IDF | ~0,4668 | ~0,7786 | Melhor até agora |
| 07_03B | HGB + CatBoostEncoder | ~0,4348 | ~0,7697 | Inferior ao 3A |
| 07_03C | XGBoost + OrdinalEncoder | ~0,4345 | ~0,7649 | Inferior ao 3A |
| 07_03D | XGBoost/LightGBM + texto | Pendente | Pendente | Próximo teste |

---

## 9. Interpretação de negócio

Mesmo sendo um modelo inicial, o baseline já mostra sinal preditivo relevante.

A taxa base de perda no holdout é aproximadamente:

```text
21,1%
```

No top 5% dos processos mais arriscados, o modelo 3A alcançou aproximadamente:

```text
60,3% de precisão para perda
```

Ou seja, o modelo consegue concentrar processos com risco de perda quase **3 vezes maior que a taxa base**.

Isso indica potencial para uso como ferramenta de priorização, principalmente para:

1. Triagem de processos de maior risco.
2. Revisão de tese jurídica.
3. Priorização de documentação.
4. Análise de acordos.
5. Gestão de exposição financeira.

---

## 10. Riscos e pontos de atenção

| Ponto | Risco | Ação |
|---|---|---|
| Regra de target | Pode haver divergência jurídica sobre o que é ganho/perda | Validar com jurídico |
| Drift temporal | Taxa de perda muda no tempo | Manter validação temporal |
| Leakage | Algumas variáveis podem carregar informação pós-desfecho | Continuar auditoria de features |
| Texto | Pode trazer ganho, mas precisa ser bem controlado | Validar 07_03D |
| Calibração | Probabilidades brutas ainda podem não ser confiáveis | Aplicar Venn-Abers após escolher modelo campeão |
| Métrica | Accuracy não é suficiente | Usar PR-AUC, top-k e métricas financeiras |

---

## 11. Próximos passos

### 11.1 Próximo passo imediato

Executar o notebook:

```text
07_03D_lightgbm_xgboost_text_early_stage.ipynb
```

Objetivo:

```text
Testar LightGBM/XGBoost com texto via TF-IDF e comparar de forma justa contra o baseline 3A.
```

### 11.2 Depois disso

1. Escolher o modelo campeão provisório.
2. Fazer calibração de probabilidades com Venn-Abers.
3. Avaliar curva de calibração.
4. Definir threshold operacional ou top-k de priorização.
5. Gerar ranking final de processos por risco.
6. Criar uma visão executiva para o jurídico com risco, valor e explicabilidade.
7. Validar a regra de target com o time jurídico.

---

## 12. Mensagem curta para a weekly

Nesta semana avançamos na estruturação do primeiro modelo de jurimetria para prever risco de perda do banco em processos judiciais. Consolidamos a base integrada entre Benner e DeepLegal, definimos um target binário onde 0 representa banco ganhou e 1 representa banco perdeu, e tomamos cuidado para trabalhar em um cenário early-stage, evitando variáveis com vazamento de informação pós-desfecho.

Também criamos um conjunto de aproximadamente 190 features, incluindo valor ajuizado, variáveis temporais, categóricas, interações e históricos calculados sem leakage. Fizemos validação temporal, pois identificamos drift relevante entre treino e holdout.

Até agora, o melhor resultado veio do baseline com Random Forest, OneHot e TF-IDF, com PR-AUC de aproximadamente 0,47 no holdout e precisão de cerca de 60% no top 5% dos processos mais arriscados, contra uma taxa base de perda de 21%. Isso mostra que já existe sinal preditivo relevante para priorização jurídica.

Como não podemos usar CatBoost por restrições de compliance, criamos alternativas com LightGBM e XGBoost. Os primeiros testes sem texto não superaram o baseline, então agora estamos rodando uma versão com texto para fazer uma comparação mais justa. Após isso, o próximo passo será escolher o modelo campeão e aplicar calibração de probabilidades com Venn-Abers.

---

## 13. Status em formato Kanban

| Etapa | Status |
|---|---|
| Entendimento das bases Benner e DeepLegal | Concluído |
| EDA forense Benner | Concluído |
| EDA integrada Benner + DeepLegal | Concluído |
| EDA financeira por valor ajuizado | Concluído |
| Definição inicial do target | Concluído, pendente validação jurídica |
| Criação de features early-stage | Concluído |
| Features históricas sem leakage | Concluído |
| Baseline Random Forest / Logistic Regression | Concluído |
| Teste com encoders avançados | Concluído |
| Teste LightGBM/XGBoost sem texto | Concluído |
| Teste LightGBM/XGBoost com texto | Em andamento |
| Calibração Venn-Abers | Próxima etapa |
| Definição de threshold operacional | Próxima etapa |
| Ranking final de priorização jurídica | Próxima etapa |
| Validação com jurídico | Pendente |