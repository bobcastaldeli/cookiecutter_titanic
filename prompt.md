Atualize o notebook `notebook_comparacao_feature_engineering_pricing.ipynb` para incluir novos baselines e técnicas de encoding/representação voltadas ao modelo de pricing de simulações que viram propostas.

Contexto:
- O problema é prever `P(virar_proposta)` usando condições atuais da simulação, perfil do cliente e histórico da jornada.
- Já existem comparações com WOE, OptBinning, DecisionTreeEncoder, TreeBinning+WOE, Splines, Polynomial Features, LightGBM, XGBoost e CatBoost.
- O split deve continuar temporal, evitando leakage.
- Encoders supervisionados devem ser ajustados apenas no treino e aplicados em validação/teste/OOT.

Adicionar novos modelos:
1. `HistGradientBoostingClassifier` baseline.
2. `HistGradientBoostingClassifier` com `monotonic_cst`.
3. `RandomTreesEmbedding + LogisticRegression`.
4. `OptBinning/WOE + RandomTreesEmbedding + LogisticRegression`, como experimento híbrido.
5. `LinearTreeClassifier`.
6. `LinearForestClassifier`.
7. `LinearBoostClassifier`.

Adicionar/avaliar encodings úteis para árvores e boosting:
1. Target Encoding out-of-fold para categóricas de alta cardinalidade.
2. CatBoost Encoding / Ordered Target Encoding.
3. Leave-One-Out Encoding com regularização.
4. Count/Frequency Encoding para categorias com cardinalidade média/alta.
5. Rare Label Encoding para agrupar categorias raras.
6. WOE Encoding apenas como benchmark interpretável ou quando melhorar estabilidade.
7. One-Hot Encoding para categorias de baixa cardinalidade.
8. Native categorical handling do CatBoost, quando aplicável.

Comparar todos os modelos usando:
- ROC AUC;
- PR AUC;
- KS;
- Brier Score;
- lift por decil;
- ordenação por grupo de score;
- calibração por grupo;
- estabilidade temporal/OOT.

Pontos de atenção:
- Não usar quantidade bruta de simulações como principal sinal comportamental.
- Priorizar features de trajetória econômica: mudanças em entrada, LTV, valor financiado, parcela, prazo, taxa, veículo e retorno lojista.
- Para modelos monotônicos, aplicar constraints apenas em variáveis com direção econômica clara, como `taxa_cliente`, `valor_parcela`, `score_cliente` e `tempo_desde_ultima_simulacao`.
- Comparar performance, estabilidade e interpretabilidade antes de escolher o modelo vencedor.