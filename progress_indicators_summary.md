# Summary of Available Progress Indicators

The project uses two main types of progress indicators:

1. **QMessageBox for Progress Updates**:
   - Used during operations like writing metadata to show progress messages.
   - Example: A message box is displayed while writing metadata to a file, with the "OK" button disabled until the operation is complete.

2. **QProgressDialog**:
   - Used for operations that can take significant time, like rotating an image.
   - The dialog provides feedback with a progress bar updating at different stages of the operation (e.g., creating a backup, rotating, and saving the image).

### Usage Details

- **QMessageBox**:
  - Displays progress message of a task.
  - Updates upon task completion with success or error messages.

- **QProgressDialog**:
  - Displays a progress bar that updates with values (e.g., 10%, 20%, etc.).
  - Integrates with the QApplication to process events and update UI during lengthy operations.

These indicators provide user feedback for time-consuming tasks and improve user experience by communicating the progress and success or failure of operations.

