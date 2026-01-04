# Plan: Display Date Metadata in TagWriter Image Viewer Panel

## Overview
This plan outlines the implementation of date-related metadata display in the Image Viewer panel of TagWriter, showing date information at the bottom of the right-side Image Viewer panel.

## Current State Analysis

### ImageViewer Structure
- **Location**: `tag-writer.py:1654` - `ImageViewer` class
- **Current Layout**: HTML table with 3 rows:
  1. File size | Dimension
  2. Resolution | Pixel count  
  3. Photometric Interpretation | Bits Per Sample
- **Table Location**: Lines 1851-1870 with consistent styling

### Date Metadata Support
- **Field Mappings** (`tag-writer.py:515-517`):
  - `DateCreated`: IPTC, XMP, XMP-photoshop fields
  - `DateModified`: EXIF, XMP, ICC_Profile fields
- **Extraction Function**: `read_metadata()` function at `tag-writer.py:484`

## Implementation Plan

### Phase 1: Core Implementation

#### 1. Add Date Extraction Method to ImageViewer
**Target**: `ImageViewer` class in `tag-writer.py`
- Add new method `extract_date_metadata(image_path)`
- Leverage existing `read_metadata()` function for consistency
- Extract `DateCreated` and `DateModified` using existing field mappings
- Handle missing/invalid dates gracefully

#### 2. Extend HTML Table Structure
**Target**: HTML table in `ImageViewer.load_image()` method
- Add 4th row to existing table for date information
- Follow exact styling pattern: bold labels, consistent spacing
- Layout: `Date Created: [value] | Date Modified: [value]`
- Use existing CSS styling: `font-weight:bold; min-width:140px; padding-right:10px`

#### 3. Update load_image() Method
**Target**: `ImageViewer.load_image()` method around line 1885
- Extract date metadata and include in table HTML formatting
- Update the `.format()` call to include date variables
- Maintain fallback behavior with "--" for missing dates

### Phase 2: Enhanced Date Support (Optional)

#### 4. Additional Date Fields
**Target**: Enhanced metadata extraction
- Support for more date types:
  - `DateTimeOriginal` (EXIF)
  - `CreateDate` (EXIF)
  - `File Modification Date/Time` 
  - `File Creation Date/Time`
- Use exiftool grep pattern to find all "Date" fields dynamically
- Consider expanding to 4th row or additional UI elements

#### 5. Date Formatting
**Target**: Consistent date display
- Maintain current `%Y:%m:%d` format for consistency
- Option to display full timestamp if available
- Follow existing date handling patterns in MetadataPanel

### Phase 3: UI Refinements

#### 6. Responsive Layout
**Target**: Table layout optimization
- Ensure date row fits well within existing table width
- Consider tooltip or expanding section for additional date fields
- Maintain visual balance with existing metadata rows

#### 7. Error Handling
**Target**: Robust error management
- Graceful fallback when metadata extraction fails
- Performance optimization for large image sets
- Consistent error handling with existing patterns

## Technical Implementation Details

### Key Files to Modify
- `tag-writer.py` - `ImageViewer` class (line 1654)

### Core Method Changes
```python
def extract_date_metadata(self, image_path):
    """Extract date-related metadata for display"""
    metadata = read_metadata(image_path)
    date_created = metadata.get('DateCreated', '--')
    date_modified = metadata.get('DateModified', '--')
    return date_created, date_modified

# HTML Table Addition (4th row):
# <tr>
#     <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Date Created:</td>
#     <td style='min-width:120px; padding-right:30px;'>{date_created}</td>
#     <td style='font-weight:bold; min-width:140px; padding-right:10px;'>Date Modified:</td>
#     <td style='min-width:120px;'>{date_modified}</td>
# </tr>
```

### Integration Points

#### Data Flow
1. `MainWindow.load_file()` → `image_viewer.load_image()`
2. `image_viewer.load_image()` → `extract_date_metadata()`
3. Date data → HTML table update
4. Automatic refresh on image change

#### Dependencies
- **Existing**: `read_metadata()` function
- **Reuse**: `MetadataManager` field mappings  
- **UI**: Follow existing table layout pattern in `setup_ui()` (line 2816)

## Benefits of This Approach

1. **Minimal Changes** - Leverages existing infrastructure
2. **Consistent UI** - Follows established styling patterns
3. **Performance** - Uses efficient existing metadata extraction
4. **Maintainability** - Simple, focused implementation
5. **User Experience** - Dates display where users expect technical metadata

## Implementation Strategy

### Recommended Approach: Quick Integration
1. **Modify `ImageViewer.load_image()`**:
   - Extract date fields from metadata
   - Update the HTML table in `table_label` to include date information
   - Use existing metadata extraction patterns

2. **Follow Existing Patterns**:
   - Maintain current table structure and styling
   - Use existing error handling approaches
   - Keep same data formatting conventions

### Alternative: Enhanced Architecture
- Refactor date handling into dedicated `DateMetadataExtractor` class
- Support for additional date fields beyond the core two
- More sophisticated UI for displaying multiple date types

## Questions for Clarification

1. **Date Fields Priority**: Which date fields are most important to display first? (Current plan: Date Created + Date Modified)

2. **Full Timestamp vs Date Only**: Should we show full timestamps (2025:03:19 15:25:32) or just dates (2025:03:19)?

3. **Additional Dates**: Would you like the system file dates (Creation, Modification, Access) or focus on image metadata dates?

4. **Layout Preference**: Keep the current 2-column layout (Date Created | Date Modified) or use a different arrangement?

## Example Output
The implementation should display date information similar to:
```
exiftool .\66-1647_verso.tif | grep Date
File Modification Date/Time     : 2026:01:03 09:59:02-06:00
File Access Date/Time           : 2026:01:04 13:09:29-06:00
File Creation Date/Time         : 2026:01:03 10:02:59-06:00
Modify Date                     : 2025:03:19 15:25:32
```

This will be displayed in the Image Viewer panel as:
- Date Created: 2025:03:19
- Date Modified: 2025:03:19

## Timeline
- **Phase 1**: Core implementation (2-3 hours)
- **Phase 2**: Enhanced features (1-2 hours)  
- **Phase 3**: UI refinements (1 hour)

## Success Criteria
- [ ] Date metadata appears in Image Viewer panel
- [ ] Consistent styling with existing table rows
- [ ] Graceful handling of missing date data
- [ ] Automatic update when new images are loaded
- [ ] No performance degradation for image loading