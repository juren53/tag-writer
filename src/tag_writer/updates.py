"""
Tag Writer - UpdatesMixin: GitHub version checking, UpdateCheckThread.
"""

import time
import logging

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from .config import config
from .dialogs.preferences_dialog import PreferencesDialog

logger = logging.getLogger(__name__)


class UpdateCheckThread(QThread):
    """Thread for checking updates in background."""
    result_ready = pyqtSignal(object)

    def __init__(self, checker):
        super().__init__()
        self.checker = checker

    def run(self):
        result = self.checker.get_latest_version()
        self.result_ready.emit(result)


class UpdatesMixin:
    """Mixin providing version checking and preferences."""

    def on_preferences(self):
        """Show Preferences dialog."""
        dialog = PreferencesDialog(config, self)
        dialog.exec()

    def on_startup_update_check(self):
        """Check for updates on startup (silent)."""
        self.check_for_updates(silent=True)

    def check_for_updates(self, silent=False):
        """Check for updates with optional silent mode."""
        if not silent:
            current_time = time.time()
            if config.last_update_check and (current_time - config.last_update_check) < config.update_check_frequency:
                reply = QMessageBox.question(
                    self, "Update Check",
                    "You recently checked for updates. Check again anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return

            config.last_update_check = current_time
            config.save_config()

        if not silent:
            self.status_label.setText("Checking for updates...")

        self.update_check_thread = UpdateCheckThread(self.version_checker)
        self.update_check_thread.result_ready.connect(self.on_update_check_complete)
        self.update_check_thread.start()

    def on_check_for_updates(self):
        """Handle Check for Updates menu action."""
        self.check_for_updates(silent=False)

    def on_update_check_complete(self, result):
        """Handle completion of version check."""
        if result.error_message:
            self.status_label.setText("Update check failed")
            error_msg = result.error_message

            if "404" in error_msg and "Not Found" in error_msg:
                friendly_msg = (
                    "TagWriter repository doesn't have any releases yet.\n\n"
                    "You're using the latest available version!"
                )
                QMessageBox.information(self, "No Releases Available", friendly_msg)
            else:
                QMessageBox.warning(
                    self,
                    "Update Check Failed",
                    f"Could not check for updates:\n\n{error_msg}"
                )
            return

        self.status_label.setText("Update check complete")

        if result.has_update and result.latest_version not in config.skipped_versions:
            self.show_update_dialog(result)
        elif result.has_update and result.latest_version in config.skipped_versions:
            self.status_label.setText(f"Skipped version {result.latest_version}")
            QMessageBox.information(
                self,
                "Update Available",
                f"Version {result.latest_version} is available but you chose to skip it."
            )
        else:
            if not result.error_message:
                self.status_label.setText("You have the latest version")
                QMessageBox.information(
                    self,
                    "Up to Date",
                    f"TagWriter {result.current_version} is the latest version available."
                )

    def show_update_dialog(self, result):
        """Show update available dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Update Available")
        dialog.resize(500, 400)

        layout = QVBoxLayout(dialog)

        info_text = f"""
        <h3>Update Available!</h3>
        <p><b>Current Version:</b> {result.current_version}</p>
        <p><b>Latest Version:</b> {result.latest_version}</p>
        <p><b>Published:</b> {result.published_date[:10]}</p>
        <p><b>Download URL:</b> <a href="{result.download_url}">{result.download_url}</a></p>
        """

        info_label = QLabel(info_text)
        info_label.setOpenExternalLinks(True)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info_label)

        if result.release_notes:
            layout.addWidget(QLabel("<h4>Release Notes:</h4>"))
            notes_edit = QTextEdit()
            notes_edit.setPlainText(result.release_notes)
            notes_edit.setReadOnly(True)
            notes_edit.setMaximumHeight(150)
            layout.addWidget(notes_edit)

        button_layout = QHBoxLayout()

        download_btn = QPushButton("Download Update")
        download_btn.clicked.connect(lambda: self.on_download_update(result.download_url))
        button_layout.addWidget(download_btn)

        skip_btn = QPushButton("Skip This Version")
        skip_btn.clicked.connect(lambda: self.on_skip_version(result.latest_version, dialog))
        button_layout.addWidget(skip_btn)

        later_btn = QPushButton("Remind Later")
        later_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(later_btn)

        layout.addLayout(button_layout)

        dialog.exec()

    def on_download_update(self, download_url):
        """Open download URL in browser."""
        import webbrowser
        try:
            webbrowser.open(download_url)
            self.status_label.setText("Opening download page...")
        except Exception as e:
            logger.error(f"Error opening download URL: {e}")
            QMessageBox.warning(self, "Error", f"Could not open download page: {str(e)}")

    def on_skip_version(self, version, dialog):
        """Skip a specific version."""
        if version not in config.skipped_versions:
            config.skipped_versions.append(version)
            config.save_config()
            self.status_label.setText(f"Skipped version {version}")
        dialog.accept()
