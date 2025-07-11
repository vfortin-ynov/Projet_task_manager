# Makefile pour la gestion des tâches

.PHONY: help install test test-unit test-integration test-cov lint format type-check clean demo all

## Affiche cette aide
help:
	@echo ''
	@echo 'Usage:'
	@echo '  make <target>'
	@echo ''
	@echo 'Targets:'
	@echo '  all            Exécute la séquence complète (test, lint, format, type-check)'
	@echo '  install        Installer les dépendances du projet'
	@echo '  test           Exécuter tous les tests'
	@echo '  test-unit      Exécuter uniquement les tests unitaires'
	@echo '  test-integration Exécuter uniquement les tests d\'intégration'
	@echo '  test-cov       Exécuter les tests avec couverture de code'
	@echo '  lint           Vérification de la qualité du code avec flake8'
	@echo '  format         Formater le code avec black et isort'
	@echo '  type-check     Vérification des types avec mypy'
	@echo '  clean          Nettoyer les fichiers temporaires'
	@echo '  demo           Lancer la démonstration'

## Exécute la séquence complète
all: clean install test lint format type-check

## Installe les dépendances du projet
install:
	@echo "Installation des dépendances..."
	pip install -r requirements.txt
	pip install -e .

## Exécute tous les tests
TEST_PATH=./tests
test: test-unit test-integration

## Exécute uniquement les tests unitaires
test-unit:
	@echo "Exécution des tests unitaires..."
	python -m pytest $(TEST_PATH)/unit -v

## Exécute uniquement les tests d'intégration
test-integration:
	@echo "Exécution des tests d'intégration..."
	python -m pytest $(TEST_PATH)/integration -v

## Exécute les tests avec couverture de code
test-cov:
	@echo "Exécution des tests avec couverture..."
	python -m pytest --cov=src --cov-report=term-missing --cov-report=html $(TEST_PATH)

## Vérification de la qualité du code
lint:
	@echo "Vérification de la qualité du code..."
	python -m flake8 src tests

## Formatage du code
format:
	@echo "Formatage du code..."
	black src tests
	isort src tests

## Vérification des types
type-check:
	@echo "Vérification des types..."
	mypy src

## Nettoie les fichiers temporaires
clean:
	@echo "Nettoyage..."
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist htmlcov rmdir /s /q htmlcov
	if exist .mypy_cache rmdir /s /q .mypy_cache
	if exist tasks_backup.json del tasks_backup.json
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	for /d /r . %%d in (.ruff_cache) do @if exist "%%d" rmdir /s /q "%%d"

## Lance la démonstration
demo:
	@echo "Lancement de la démonstration..."
	python -m demo
