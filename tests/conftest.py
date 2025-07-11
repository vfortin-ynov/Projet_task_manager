"""Configuration file for pytest."""

# Use pytest_plugins to import fixtures instead of direct imports
pytest_plugins = [
    "tests.fixtures.manager_fixtures",
    "tests.fixtures.task_fixtures",
]
