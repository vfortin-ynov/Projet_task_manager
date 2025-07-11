"""Tests pour les services du gestionnaire de tâches."""

import smtplib
from datetime import datetime, timedelta
from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.task_manager.services import EmailService, ReportService
from src.task_manager.task import Priority, Status, Task


class TestEmailService:
    """Tests pour le service d'emails."""

    def setup_method(self):
        """Initialisation avant chaque test."""
        self.email_service = EmailService()
        self.mock_smtp = MagicMock()
        self.mock_smtp.starttls.return_value = True
        self.mock_smtp.login.return_value = True
        self.mock_smtp.send_message.return_value = {}

    @patch("smtplib.SMTP")
    def test_connect_success(self, mock_smtp_constructor):
        """Test de connexion réussie au serveur SMTP."""
        mock_smtp_constructor.return_value = self.mock_smtp

        self.email_service.connect("user@example.com", "password123")

        # Vérifier que le constructeur SMTP est appelé avec les bons arguments,
        # y compris le timeout
        mock_smtp_constructor.assert_called_once_with(
            "smtp.gmail.com", 587, timeout=5
        )
        self.mock_smtp.starttls.assert_called_once()
        self.mock_smtp.login.assert_called_once_with(
            "user@example.com", "password123"
        )

    @patch("smtplib.SMTP")
    def test_connect_failure(self, mock_smtp_constructor):
        """Test d'échec de connexion au serveur SMTP."""
        # Configurer le mock pour lever une exception lors
        # de l'appel à starttls()
        self.mock_smtp.starttls.side_effect = smtplib.SMTPException(
            "Erreur SMTP"
        )
        mock_smtp_constructor.return_value = self.mock_smtp

        # Vérifier que l'exception est levée avec le bon message
        with pytest.raises(
            ConnectionError, match="Échec de la connexion SMTP"
        ):
            self.email_service.connect("user@example.com", "password123")

        # Vérifier que la connexion a bien été nettoyée
        assert self.email_service.connection is None

        # Vérifier que les méthodes ont été appelées comme prévu
        mock_smtp_constructor.assert_called_once_with(
            "smtp.gmail.com", 587, timeout=5
        )
        self.mock_smtp.starttls.assert_called_once()
        self.mock_smtp.login.assert_not_called()

    def test_validate_email_valid(self):
        """Test de validation d'email valide."""
        assert self.email_service._validate_email("test@example.com") is True

    def test_validate_email_invalid(self):
        """Test de validation d'email invalide."""
        with pytest.raises(ValueError, match="Format d'email invalide"):
            self.email_service._validate_email("invalid-email")

    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp_constructor):
        """Test d'envoi d'email réussi."""
        mock_smtp_constructor.return_value = self.mock_smtp
        self.email_service.connect("user@example.com", "password123")

        result = self.email_service.send_email(
            "recipient@example.com", "Sujet", "Corps du message"
        )

        assert result is True
        self.mock_smtp.send_message.assert_called_once()

    @patch("smtplib.SMTP")
    def test_send_task_reminder(self, mock_smtp_constructor):
        """Test d'envoi de rappel de tâche."""
        mock_smtp_constructor.return_value = self.mock_smtp
        self.email_service.connect("user@example.com", "password123")

        # Utiliser une date fixe sans fuseau horaire
        due_date = datetime(2023, 1, 1, 12, 0)
        result = self.email_service.send_task_reminder(
            "user@example.com", "Tâche importante", due_date
        )

        assert result is True
        self.mock_smtp.send_message.assert_called_once()

        # Récupérer le message envoyé
        msg = self.mock_smtp.send_message.call_args[0][0]

        # Vérifier le sujet
        assert "Rappel: Tâche importante" in msg["Subject"]

        # Extraire le corps du message de manière plus fiable
        body = ""
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                break

        # Vérifier que le corps contient la date formatée correctement
        expected_date = due_date.strftime("%d/%m/%Y %H:%M")
        assert (
            expected_date in body
        ), f"Date attendue '{expected_date}' non trouvée dans le \
            corps de l'email: {body}"

    def test_send_task_reminder_invalid_email(self):
        """Test d'envoi de rappel avec email invalide."""
        with pytest.raises(ValueError, match="Format d'email invalide"):
            self.email_service.send_task_reminder(
                "invalid-email", "Tâche", datetime.now()
            )

    @patch("smtplib.SMTP")
    def test_connect_smtp_exception(self, mock_smtp):
        """Test de l'échec de connexion avec exception SMTP"""
        mock_smtp.return_value.starttls.side_effect = smtplib.SMTPException(
            "Erreur SMTP"
        )

        with pytest.raises(ConnectionError):
            self.email_service.connect("test@example.com", "password")

        # Vérifie que la connexion a bien été fermée en cas d'erreur
        mock_smtp.return_value.quit.assert_called_once()
        assert self.email_service.connection is None

    @patch("smtplib.SMTP")
    def test_connect_os_error(self, mock_smtp):
        """Test de l'échec de connexion avec OSError"""
        mock_smtp.side_effect = OSError("Erreur de connexion")

        with pytest.raises(ConnectionError):
            self.email_service.connect("test@example.com", "password")

        # Vérifie que la connexion est bien None en cas d'erreur
        assert self.email_service.connection is None

    @patch("smtplib.SMTP")
    def test_disconnect_with_error(self, mock_smtp):
        """Test de la déconnexion avec erreur"""
        # Configurer le mock pour simuler une erreur lors de la déconnexion
        mock_connection = MagicMock()
        mock_connection.quit.side_effect = smtplib.SMTPException(
            "Erreur de déconnexion"
        )

        # Créer une instance de EmailService et définir
        # manuellement la connexion
        email_service = EmailService()
        email_service.connection = mock_connection

        # Appeler la méthode disconnect (ne devrait pas lever d'exception)
        email_service.disconnect()

        # Vérifier que la connexion a été nettoyée malgré l'erreur
        assert email_service.connection is None

    def test_send_email_not_connected(self):
        """Test d'envoi d'email sans être connecté"""
        with pytest.raises(ConnectionError):
            self.email_service.send_email("test@example.com", "Sujet", "Corps")

    @patch("smtplib.SMTP")
    def test_send_email_smtp_error(self, mock_smtp):
        """Test d'erreur lors de l'envoi d'email"""
        self.email_service.connect("test@example.com", "password")
        mock_smtp.return_value.send_message.side_effect = (
            smtplib.SMTPException("Erreur d'envoi")
        )

        with pytest.raises(RuntimeError):
            self.email_service.send_email("test@example.com", "Sujet", "Corps")

    def test_send_completion_notification_invalid_email(self):
        """Test d'envoi de notification avec email invalide"""
        with pytest.raises(ValueError):
            self.email_service.send_completion_notification(
                "email-invalide", "Tâche"
            )

    @patch("smtplib.SMTP")
    def test_send_completion_notification_success(self, mock_smtp_constructor):
        """Test d'envoi réussi d'une notification de complétion"""
        # Configurer le mock SMTP
        mock_smtp = MagicMock()
        mock_smtp_constructor.return_value = mock_smtp

        # Créer une nouvelle instance pour éviter les interférences
        email_service = EmailService()
        email_service.connection = mock_smtp

        # Tester l'envoi de notification
        result = email_service.send_completion_notification(
            "recipient@example.com", "Tâche importante"
        )

        # Vérifications
        assert result is True
        mock_smtp.send_message.assert_called_once()

        # Récupérer le message envoyé
        msg = mock_smtp.send_message.call_args[0][0]

        # Vérifier le sujet
        assert "Tâche terminée" in msg["Subject"]

        # Extraire le contenu du message
        content = ""
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                content = part.get_payload(decode=True).decode()
                break

        # Vérifier que le contenu contient le titre de la tâche
        assert (
            "Tâche importante" in content
        ), f"Le contenu du message ne contient pas le titre \
        de la tâche: {content}"

    def test_disconnect_success(self):
        """Test de déconnexion réussie"""
        # Créer un mock pour la connexion
        mock_connection = MagicMock()

        # Créer une nouvelle instance et définir manuellement la connexion
        email_service = EmailService()
        email_service.connection = mock_connection

        # Appeler la méthode disconnect
        email_service.disconnect()

        # Vérifier que quit() a été appelé et que la connexion est None
        mock_connection.quit.assert_called_once()
        assert email_service.connection is None

    @patch("smtplib.SMTP")
    def test_connect_smtp_exception_during_login(self, mock_smtp_constructor):
        """Test d'échec de connexion avec exception SMTP lors du login"""
        # Configurer le mock pour lever une exception lors du login
        mock_smtp = MagicMock()
        mock_smtp_constructor.return_value = mock_smtp
        mock_smtp.login.side_effect = smtplib.SMTPException(
            "Erreur d'authentification"
        )

        # Créer une nouvelle instance
        email_service = EmailService()

        # Vérifier que l'exception est levée
        with pytest.raises(
            ConnectionError, match="Échec de la connexion SMTP"
        ):
            email_service.connect("user@example.com", "password")

        # Vérifier que la connexion a été nettoyée
        assert email_service.connection is None
        mock_smtp.quit.assert_called_once()

    @patch("smtplib.SMTP")
    def test_connect_os_error_during_connection(self, mock_smtp_constructor):
        """Test d'échec de connexion avec OSError lors de la connexion"""
        # Configurer le mock pour lever une OSError
        mock_smtp_constructor.side_effect = OSError("Erreur de connexion")

        # Créer une nouvelle instance
        email_service = EmailService()

        # Vérifier que l'exception est levée
        with pytest.raises(
            ConnectionError, match="Échec de la connexion SMTP"
        ):
            email_service.connect("user@example.com", "password")

        # Vérifier que la connexion est None
        assert email_service.connection is None

    def test_disconnect_no_connection(self):
        """Test de déconnexion quand aucune connexion n'est établie"""
        # Créer une nouvelle instance sans connexion
        email_service = EmailService()

        # Appeler la méthode disconnect ne devrait pas lever d'exception
        email_service.disconnect()

        # Vérifier que la connexion reste None
        assert email_service.connection is None

    def test_validate_email_edge_cases(self):
        """Test des cas limites de validation d'email"""
        # Test avec un email vide
        with pytest.raises(ValueError, match="Format d'email invalide"):
            self.email_service._validate_email("")

        # Test avec None
        with pytest.raises(ValueError, match="Format d'email invalide"):
            self.email_service._validate_email(None)

        # Test avec un type non string
        with pytest.raises(ValueError, match="Format d'email invalide"):
            self.email_service._validate_email(123)

        # Test sans @
        with pytest.raises(ValueError, match="Format d'email invalide"):
            self.email_service._validate_email("invalid-email")

        # Test avec @ mais sans domaine
        with pytest.raises(ValueError, match="Format d'email invalide"):
            self.email_service._validate_email("test@")

        # Test avec @ mais sans nom d'utilisateur
        with pytest.raises(ValueError, match="Format d'email invalide"):
            self.email_service._validate_email("@example.com")

        # Test avec un domaine sans extension (sans point)
        with pytest.raises(ValueError, match="Format d'email invalide"):
            self.email_service._validate_email("test@example")

        # Test avec une extension de domaine trop courte
        with pytest.raises(ValueError, match="Format d'email invalide"):
            self.email_service._validate_email("test@example.c")

        # Test avec un point à la fin (invalide car crée une extension vide)
        with pytest.raises(ValueError, match="Format d'email invalide"):
            self.email_service._validate_email("test@example.com.")

        # Test avec plusieurs @
        with pytest.raises(ValueError, match="Format d'email invalide"):
            self.email_service._validate_email("te@st@example.com")

        # Test avec un email valide avec des espaces
        # (doit être valide après strip)
        assert (
            self.email_service._validate_email("  test@example.com  ") is True
        )

        # Test avec un email valide standard
        assert self.email_service._validate_email("test@example.com") is True

        # Test avec un sous-domaine
        assert (
            self.email_service._validate_email("test@sub.example.com") is True
        )

    @patch("smtplib.SMTP")
    def test_connect_quit_failure(self, mock_smtp_constructor):
        """Test d'échec de déconnexion lors d'une erreur de connexion"""
        # Configurer le mock pour échouer lors de la déconnexion
        mock_smtp = MagicMock()
        mock_smtp_constructor.return_value = mock_smtp
        mock_smtp.login.side_effect = smtplib.SMTPException(
            "Erreur de connexion"
        )
        mock_smtp.quit.side_effect = smtplib.SMTPException(
            "Erreur de déconnexion"
        )

        # Tester la connexion
        email_service = EmailService()
        with pytest.raises(
            ConnectionError, match="Échec de la connexion SMTP"
        ):
            email_service.connect("user@example.com", "password")

        # Vérifier que la connexion a été nettoyée malgré l'échec de quit()
        assert email_service.connection is None


