"""
Tag Writer - ThemeMixin: apply_theme, zoom_ui, dark mode toggle.
"""

import logging

from PyQt6.QtWidgets import QApplication, QDialog, QWidget
from PyQt6.QtCore import Qt

from .config import config
from .theme import DEFAULT_THEME, is_dark_theme, get_fusion_palette
from .dialogs.theme_dialog import ThemeDialog

logger = logging.getLogger(__name__)


class ThemeMixin:
    """Mixin providing theme application, UI zoom, and dark mode toggle."""

    def apply_theme(self):
        """Apply the current theme palette to the application."""
        QApplication.instance().setPalette(get_fusion_palette(self.current_theme))
        self.status_label.setText(f"Applied {self.current_theme} theme")
        logger.info(f"Applied theme: {self.current_theme}")

    def on_select_theme(self):
        """Handle theme selection from menu."""
        dialog = ThemeDialog(self.current_theme, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected = dialog.get_selected_theme()
            if selected != self.current_theme:
                self.current_theme = selected
                self.apply_theme()
                self.dark_mode = is_dark_theme(self.current_theme)
                self.dark_mode_action.setChecked(self.dark_mode)
                config.current_theme = self.current_theme
                config.dark_mode = self.dark_mode
                config.save_config()
                self.status_label.setText(f"Theme changed to {self.current_theme}")
                logger.info(f"Theme changed to {self.current_theme}")

    def on_toggle_dark_mode(self):
        """Quick toggle between light (Default Light) and dark themes."""
        self.current_theme = DEFAULT_THEME if is_dark_theme(self.current_theme) else "dark"
        self.apply_theme()
        self.dark_mode = is_dark_theme(self.current_theme)
        self.dark_mode_action.setChecked(self.dark_mode)
        config.current_theme = self.current_theme
        config.dark_mode = self.dark_mode
        config.save_config()

    # ── UI Zoom ───────────────────────────────────────────────────────────

    def zoom_ui(self, zoom_delta):
        """Change the UI zoom level by the specified delta."""
        new_zoom = self.ui_scale_factor + zoom_delta
        new_zoom = round(new_zoom, 1)

        logger.debug(f"zoom_ui called - current={self.ui_scale_factor}, delta={zoom_delta}, new={new_zoom}")

        if 0.5 <= new_zoom <= 1.5:
            self.ui_scale_factor = new_zoom
            self.apply_ui_zoom()
            self.zoom_label.setText(f"UI Zoom: {int(self.ui_scale_factor * 100)}%")
            config.ui_zoom_factor = self.ui_scale_factor
            config.save_config()
            self.status_label.setText(f"UI Zoom: {int(self.ui_scale_factor * 100)}%")
        else:
            if new_zoom > 1.5:
                self.status_label.setText("Maximum zoom reached (150%)")
            elif new_zoom < 0.5:
                self.status_label.setText("Minimum zoom reached (50%)")

    def reset_zoom(self):
        """Reset UI zoom to 100%."""
        self.ui_scale_factor = 1.0
        self.apply_ui_zoom()
        self.zoom_label.setText("UI Zoom: 100%")
        config.ui_zoom_factor = self.ui_scale_factor
        config.save_config()

    def apply_ui_zoom(self):
        """Apply the current zoom factor to all UI elements."""
        base_font_size = 9
        scaled_font_size = base_font_size * self.ui_scale_factor

        app_font = QApplication.instance().font()
        app_font.setPointSizeF(scaled_font_size)
        QApplication.instance().setFont(app_font)

        self._apply_font_to_widgets(self, scaled_font_size)

        scaled_css = f"""
        QWidget {{
            font-size: {scaled_font_size}pt;
        }}
        QPushButton {{
            font-size: {scaled_font_size}pt;
            padding: {int(6 * self.ui_scale_factor)}px {int(12 * self.ui_scale_factor)}px;
            min-width: {int(80 * self.ui_scale_factor)}px;
        }}
        QLabel {{
            font-size: {scaled_font_size}pt;
        }}
        QLineEdit {{
            font-size: {scaled_font_size}pt;
            padding: {int(4 * self.ui_scale_factor)}px;
        }}
        QTextEdit {{
            font-size: {scaled_font_size}pt;
        }}
        QComboBox {{
            font-size: {scaled_font_size}pt;
            padding: {int(4 * self.ui_scale_factor)}px {int(8 * self.ui_scale_factor)}px;
            min-width: {int(100 * self.ui_scale_factor)}px;
        }}
        QMenuBar {{
            font-size: {scaled_font_size}pt;
            padding: {int(4 * self.ui_scale_factor)}px {int(8 * self.ui_scale_factor)}px;
        }}
        QMenu {{
            font-size: {scaled_font_size}pt;
            padding: {int(6 * self.ui_scale_factor)}px {int(12 * self.ui_scale_factor)}px;
        }}
        QStatusBar {{
            font-size: {scaled_font_size}pt;
        }}
        QToolBar {{
            spacing: {int(2 * self.ui_scale_factor)}px;
        }}
        """

        current_stylesheet = QApplication.instance().styleSheet()
        if '/* ZOOM_STYLES_START */' in current_stylesheet:
            current_stylesheet = current_stylesheet.split('/* ZOOM_STYLES_START */')[0]

        enhanced_stylesheet = current_stylesheet + '\n/* ZOOM_STYLES_START */\n' + scaled_css + '\n/* ZOOM_STYLES_END */'
        QApplication.instance().setStyleSheet(enhanced_stylesheet)

        logger.info(f"Set UI zoom to {int(self.ui_scale_factor * 100)}% with font size {scaled_font_size:.1f}pt")

    def _apply_font_to_widgets(self, widget, font_size):
        """Recursively apply font size to all widgets."""
        try:
            font = widget.font()
            font.setPointSizeF(font_size)
            widget.setFont(font)

            for child in widget.findChildren(QWidget):
                if child.parent() == widget:
                    child_font = child.font()
                    child_font.setPointSizeF(font_size)
                    child.setFont(child_font)
        except Exception as e:
            logger.debug(f"Could not apply font to widget {type(widget)}: {e}")
