"""Fixtures pour les tests du TaskManager."""
import pytest
from src.task_manager.task import Task, Priority, Status
from src.task_manager.manager import TaskManager

@pytest.fixture
def empty_manager():
    """Retourne un TaskManager vide."""
    return TaskManager(":memory:")

@pytest.fixture
def manager_with_tasks():
    """Retourne un TaskManager avec des tâches de test."""
    manager = TaskManager(":memory:")
    
    # Ajout de tâches de test
    tasks = [
        ("Tâche 1", "Description 1", Priority.HIGH, Status.TODO, "PROJ-1"),
        ("Tâche 2", "Description 2", Priority.MEDIUM, Status.IN_PROGRESS, None),
        ("Tâche 3", "Description 3", Priority.LOW, Status.DONE, "PROJ-1"),
        ("Tâche 4", "Description 4", Priority.HIGH, Status.TODO, "PROJ-2"),
    ]
    
    for title, desc, priority, status, project_id in tasks:
        task_id = manager.add_task(title, desc, priority)
        task = manager.get_task(task_id)
        task.status = status
        if project_id:
            task.assign_to_project(project_id)
    
    return manager

@pytest.fixture
def sample_task_data():
    """Retourne des données de tâche pour les tests de sérialisation."""
    task = Task("Tâche test", "Description test", Priority.HIGH)
    task.assign_to_project("TEST-123")
    task.mark_completed()
    return task.to_dict()
