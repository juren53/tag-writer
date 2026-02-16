"""
Tag Writer - MenuMixin: create_menu_bar() and create_toolbar().
"""

from PyQt6.QtWidgets import QPushButton, QLabel, QToolBar
from PyQt6.QtGui import QAction, QFont


class MenuMixin:
    """Mixin providing menu bar and toolbar creation."""

    def create_menu_bar(self):
        """Create the application menu bar."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.on_open)
        file_menu.addAction(open_action)

        self.recent_menu = file_menu.addMenu("Recent Files")
        self.update_recent_menu()

        self.recent_directories_menu = file_menu.addMenu("Recent Directories")
        self.update_recent_directories_menu()

        file_menu.addSeparator()

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.on_save)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")

        clear_action = QAction("&Clear Fields", self)
        clear_action.setShortcut("Ctrl+L")
        clear_action.triggered.connect(self.on_clear)
        edit_menu.addAction(clear_action)

        edit_menu.addSeparator()

        export_action = QAction("&Export to JSON...", self)
        export_action.triggered.connect(self.on_export)
        edit_menu.addAction(export_action)

        import_action = QAction("&Import from JSON...", self)
        import_action.triggered.connect(self.on_import)
        edit_menu.addAction(import_action)

        edit_menu.addSeparator()

        date_action = QAction("Set &Today's Date", self)
        date_action.triggered.connect(self.on_set_today_date)
        edit_menu.addAction(date_action)

        edit_menu.addSeparator()

        rename_action = QAction("&Rename File", self)
        rename_action.triggered.connect(self.on_rename_file)
        edit_menu.addAction(rename_action)

        copy_path_action = QAction("Copy F&QFN to Clipboard", self)
        copy_path_action.triggered.connect(self.on_copy_path_to_clipboard)
        copy_path_action.setToolTip("Copy the Fully Qualified File Name to the clipboard")
        edit_menu.addAction(copy_path_action)

        open_editor_action = QAction("Open in &Default Editor", self)
        open_editor_action.triggered.connect(self.on_open_in_default_editor)
        open_editor_action.setShortcut("Ctrl+Shift+E")
        open_editor_action.setToolTip("Open the current image in your system's default image editor")
        edit_menu.addAction(open_editor_action)

        edit_menu.addSeparator()
        rotate_menu = edit_menu.addMenu("Rotate Image")

        rotate_cw_action = QAction("Rotate &Clockwise", self)
        rotate_cw_action.triggered.connect(lambda: self.on_rotate_image(90))
        rotate_menu.addAction(rotate_cw_action)

        rotate_ccw_action = QAction("Rotate &Counter-clockwise", self)
        rotate_ccw_action.triggered.connect(lambda: self.on_rotate_image(-90))
        rotate_menu.addAction(rotate_ccw_action)

        edit_menu.addSeparator()
        preferences_action = QAction("&Preferences...", self)
        preferences_action.triggered.connect(self.on_preferences)
        edit_menu.addAction(preferences_action)

        # View menu
        view_menu = menu_bar.addMenu("&View")

        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.on_refresh)
        view_menu.addAction(refresh_action)

        view_menu.addSeparator()

        tags_action = QAction("&View All Tags...", self)
        tags_action.setShortcut("Ctrl+T")
        tags_action.triggered.connect(self.on_view_all_tags)
        view_menu.addAction(tags_action)

        view_menu.addSeparator()

        theme_action = QAction("&Theme...", self)
        theme_action.triggered.connect(self.on_select_theme)
        view_menu.addAction(theme_action)

        self.dark_mode_action = QAction("&Toggle Dark Mode", self)
        self.dark_mode_action.setShortcut("Ctrl+D")
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(self.dark_mode)
        self.dark_mode_action.triggered.connect(self.on_toggle_dark_mode)
        view_menu.addAction(self.dark_mode_action)

        # Help menu
        help_menu = menu_bar.addMenu("&Help")

        help_action = QAction("&Help", self)
        help_action.triggered.connect(self.on_help)
        help_menu.addAction(help_action)

        user_guide_action = QAction("&User Guide", self)
        user_guide_action.triggered.connect(self.on_user_guide)
        help_menu.addAction(user_guide_action)

        glossary_action = QAction("&Glossary", self)
        glossary_action.triggered.connect(self.on_glossary)
        help_menu.addAction(glossary_action)

        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self.on_keyboard_shortcuts)
        help_menu.addAction(shortcuts_action)

        changelog_action = QAction("&Changelog", self)
        changelog_action.triggered.connect(self.on_changelog)
        help_menu.addAction(changelog_action)

        help_menu.addSeparator()

        check_updates_action = QAction("Check for &Updates", self)
        check_updates_action.triggered.connect(self.on_check_for_updates)
        help_menu.addAction(check_updates_action)

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        select_btn = QPushButton("Select File")
        select_btn.clicked.connect(self.on_open)
        toolbar.addWidget(select_btn)

        button_style = (
            "QPushButton {"
            "    padding: 8px;"
            "    letter-spacing: 1px;"
            "    background-color: #2b2b2b;"
            "    color: #ffffff;"
            "    border: 1px solid #555555;"
            "    border-radius: 4px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #404040;"
            "    border-color: #666666;"
            "}"
            "QPushButton:pressed {"
            "    background-color: #202020;"
            "    border-color: #888888;"
            "}"
        )

        prev_btn = QPushButton("\u25c0  Previous")
        prev_btn.setFixedWidth(120)
        prev_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        prev_btn.setStyleSheet(button_style)
        prev_btn.clicked.connect(self.on_previous)
        toolbar.addWidget(prev_btn)

        next_btn = QPushButton("Next  \u25b6")
        next_btn.setFixedWidth(120)
        next_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        next_btn.setStyleSheet(button_style)
        next_btn.clicked.connect(self.on_next)
        toolbar.addWidget(next_btn)

        toolbar.addSeparator()

        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedWidth(30)
        zoom_out_btn.clicked.connect(lambda: self.zoom_ui(-0.1))
        toolbar.addWidget(zoom_out_btn)

        self.zoom_label = QLabel(f"UI Zoom: {int(self.ui_scale_factor * 100)}%")
        toolbar.addWidget(self.zoom_label)

        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedWidth(30)
        zoom_in_btn.clicked.connect(lambda: self.zoom_ui(0.1))
        toolbar.addWidget(zoom_in_btn)

        reset_zoom_btn = QPushButton("Reset")
        reset_zoom_btn.clicked.connect(self.reset_zoom)
        toolbar.addWidget(reset_zoom_btn)

        # Keyboard shortcuts for UI zoom
        zoom_in_action1 = QAction("Zoom In", self)
        zoom_in_action1.setShortcut("Ctrl++")
        zoom_in_action1.triggered.connect(lambda: self.zoom_ui(0.1))
        self.addAction(zoom_in_action1)

        zoom_in_action2 = QAction("Zoom In", self)
        zoom_in_action2.setShortcut("Ctrl+Shift+=")
        zoom_in_action2.triggered.connect(lambda: self.zoom_ui(0.1))
        self.addAction(zoom_in_action2)

        zoom_out_action1 = QAction("Zoom Out", self)
        zoom_out_action1.setShortcut("Ctrl+-")
        zoom_out_action1.triggered.connect(lambda: self.zoom_ui(-0.1))
        self.addAction(zoom_out_action1)

        zoom_out_action2 = QAction("Zoom Out", self)
        zoom_out_action2.setShortcut("Ctrl+_")
        zoom_out_action2.triggered.connect(lambda: self.zoom_ui(-0.1))
        self.addAction(zoom_out_action2)

        reset_zoom_action = QAction("Reset Zoom", self)
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.triggered.connect(self.reset_zoom)
        self.addAction(reset_zoom_action)

        toolbar.addSeparator()

        self.file_label = QLabel("No file selected")
        toolbar.addWidget(self.file_label)
