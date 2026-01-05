#!/usr/bin/env python3

# Debug script to test zoom functionality
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer, Qt
    
    # Import modules
    from tag_writer import Config, MainWindow
    
    # Create config instance
    config = Config()
    print(f"1. Initial config.ui_zoom_factor: {config.ui_zoom_factor}")
    
    # Create main window instance
    app = QApplication(sys.argv)
    main_window = tag_writer.MainWindow()
    
    print(f"2. After MainWindow init, main_window.ui_scale_factor: {main_window.ui_scale_factor}")
    print(f"3. After MainWindow init, config.ui_zoom_factor: {config.ui_zoom_factor}")
    
    # Test zoom_ui call
    print("4. Testing zoom_ui call with +0.1...")
    main_window.zoom_ui(0.1)
    
    print(f"5. After zoom_ui(+0.1), main_window.ui_scale_factor: {main_window.ui_scale_factor}")
    print(f"6. After zoom_ui(+0.1), config.ui_zoom_factor: {config.ui_zoom_factor}")
    
    # Test zoom_ui call with negative
    print("7. Testing zoom_ui call with -0.1...")
    main_window.zoom_ui(-0.1)
    
    print(f"8. After zoom_ui(-0.1), main_window.ui_scale_factor: {main_window.ui_scale_factor}")
    print(f"9. After zoom_ui(-0.1), config.ui_zoom_factor: {config.ui_zoom_factor}")
    
    # Test mouse wheel simulation
    print("10. Testing Ctrl+mouse wheel simulation...")
    from PyQt6.QtCore import QEvent
    from PyQt6.QtGui import QWheelEvent
    
    # Create a wheel event
    wheel_event = QWheelEvent(
        QPoint(),  # position
        QPoint(),  # globalPosition  
        QPoint(0, 120),  # Scroll up
        Qt.KeyboardModifier.ControlModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
        Qt.MouseEventSource.MouseEventNotSynthesized
    )
    
    # Send event to main window
    main_window.eventFilter(main_window, wheel_event)
    
    print(f"11. After mouse wheel simulation, main_window.ui_scale_factor: {main_window.ui_scale_factor}")
    print(f"12. After mouse wheel simulation, config.ui_zoom_factor: {config.ui_zoom_factor}")
    
    print("✅ All zoom functionality tests completed successfully!")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()