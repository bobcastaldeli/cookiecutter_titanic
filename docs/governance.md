# Governança do Projeto

## Checklist de modelagem

- [ ] Problema de negócio documentado
- [ ] Unidade de análise definida
- [ ] Target definido
- [ ] Horizonte de predição definido
- [ ] Critério de split documentado
- [ ] Riscos de leakage avaliados
- [ ] Métricas offline definidas
- [ ] Limitações conhecidas documentadas
- [ ] Experimento registrado no MLflow
- [ ] Dados versionados com DVC
- [ ] Merge Request com relatório CML

## Dados sensíveis

Não versionar dados sensíveis diretamente no Git. Use DVC com remote seguro no Azure Blob Storage e credenciais via variáveis protegidas do GitLab.
