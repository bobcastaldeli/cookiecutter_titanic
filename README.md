# teste

teste

## Objetivo

Descreva aqui o problema de negócio, público-alvo, unidade de análise, target, horizonte de predição e principais métricas de sucesso.

## Estrutura

```text
.
├── conf/
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── features/
├── docs/
├── models/
├── notebooks/
├── reports/
├── src/
│   └── src/
├── tests/
├── dvc.yaml
├── params.yaml
├── pyproject.toml
├── Makefile
└── .gitlab-ci.yml
```

## Setup local

```bash
make install
```

## Baixar dados versionados

```bash
dvc pull
```

## Rodar pipeline reprodutível

```bash
make repro
```

## Rodar testes

```bash
make test
```

## Rodar qualidade de código

```bash
make check
```

## MLflow

O projeto usa MLflow para rastrear experimentos.

```bash
export MLFLOW_TRACKING_URI=teste
make train
```

## GitLab CI

A cada Merge Request, o pipeline pode executar:

1. Lint
2. Testes
3. Pipeline DVC
4. Registro no MLflow
5. Comentário automático no MR com CML

## Governança mínima

1. Não versionar dados sensíveis diretamente no Git.
2. Não versionar `.env`, connection strings, tokens ou secrets.
3. Usar Azure Blob/DVC para datasets e artefatos grandes.
4. Usar GitLab protected variables para credenciais.
5. Todo modelo deve documentar:
   - definição de target;
   - janela temporal;
   - unidade de análise;
   - critério de split;
   - métricas offline;
   - limitações conhecidas;
   - responsável técnico;
   - link do experimento MLflow.
