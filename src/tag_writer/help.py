"""
Tag Writer - HelpMixin: about, credits, help, user guide, glossary, shortcuts, changelog.
"""

import os
import logging

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from pyqt_app_info import AppIdentity, ToolSpec, ToolRegistry, gather_info
from pyqt_app_info.qt import AboutDialog

from .config import config
from .constants import APP_NAME, APP_VERSION, APP_TIMESTAMP
from .exiftool_utils import get_exiftool_path

logger = logging.getLogger(__name__)


def _get_project_root():
    """Get the project root directory."""
    # From src/tag_writer/ go up two levels
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


class HelpMixin:
    """Mixin providing help, about, credits, user guide, glossary, shortcuts, changelog."""

    def on_about(self):
        """Show About dialog using pyqt_app_info."""
        identity = AppIdentity(
            name=APP_NAME,
            version=APP_VERSION,
            commit_date=APP_TIMESTAMP,
            description="A tool for editing image metadata.",
        )

        registry = ToolRegistry()
        registry.register(ToolSpec(
            name="ExifTool",
            command=get_exiftool_path(),
            version_flag="-ver",
        ))

        info = gather_info(identity, registry=registry, caller_file=__file__)
        AboutDialog(info, parent=self).exec()

    def on_credits(self, parent_dialog=None):
        """Show Credits dialog."""
        dialog = QDialog(parent_dialog if parent_dialog else self)
        dialog.setWindowTitle("Credits")
        dialog.resize(500, 350)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)

        credits_text = QLabel(
            "<h2>Tag Writer Credits</h2>"
            "<p>Tag Writer would not be possible without the incredible work of:</p>"
            "<hr>"
            "<h3>Phil Harvey</h3>"
            "<p><b>Father of ExifTool</b></p>"
            "<p>For creating and maintaining ExifTool, the comprehensive metadata toolkit "
            "that powers Tag Writer's ability to read and write image metadata.</p>"
            "<hr>"
            "<h3>The PyQt Team</h3>"
            "<p><b>GUI Framework</b></p>"
            "<p>For providing the excellent PyQt libraries that enable Tag Writer's "
            "user-friendly graphical interface.</p>"
            "<hr>"
            "<h3>Guido van Rossum</h3>"
            "<p><b>Father of Python</b></p>"
            "<p>For creating the Python programming language, which makes development "
            "accessible, enjoyable, and productive.</p>"
            "<hr>"
            "<p style='text-align: center; margin-top: 20px;'>"
            "<i>Thank you for your contributions to the open source community!</i></p>"
        )
        credits_text.setWordWrap(True)
        credits_text.setTextFormat(Qt.TextFormat.RichText)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(credits_text)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(scroll)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        dialog.exec()

    def on_help(self):
        """Show Help dialog."""
        QMessageBox.information(self,
            "Tag Writer Help",
            "This application allows you to edit and save metadata for image files.\n\n"
            "Usage:\n"
            "1. Open an image file using File > Open or the Select File button\n"
            "2. Edit metadata fields in the left panel\n"
            "3. Click 'Write Metadata' or use File > Save to save changes\n"
            "4. Use the navigation buttons to move between images in a directory"
        )

    def _show_markdown_dialog(self, title, file_path, fallback_url, window_size=(700, 600)):
        """Show a dialog displaying markdown content from a file, with URL fallback."""
        if os.path.exists(file_path):
            try:
                dialog = QDialog(self)
                dialog.setWindowTitle(title)
                dialog.resize(*window_size)

                dialog.setWindowFlags(Qt.WindowType.Window |
                                    Qt.WindowType.WindowMinimizeButtonHint |
                                    Qt.WindowType.WindowMaximizeButtonHint |
                                    Qt.WindowType.WindowCloseButtonHint)

                layout = QVBoxLayout(dialog)

                with open(file_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()

                # Replace relative image paths for user guide
                if 'user-guide' in file_path:
                    project_root = _get_project_root()
                    markdown_content = markdown_content.replace(
                        '![Tag Writer Main Window](images/',
                        f'![Tag Writer Main Window]({project_root}/Docs/images/'
                    )

                text_edit = QTextEdit()
                text_edit.setReadOnly(True)
                font = QFont()
                font.setPointSize(10)
                text_edit.setFont(font)

                if file_path.endswith('.md'):
                    text_edit.setMarkdown(markdown_content)
                else:
                    text_edit.setPlainText(markdown_content)

                layout.addWidget(text_edit)

                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

                dialog.exec()
                return
            except Exception as e:
                logger.error(f"Error displaying local {title}: {e}")

        # Fallback to URL
        import webbrowser
        try:
            webbrowser.open(fallback_url)
        except Exception as e:
            logger.error(f"Error opening {title} URL: {e}")
            QMessageBox.warning(self, "Error", f"Error opening {title}: {str(e)}\n\nURL: {fallback_url}")

    def on_user_guide(self):
        """Show User Guide from local file or GitHub URL if not found locally."""
        project_root = _get_project_root()
        user_guide_file = os.path.join(project_root, "Docs", "user-guide.md")
        self._show_markdown_dialog(
            "Tag Writer User Guide",
            user_guide_file,
            "https://github.com/juren53/tag-writer/blob/main/Docs/user-guide.md"
        )

    def on_glossary(self):
        """Show Glossary from local file or GitHub URL if not found locally."""
        project_root = _get_project_root()
        glossary_file = os.path.join(project_root, "Docs", "glossary.md")
        self._show_markdown_dialog(
            "Tag Writer Glossary",
            glossary_file,
            "https://github.com/juren53/tag-writer/blob/main/Docs/glossary.md"
        )

    def on_keyboard_shortcuts(self):
        """Show keyboard shortcuts documentation."""
        project_root = _get_project_root()
        possible_paths = [
            os.path.join(project_root, "Docs", "KeyBoard-ShortCuts.md"),
            os.path.join(project_root, "usr", "bin", "docs", "KeyBoard-ShortCuts.md"),
        ]

        shortcuts_file = None
        for path in possible_paths:
            if os.path.exists(path):
                shortcuts_file = path
                break

        logger.info(f"Looking for keyboard shortcuts file in paths:")
        for path in possible_paths:
            logger.info(f"  {path} - {'Exists' if os.path.exists(path) else 'Not found'}")

        if shortcuts_file and os.path.exists(shortcuts_file):
            self._show_markdown_dialog(
                "Keyboard Shortcuts",
                shortcuts_file,
                "https://github.com/juren53/tag-writer/blob/main/Docs/KeyBoard-ShortCuts.md",
                window_size=(600, 500)
            )
        else:
            import webbrowser
            url = "https://github.com/juren53/tag-writer/blob/main/Docs/KeyBoard-ShortCuts.md"
            try:
                webbrowser.open(url)
            except Exception as e:
                logger.error(f"Error opening keyboard shortcuts URL: {e}")
                QMessageBox.warning(self, "Error", f"Error opening keyboard shortcuts: {str(e)}\n\nURL: {url}")

    def on_changelog(self):
        """Open changelog from local file or GitHub URL if not found locally."""
        project_root = _get_project_root()
        possible_paths = [
            os.path.join(project_root, "CHANGELOG.md"),
            os.path.join(project_root, "usr", "bin", "docs", "CHANGELOG.md"),
        ]

        changelog_file = None
        for path in possible_paths:
            if os.path.exists(path):
                changelog_file = path
                break

        logger.info(f"Looking for changelog file in paths:")
        for path in possible_paths:
            logger.info(f"  {path} - {'Exists' if os.path.exists(path) else 'Not found'}")

        if changelog_file and os.path.exists(changelog_file):
            try:
                dialog = QDialog(self)
                dialog.setWindowTitle("Changelog")
                dialog.resize(800, 600)

                text_widget = QTextEdit()
                text_widget.setReadOnly(True)

                with open(changelog_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                text_widget.setPlainText(content)
                layout = QVBoxLayout(dialog)
                layout.addWidget(text_widget)

                close_btn = QPushButton("Close")
                close_btn.clicked.connect(dialog.accept)
                layout.addWidget(close_btn)

                dialog.exec()
            except Exception as e:
                logger.error(f"Error opening changelog file: {e}")
                QMessageBox.warning(self, "Error", f"Could not open changelog: {str(e)}")
        else:
            import webbrowser
            changelog_url = "https://github.com/juren53/tag-writer/blob/main/CHANGELOG.md"
            try:
                webbrowser.open(changelog_url)
            except Exception as e:
                logger.error(f"Error opening changelog URL: {e}")
                QMessageBox.warning(self, "Error", f"Could not open changelog: {str(e)}\n\nURL: {changelog_url}")
