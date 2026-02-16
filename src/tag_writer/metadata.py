"""
Tag Writer - MetadataManager class for image metadata operations.
"""

import os
import json
import logging
from datetime import datetime

from .config import config
from .exiftool_utils import create_exiftool_instance, execute_with_timeout

logger = logging.getLogger(__name__)


class MetadataManager:
    """Manages image metadata operations using ExifTool."""

    def __init__(self):
        self.metadata = {}
        self.field_mappings = {
            'Headline': ['IPTC:Headline', 'XMP-photoshop:Headline', 'XMP:Headline', 'XMP:Title'],
            'Caption-Abstract': ['IPTC:Caption-Abstract', 'XMP:Description', 'EXIF:ImageDescription'],
            'Credit': ['IPTC:Credit', 'XMP:Credit', 'XMP-photoshop:Credit'],
            'ObjectName': ['IPTC:ObjectName', 'IPTC:Object Name', 'XMP:Title'],
            'Writer-Editor': ['IPTC:Writer-Editor', 'XMP:CaptionWriter', 'XMP-photoshop:CaptionWriter'],
            'By-line': ['IPTC:By-line', 'XMP:Creator', 'EXIF:Artist'],
            'By-lineTitle': ['IPTC:By-lineTitle', 'XMP:AuthorsPosition', 'XMP-photoshop:AuthorsPosition'],
            'Source': ['IPTC:Source', 'XMP:Source', 'XMP-photoshop:Source'],
            'DateCreated': ['IPTC:DateCreated', 'XMP:DateCreated', 'XMP-photoshop:DateCreated'],
            'DateModified': ['EXIF:ModifyDate', 'EXIF:FileModifyDate', 'XMP:ModifyDate', 'ICC_Profile:ProfileDateTime'],
            'CopyrightNotice': ['IPTC:CopyrightNotice', 'XMP:Rights', 'EXIF:Copyright'],
            'Contact': ['IPTC:Contact', 'XMP:Contact']
        }

    def load_from_file(self, file_path):
        """Load metadata from an image file."""
        if not os.path.exists(file_path):
            return False

        try:
            et_instance = create_exiftool_instance()
            with et_instance as et:
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext in ['.tif', '.tiff']:
                    metadata_json = execute_with_timeout(et.execute_json, "-j", "-m", "-ignoreMinorErrors", file_path)
                else:
                    metadata_json = execute_with_timeout(et.execute_json, "-j", file_path)

                if metadata_json and len(metadata_json) > 0:
                    raw_metadata = metadata_json[0]
                    self.metadata = self._process_metadata(raw_metadata)
                    return True
                else:
                    self.metadata = {}
                    return False

        except Exception as e:
            logger.error(f"Error loading metadata from {file_path}: {e}")
            self.metadata = {}
            return False

    def _process_metadata(self, raw_metadata):
        """Process raw metadata to standardize field names."""
        processed = {}

        for field, possible_names in self.field_mappings.items():
            if field == 'DateModified':
                found_date = None
                used_field = None

                logger.info("Raw metadata date fields:")
                for key, value in raw_metadata.items():
                    if any(date_key in key.lower() for date_key in ['date', 'time']):
                        logger.info(f"  {key}: {value}")

                priority_fields = ['EXIF:ModifyDate', 'EXIF:FileModifyDate', 'XMP:ModifyDate', 'ICC_Profile:ProfileDateTime']

                for name in priority_fields:
                    if name in raw_metadata and raw_metadata[name]:
                        found_date = raw_metadata[name]
                        used_field = name
                        logger.info(f"Found date in {name}: {found_date}")
                        break

                if found_date:
                    processed[field] = found_date
                    logger.info(f"DateModified using {used_field}: {found_date}")
                else:
                    logger.info("No date found in any of the date fields")
            else:
                for name in possible_names:
                    if name in raw_metadata:
                        processed[field] = raw_metadata[name]
                        break

        return processed

    def get_field(self, field_name, default=""):
        """Get a metadata field value."""
        return self.metadata.get(field_name, default)

    def set_field(self, field_name, value):
        """Set a metadata field value."""
        self.metadata[field_name] = value

    def get_field_names(self):
        """Get all available field names."""
        return list(self.field_mappings.keys())

    def clear(self):
        """Clear all metadata."""
        self.metadata = {}

    @staticmethod
    def _sanitize_value(value):
        """Sanitize a metadata value before writing to ExifTool."""
        if not isinstance(value, str):
            return value
        value = value.replace('\x00', '')
        value = value.replace('\r\n', '\n').replace('\r', '\n')
        value = value.strip()
        if len(value) > 2000:
            value = value[:2000]
        return value

    def save_to_file(self, file_path):
        """Save metadata to an image file."""
        if not os.path.exists(file_path):
            return False

        try:
            et_instance = create_exiftool_instance()
            with et_instance as et:
                args = []

                for field_name, value in self.metadata.items():
                    if value:
                        value = self._sanitize_value(value)
                        if not value:
                            continue
                        if field_name in self.field_mappings:
                            exiftool_tag = self.field_mappings[field_name][0]
                            args.extend([f"-{exiftool_tag}={value}"])
                        else:
                            args.extend([f"-{field_name}={value}"])

                if not args:
                    return True

                args.append("-overwrite_original")
                args.append(file_path)

                result = execute_with_timeout(et.execute, *args)

                success_patterns = [
                    "1 image files updated",
                    "1 image files created",
                    "files updated",
                    "files created"
                ]

                result_lines = result.strip().split('\n')
                success = False

                for line in result_lines:
                    line_clean = line.strip().lower()
                    if any(pattern.lower() in line_clean for pattern in success_patterns):
                        success = True
                        break

                logger.debug(f"ExifTool result: {result[:200]}...")

                return success

        except Exception as e:
            logger.error(f"Error saving metadata to {file_path}: {e}")
            return False

    def export_to_json(self, file_path):
        """Export metadata to a JSON file."""
        try:
            export_data = {
                'filename': os.path.basename(config.selected_file) if config.selected_file else 'unknown',
                'export_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'metadata': self.metadata
            }

            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=4)

            return True
        except Exception as e:
            logger.error(f"Error exporting metadata to JSON: {e}")
            return False

    def import_from_json(self, file_path):
        """Import metadata from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            if 'metadata' in data:
                imported_metadata = data['metadata']
            else:
                imported_metadata = data

            for field_name in self.get_field_names():
                if field_name in imported_metadata:
                    self.set_field(field_name, imported_metadata[field_name])

            return True
        except Exception as e:
            logger.error(f"Error importing metadata from JSON: {e}")
            return False
