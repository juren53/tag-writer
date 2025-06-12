#!/usr/bin/python3
"""
Metadata panel module for tag-writer application.

This module provides the UI components for displaying and editing
image metadata fields.
"""

import os
import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, 
    QTextEdit, QScrollArea, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

from tag_writer.utils.config import config

# Configure logging
logger = logging.getLogger(__name__)

class MetadataPanel(QWidget):
    """
    Panel for displaying and editing image metadata.
    
    This class provides a form interface for editing various
    metadata fields like headline, caption, credit, etc.
    """
    
    def __init__(self, metadata_manager, parent=None):
        """
        Initialize the metadata panel.
        
        Args:
            metadata_manager: Instance of MetadataManager to handle metadata
            parent: Parent widget (default: None)
        """
        super().__init__(parent)
        self.metadata_manager = metadata_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Form layout for metadata fields
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(10)
        
        # Create metadata fields with mapping to model fields
        self.headline = QLineEdit()
        form.addRow("Headline:", self.headline)
        
        # Caption/Abstract with character count
        caption_container = QWidget()
        caption_layout = QVBoxLayout(caption_container)
        caption_layout.setContentsMargins(0, 0, 0, 0)
        caption_layout.setSpacing(2)
        
        self.caption = QTextEdit()
        self.caption.setMaximumHeight(100)
        caption_layout.addWidget(self.caption)
        
        # Character count label
        self.char_count_label = QLabel("0/1000 characters")
        self.char_count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.char_count_label.setStyleSheet("font-size: 8pt;")
        caption_layout.addWidget(self.char_count_label)
        
        # Connect text changed signal to update character count
        self.caption.textChanged.connect(self.update_char_count)
        
        form.addRow("Caption/Abstract:", caption_container)
        
        self.credit = QLineEdit()
        form.addRow("Credit:", self.credit)
        
        self.object_name = QLineEdit()
        form.addRow("Object Name:", self.object_name)
        
        self.writer = QLineEdit()
        form.addRow("Writer/Editor:", self.writer)
        
        self.byline = QLineEdit()
        form.addRow("By-line:", self.byline)
        
        self.byline_title = QLineEdit()
        form.addRow("By-line Title:", self.byline_title)
        
        self.source = QLineEdit()
        form.addRow("Source:", self.source)
        
        self.date = QLineEdit()
        form.addRow("Date Created:", self.date)
        
        self.copyright = QLineEdit()
        form.addRow("Copyright Notice:", self.copyright)
        
        # Wrap form in a scroll area for better handling of different screen sizes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_widget = QWidget()
        form_widget.setLayout(form)
        scroll.setWidget(form_widget)
        
        # Add scroll area to main layout
        layout.addWidget(scroll)
        
        # Write metadata button
        self.write_button = QPushButton("Write Metadata")
        self.write_button.clicked.connect(self.on_write_metadata)
        layout.addWidget(self.write_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        
    def update_from_manager(self):
        """Update UI fields from metadata manager."""
        # Map field names to UI controls
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
            "Copyright": self.copyright
        }
        
        # Update each field
        for field_name, control in field_mappings.items():
            value = self.metadata_manager.get_field(field_name, "")
            if isinstance(control, QTextEdit):
                control.setPlainText(str(value))
            else:
                control.setText(str(value))
        
        logger.info("Updated UI from metadata manager")
    
    def update_manager_from_ui(self):
        """Update metadata manager from UI fields."""
        # Map UI controls to field names
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
            "Copyright": self.copyright.text()
        }
        
        # Update metadata manager
        for field_name, value in field_mappings.items():
            if value:  # Only set non-empty values
                self.metadata_manager.set_field(field_name, value)
        
        logger.info("Updated metadata manager from UI")
    
    def update_char_count(self):
        """Update the character count label for the caption field."""
        text = self.caption.toPlainText()
        count = len(text)
        
        # Update the label
        self.char_count_label.setText(f"{count}/1000 characters")
        
        # Apply visual feedback based on count
        if count > 1000:
            # Red for exceeding limit
            self.char_count_label.setStyleSheet("font-size: 8pt; color: red;")
            
            # Truncate text if over limit
            self.caption.blockSignals(True)  # Prevent recursive signal calls
            self.caption.setPlainText(text[:1000])
            self.caption.blockSignals(False)
            
            # Update count after truncation
            self.char_count_label.setText("1000/1000 characters")
        elif count > 256:
            # Yellow for approaching limit
            self.char_count_label.setStyleSheet("font-size: 8pt; color: #FF9900;")  # Orange-yellow
        else:
            # Normal color
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
        
        # Reset character count
        self.update_char_count()
        
    def set_today_date(self):
        """Set the date field to today's date."""
        today = datetime.now().strftime("%Y:%m:%d")
        self.date.setText(today)
        logger.info(f"Set date field to today: {today}")
    
    def on_write_metadata(self):
        """Handle Write Metadata button click."""
        if not config.selected_file:
            QMessageBox.warning(self, "No File Selected", "Please select an image file first.")
            return
        
        # Show a progress dialog
        from PyQt6.QtWidgets import QApplication
        
        progress_dialog = QMessageBox(QMessageBox.Icon.Information, "Writing Metadata",
                                     f"Writing metadata to {os.path.basename(config.selected_file)}...",
                                     QMessageBox.StandardButton.Ok, self)
        progress_dialog.button(QMessageBox.StandardButton.Ok).setEnabled(False)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            # Update metadata manager from UI
            self.update_manager_from_ui()
            
            # Save to file
            if self.metadata_manager.save_to_file(config.selected_file):
                progress_dialog.button(QMessageBox.StandardButton.Ok).setEnabled(True)
                progress_dialog.setText("Metadata saved successfully!")
                logger.info(f"Metadata saved to {config.selected_file}")
            else:
                progress_dialog.button(QMessageBox.StandardButton.Ok).setEnabled(True)
                progress_dialog.setIcon(QMessageBox.Icon.Critical)
                progress_dialog.setText("Error saving metadata")
                logger.error(f"Error saving metadata to {config.selected_file}")
        except Exception as e:
            progress_dialog.button(QMessageBox.StandardButton.Ok).setEnabled(True)
            progress_dialog.setIcon(QMessageBox.Icon.Critical)
            progress_dialog.setText(f"Error saving metadata: {str(e)}")
            logger.error(f"Exception saving metadata: {e}")