class TestReportService:
    """Tests pour ReportService"""

    def setup_method(self):
        self.report_service = ReportService()

        # Création de tâches de test
        self.today = datetime.now()
        self.yesterday = self.today - timedelta(days=1)

        self.task1 = Task("Tâche 1", "Description 1", Priority.HIGH)
        self.task1.created_at = self.today.isoformat()
        self.task1.status = Status.TODO

        self.task2 = Task("Tâche 2", "Description 2", Priority.MEDIUM)
        self.task2.created_at = self.today.isoformat()
        self.task2.status = Status.DONE

        self.old_task = Task("Tâche ancienne", "Description", Priority.LOW)
        self.old_task.created_at = self.yesterday.isoformat()

        self.tasks = [self.task1, self.task2, self.old_task]

    def test_generate_daily_report_default_date(self):
        """Test de génération de rapport avec date par défaut."""
        report = self.report_service.generate_daily_report(self.tasks)

        assert report["total_tasks"] == 2  # Seulement les tâches d'aujourd'hui
        assert report["tasks_by_status"]["TODO"] == 1
        assert report["tasks_by_status"]["DONE"] == 1
        assert report["tasks_by_priority"]["HIGH"] == 1
        assert report["tasks_by_priority"]["MEDIUM"] == 1
        assert report["completed_tasks"] == 1

    @patch("src.task_manager.services.datetime")
    def test_generate_daily_report_fixed_date(self, mock_datetime):
        """Test de génération de rapport avec date fixe."""
        # Configuration de la date fixe
        fixed_date = datetime(2023, 1, 1, 12, 0)

        # Création d'une tâche pour la date fixe
        task = Task("Tâche fixe", "Description", Priority.HIGH)
        # Forcer la date de création à notre date fixe
        task.created_at = fixed_date.isoformat()

        # Configurer le mock pour datetime.now()
        mock_datetime.now.return_value = fixed_date

        # Créer un mock pour fromisoformat qui ignore les fuseaux horaires
        def mock_fromisoformat(iso_str):
            # Nettoyer la chaîne ISO pour enlever le fuseau horaire s'il existe
            if "+" in iso_str:
                iso_str = iso_str.split("+")[0]
            return datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S")

        mock_datetime.fromisoformat.side_effect = mock_fromisoformat

        # S'assurer que date() retourne la bonne date
        mock_date = MagicMock()
        mock_date.return_value = fixed_date.date()
        mock_datetime.return_value.date = mock_date

        # Appel de la méthode avec la date fixe
        report = self.report_service.generate_daily_report(
            [task], date=fixed_date
        )

        # Vérifications
        assert report["date"] == "01/01/2023"
        assert report["total_tasks"] == 1, (
            f"Expected 1 task, got {report['total_tasks']}. "
            f"Task created_at: {task.created_at}, "
            f"Report date: {report['date']}"
        )
        assert "HIGH" in report["tasks_by_priority"]
        assert report["tasks_by_priority"]["HIGH"] == 1

    @patch("builtins.open", new_callable=mock_open)
    def test_export_tasks_csv(self, mock_file):
        """Test d'exportation des tâches en CSV."""
        # Appel de la méthode à tester
        result = self.report_service.export_tasks_csv(
            self.tasks, "test_export.csv"
        )

        # Vérifications
        assert result is True
        mock_file.assert_called_once_with(
            "test_export.csv", "w", newline="", encoding="utf-8"
        )

        # Vérification que write a été appelé (pour l'en-tête et les données)
        assert mock_file().write.call_count > 0

        # Vérification du contenu de l'en-tête
        header_call = mock_file().write.call_args_list[0][0][0]
        expected_header = (
            "id,title,description,priority,status,created_at,completed_at,"
            "project_id"
        )
        assert expected_header in header_call

    def test_export_tasks_csv_empty_list(self):
        """Test d'exportation avec une liste vide de tâches."""
        with patch("builtins.open") as mock_file:
            result = self.report_service.export_tasks_csv(
                [], "empty_export.csv"
            )
            assert result is False
            mock_file.assert_not_called()

    @patch("builtins.open", side_effect=IOError("Erreur d'écriture"))
    def test_export_tasks_csv_io_error(self, mock_file):
        """Test de gestion des erreurs d'écriture lors de l'export CSV."""
        result = self.report_service.export_tasks_csv(
            self.tasks, "error_export.csv"
        )
        assert result is False

    def test_generate_daily_report_empty(self):
        """Test de génération de rapport journalier sans tâches"""
        report = self.report_service.generate_daily_report([])
        assert report["total_tasks"] == 0
        assert report["completed_tasks"] == 0
        assert report["tasks_by_status"] == {}
        assert report["tasks_by_priority"] == {}
