"""
Tag Writer - Preferences dialog.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QGroupBox, QCheckBox, QDialogButtonBox
)


class PreferencesDialog(QDialog):
    """Dialog for application preferences."""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Preferences")
        self.setFixedSize(450, 200)

        layout = QVBoxLayout(self)

        title_label = QLabel("<h3>Application Preferences</h3>")
        layout.addWidget(title_label)

        updates_group = QGroupBox("Updates")
        updates_layout = QVBoxLayout()

        self.auto_check_updates_checkbox = QCheckBox("Automatically check for updates on startup")
        self.auto_check_updates_checkbox.setChecked(self.config.auto_check_updates)
        self.auto_check_updates_checkbox.setToolTip(
            "When enabled, Tag Writer will check for new versions on startup.\n"
            "You can still manually check for updates from the Help menu."
        )
        updates_layout.addWidget(self.auto_check_updates_checkbox)

        updates_group.setLayout(updates_layout)
        layout.addWidget(updates_group)

        layout.addStretch()

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def on_accept(self):
        """Save preferences when OK is clicked."""
        self.config.auto_check_updates = self.auto_check_updates_checkbox.isChecked()
        self.config.save_config()
        self.accept()
