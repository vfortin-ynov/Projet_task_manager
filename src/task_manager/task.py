from datetime import datetime
from enum import Enum, auto


class Priority(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    URGENT = auto()


class Status(Enum):
    TODO = auto()
    IN_PROGRESS = auto()
    DONE = auto()
    CANCELLED = auto()


class Task:
    """Une tâche avec toutes ses propriétés"""

    _id_counter = 0  # Compteur de classe pour les IDs uniques

    def __init__(self, title, description="", priority=Priority.MEDIUM):
        # Validation des paramètres
        if not title or not isinstance(title, str):
            raise ValueError("Le titre ne peut pas être vide")
        if not isinstance(priority, Priority):
            raise TypeError(
                "La priorité doit être une valeur de l'énumération Priority"
            )

        # Initialisation des attributs
        Task._id_counter += 1
        self.id = Task._id_counter  # Utilisation du compteur pour un ID unique
        self.title = title
        self.description = description
        self.priority = priority
        self.status = Status.TODO
        self.created_at = datetime.now().isoformat()
        self.completed_at = None
        self.project_id = None

    def mark_completed(self):
        """Marque la tâche comme terminée"""
        self.status = Status.DONE
        self.completed_at = datetime.now().isoformat()

    def update_priority(self, new_priority):
        """Met à jour la priorité de la tâche"""
        if not isinstance(new_priority, Priority):
            raise TypeError(
                "La priorité doit être une valeur de l'énumération Priority"
            )
        self.priority = new_priority

    def assign_to_project(self, project_id):
        """Assigne la tâche à un projet"""
        if project_id is not None and not isinstance(project_id, str):
            raise TypeError(
                "L'ID du projet doit être une chaîne de caractères ou None"
            )
        self.project_id = project_id

    def to_dict(self):
        """Convertit la tâche en dictionnaire pour la sérialisation JSON"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.name,
            "status": self.status.name,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "project_id": self.project_id,
        }

    @classmethod
    def from_dict(cls, data):
        """Crée une tâche à partir d'un dictionnaire"""
        # Création d'une nouvelle instance avec les champs obligatoires
        task = cls(
            title=data["title"],
            description=data.get("description", ""),
            priority=Priority[data["priority"]],
        )

        # Mise à jour des autres champs
        task.id = data["id"]
        task.status = Status[data["status"]]
        task.created_at = data["created_at"]
        task.completed_at = data.get("completed_at")
        task.project_id = data.get("project_id")

        return task
