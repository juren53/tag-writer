# Tag Writer Improvement Recommendations

*Analysis Date: 2026-02-15*
*Analyzed Version: Tag Writer v0.1.7a*
*Analyst: Claude Opus 4.6 (Claude Code)*

---

## High Priority

### 1. Add Timeouts to ExifTool Operations
Metadata read/write via PyExifTool has no timeout. If ExifTool hangs, the UI freezes indefinitely. The resolution detection at line 1836 has a 10-second timeout but the core operations (lines 604, 644, 749) don't.

### 2. JPEG Quality Loss on Rotation
Line 4269: `rotated_image.save(config.selected_file)` uses PIL's default compression. Each rotation degrades JPEG quality. Should pass `quality=95` or preserve the original quality setting.

### 3. Sanitize Metadata Values Before ExifTool Write
Line 736: values are passed via f-string `f"-{exiftool_tag}={value}"` with no escaping. Special characters like `=` or `;` in metadata could break ExifTool parsing or corrupt data.

### 4. Thread the Metadata Operations
Metadata reads and writes block the UI. A `QThread` worker (like SysMon's `ProcessWorker`) would keep the app responsive, especially for large TIFFs.

---

## Medium Priority

### 5. Path Traversal in File Rename
Line 3831: user-supplied filename from the rename dialog isn't validated. A name containing `../` could rename files outside the intended directory. Fix with `os.path.basename()`.

### 6. Large Directory Performance
Line 4924: `get_image_files()` loads every image path at once. A directory with 10K+ images will lag. Consider lazy loading or background scanning.

### 7. Remove Debug Print Statements
Lines 2968, 3377 still have `print(f"DEBUG: ...")` in production code. These should be `logger.debug()` calls.

### 8. Metadata Write Then Rotate Ordering
Lines 4268-4282: image is saved first (overwriting original), then metadata is reapplied. If the metadata write fails, the original metadata is lost. Safer to backup, rotate, then write metadata, with rollback on failure.

---

## Lower Priority

### 9. PyExifTool is Outdated
Pinned to v0.5.6 (2021). No Python 3.11+ support statement. Worth evaluating if a newer fork or alternative exists.

### 10. File Modification Detection
If another tool edits metadata while the file is open in TagWriter, the cached metadata is stale. A file watcher or timestamp check on focus would prevent silent overwrites.

### 11. 16-bit TIFF Handling
Lines 516-517 convert 16-bit to 8-bit for display, which is fine for the viewer, but worth noting in the UI so users know they're seeing a reduced representation.

---

## Notes

The MainWindow size (2200+ lines) is worth addressing eventually, but the functional issues above should be tackled first — they affect data integrity and user experience directly.

---

*Analysis by: Claude Opus 4.6 (Claude Code)*
*Date: 2026-02-15*
