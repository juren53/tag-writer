"""
Tag Writer - FileOpsMixin: save, export, import, rename, rotate, refresh.
"""

import os
import logging

from PyQt6.QtWidgets import (
    QFileDialog, QMessageBox, QApplication, QDialog, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QLineEdit, QDialogButtonBox,
    QProgressDialog, QMenu, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor, QGuiApplication

from .config import config
from .file_utils import backup_file, read_metadata

logger = logging.getLogger(__name__)


class FileOpsMixin:
    """Mixin providing file operations: save, export, import, rename, rotate, refresh."""

    def show_auto_close_message(self, title, message, icon=QMessageBox.Icon.Information, timeout=3000):
        """Show a message box that auto-closes after a timeout."""
        self._auto_close_msg_box = QMessageBox(self)
        self._auto_close_msg_box.setWindowTitle(title)
        self._auto_close_msg_box.setText(message)
        self._auto_close_msg_box.setIcon(icon)
        self._auto_close_msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        self._auto_close_msg_box.setModal(True)

        self._auto_close_timer = QTimer(self)
        self._auto_close_timer.setSingleShot(True)
        self._auto_close_timer.timeout.connect(self._close_auto_message)
        self._auto_close_timer.start(timeout)

        self._auto_close_msg_box.open()

    def _close_auto_message(self):
        """Helper to close the auto-close message box."""
        if hasattr(self, '_auto_close_msg_box') and self._auto_close_msg_box.isVisible():
            self._auto_close_msg_box.close()

    def on_save(self):
        """Handle Save action."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return

        self.metadata_panel.update_manager_from_ui()

        success = self.metadata_manager.save_to_file(config.selected_file)

        if success:
            self.status_label.setText("Metadata saved")
        else:
            QMessageBox.critical(self, "Error", "Failed to save metadata.")
            self.status_label.setText("Error saving metadata")

    def on_clear(self):
        """Handle Clear Fields action."""
        self.metadata_panel.clear_fields()
        self.metadata_manager.clear()
        self.status_label.setText("All fields cleared")

    def on_export(self):
        """Handle Export to JSON action."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return

        file_dialog = QFileDialog()
        base_name = os.path.splitext(os.path.basename(config.selected_file))[0]
        default_path = f"{base_name}_metadata.json"
        start_dir = config.last_directory or ""
        file_path, _ = file_dialog.getSaveFileName(
            self,
            "Export Metadata to JSON",
            os.path.join(start_dir, default_path),
            "JSON Files (*.json)"
        )

        if file_path:
            self.metadata_panel.update_manager_from_ui()

            if self.metadata_manager.export_to_json(file_path):
                QMessageBox.information(self, "Export Successful", f"Metadata exported to {file_path}")
                self.status_label.setText("Metadata exported")
            else:
                QMessageBox.critical(self, "Export Failed", "Failed to export metadata.")
                self.status_label.setText("Error exporting metadata")

    def on_import(self):
        """Handle Import from JSON action."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return

        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Import Metadata from JSON",
            config.last_directory or "",
            "JSON Files (*.json)"
        )

        if file_path:
            if self.metadata_manager.import_from_json(file_path):
                self.metadata_panel.update_from_manager()
                QMessageBox.information(self, "Import Successful", f"Metadata imported from {file_path}")
                self.status_label.setText("Metadata imported")
            else:
                QMessageBox.critical(self, "Import Failed", "Failed to import metadata.")
                self.status_label.setText("Error importing metadata")

    def on_set_today_date(self):
        """Handle Set Today's Date action."""
        self.metadata_panel.set_today_date()
        self.status_label.setText("Date set to today")

    def on_copy_path_to_clipboard(self):
        """Copy the fully qualified file name to the clipboard."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return

        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(config.selected_file)
            self.status_label.setText(f"Full path copied to clipboard: {config.selected_file}")
        except Exception as e:
            logger.error(f"Error copying path to clipboard: {e}")
            QMessageBox.critical(self, "Error", f"Failed to copy path to clipboard: {str(e)}")

    def on_open_in_default_editor(self):
        """Open the current image in the system's default image editor."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return

        try:
            result = QMessageBox.information(
                self,
                "Opening External Editor",
                "The image will open in your default image editor.\n\n"
                "Note: Changes made in external editors may affect metadata.\n"
                "Consider refreshing the image (F5) after saving external changes.",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
            )

            if result != QMessageBox.StandardButton.Ok:
                return

            import subprocess
            import platform

            system = platform.system()

            if system == "Windows":
                os.startfile(config.selected_file)
            elif system == "Darwin":
                subprocess.call(["open", config.selected_file])
            else:
                subprocess.call(["xdg-open", config.selected_file])

            self.status_label.setText(f"Opened {os.path.basename(config.selected_file)} in default editor")

        except Exception as e:
            logger.error(f"Error opening file in default editor: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open file in default editor: {str(e)}")

    def on_rename_file(self):
        """Handle Rename File action."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return

        current_filename = os.path.basename(config.selected_file)
        current_directory = os.path.dirname(config.selected_file)

        dialog = QDialog(self)
        dialog.setWindowTitle("Rename File")
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Enter new filename:"))

        line_edit = QLineEdit(current_filename)
        line_edit.selectAll()
        layout.addWidget(line_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # Temporarily remove application event filter
        QApplication.instance().removeEventFilter(self)

        dialog_shown = False
        original_show_event = dialog.showEvent

        def showEvent(event):
            nonlocal dialog_shown
            original_show_event(event)
            if not dialog_shown:
                dialog_shown = True
                QTimer.singleShot(50, lambda: line_edit.setFocus())
                QTimer.singleShot(100, lambda: line_edit.selectAll())

        dialog.showEvent = showEvent

        def keyPressEvent(event):
            if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
                if line_edit.hasFocus():
                    line_edit.keyPressEvent(event)
                else:
                    line_edit.setFocus()
                    line_edit.keyPressEvent(event)
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
                dialog.accept()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Escape:
                dialog.reject()
                event.accept()
                return
            QDialog.keyPressEvent(dialog, event)

        dialog.keyPressEvent = keyPressEvent

        def lineEditEventFilter(watched, event):
            if event.type() == event.Type.KeyPress and watched == line_edit:
                if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
                    line_edit.keyPressEvent(event)
                    return True
            return False

        line_edit.installEventFilter(dialog)
        dialog.eventFilter = lineEditEventFilter

        ok = dialog.exec() == QDialog.DialogCode.Accepted
        new_filename = line_edit.text() if ok else ""

        # Restore the application event filter
        QApplication.instance().installEventFilter(self)

        if not ok or not new_filename or new_filename == current_filename:
            return

        new_filename = os.path.basename(new_filename)
        if not new_filename or new_filename in ('.', '..') or '\x00' in new_filename:
            QMessageBox.warning(self, "Invalid Filename", "The filename is invalid. Please enter a valid filename.")
            return

        new_file_path = os.path.join(current_directory, new_filename)

        if os.path.exists(new_file_path):
            result = QMessageBox.question(
                self, "File Exists",
                f"A file named '{new_filename}' already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result != QMessageBox.StandardButton.Yes:
                return

        try:
            backup_path = backup_file(config.selected_file)
            if not backup_path:
                raise Exception("Failed to create backup file")

            import shutil
            shutil.move(config.selected_file, new_file_path)

            config.selected_file = new_file_path

            if config.directory_image_files and config.current_file_index >= 0:
                config.directory_image_files[config.current_file_index] = new_file_path

            self.load_file(new_file_path)

            self.status_label.setText(f"Renamed to {new_filename}")
            QMessageBox.information(
                self, "File Renamed",
                f"File successfully renamed to '{new_filename}'\nA backup was created at '{os.path.basename(backup_path)}'"
            )

        except Exception as e:
            logger.error(f"Error renaming file: {e}")
            QMessageBox.critical(self, "Error", f"Failed to rename file: {str(e)}")
            if 'backup_path' in locals() and os.path.exists(backup_path):
                try:
                    import shutil
                    shutil.copy2(backup_path, config.selected_file)
                    self.status_label.setText("Restored from backup after rename error")
                except Exception as restore_err:
                    logger.error(f"Error restoring from backup: {restore_err}")
                    self.status_label.setText("Error during rename and restore")

    def on_view_all_tags(self):
        """Handle View All Tags action."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return

        metadata = read_metadata(config.selected_file)

        if not metadata:
            QMessageBox.information(self, "No Metadata", "No metadata found in the selected file.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"All Tags: {os.path.basename(config.selected_file)}")

        dialog.setWindowFlags(Qt.WindowType.Window |
                             Qt.WindowType.WindowMinimizeButtonHint |
                             Qt.WindowType.WindowMaximizeButtonHint |
                             Qt.WindowType.WindowCloseButtonHint)

        screen_geometry = QGuiApplication.primaryScreen().geometry()
        dialog.setGeometry(screen_geometry)
        dialog.showMaximized()

        layout = QVBoxLayout(dialog)

        # Search bar
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)

        search_label = QLabel("Search:")
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("Type to search tags and values (Ctrl+F to focus)")

        search_status = QLabel("")
        search_status.setStyleSheet("font-size: 10pt; color: gray;")

        search_layout.addWidget(search_label)
        search_layout.addWidget(search_edit)
        search_layout.addWidget(search_status)

        layout.addWidget(search_container)

        # Table
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Tag", "Value"])
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.setColumnWidth(0, 400)

        original_metadata = list(sorted(metadata.items()))

        def populate_table(items):
            table.setRowCount(len(items))
            for i, (key, value) in enumerate(items):
                table.setItem(i, 0, QTableWidgetItem(key))
                table.setItem(i, 1, QTableWidgetItem(str(value)))

        populate_table(original_metadata)

        def search_metadata():
            search_text = search_edit.text().lower()
            if not search_text:
                populate_table(original_metadata)
                search_status.setText("")
                return

            filtered_items = []
            for key, value in original_metadata:
                if (search_text in key.lower() or
                    search_text in str(value).lower()):
                    filtered_items.append((key, value))

            populate_table(filtered_items)

            if filtered_items:
                search_status.setText(f"Found {len(filtered_items)} matches")
            else:
                search_status.setText("No matches found")

        search_edit.textChanged.connect(search_metadata)

        layout.addWidget(table)

        # Buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)

        clear_btn = QPushButton("Clear Search")
        clear_btn.clicked.connect(lambda: search_edit.clear())
        button_layout.addWidget(clear_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)

        layout.addWidget(button_container)

        # Event filter for Ctrl+F
        def event_filter(watched, event):
            if event.type() == event.Type.KeyPress:
                if event.key() == Qt.Key.Key_F and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    search_edit.setFocus()
                    search_edit.selectAll()
                    return True
                elif event.key() == Qt.Key.Key_Escape:
                    if search_edit.hasFocus() and search_edit.text():
                        search_edit.clear()
                        return True
                    else:
                        dialog.reject()
                        return True
            return False

        dialog.installEventFilter(dialog)
        table.installEventFilter(dialog)
        dialog.eventFilter = event_filter

        table.setFocus()
        dialog.exec()

    def on_rotate_image(self, degrees):
        """Rotate the current image by the specified degrees."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return

        result = QMessageBox.question(
            self,
            "Confirm Rotation",
            f"This will rotate the image {abs(degrees)}\u00b0 {'clockwise' if degrees > 0 else 'counter-clockwise'}.\n\n"
            "A backup of the original file will be created before modification.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if result != QMessageBox.StandardButton.Yes:
            return

        progress_dialog = QProgressDialog(
            f"Rotating image {abs(degrees)}\u00b0 {'clockwise' if degrees > 0 else 'counter-clockwise'}...",
            "Cancel", 0, 100, self
        )
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(10)
        QApplication.processEvents()

        try:
            bp = backup_file(config.selected_file)
            if not bp:
                raise Exception("Failed to create backup file")

            progress_dialog.setValue(20)
            QApplication.processEvents()

            self.metadata_panel.update_manager_from_ui()

            field_names = self.metadata_manager.get_field_names()
            metadata_dict = {}
            for field_name in field_names:
                metadata_dict[field_name] = self.metadata_manager.get_field(field_name)

            progress_dialog.setValue(30)
            QApplication.processEvents()

            from PIL import Image
            image = Image.open(config.selected_file)

            rotated_image = image.rotate(
                -degrees,
                expand=True
            )

            progress_dialog.setValue(60)
            QApplication.processEvents()

            file_ext = os.path.splitext(config.selected_file)[1].lower()
            if file_ext in ('.jpg', '.jpeg'):
                rotated_image.save(config.selected_file, quality=95, subsampling=0)
            elif file_ext in ('.tif', '.tiff'):
                rotated_image.save(config.selected_file, compression='tiff_lzw')
            else:
                rotated_image.save(config.selected_file)

            progress_dialog.setValue(70)
            QApplication.processEvents()

            for field_name, value in metadata_dict.items():
                self.metadata_manager.set_field(field_name, value)

            metadata_saved = self.metadata_manager.save_to_file(config.selected_file)

            progress_dialog.setValue(90)
            QApplication.processEvents()

            self.load_file(config.selected_file)

            progress_dialog.setValue(100)
            QApplication.processEvents()

            if metadata_saved:
                QMessageBox.information(
                    self,
                    "Rotation Complete",
                    f"Image rotated {abs(degrees)}\u00b0 {'clockwise' if degrees > 0 else 'counter-clockwise'} successfully.\n"
                    f"Metadata preserved and backup saved to: {os.path.basename(bp)}"
                )
            else:
                result = QMessageBox.warning(
                    self,
                    "Metadata Warning",
                    f"Image was rotated successfully, but metadata could not be re-applied.\n\n"
                    f"Would you like to restore from backup to preserve your metadata?\n"
                    f"Backup: {os.path.basename(bp)}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if result == QMessageBox.StandardButton.Yes:
                    try:
                        import shutil
                        shutil.copy2(bp, config.selected_file)
                        self.load_file(config.selected_file)
                        QMessageBox.information(self, "Restored", "File restored from backup successfully.")
                    except Exception as restore_err:
                        logger.error(f"Error restoring backup: {restore_err}")
                        QMessageBox.critical(self, "Restore Error",
                            f"Failed to restore from backup: {restore_err}\n"
                            f"Backup file is still available at:\n{bp}")
        except Exception as e:
            progress_dialog.cancel()
            logger.error(f"Error rotating image: {e}")
            QMessageBox.critical(self, "Rotation Error", f"Error rotating image: {str(e)}")

    def on_refresh(self):
        """Refresh the current image and metadata."""
        if not config.selected_file:
            self.status_label.setText("No file to refresh")
            return

        file_path = config.selected_file

        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", f"The file {file_path} no longer exists.")
            self.status_label.setText("File not found")
            return

        # Save cursor positions
        cursor_positions = {}
        selections = {}
        field_mappings = {
            "headline": self.metadata_panel.headline,
            "caption": self.metadata_panel.caption,
            "credit": self.metadata_panel.credit,
            "object_name": self.metadata_panel.object_name,
            "writer": self.metadata_panel.writer,
            "byline": self.metadata_panel.byline,
            "byline_title": self.metadata_panel.byline_title,
            "source": self.metadata_panel.source,
            "date": self.metadata_panel.date,
            "copyright": self.metadata_panel.copyright,
            "additional_info": self.metadata_panel.additional_info,
            "date_modified": self.metadata_panel.date_modified
        }

        for field_name, widget in field_mappings.items():
            if isinstance(widget, QLineEdit):
                cursor_positions[field_name] = widget.cursorPosition()
                selections[field_name] = (widget.selectionStart(), widget.selectionLength())
            elif isinstance(widget, QTextEdit):
                cursor = widget.textCursor()
                cursor_positions[field_name] = cursor.position()
                selections[field_name] = (cursor.selectionStart(), cursor.selectionEnd())

        self.status_label.setText("Refreshing...")
        QApplication.processEvents()

        self.metadata_manager.load_from_file(file_path)
        self.metadata_panel.update_from_manager()
        self.image_viewer.load_image(file_path)

        # Restore cursor positions
        for field_name, widget in field_mappings.items():
            if isinstance(widget, QLineEdit) and field_name in cursor_positions:
                widget.setCursorPosition(cursor_positions[field_name])
                if selections[field_name][1] > 0:
                    widget.setSelection(selections[field_name][0], selections[field_name][1])
            elif isinstance(widget, QTextEdit) and field_name in cursor_positions:
                cursor = widget.textCursor()
                cursor.setPosition(cursor_positions[field_name])
                if selections[field_name][0] != selections[field_name][1]:
                    cursor.setPosition(selections[field_name][0])
                    cursor.setPosition(selections[field_name][1], QTextCursor.MoveMode.KeepAnchor)
                widget.setTextCursor(cursor)

        self.file_label.setText(os.path.basename(file_path))
        self.path_label.setText(os.path.dirname(file_path))
        self.status_label.setText(f"Refreshed {os.path.basename(file_path)}")
        logger.info(f"Refreshed file: {file_path}")
