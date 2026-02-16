"""
Tag Writer - MetadataPanel widget for editing image metadata.
"""

import logging
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFormLayout, QScrollArea, QFrame,
    QMainWindow, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt

from ..config import config

logger = logging.getLogger(__name__)


class MetadataPanel(QWidget):
    """Panel for displaying and editing image metadata."""

    def __init__(self, metadata_manager, parent=None):
        super().__init__(parent)
        self.metadata_manager = metadata_manager
        self.text_fields = []
        self.setup_ui()
        self.install_event_filters()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(10)

        # Headline
        self.headline = QLineEdit()
        self.text_fields.append(self.headline)
        headline_label = QLabel("Headline:")
        headline_label.setToolTip("Title")
        headline_label.setToolTipDuration(10000)
        headline_label.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
        headline_label.setMouseTracking(True)
        form.addRow(headline_label, self.headline)

        # Caption/Abstract with character count
        caption_container = QWidget()
        caption_layout = QVBoxLayout(caption_container)
        caption_layout.setContentsMargins(0, 0, 0, 0)
        caption_layout.setSpacing(2)

        self.caption = QTextEdit()
        self.caption.setMinimumHeight(80)
        self.caption.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        caption_layout.addWidget(self.caption)

        self.char_count_label = QLabel("0/1000 characters")
        self.char_count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.char_count_label.setStyleSheet("font-size: 8pt;")
        caption_layout.addWidget(self.char_count_label)

        self.caption.textChanged.connect(self.update_char_count)

        caption_label = QLabel("Caption/Abstract:")
        caption_label.setToolTip("Description")
        caption_label.setToolTipDuration(10000)
        caption_label.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
        caption_label.setMouseTracking(True)
        form.addRow(caption_label, caption_container)

        self.credit = QLineEdit()
        form.addRow("Credit:", self.credit)

        self.object_name = QLineEdit()
        object_name_label = QLabel("Object Name:")
        object_name_label.setToolTip("Unique Identifier / Accession Number")
        object_name_label.setToolTipDuration(10000)
        object_name_label.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
        object_name_label.setMouseTracking(True)
        form.addRow(object_name_label, self.object_name)

        self.byline = QLineEdit()
        byline_label = QLabel("By-line:")
        byline_label.setToolTip("Photographer")
        byline_label.setToolTipDuration(10000)
        byline_label.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
        byline_label.setMouseTracking(True)
        form.addRow(byline_label, self.byline)

        self.byline_title = QLineEdit()
        byline_title_label = QLabel("By-line Title:")
        byline_title_label.setToolTip("Photographer's organization")
        byline_title_label.setToolTipDuration(10000)
        byline_title_label.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
        byline_title_label.setMouseTracking(True)
        form.addRow(byline_title_label, self.byline_title)

        # Date Created and Source on same line
        date_source_container = QWidget()
        date_source_layout = QHBoxLayout(date_source_container)
        date_source_layout.setContentsMargins(0, 0, 0, 0)
        date_source_layout.setSpacing(10)

        date_label = QLabel("Date Created:")
        date_label.setMinimumWidth(90)
        self.date = QLineEdit()
        self.date.setMaximumWidth(120)
        date_source_layout.addWidget(date_label)
        date_source_layout.addWidget(self.date)

        source_label = QLabel("Source:")
        source_label.setMinimumWidth(50)
        self.source = QLineEdit()
        date_source_layout.addWidget(source_label)
        date_source_layout.addWidget(self.source)

        form.addRow(date_source_container)

        self.copyright = QLineEdit()
        form.addRow("Copyright Notice:", self.copyright)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #888888; margin: 5px 0px;")
        form.addRow(separator)

        self.additional_info = QLineEdit()
        form.addRow("Additional Info:", self.additional_info)

        # Date Modified and Writer/Editor on same line
        date_writer_container = QWidget()
        date_writer_layout = QHBoxLayout(date_writer_container)
        date_writer_layout.setContentsMargins(0, 0, 0, 0)
        date_writer_layout.setSpacing(10)

        date_mod_label = QLabel("Date Modified:")
        date_mod_label.setMinimumWidth(90)
        self.date_modified = QLineEdit()
        self.date_modified.setMaximumWidth(120)
        date_writer_layout.addWidget(date_mod_label)
        date_writer_layout.addWidget(self.date_modified)

        writer_label = QLabel("Writer/Editor:")
        writer_label.setMinimumWidth(90)
        self.writer = QLineEdit()
        date_writer_layout.addWidget(writer_label)
        date_writer_layout.addWidget(self.writer)

        form.addRow(date_writer_container)

        # Add all text fields to tracking list
        self.text_fields.extend([
            self.credit, self.object_name, self.writer,
            self.byline, self.byline_title, self.source,
            self.date, self.copyright, self.additional_info, self.date_modified
        ])
        self.text_fields.append(self.caption)

        # Wrap form in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_widget = QWidget()
        form_widget.setLayout(form)
        scroll.setWidget(form_widget)

        layout.addWidget(scroll, 1)

        # Write metadata button
        self.write_button = QPushButton("Write Metadata")
        self.write_button.clicked.connect(self.on_write_metadata)
        layout.addWidget(self.write_button, alignment=Qt.AlignmentFlag.AlignHCenter)

    def install_event_filters(self):
        """Install event filters on all text fields to properly handle keyboard focus."""
        for text_field in self.text_fields:
            text_field.installEventFilter(self)

    def eventFilter(self, watched, event):
        """Handle keyboard events in text fields to prevent arrow key propagation to main window."""
        if event.type() == event.Type.KeyPress and watched in self.text_fields:
            if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                event.accept()
                watched.event(event)
                return True

        return super().eventFilter(watched, event)

    def update_from_manager(self):
        """Update UI fields from metadata manager."""
        field_mappings = {
            "Headline": self.headline,
            "Caption-Abstract": self.caption,
            "Credit": self.credit,
            "ObjectName": self.object_name,
            "Writer-Editor": self.writer,
            "By-line": self.byline,
            "By-lineTitle": self.byline_title,
            "Source": self.source,
            "DateCreated": self.date,
            "DateModified": self.date_modified,
            "Copyright Notice": self.copyright,
            "Contact": self.additional_info
        }

        # Special handling for copyright notice
        copyright_value = self.metadata_manager.get_field("Copyright Notice", "")
        if not copyright_value:
            copyright_value = self.metadata_manager.get_field("CopyrightNotice", "")
        if not copyright_value:
            copyright_value = self.metadata_manager.get_field("Copyright", "")

        self.copyright.setText(copyright_value)
        print(f"Setting Copyright Notice field to: {copyright_value}")

        for field_name, control in field_mappings.items():
            if field_name != "Copyright Notice":
                value = self.metadata_manager.get_field(field_name, "")
                if isinstance(control, QTextEdit):
                    control.setPlainText(str(value))
                else:
                    control.setText(str(value))

        logger.info("Updated UI from metadata manager")

    def update_manager_from_ui(self):
        """Update metadata manager from UI fields."""
        field_mappings = {
            "Headline": self.headline.text(),
            "Caption-Abstract": self.caption.toPlainText(),
            "Credit": self.credit.text(),
            "ObjectName": self.object_name.text(),
            "Writer-Editor": self.writer.text(),
            "By-line": self.byline.text(),
            "By-lineTitle": self.byline_title.text(),
            "Source": self.source.text(),
            "DateCreated": self.date.text(),
            "DateModified": self.date_modified.text(),
            "CopyrightNotice": self.copyright.text(),
            "Contact": self.additional_info.text()
        }

        for field_name, value in field_mappings.items():
            if value:
                self.metadata_manager.set_field(field_name, value)

        logger.info("Updated metadata manager from UI")

    def update_char_count(self):
        """Update the character count label for the caption field."""
        text = self.caption.toPlainText()
        count = len(text)

        self.char_count_label.setText(f"{count} characters")

        if count > 1000:
            self.char_count_label.setStyleSheet("font-size: 8pt; color: red;")
            self.caption.blockSignals(True)
            self.caption.setPlainText(text[:1000])
            self.caption.blockSignals(False)
            self.char_count_label.setText("1000 characters")
        elif count > 256:
            self.char_count_label.setStyleSheet("font-size: 8pt; color: #FF9900;")
        else:
            self.char_count_label.setStyleSheet("font-size: 8pt;")

    def clear_fields(self):
        """Clear all metadata fields."""
        self.headline.clear()
        self.caption.clear()
        self.credit.clear()
        self.object_name.clear()
        self.writer.clear()
        self.byline.clear()
        self.byline_title.clear()
        self.source.clear()
        self.date.clear()
        self.copyright.clear()
        self.additional_info.clear()
        self.date_modified.clear()
        self.update_char_count()

    def set_today_date(self):
        """Set the date modified field to today's date."""
        today = datetime.now().strftime("%Y:%m:%d")
        self.date_modified.setText(today)
        logger.info(f"Set date modified field to today: {today}")

    def on_write_metadata(self):
        """Handle Write Metadata button click."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return

        try:
            self.update_manager_from_ui()

            if self.metadata_manager.save_to_file(config.selected_file):
                parent = self.parent()
                while parent is not None and not isinstance(parent, QMainWindow):
                    parent = parent.parent()

                if parent and hasattr(parent, 'status_label'):
                    parent.status_label.setText("Metadata saved")

                logger.info(f"Metadata saved to {config.selected_file}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save metadata")
                logger.error(f"Error saving metadata to {config.selected_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving metadata: {str(e)}")
            logger.error(f"Exception saving metadata: {e}")
