"""Fixtures pour les tests du TaskManager."""
import pytest
from src.task_manager.task import Task, Priority, Status
from src.task_manager.manager import TaskManager
import os
import tempfile
import json

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

@pytest.fixture
def temp_task_file():
    """Crée un fichier temporaire pour les tests de TaskManager."""
    with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.json') as temp_file:
        temp_file.write('[]')  # Fichier JSON vide valide
        temp_path = temp_file.name
    
    yield temp_path
    
    # Nettoyage
    if os.path.exists(temp_path):
        try:
            os.unlink(temp_path)
        except (OSError, PermissionError):
            pass

@pytest.fixture
def manager_with_temp_file(temp_task_file):
    """Crée un TaskManager avec un fichier temporaire pour les tests."""
    from src.task_manager.manager import TaskManager
    
    # Créer un nouveau TaskManager avec le fichier temporaire
    manager = TaskManager(storage_file=temp_task_file)
    
    # S'assurer que le fichier de sauvegarde est bien défini
    manager.storage_file = temp_task_file
    manager.save_file = temp_task_file
    
    # S'assurer que le fichier existe et est vide
    with open(temp_task_file, 'w') as f:
        json.dump([], f)
    
    yield manager
    
    # Nettoyage supplémentaire si nécessaire
    if os.path.exists(temp_task_file):
        try:
            os.unlink(temp_task_file)
        except (OSError, PermissionError):
            pass
