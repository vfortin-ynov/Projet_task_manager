"""Tests d'intégration pour le workflow complet des tâches."""
import os
import json
import pytest
from src.task_manager.manager import TaskManager
from src.task_manager.task import Status, Priority, Task

class TestTaskWorkflow:
    """Tests d'intégration pour le cycle de vie complet d'une tâche."""
    
    def test_complete_task_workflow(self, manager_with_temp_file):
        """Test le cycle de vie complet d'une tâche avec persistance."""
        manager = manager_with_temp_file
        
        # 1. Création d'une tâche
        task_id = manager.add_task("Tâche de test", "Description de test")
        assert task_id is not None
        
        # 2. Récupération de la tâche
        task = manager.get_task(task_id)
        assert task is not None
        assert task.title == "Tâche de test"
        assert task.status == Status.TODO
        
        # 3. Mise à jour de la tâche
        manager.update_task(task_id, status=Status.IN_PROGRESS)
        
        task_updated = manager.get_task(task_id)
        assert task_updated.status == Status.IN_PROGRESS
        
        # 4. Sauvegarde dans un fichier
        manager.save_to_file()
        assert os.path.exists(manager.save_file)
        
        # Vérifier que le fichier contient des données valides
        with open(manager.save_file, 'r') as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) > 0
            assert 'title' in data[0]
            # Vérifier que la tâche est bien dans le fichier
            task_in_file = next((t for t in data if t['id'] == task_id), None)
            assert task_in_file is not None
            assert task_in_file['status'] == Status.IN_PROGRESS.name
        
        # 5. Chargement à partir du fichier
        new_manager = TaskManager()
        new_manager.save_file = manager.save_file  # Utiliser le même fichier
        new_manager.storage_file = manager.save_file  # S'assurer que storage_file est également défini
        
        # Vérifier que le fichier existe avant de le charger
        assert os.path.exists(manager.save_file), f"Le fichier {manager.save_file} n'existe pas"
        
        # Charger les tâches depuis le fichier
        loaded = new_manager.load_from_file()
        assert loaded is True, "Le chargement du fichier a échoué"
        
        # 6. Vérification que la tâche est toujours là avec le bon état
        loaded_task = new_manager.get_task(task_id)
        assert loaded_task is not None, "La tâche n'a pas été chargée depuis le fichier"
        assert loaded_task.title == "Tâche de test", "Le titre de la tâche chargée est incorrect"
        assert loaded_task.status == Status.IN_PROGRESS, f"Le statut de la tâche chargée est incorrect: {loaded_task.status} au lieu de {Status.IN_PROGRESS}"
        
        # 7. Marquage comme terminé
        new_manager.update_task(task_id, status=Status.DONE)
        task = new_manager.get_task(task_id)
        assert task.status == Status.DONE, "La tâche n'a pas été marquée comme terminée"
        
        # 8. Vérification que le fichier a bien été mis à jour
        new_manager.save_to_file()
        
        # Vérifier que le fichier existe toujours
        assert os.path.exists(new_manager.save_file), f"Le fichier {new_manager.save_file} n'existe plus après la sauvegarde"
        
        # Lire le fichier directement pour vérifier son contenu
        with open(new_manager.save_file, 'r') as f:
            updated_data = json.load(f)
            assert len(updated_data) > 0, "Le fichier ne contient aucune tâche après la mise à jour"
            updated_task = next((t for t in updated_data if t['id'] == task_id), None)
            assert updated_task is not None, "La tâche mise à jour n'est pas dans le fichier"
            assert updated_task['status'] == Status.DONE.name, f"Le statut de la tâche dans le fichier n'est pas à jour: {updated_task['status']} au lieu de {Status.DONE.name}"
    
    def test_task_filtering_workflow(self, manager_with_temp_file):
        """Test le filtrage des tâches avec différents critères."""
        manager = manager_with_temp_file
        
        # Création de plusieurs tâches avec des attributs différents
        task1_id = manager.add_task("Tâche 1", "")
        manager.update_task(task1_id, status=Status.TODO, priority=Priority.LOW)
        
        task2_id = manager.add_task("Tâche 2", "")
        manager.update_task(task2_id, status=Status.IN_PROGRESS, priority=Priority.HIGH)
        
        task3_id = manager.add_task("Tâche 3", "")
        manager.update_task(task3_id, status=Status.DONE, priority=Priority.HIGH)
        
        # Test du filtrage par statut
        todo_tasks = manager.filter_tasks(status=Status.TODO)
        assert len(todo_tasks) == 1
        assert todo_tasks[0].id == task1_id
        
        # Test du filtrage par priorité
        high_priority = manager.filter_tasks(priority=Priority.HIGH)
        assert len(high_priority) == 2
        assert {t.id for t in high_priority} == {task2_id, task3_id}
        
        # Test du filtrage combiné
        high_priority_in_progress = manager.filter_tasks(
            priority=Priority.HIGH,
            status=Status.IN_PROGRESS
        )
        assert len(high_priority_in_progress) == 1
        assert high_priority_in_progress[0].id == task2_id
