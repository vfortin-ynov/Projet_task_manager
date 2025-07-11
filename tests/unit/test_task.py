"""Tests unitaires pour la classe Task."""
from datetime import datetime
import pytest
from src.task_manager.task import Task, Priority, Status

# Import des fixtures
pytest_plugins = ['tests.fixtures.task_fixtures']

class TestTaskCreation:
    """Tests de création de tâches"""
    
    def test_create_task_sets_title_correctly(self):
        """Vérifie que le titre est correctement défini à la création."""
        task = Task("Tâche de test")
        assert task.title == "Tâche de test"

    def test_create_task_without_description_sets_empty_string(self):
        """Vérifie que la description est vide par défaut."""
        task = Task("Tâche")
        assert task.description == ""

    def test_create_task_with_description_sets_correct_value(self):
        """Vérifie que la description est correctement définie."""
        task = Task("Tâche", "Description détaillée")
        assert task.description == "Description détaillée"

    def test_create_task_sets_medium_priority_by_default(self):
        """Vérifie que la priorité par défaut est MEDIUM."""
        task = Task("Tâche")
        assert task.priority == Priority.MEDIUM

    def test_create_task_sets_todo_status_by_default(self):
        """Vérifie que le statut par défaut est TODO."""
        task = Task("Tâche")
        assert task.status == Status.TODO

    def test_create_task_sets_created_at_timestamp(self):
        """Vérifie que la date de création est définie."""
        before_creation = datetime.now()
        task = Task("Tâche")
        after_creation = datetime.now()
        created_at = datetime.fromisoformat(task.created_at)
        assert before_creation <= created_at <= after_creation

    def test_create_task_has_no_completed_at_by_default(self):
        """Vérifie que completed_at est None par défaut."""
        task = Task("Tâche")
        assert task.completed_at is None

    def test_create_task_has_no_project_by_default(self):
        """Vérifie que project_id est None par défaut."""
        task = Task("Tâche")
        assert task.project_id is None

    def test_create_task_with_empty_title_raises_value_error(self):
        """Vérifie qu'une erreur est levée si le titre est vide."""
        with pytest.raises(ValueError, match="Le titre ne peut pas être vide"):
            Task("")

    def test_create_task_with_none_title_raises_value_error(self):
        """Vérifie qu'une erreur est levée si le titre est None."""
        with pytest.raises(ValueError):
            Task(None)

    def test_create_task_with_invalid_priority_raises_type_error(self):
        """Vérifie qu'une erreur est levée si la priorité est invalide."""
        with pytest.raises(TypeError):
            Task("Tâche", priority="HAUTE")  # type: ignore


class TestTaskOperations:
    """Tests des opérations sur les tâches"""

    def setup_method(self):
        """Fixture : tâche de test"""
        self.task = Task("Tâche de test", description="Description")

    def test_mark_completed_changes_status_to_done(self):
        """Vérifie que marquer une tâche comme terminée change son statut."""
        self.task.mark_completed()
        assert self.task.status == Status.DONE

    def test_mark_completed_sets_completed_at_timestamp(self):
        """Vérifie que marquer une tâche comme terminée définit la date de fin."""
        before_completion = datetime.now()
        self.task.mark_completed()
        after_completion = datetime.now()
        completed_at = datetime.fromisoformat(self.task.completed_at)
        assert before_completion <= completed_at <= after_completion

    def test_update_priority_changes_priority(self):
        """Vérifie que la priorité peut être mise à jour."""
        self.task.update_priority(Priority.URGENT)
        assert self.task.priority == Priority.URGENT

    def test_update_priority_with_invalid_type_raises_type_error(self):
        """Vérifie qu'une erreur est levée pour une priorité invalide."""
        with pytest.raises(TypeError):
            self.task.update_priority("HAUTE")  # type: ignore

    def test_assign_to_project_sets_project_id(self):
        """Vérifie qu'on peut assigner une tâche à un projet."""
        self.task.assign_to_project("PROJ-123")
        assert self.task.project_id == "PROJ-123"

    def test_assign_to_project_with_none_removes_project(self):
        """Vérifie que project_id devient None quand on assigne None."""
        self.task.assign_to_project("PROJ-123")
        self.task.assign_to_project(None)
        assert self.task.project_id is None

    def test_assign_to_project_with_invalid_type_raises_type_error(self):
        """Vérifie qu'une erreur est levée pour un type de projet invalide."""
        with pytest.raises(TypeError):
            self.task.assign_to_project(123)  # type: ignore


class TestTaskSerialization:
    """Tests de sérialisation JSON"""
    
    def setup_method(self):
        """Crée une tâche complexe avec tous les attributs"""
        self.task = Task(
            "Tâche complexe",
            description="Description détaillée",
            priority=Priority.HIGH
        )
        self.task.assign_to_project("PROJ-123")
        self.task.mark_completed()

    def test_to_dict_includes_all_fields(self):
        """Vérifie que to_dict() inclut tous les champs."""
        task_dict = self.task.to_dict()
        expected_keys = {
            'id', 'title', 'description', 'priority',
            'status', 'created_at', 'completed_at', 'project_id'
        }
        assert set(task_dict.keys()) == expected_keys

    def test_to_dict_converts_priority_to_string(self):
        """Vérifie que la priorité est convertie en chaîne de caractères."""
        task_dict = self.task.to_dict()
        assert task_dict['priority'] == "HIGH"

    def test_to_dict_converts_status_to_string(self):
        """Vérifie que le statut est converti en chaîne de caractères."""
        task_dict = self.task.to_dict()
        assert task_dict['status'] == "DONE"

    def test_from_dict_recreates_task_with_same_attributes(self):
        """Vérifie qu'on peut recréer une tâche identique à partir d'un dictionnaire."""
        task_dict = self.task.to_dict()
        recreated = Task.from_dict(task_dict)
        assert recreated.title == self.task.title
        assert recreated.description == self.task.description
        assert recreated.priority == self.task.priority
        assert recreated.status == self.task.status
        assert recreated.created_at == self.task.created_at
        assert recreated.completed_at == self.task.completed_at
        assert recreated.project_id == self.task.project_id

    def test_from_dict_with_missing_required_field_raises_key_error(self):
        """Vérifie qu'une erreur est levée si un champ requis est manquant."""
        with pytest.raises(KeyError):
            Task.from_dict({"title": "Tâche incomplète"})  # manque les champs obligatoires