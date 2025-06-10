# Photo and Image Metadata Glossary

A comprehensive reference guide for terms related to digital photography, image files, and metadata standards.

## Table of Contents
- [File Formats](#file-formats)
- [EXIF Metadata](#exif-metadata)
- [IPTC Metadata](#iptc-metadata)
- [XMP Metadata](#xmp-metadata)
- [Color and Image Properties](#color-and-image-properties)
- [Camera and Photography Terms](#camera-and-photography-terms)
- [Technical Standards](#technical-standards)

---

## File Formats

**JPEG (Joint Photographic Experts Group)**
- A lossy compression format commonly used for photographs
- File extensions: .jpg, .jpeg
- Supports EXIF, IPTC, and XMP metadata

**RAW**
- Unprocessed image data directly from camera sensor
- Proprietary formats like .CR2 (Canon), .NEF (Nikon), .ARW (Sony)
- Contains maximum image information and metadata

**TIFF (Tagged Image File Format)**
- Lossless compression format
- File extension: .tif, .tiff
- Excellent metadata support, often used for archival purposes

**PNG (Portable Network Graphics)**
- Lossless compression format
- File extension: .png
- Limited metadata support compared to JPEG/TIFF

**HEIF/HEIC (High Efficiency Image Format)**
- Modern format with better compression than JPEG
- Used by Apple devices since iOS 11
- Supports extensive metadata

---

## EXIF Metadata

**EXIF (Exchangeable Image File Format)**
- Technical metadata automatically recorded by digital cameras
- Embedded in image files
- Contains camera settings and shooting conditions

**Aperture (F-stop)**
- Size of the camera's aperture opening
- Controls depth of field
- Examples: f/1.4, f/2.8, f/5.6

**Shutter Speed**
- Duration the camera sensor is exposed to light
- Measured in seconds or fractions
- Examples: 1/60s, 1/250s, 2s

**ISO Speed**
- Sensor sensitivity to light
- Higher numbers = more sensitive but more noise
- Examples: ISO 100, ISO 800, ISO 3200

**Focal Length**
- Distance from lens to sensor when focused at infinity
- Measured in millimeters (mm)
- Determines field of view and magnification

**White Balance**
- Color temperature setting to correct color cast
- Measured in Kelvin (K)
- Examples: Daylight (5500K), Tungsten (3200K)

**GPS Coordinates**
- Geographic location where photo was taken
- Latitude and longitude coordinates
- May include altitude and direction

**Date/Time Original**
- Timestamp when photo was captured
- Usually in camera's local time zone

**Camera Make/Model**
- Manufacturer and specific camera model
- Examples: "Canon", "EOS R5"

**Lens Information**
- Lens model, focal length range, aperture range
- May include lens serial number

---

## IPTC Metadata

**IPTC (International Press Telecommunications Council)**
- Standardized metadata for news and media industries
- adopted by NARA and other archivists to capture archival data
- Focuses on editorial, creation and rights information
- Embedded in the header area of image files 
- TIFF, JPEG, PNG and GIF can contain IPTC metadata

### **A Note on IPTC Metadata Implementation:** 
It must be stated up front that many IPTC fields overlap, and their 
use will often vary. How an organization implements IPTC metadata 
largely depends on its specific needs, the tools it uses, 
and its industry practices.

**Abstract Caption**
- Textual description of image content
- What is happening in the photograph

**Keywords**
- Searchable tags describing image content
- Subjects, locations, events, concepts

**Title**
- Brief headline or name for the image
- Often used as filename or display name

**Creator/Photographer**
- Name of person who created the image
- Copyright holder information

**Copyright Notice**
- Legal copyright statement
- Usage rights and restrictions

**Contact Information**
- Creator's address, phone, email, website
- For licensing and permission requests

**Location Information**
- City, state/province, country
- Specific location names and codes

**Date Created**
- When the image was originally created
- Will often differ from EXIF date 

**Credit**
- institution providing the image and content

**By-line**
- person who created the image 
- usually the photographer's name


**By-line Title**
- photographer's title 
- or photographers affiliation


**Instructions/Special Instructions**
- Usage guidelines or handling notes
- Editorial instructions for publishers

**Category/Supplemental Categories**
- Subject classification codes
- News category assignments

**Urgency**
- Editorial priority level (1-8 scale)
- 1 = most urgent, 8 = least urgent



For more in-depth information on IPTC Photo Metadata, refer to the [IPTC Photo Metadata User Guide](https://www.iptc.org/std/photometadata/documentation/userguide/).
---

## XMP Metadata

**XMP (Extensible Metadata Platform)**
- Adobe's open metadata standard
- XML-based, extensible format
- Used by Adobe Creative Suite and other applications

**Rating**
- Star rating system (typically 1-5 stars)
- Quality or preference indicator

**Color Label**
- Color-coded classification system
- Red, yellow, green, blue, purple labels

**Collections**
- Groupings of related images
- Virtual albums or sets

**Processing History**
- Record of edits and adjustments
- Software versions and settings used

**Develop Settings**
- RAW processing parameters
- Exposure, contrast, saturation adjustments

---

## Color and Image Properties

**Color Space**
- Mathematical model for representing colors
- Examples: sRGB, Adobe RGB, ProPhoto RGB

**Color Profile/ICC Profile**
- Device-specific color calibration data
- Ensures consistent color reproduction

**Bit Depth**
- Number of bits per color channel
- 8-bit (256 levels), 16-bit (65,536 levels)

**Resolution/DPI (Dots Per Inch)**
- Print resolution specification
- Common values: 72 DPI (web), 300 DPI (print)

**Pixel Dimensions**
- Width and height in pixels
- Examples: 1920x1080, 4000x6000

**Compression**
- Method used to reduce file size
- Lossless (no quality loss) vs. Lossy (some quality loss)

**Orientation**
- Image rotation information
- Landscape, portrait, or specific rotation angles

---

## Camera and Photography Terms

**Depth of Field**
- Range of distance in acceptable focus
- Shallow (blurred background) vs. Deep (everything in focus)

**Exposure**
- Amount of light reaching the sensor
- Combination of aperture, shutter speed, and ISO

**Exposure Compensation**
- Manual adjustment to automatic exposure
- Measured in stops (+/-)

**Metering Mode**
- How camera measures light for exposure
- Matrix, center-weighted, spot metering

**Focus Mode**
- How camera achieves focus
- Single-point, continuous, automatic selection

**Flash**
- Artificial light source
- On, off, auto, fill-flash, red-eye reduction

**Image Stabilization**
- Technology to reduce camera shake
- Optical (lens-based) or sensor-based

---

## Technical Standards

**Dublin Core**
- Metadata standard for digital resources
- 15 core elements for resource description

**EXIF 2.3**
- Current EXIF standard specification
- Defines technical metadata fields

**IPTC Core**
- Current IPTC metadata schema
- Descriptive and administrative metadata

**IPTC Extension**
- Extended IPTC schema
- Additional fields for specific industries

**XMP Specification**
- Adobe's metadata framework standard
- Extensible and platform-independent

**JPEG EXIF**
- EXIF data embedded in JPEG files
- Most common metadata implementation

**Sidecar Files**
- External metadata files
    - .XMP files containing metadata separate from image
    - JASON files containing metadata separate from image
---

## Metadata Management

**Embedded Metadata**
- Information stored within the image file itself
- Travels with the file when copied or moved

**External Metadata**
- Information stored in separate database or files
- May be lost if not properly maintained

**Metadata Synchronization**
- Keeping embedded and external metadata consistent
- Important for asset management workflows

**Metadata Templates**
- Pre-defined sets of metadata fields
- Speeds up consistent metadata entry

**Batch Processing**
- Applying metadata to multiple images simultaneously
- Efficient workflow for large collections

**Metadata Extraction**
- Reading metadata from image files
- Converting between different metadata formats

---

*This glossary is a living document. Terms and definitions will be updated 
as new standards and technologies emerge in digital photography 
and image metadata management.*

**Related Documentation:**
- [Tag Writer User Guide](user-guide.md)
- [Tag Writer Help](tag-writer-help.md)

**Last Updated:** 2025-06-10 08-00

