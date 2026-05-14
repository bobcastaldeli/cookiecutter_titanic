.DEFAULT_GOAL := help

.PHONY: help install check test format dvc-pull dvc-push repro train clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make install     - instala ambiente local"
	@echo "  make check       - roda lint e formatação"
	@echo "  make test        - roda testes"
	@echo "  make format      - formata código"
	@echo "  make dvc-pull    - baixa dados versionados"
	@echo "  make dvc-push    - envia dados versionados"
	@echo "  make repro       - executa pipeline DVC"
	@echo "  make train       - executa pipeline Python"
	@echo "  make clean       - remove caches locais"

install:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"
	pre-commit install

check:
	ruff check .
	ruff format --check .

format:
	ruff check . --fix
	ruff format .

test:
	pytest --cov=src --cov-report=term-missing

dvc-pull:
	dvc pull

dvc-push:
	dvc push

repro:
	dvc repro

train:
	python -m src.pipelines.train_pipeline

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage
