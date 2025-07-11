# Task Manager

Un gestionnaire de tâches simple et efficace développé en Python.

## 📋 Fonctionnalités

- Création, lecture, mise à jour et suppression de tâches
- Gestion des priorités (faible, moyenne, haute)
- Filtrage des tâches par statut et priorité
- Sauvegarde et chargement des tâches

## 🚀 Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/vfortin-ynov/Projet_task_manager.git
   cd Projet_task_manager
   ```

2. Créez un environnement virtuel (recommandé) :
   ```bash
   python -m venv venv
   
   # Sur Windows :
   .\venv\Scripts\activate

   # Sur macOS/Linux :
   source venv/bin/activate
   ```

3. Installez les dépendances avec la commande :
   ```bash
   make install
   ```
   
   Cette commande va :
   - Installer les dépendances listées dans `requirements.txt`
   - Installer le package en mode développement avec `pip install -e .`

Alternative : Si vous préférez ne pas utiliser le Makefile, vous pouvez exécuter manuellement :
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## 🛠️ Utilisation

### Lancer la démonstration
```bash
make demo
```

### Commandes disponibles

- `make` ou `make help` : Affiche l'aide
- `make install` : Installe les dépendances
- `make test` : Exécute les tests unitaires et d'intégration
- `make test-unit` : Exécute uniquement les tests unitaires
- `make test-integration` : Exécute uniquement les tests d'intégration
- `make test-cov` : Génère un rapport de couverture de code
- `make lint` : Vérifie la qualité du code
- `make format` : Formate le code automatiquement
- `make type-check` : Vérifie les types avec mypy
- `make clean` : Nettoie les fichiers temporaires
- `make all` : Exécute l'ensemble des vérifications (test, lint, format, type-check)

## 🧪 Tests

Le projet inclut une suite complète de tests unitaires et d'intégration :

```bash
# Tous les tests
make test

# Tests unitaires uniquement
make test-unit

# Tests d'intégration uniquement
make test-integration

# Couverture de code
make test-cov
```

## 🛠️ Développement

### Structure du projet

```
task-manager/
├── src/                 # Code source du projet
├── tests/               # Tests unitaires et d'intégration
│   ├── unit/           # Tests unitaires
│   └── integration/    # Tests d'intégration
├── demo.py             # Script de démonstration
├── Makefile            # Commandes utiles
├── pyproject.toml      # Configuration du projet
└── requirements.txt    # Dépendances
```

### Bonnes pratiques

- Le code suit les conventions PEP 8
- Utilisation de type hints pour une meilleure maintenabilité
- Tests unitaires pour toutes les fonctionnalités clés
- Documentation complète des fonctions et classes

## 👥 Auteur

Valentin FORTIN - valentin.fortin@ynov.com