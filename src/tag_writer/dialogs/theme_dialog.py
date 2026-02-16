"""
Tag Writer - Theme selection dialog.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QDialogButtonBox
)


class ThemeDialog(QDialog):
    """Dialog for selecting application theme."""

    def __init__(self, current_theme, theme_manager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.selected_theme = current_theme

        self.setWindowTitle("Select Theme")
        self.setFixedSize(450, 300)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Choose a theme for the application:"))

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.theme_manager.get_theme_names())
        self.theme_combo.setCurrentText(current_theme)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        layout.addWidget(self.theme_combo)

        self.preview_label = QLabel("Preview: This is how text will look with the selected theme")
        self.preview_label.setStyleSheet("padding: 15px; border: 1px solid gray; min-height: 60px;")
        self.preview_label.setWordWrap(True)
        layout.addWidget(self.preview_label)

        self.preview_button = QPushButton("Sample Button")
        layout.addWidget(self.preview_button)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.update_preview()

    def on_theme_changed(self, theme_name):
        """Handle theme selection change."""
        self.selected_theme = theme_name
        self.update_preview()

    def update_preview(self):
        """Update the preview with selected theme colors."""
        theme = self.theme_manager.get_theme(self.selected_theme)

        self.preview_label.setStyleSheet(f"""
            background-color: {theme['background']};
            color: {theme['text']};
            padding: 15px;
            border: 1px solid {theme['border']};
            min-height: 60px;
        """)

        self.preview_button.setStyleSheet(f"""
            background-color: {theme['button_bg']};
            color: {theme['button_text']};
            border: 1px solid {theme['border']};
            border-radius: 3px;
            padding: 6px 12px;
        """)

    def get_selected_theme(self):
        """Get the selected theme name."""
        return self.selected_theme
