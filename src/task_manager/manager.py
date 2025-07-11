import json
import os
from typing import List, Dict, Optional, Any
from .task import Task, Priority, Status


class TaskManager:
    """Gestionnaire principal des tâches"""

    def __init__(self, storage_file="tasks.json"):
        self.tasks: Dict[int, Task] = {}
        self.storage_file = storage_file
        # Charge automatiquement les tâches si le fichier existe
        if os.path.exists(self.storage_file):
            self.load_from_file()

    def add_task(self, title: str, description: str = "", priority: Priority = Priority.MEDIUM) -> int:
        """Crée et ajoute une nouvelle tâche"""
        task = Task(title, description, priority)
        self.tasks[task.id] = task
        return task.id

    def get_task(self, task_id: int) -> Optional[Task]:
        """Trouve une tâche par son ID"""
        return self.tasks.get(task_id)

    def get_tasks_by_status(self, status: Status) -> List[Task]:
        """Filtre les tâches par statut"""
        return [task for task in self.tasks.values() if task.status == status]

    def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
        """Filtre les tâches par priorité"""
        return [task for task in self.tasks.values() if task.priority == priority]

    def update_task(self, task_id: int, title: str = None, description: str = None, 
                  priority = None, status: Status = None) -> bool:
        """Met à jour une tâche existante"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError("Tâche non trouvée")
            
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if priority is not None:
            if isinstance(priority, str):
                priority = Priority[priority]  # Convert string to Priority enum
            task.priority = priority
        if status is not None:
            task.status = status
            
        return True

    def filter_tasks(self, status: Status = None, priority: Priority = None, 
                    project_id: str = None) -> List[Task]:
        """Filtre les tâches selon différents critères"""
        filtered = list(self.tasks.values())
        
        if status is not None:
            filtered = [t for t in filtered if t.status == status]
        if priority is not None:
            filtered = [t for t in filtered if t.priority == priority]
        if project_id is not None:
            filtered = [t for t in filtered if hasattr(t, 'project_id') and t.project_id == project_id]
            
        return filtered

    def delete_task(self, task_id: int) -> bool:
        """Supprime une tâche par son ID"""
        if task_id not in self.tasks:
            raise ValueError("Tâche non trouvée")
            
        del self.tasks[task_id]
        return True

    def save_to_file(self, filename: str = None) -> bool:
        """Sauvegarde toutes les tâches dans un fichier JSON"""
        file_path = filename or self.storage_file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                tasks_data = [task.to_dict() for task in self.tasks.values()]
                json.dump(tasks_data, f, ensure_ascii=False, indent=2)
            return True
        except (IOError, OSError) as e:
            raise OSError(f"Erreur lors de la sauvegarde: {e}")

    def load_from_file(self, filename: str = None) -> bool:
        """Charge les tâches depuis un fichier JSON"""
        file_path = filename or self.storage_file
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    tasks_data = json.load(f)
                    self.tasks = {task_data['id']: Task.from_dict(task_data) for task_data in tasks_data}
                except json.JSONDecodeError as e:
                    raise ValueError("Fichier de tâches corrompu") from e
                except (KeyError, TypeError) as e:
                    # Handle case where the JSON structure is invalid
                    raise ValueError("Fichier de tâches corrompu") from e
            return True
        except FileNotFoundError:
            return False
        except json.JSONDecodeError as e:
            raise ValueError("Fichier de tâches corrompu") from e
        except (IOError, OSError) as e:
            raise OSError(f"Erreur de lecture du fichier: {e}") from e

    def get_statistics(self) -> Dict[str, Any]:
        """Retourne des statistiques sur les tâches"""
        tasks_list = list(self.tasks.values())
        
        # Comptage des tâches par priorité
        tasks_by_priority = {priority.name: 0 for priority in Priority}
        # Comptage des tâches par statut
        tasks_by_status = {status.name: 0 for status in Status}
        
        completed_tasks = 0
        
        for task in tasks_list:
            tasks_by_priority[task.priority.name] += 1
            tasks_by_status[task.status.name] += 1
            if task.status == Status.DONE:
                completed_tasks += 1
        
        return {
            'total': len(tasks_list),
            'completed': completed_tasks,
            'by_priority': tasks_by_priority,
            'by_status': tasks_by_status
        }
        
    # Alias for backward compatibility with tests
    get_stats = get_statistics