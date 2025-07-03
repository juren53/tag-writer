# 16-bit TIFF Image Support Fix - Tag Writer Application

## Issue Description

The tag-writer application was encountering errors when trying to display 16-bit TIFF images. The application would load and read metadata from these images successfully, but failed when attempting to display them as thumbnails or in the image viewer.

### Error Messages
- `Error loading image: 'ptp' was removed from the ndarray class in NumPy 2.0. Use np.ptp(arr, ...) instead.`
- 16-bit images (`2023-1742.tif`, `2023-1743.tif`) were not displaying

## Root Cause

1. **PIL/Pillow Limitation**: Pillow loads 16-bit grayscale TIFFs as `mode='I;16'` or `mode='I;16B'`, but these modes are not directly compatible with display methods that expect 8-bit images.

2. **NumPy 2.0 Compatibility**: The code was using the deprecated `array.ptp()` method which was removed in NumPy 2.0.

## Solution Implemented

### 1. Added 16-bit to 8-bit Conversion

Modified the `load_image()` function in `tag-writer.py` to automatically convert 16-bit images to 8-bit for display:

```python
# Convert 16-bit images to 8-bit for display
if image.mode in ['I;16', 'I;16B']:
    import numpy as np
    np_image = np.array(image)
    # Normalize to 8-bit range (0-255)
    ptp_value = np.ptp(np_image)  # Use np.ptp() instead of array.ptp()
    if ptp_value > 0:  # Avoid division by zero
        norm_image = ((np_image - np_image.min()) / ptp_value * 255).astype(np.uint8)
    else:
        norm_image = np.zeros_like(np_image, dtype=np.uint8)
    image = Image.fromarray(norm_image, mode='L')
```

### 2. Fixed NumPy 2.0 Compatibility

- Replaced deprecated `array.ptp()` with `np.ptp(array)`
- Added proper error handling for edge cases (division by zero)

## Technical Details

### Image Mode Handling
- **16-bit modes detected**: `'I;16'` (little-endian) and `'I;16B'` (big-endian)
- **Conversion method**: Normalize pixel values from 16-bit range (0-65535) to 8-bit range (0-255)
- **Output format**: Grayscale 8-bit (`mode='L'`)

### Normalization Algorithm
1. Convert PIL image to NumPy array
2. Calculate pixel value range using `np.ptp()` (peak-to-peak)
3. Normalize: `(pixel - min_value) / range * 255`
4. Convert back to PIL Image with 8-bit grayscale mode

## Results

### Before Fix
- ❌ 16-bit TIFF images failed to load with NumPy errors
- ❌ Application displayed error messages in logs
- ❌ Thumbnails not generated for 16-bit images
- ❌ Full image viewer not working for 16-bit images

### After Fix
- ✅ 16-bit TIFF images load correctly without errors
- ✅ Thumbnails display properly for all image types
- ✅ Full image viewer works with both 8-bit and 16-bit images
- ✅ All metadata functionality preserved
- ✅ NumPy 2.0 compatibility ensured
- ✅ No performance impact on 8-bit images

## Test Results

The fix was verified by testing with the problematic images:
- `2023-1742.tif` - Now loads and displays correctly
- `2023-1743.tif` - Now loads and displays correctly
- All other 16-bit TIFF images in the test directory work properly

Log output shows successful loading:
```
2025-07-03 17:18:07,681 - INFO - Loaded file: .../2023-1743.tif
2025-07-03 17:18:07,790 - INFO - Updated thumbnail to fit available space: 411x217
```

## Files Modified

- `tag-writer.py` - Main application file
  - Modified `load_image()` function (lines 268-278)
  - Added 16-bit image mode detection and conversion

## Backward Compatibility

- ✅ No impact on existing 8-bit image functionality
- ✅ All existing features continue to work as before
- ✅ Metadata reading/writing unchanged
- ✅ UI and navigation unaffected

## Future Considerations

- The conversion preserves the visual appearance but converts to 8-bit for display only
- Original 16-bit data is not modified when saving metadata
- Consider adding user preference for 16-bit handling (stretch vs. normalize)
- Monitor for other image modes that might need similar handling

---

**Fix Date**: July 3, 2025  
**Application Version**: 0.07u  
**Python Environment**: Windows with NumPy 2.0  
**Status**: ✅ Resolved
