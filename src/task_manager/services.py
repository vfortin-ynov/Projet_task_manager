import smtplib
import csv
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from .task import Task


class EmailService:
    """Service d'envoi d'emails (à mocker dans les tests)"""

    def __init__(self, smtp_server: str = "smtp.gmail.com", port: int = 587):
        """Initialise la configuration SMTP"""
        self.smtp_server = smtp_server
        self.port = port
        self.connection = None

    def _validate_email(self, email: str) -> bool:
        """Valide le format d'une adresse email
        
        Args:
            email: L'adresse email à valider
            
        Returns:
            bool: True si l'email est valide
            
        Raises:
            ValueError: Si le format de l'email est invalide
        """
        if not isinstance(email, str):
            raise ValueError("Format d'email invalide")
            
        parts = email.split('@')
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError("Format d'email invalide")
            
        domain_parts = parts[1].rsplit('.', 1)
        if len(domain_parts) != 2 or not domain_parts[0] or len(domain_parts[1]) < 2:
            raise ValueError("Format d'email invalide")
            
        return True

    def connect(self, username: str, password: str) -> None:
        """Établit la connexion au serveur SMTP"""
        try:
            self.connection = smtplib.SMTP(self.smtp_server, self.port, timeout=5)
            self.connection.starttls()
            self.connection.login(username, password)
        except (smtplib.SMTPException, OSError) as e:
            if self.connection:
                try:
                    self.connection.quit()
                except:
                    pass
                self.connection = None
            raise ConnectionError("Échec de la connexion SMTP") from e

    def disconnect(self) -> None:
        """Ferme la connexion SMTP"""
        if self.connection:
            try:
                self.connection.quit()
            except smtplib.SMTPException:
                pass
            finally:
                self.connection = None

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Envoie un email générique"""
        if not self.connection:
            raise ConnectionError("Non connecté au serveur SMTP")

        self._validate_email(to_email)
        
        msg = MIMEMultipart()
        msg['From'] = 'taskmanager@example.com'
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            self.connection.send_message(msg)
            return True
        except smtplib.SMTPException as e:
            raise RuntimeError(f"Échec de l'envoi de l'email: {e}")

    def send_task_reminder(self, email: str, task_title: str, due_date: datetime) -> bool:
        """Envoie un email de rappel pour une tâche"""
        self._validate_email(email)
        
        subject = f"🔔 Rappel: {task_title}"
        body = (
            f"Bonjour,\n\n"
            f"Ceci est un rappel pour la tâche : {task_title}\n"
            f"Date d'échéance : {due_date.strftime('%d/%m/%Y %H:%M')}\n\n"
            f"Cordialement,\nVotre gestionnaire de tâches"
        )
        
        return self.send_email(email, subject, body)

    def send_completion_notification(self, email: str, task_title: str) -> bool:
        """Envoie une notification de complétion de tâche"""
        self._validate_email(email)
        
        subject = "✅ Tâche terminée !"
        body = (
            f"Bonjour,\n\n"
            f"Félicitations ! Vous avez terminé la tâche : {task_title}\n\n"
            f"Cordialement,\nVotre gestionnaire de tâches"
        )
        
        return self.send_email(email, subject, body)


class ReportService:
    """Service de génération de rapports"""

    def generate_daily_report(self, tasks: List[Task], date: Optional[datetime] = None) -> Dict[str, Any]:
        """Génère un rapport quotidien des tâches"""
        report_date = date or datetime.now()
        date_str = report_date.strftime('%d/%m/%Y')
        
        # Filtre les tâches du jour
        daily_tasks = [
            task for task in tasks 
            if task.created_at and 
            datetime.fromisoformat(task.created_at).date() == report_date.date()
        ]
        
        # Compte les tâches par statut et priorité
        status_count = {}
        priority_count = {}
        
        for task in daily_tasks:
            status = task.status.name
            priority = task.priority.name
            
            status_count[status] = status_count.get(status, 0) + 1
            priority_count[priority] = priority_count.get(priority, 0) + 1
        
        return {
            'date': date_str,
            'total_tasks': len(daily_tasks),
            'tasks_by_status': status_count,
            'tasks_by_priority': priority_count,
            'completed_tasks': sum(1 for t in daily_tasks if t.status.name == 'DONE')
        }

    def export_tasks_csv(self, tasks: List[Task], filename: str) -> bool:
        """Exporte les tâches vers un fichier CSV"""
        if not tasks:
            return False
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Définition des en-têtes basés sur les attributs de Task
                fieldnames = [
                    'id', 'title', 'description', 
                    'priority', 'status', 'created_at',
                    'completed_at', 'project_id'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for task in tasks:
                    task_dict = {
                        'id': task.id,
                        'title': task.title,
                        'description': task.description,
                        'priority': task.priority.name,
                        'status': task.status.name,
                        'created_at': task.created_at,
                        'completed_at': task.completed_at or '',
                        'project_id': task.project_id or ''
                    }
                    writer.writerow(task_dict)
                    
            return True
            
        except (IOError, OSError) as e:
            print(f"Erreur lors de l'export CSV: {e}")
            return False