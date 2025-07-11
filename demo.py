#!/usr/bin/env python3
"""
Démonstration du module TaskManager
"""
import json
import os
from datetime import datetime, timedelta
from src.task_manager.manager import TaskManager
from src.task_manager.task import Priority, Status
from src.task_manager.services import EmailService, ReportService

def main():
    print("=== Démonstration TaskManager ===\n")

    # Créez un gestionnaire
    task_manager = TaskManager()

    # Ajoutez plusieurs tâches avec différentes priorités
    task1 = task_manager.add_task("Faire les courses", "Acheter du lait et des œufs", Priority.HIGH)
    task2 = task_manager.add_task("Répondre aux emails", "Vérifier la boîte de réception", Priority.MEDIUM)
    task3 = task_manager.add_task("Faire du sport", "30 minutes de course", Priority.LOW)
    task4 = task_manager.add_task("Préparer la réunion", "Préparer les slides pour demain", Priority.HIGH)
    
    # Affichez les tâches
    print("Tâches ajoutées :")
    for task in task_manager.tasks.values():
        print(f"- {task.title} (Priorité: {task.priority.name})")
    print()

    # Marquez certaines comme terminées
    task_manager.update_task(task1, status=Status.DONE)
    task_manager.update_task(task3, status=Status.DONE)
    print(f"Tâches marquées comme terminées : {task_manager.get_task(task1).title}, {task_manager.get_task(task3).title}\n")

    # Affichez les statistiques
    stats = task_manager.get_statistics()
    print("Statistiques :")
    print(f"Total des tâches : {stats['total']}")
    print(f"Tâches complétées : {stats['completed']} ({(stats['completed']/stats['total'])*100:.1f}%)")
    print(f"Tâches par priorité :")
    for priority, count in stats['by_priority'].items():
        print(f"  - {priority}: {count}")
    print()

    # Sauvegardez dans un fichier
    filename = "tasks_backup.json"
    task_manager.save_to_file(filename)
    print(f"Tâches sauvegardées dans {filename}")

    # Créez un nouveau gestionnaire et rechargez
    new_manager = TaskManager()
    new_manager.load_from_file(filename)
    print(f"\nTâches rechargées depuis {filename} :")
    for task in new_manager.tasks.values():
        print(f"- {task.title} (Statut: {task.status.name})")
    
    print("\nNote: Les tâches ont été sauvegardées dans", filename)
    print("Démo terminée avec succès !")

if __name__ == "__main__":
    main()
