from https://claude.ai/chat/2a93bc47-4c4d-49eb-9928-8b4c0a5084db

## What is IFD0?

IFD0 (Image File Directory 0) is a fundamental component of the TIFF (Tagged Image File Format) file structure, which is also used in EXIF (Exchangeable Image File Format) data found in JPEG and other image formats.

IFD0 represents the primary image file directory that contains metadata tags describing the main image in a file. Think of it as the "table of contents" or index that tells software how to interpret and display the image data.

## Structure and Function

An IFD consists of:
- A count of directory entries
- A series of 12-byte directory entries (tags)
- An offset to the next IFD (if any)

Each directory entry contains:
- **Tag ID**: Identifies what type of information is stored
- **Data type**: Specifies the format (byte, ASCII, short, long, rational, etc.)
- **Count**: Number of values
- **Value/Offset**: Either the actual data (if small enough) or a pointer to where the data is located

## Common IFD0 Tags

IFD0 typically contains essential image information such as:
- **ImageWidth** and **ImageLength**: Dimensions of the image
- **BitsPerSample**: Number of bits per color component
- **Compression**: Compression scheme used
- **PhotometricInterpretation**: Color space information
- **StripOffsets/TileOffsets**: Location of image data
- **SamplesPerPixel**: Number of color components
- **XResolution/YResolution**: Image resolution
- **DateTime**: When the image was created or modified

## Relationship to Other IFDs

In multi-image files or files with thumbnails, you might encounter:
- **IFD1**: Often contains thumbnail image information
- **EXIF IFD**: Contains camera-specific metadata (accessed via a tag in IFD0)
- **GPS IFD**: Contains location information
- **Interoperability IFD**: Contains interoperability information

## Practical Importance

Understanding IFD0 is crucial for:
- Image processing applications that need to read metadata
- Digital asset management systems
- Photo editing software
- Forensic analysis of digital images
- Custom image format parsers

The IFD structure makes TIFF and EXIF formats highly extensible, allowing new metadata types to be added without breaking compatibility with existing software.

------------------------------------------------------------------------------
from https://www.perplexity.ai/search/ifd0-image-file-directory-0-hEQ2tH5gTPOdnxXzByiX2Q

IFD0 (Image File Directory 0) is the first and primary directory of metadata in image formats like TIFF and Exif JPEGs. It contains tags describing the main image, including dimensions, compression, color encoding, and camera details[5][1][6]. IFD0 is often called the "zeroth" image directory and provides the core technical and descriptive information for the main image in the file[7][8].

Key points about IFD0:
- **Purpose**: IFD0 stores the metadata for the full-resolution (main) image, such as image width, height, orientation, bit depth, manufacturer, and more[6][1].
- **Structure**: Each entry (tag) in IFD0 corresponds to a particular piece of metadata (e.g., ImageWidth, ImageHeight, Make, Model, Orientation)[6][1].
- **Location**: IFD0 is always the first directory in TIFF and TIFF-based formats. Subsequent IFDs (like IFD1) may hold reduced-resolution or thumbnail images[5][6].
- **Extensions**: IFD0 may also point to subdirectories, such as the Exif SubIFD or GPS IFD, for additional, more specialized metadata[1].
- **Standardization**: Tags within IFD0 (e.g., 0x0100 ImageWidth, 0x0101 ImageHeight) are standardized and documented in the TIFF and Exif specifications[2][1].

IFD0 is essential for any software parsing technical and descriptive information from digital image files in these formats[5][7][8].

[1] https://www.media.mit.edu/pia/Research/deepview/exif.html
[2] https://exiftool.org/TagNames/EXIF.html
[3] https://exiv2.org/tags.html
[4] https://www.php.net/manual/en/function.exif-read-data.php
[5] https://dpb587.me/entries/tiff-ifd-and-subifd-20240226
[6] https://www.bitsgalore.org/2024/03/11/multi-image-tiffs-subfiles-and-image-file-directories
[7] https://auth0.com/blog/read-edit-exif-metadata-in-photos-with-javascript/
[8] https://hexdocs.pm/exif_parser/ExifParser.html
[9] https://exiftool.org/forum/index.php?topic=4927.0
[10] https://www.photools.com/community/index.php?topic=13589.0
