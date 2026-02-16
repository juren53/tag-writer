"""
Tag Writer - ImageViewer widget for displaying images and metadata.
"""

import os
import json
import subprocess
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
    QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer

from ..config import config
from ..image_utils import load_image, create_thumbnail, pil_to_pixmap
from ..file_utils import read_metadata

logger = logging.getLogger(__name__)


class ImageViewer(QWidget):
    """Widget for displaying and interacting with images."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_image_path = None
        self.pil_image = None
        self.original_thumbnail = None
        self.setup_ui()

    def _get_image_resolution(self, image_path):
        """Get image resolution from multiple sources with fallback."""
        try:
            # Method 1: Try exiftool
            try:
                cmd = ["exiftool", "-j", "-XResolution", "-YResolution", "-ResolutionUnit", image_path]
                result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=10)

                if result.returncode == 0 and result.stdout.strip():
                    metadata_list = json.loads(result.stdout)
                    if metadata_list and isinstance(metadata_list, list) and len(metadata_list) > 0:
                        metadata = metadata_list[0]

                        x_res = metadata.get('XResolution')
                        y_res = metadata.get('YResolution')
                        res_unit = metadata.get('ResolutionUnit', '').lower()

                        if x_res and y_res:
                            unit_suffix = "DPI"
                            if 'cm' in res_unit or 'centimeter' in res_unit:
                                unit_suffix = "DPC"

                            try:
                                x_val = float(x_res)
                                y_val = float(y_res)

                                if x_val == y_val:
                                    return f"Resolution: {x_val:.0f} {unit_suffix}"
                                else:
                                    return f"Resolution: {x_val:.0f} x {y_val:.0f} {unit_suffix}"
                            except (ValueError, TypeError):
                                pass
            except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
                logger.debug(f"Exiftool resolution detection failed: {e}")

            # Method 2: Try PIL's DPI info
            if self.pil_image:
                dpi = getattr(self.pil_image, 'info', {}).get('dpi', None)
                if dpi and isinstance(dpi, (tuple, list)) and len(dpi) >= 2:
                    x_dpi, y_dpi = dpi[0], dpi[1]
                    if x_dpi and y_dpi and x_dpi > 0 and y_dpi > 0:
                        if x_dpi == y_dpi:
                            return f"Resolution: {x_dpi:.0f} DPI"
                        else:
                            return f"Resolution: {x_dpi:.0f} x {y_dpi:.0f} DPI"

            # Method 3: Try PIL's getexif()
            if self.pil_image and hasattr(self.pil_image, 'getexif'):
                try:
                    exif = self.pil_image.getexif()
                    if exif:
                        x_res = exif.get(282)
                        y_res = exif.get(283)
                        res_unit = exif.get(296, 2)

                        if x_res and y_res:
                            unit_suffix = "DPI" if res_unit == 2 else "DPC"

                            if isinstance(x_res, tuple) and len(x_res) == 2:
                                x_val = x_res[0] / x_res[1] if x_res[1] != 0 else x_res[0]
                            else:
                                x_val = float(x_res)

                            if isinstance(y_res, tuple) and len(y_res) == 2:
                                y_val = y_res[0] / y_res[1] if y_res[1] != 0 else y_res[0]
                            else:
                                y_val = float(y_res)

                            if x_val > 0 and y_val > 0:
                                if x_val == y_val:
                                    return f"Resolution: {x_val:.0f} {unit_suffix}"
                                else:
                                    return f"Resolution: {x_val:.0f} x {y_val:.0f} {unit_suffix}"
                except Exception as e:
                    logger.debug(f"PIL EXIF resolution detection failed: {e}")

            return "Resolution: --"

        except Exception as e:
            logger.debug(f"Resolution detection error: {e}")
            return "Resolution: --"

    def extract_photometric_interpretation_bits_per_sample(self, image_path):
        """Extract photometric interpretation and bits per sample data."""
        try:
            metadata = read_metadata(image_path)
            if not metadata:
                return '--', '--'

            relevant_keys = [key for key in metadata.keys() if 'photometric' in key.lower()]
            logger.info(f"Photometric related metadata keys found: {relevant_keys}")

            photometric_raw = metadata.get('EXIF:PhotometricInterpretation', '--')
            logger.info(f"Found raw photometric interpretation value: {photometric_raw}")

            photometric_interpretation = self._convert_photometric_interpretation(photometric_raw)

            bits_per_sample = '--'
            for field in ['File:BitsPerSample', 'BitsPerSample', 'EXIF:BitsPerSample', 'Bits Per Sample']:
                if field in metadata and metadata[field]:
                    bits_per_sample = str(metadata[field])
                    break

            return photometric_interpretation, bits_per_sample

        except Exception as e:
            logger.debug(f"Photometric Interpretation/bits per sample extraction error: {e}")
            return '--', '--'

    def _convert_photometric_interpretation(self, raw_value):
        """Convert numeric photometric interpretation values to descriptive text."""
        if raw_value == '--' or raw_value is None:
            return '--'

        photometric_map = {
            '0': 'WhiteIsZero',
            '1': 'BlackIsZero',
            '2': 'RGB',
            '3': 'Palette',
            '4': 'Transparency Mask',
            '5': 'CMYK',
            '6': 'YCbCr',
            '8': 'CIELab',
            '9': 'ICCLab',
            '10': 'ITULab'
        }

        str_value = str(raw_value).strip()
        return photometric_map.get(str_value, str_value)

    def extract_date_metadata(self, image_path):
        """Extract date-related metadata for display."""
        try:
            import datetime

            dates = {
                'date_created': {'value': '--', 'source': '--'},
                'date_modified': {'value': '--', 'source': '--'},
                'file_creation_date': {'value': '--', 'source': 'File System'},
                'file_modification_date': {'value': '--', 'source': 'File System'}
            }

            metadata = read_metadata(image_path)
            if metadata:
                date_created_fields = [
                    'IPTC:DateCreated', 'XMP:DateCreated', 'XMP-photoshop:DateCreated',
                    'EXIF:DateTimeOriginal', 'EXIF:CreateDate'
                ]
                date_modified_fields = [
                    'EXIF:ModifyDate', 'EXIF:FileModifyDate', 'XMP:ModifyDate',
                    'ICC_Profile:ProfileDateTime'
                ]
                time_created_fields = [
                    'IPTC:TimeCreated', 'XMP:TimeCreated', 'EXIF:TimeOriginal'
                ]

                for field in date_created_fields:
                    if field in metadata and metadata[field]:
                        date_value = self._format_date_value(metadata[field])

                        if len(date_value.replace('-', ':').split(':')) <= 3:
                            for time_field in time_created_fields:
                                if time_field in metadata and metadata[time_field]:
                                    time_value = str(metadata[time_field]).strip()
                                    date_value = f"{date_value} {time_value}"
                                    break

                        dates['date_created'] = {
                            'value': date_value,
                            'source': field
                        }
                        break

                for field in date_modified_fields:
                    if field in metadata and metadata[field]:
                        dates['date_modified'] = {
                            'value': self._format_date_value(metadata[field]),
                            'source': field
                        }
                        break

            if os.path.exists(image_path):
                try:
                    stat = os.stat(image_path)

                    creation_time = datetime.datetime.fromtimestamp(stat.st_ctime)
                    modification_time = datetime.datetime.fromtimestamp(stat.st_mtime)

                    dates['file_creation_date'] = {
                        'value': creation_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'source': 'File System'
                    }
                    dates['file_modification_date'] = {
                        'value': modification_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'source': 'File System'
                    }

                except Exception as e:
                    logger.debug(f"Error getting system file dates: {e}")

            return dates

        except Exception as e:
            logger.debug(f"Date metadata extraction error: {e}")
            return {
                'date_created': {'value': '--', 'source': '--'},
                'date_modified': {'value': '--', 'source': '--'},
                'file_creation_date': {'value': '--', 'source': 'File System'},
                'file_modification_date': {'value': '--', 'source': 'File System'}
            }

    def _format_date_value(self, date_str):
        """Format date string to YYYY-MM-DD HH:MM:SS format."""
        if date_str == '--' or not date_str:
            return '--'

        cleaned_date = str(date_str).strip()

        if ':' in cleaned_date:
            parts = cleaned_date.split(' ')
            if len(parts) > 0:
                date_part = parts[0].replace(':', '-', 2)
                if len(parts) > 1:
                    return f"{date_part} {' '.join(parts[1:])}"
                else:
                    return date_part

        return cleaned_date

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(200, 200)
        self.image_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.image_label.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.image_label)

        self.view_button = QPushButton("View Full Image")
        self.view_button.clicked.connect(self.on_view_full_image)
        layout.addWidget(self.view_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.filename_label = QLabel("File: --")
        self.filename_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.filename_label)

        # Hidden labels for data storage
        self.dimensions_label = QLabel("Dimensions: --")
        self.file_size_label = QLabel("File size: --")
        self.resolution_label = QLabel("Resolution: --")
        self.pixel_count_label = QLabel("Pixel count: --")

        # Scrollable metadata table
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        table_html = self._build_table_html()
        self.table_label = QLabel(table_html)
        self.table_label.setWordWrap(True)

        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(5, 5, 5, 5)
        table_layout.addWidget(self.table_label)
        table_layout.addStretch()

        scroll.setWidget(table_widget)
        layout.addWidget(scroll, 1)

    def _build_table_html(self, date_data=None):
        """Build the HTML table for metadata display."""
        dim = self.dimensions_label.text().split(': ', 1)[1] if ': ' in self.dimensions_label.text() else '--'
        fsize = self.file_size_label.text().split(': ', 1)[1] if ': ' in self.file_size_label.text() else '--'
        res = self.resolution_label.text().split(': ', 1)[1] if ': ' in self.resolution_label.text() else '--'
        pxc = self.pixel_count_label.text().split(': ', 1)[1] if ': ' in self.pixel_count_label.text() else '--'

        if date_data is None:
            date_data = {
                'date_created': {'value': '--', 'source': '--'},
                'date_modified': {'value': '--', 'source': '--'},
                'file_creation_date': {'value': '--', 'source': 'File System'},
                'file_modification_date': {'value': '--', 'source': 'File System'}
            }

        return f"""
        <table style='width:100%; text-align:left; margin-left:10px; margin-right:10px; border-spacing:5px 3px;'>
            <tr>
                <td style='font-weight:bold; padding-right:10px;'>File size:</td>
                <td colspan='2'>{fsize}</td>
            </tr>
            <tr>
                <td style='font-weight:bold; padding-right:10px;'>Dimension:</td>
                <td colspan='2'>{dim}</td>
            </tr>
            <tr>
                <td style='font-weight:bold; padding-right:10px;'>Resolution:</td>
                <td colspan='2'>{res}</td>
            </tr>
            <tr>
                <td style='font-weight:bold; padding-right:10px;'>Pixel count:</td>
                <td colspan='2'>{pxc}</td>
            </tr>
            <tr>
                <td colspan='3' style='height:8px;'></td>
            </tr>
            <tr>
                <td style='font-weight:bold; padding-right:10px;'>Date Created:</td>
                <td style='padding-right:10px;'>{date_data['date_created']['value']}</td>
                <td style='font-style:italic; color:#666;'>{date_data['date_created']['source']}</td>
            </tr>
            <tr>
                <td style='font-weight:bold; padding-right:10px;'>Date Modified:</td>
                <td style='padding-right:10px;'>{date_data['date_modified']['value']}</td>
                <td style='font-style:italic; color:#666;'>{date_data['date_modified']['source']}</td>
            </tr>
            <tr>
                <td style='font-weight:bold; padding-right:10px;'>File Creation:</td>
                <td style='padding-right:10px;'>{date_data['file_creation_date']['value']}</td>
                <td style='font-style:italic; color:#666;'>{date_data['file_creation_date']['source']}</td>
            </tr>
            <tr>
                <td style='font-weight:bold; padding-right:10px;'>File Modified:</td>
                <td style='padding-right:10px;'>{date_data['file_modification_date']['value']}</td>
                <td style='font-style:italic; color:#666;'>{date_data['file_modification_date']['source']}</td>
            </tr>
        </table>
        """

    def load_image(self, image_path):
        """Load and display an image."""
        if not os.path.exists(image_path):
            logger.error(f"File not found: {image_path}")
            return False

        try:
            self.pil_image = load_image(image_path)
            if self.pil_image is None:
                logger.error(f"Failed to load image: {image_path}")
                return False

            self.original_thumbnail = create_thumbnail(self.pil_image, (800, 800))
            if self.original_thumbnail is None:
                logger.error(f"Failed to create thumbnail for: {image_path}")
                return False

            self.update_thumbnail()

            filename = os.path.basename(image_path)
            self.filename_label.setText(f"File: {filename}")

            width, height = self.pil_image.size
            self.dimensions_label.setText(f"Dimensions: {width} x {height} pixels")

            file_size_bytes = os.path.getsize(image_path)
            if file_size_bytes < 1024:
                file_size_str = f"{file_size_bytes} bytes"
            elif file_size_bytes < 1024 * 1024:
                file_size_str = f"{file_size_bytes / 1024:.1f} KB"
            else:
                file_size_str = f"{file_size_bytes / (1024 * 1024):.1f} MB"
            self.file_size_label.setText(f"File size: {file_size_str}")

            try:
                resolution_text = self._get_image_resolution(image_path)
                self.resolution_label.setText(resolution_text)
            except Exception as e:
                logger.debug(f"Error getting resolution: {e}")
                self.resolution_label.setText("Resolution: --")

            pixel_count = width * height
            if pixel_count >= 1_000_000:
                megapixels = pixel_count / 1_000_000
                self.pixel_count_label.setText(f"Pixel count: {megapixels:.1f} MP")
            else:
                formatted_count = f"{pixel_count:,}"
                self.pixel_count_label.setText(f"Pixel count: {formatted_count} pixels")

            date_data = self.extract_date_metadata(image_path)
            self.table_label.setText(self._build_table_html(date_data))

            self.current_image_path = image_path
            return True
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return False

    def update_thumbnail(self):
        """Update the thumbnail to fit the current view size."""
        if self.original_thumbnail is None:
            return

        try:
            available_width = self.image_label.width()
            available_height = self.image_label.height()

            if available_width < 50 or available_height < 50:
                available_width = max(available_width, 200)
                available_height = max(available_height, 200)

            thumbnail = create_thumbnail(self.original_thumbnail, (available_width, available_height))
            if thumbnail is None:
                return

            pixmap = pil_to_pixmap(thumbnail)
            if pixmap is None:
                return

            self.image_label.setPixmap(pixmap)

        except Exception as e:
            logger.error(f"Error updating thumbnail: {e}")

    def resizeEvent(self, event):
        """Handle resize events to update the thumbnail."""
        super().resizeEvent(event)
        if self.original_thumbnail:
            QTimer.singleShot(100, self.update_thumbnail)

    def clear(self):
        """Clear the image display."""
        self.image_label.clear()
        self.image_label.setText("No image loaded")
        self.filename_label.setText("File: --")
        self.dimensions_label.setText("Dimensions: --")
        self.file_size_label.setText("File size: --")
        self.resolution_label.setText("Resolution: --")
        self.pixel_count_label.setText("Pixel count: --")

        table_html = """
        <table style='width:100%; text-align:left; margin-left:20px; border-spacing:15px 5px;'>
            <tr>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>File size:</td>
                <td style='min-width:120px; padding-right:30px;'>--</td>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Dimension:</td>
                <td style='min-width:120px;'>--</td>
            </tr>
            <tr>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Resolution:</td>
                <td style='min-width:120px; padding-right:30px;'>--</td>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Pixel count:</td>
                <td style='min-width:120px;'>--</td>
            </tr>
            <tr>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Photometric Interpretation:</td>
                <td style='min-width:120px; padding-right:30px;'>--</td>
                <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Bits Per Sample:</td>
                <td style='min-width:120px;'>--</td>
            </tr>
        </table>
        """
        self.table_label.setText(table_html)

        self.current_image_path = None
        self.pil_image = None
        self.original_thumbnail = None

    def show_context_menu(self, position):
        """Show context menu for the image thumbnail."""
        if not self.current_image_path:
            return

        main_window = None
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'on_open_in_default_editor'):
                main_window = parent
                break
            parent = parent.parent()

        if main_window is None:
            return

        menu = QMenu(self)

        view_action = menu.addAction("View Full Image")
        view_action.triggered.connect(self.on_view_full_image)

        edit_action = menu.addAction("Open in Default Editor (Ctrl+Shift+E)")
        edit_action.triggered.connect(main_window.on_open_in_default_editor)

        copy_path_action = menu.addAction("Copy Path to Clipboard")
        copy_path_action.triggered.connect(lambda: main_window.on_copy_path_to_clipboard())

        menu.exec(self.image_label.mapToGlobal(position))

    def on_view_full_image(self):
        """Handle View Full Image button click."""
        if not self.current_image_path or not self.pil_image:
            QMessageBox.warning(self, "No Image", "No image is currently loaded.")
            return

        from .full_image_viewer import FullImageViewer

        main_window = self
        while main_window.parent() is not None:
            main_window = main_window.parent()

        viewer = FullImageViewer(main_window, self.current_image_path, self.pil_image)
        viewer.show()
