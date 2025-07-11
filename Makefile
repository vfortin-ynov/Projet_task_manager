# TODO: Créez les cibles suivantes :
# - install : installer les dépendances
# - test : lancer les tests
# - test-unit : seulement les tests unitaires
# - test-integration : seulement les tests d'intégration
# - coverage : couverture avec rapport HTML
# - clean : nettoyer les fichiers temporaires
# - lint : vérification syntaxique
# - all : séquence complète

.PHONY: help install test test-cov lint format type-check clean

# Couleurs
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

## Affiche cette aide
help:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/(^[a-zA-Z\-\_0-9]+:.*?## .*$$)|(^##)/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM-30)s${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST) | sort -u

## Installe les dépendances du projet
install:
	@echo "${YELLOW}Installation des dépendances...${RESET}"
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

## Exécute tous les tests
TEST_PATH=./tests
test:
	@echo "${YELLOW}Exécution des tests...${RESET}"
	pytest $(TEST_PATH) -v

## Exécute les tests avec couverture de code
test-cov:
	@echo "${YELLOW}Exécution des tests avec couverture...${RESET}"
	pytest --cov=src --cov-report=term-missing --cov-report=html $(TEST_PATH)
	@echo "${GREEN}Rapport de couverture généré dans htmlcov/index.html${RESET}"

## Vérifie la qualité du code avec flake8
lint:
	@echo "${YELLOW}Vérification de la qualité du code...${RESET}"
	flake8 src/

## Formate le code avec black
format:
	@echo "${YELLOW}Formatage du code...${RESET}"
	black src/ tests/

## Vérifie les types avec mypy
type-check:
	@echo "${YELLOW}Vérification des types...${RESET}"
	mypy src/

## Nettoie les fichiers temporaires
clean:
	@echo "${YELLOW}Nettoyage...${RESET}"
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} +

## Installe les hooks git
install-hooks:
	@echo "${YELLOW}Installation des hooks git...${RESET}"
	pre-commit install

## Exécute toutes les vérifications (tests, lint, format, type-check)
check-all: test lint format type-check

## Démarre l'application
run:
	@echo "${YELLOW}Démarrage de l'application...${RESET}"
	python -m src.task_manager.manager
