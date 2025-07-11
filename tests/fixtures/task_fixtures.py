"""Fixtures pour les tests de tâches."""
import pytest
from src.task_manager.task import Task, Priority

@pytest.fixture
def minimal_task():
    """Retourne une tâche avec les paramètres minimaux."""
    return Task("Tâche minimale")

@pytest.fixture
def complete_task():
    """Retourne une tâche avec tous les paramètres."""
    return Task(
        title="Tâche complète",
        description="Description détaillée",
        priority=Priority.HIGH
    )

@pytest.fixture
def completed_task():
    """Retourne une tâche marquée comme terminée."""
    task = Task("Tâche terminée")
    task.mark_completed()
    return task

@pytest.fixture
def task_with_project():
    """Retourne une tâche assignée à un projet."""
    task = Task("Tâche avec projet", "Description", Priority.MEDIUM)
    task.assign_to_project("PROJ-123")
    return task
