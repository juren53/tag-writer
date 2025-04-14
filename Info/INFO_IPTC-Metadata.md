## IPTC Metadata Fields

The **IPTC (International Press Telecommunications Council)** metadata standard specifies various fields, each with its own maximum character limits. These limits can vary depending on the specific schema/version (e.g., **IPTC-IIM**, **IPTC Core**, or **IPTC Extension**), but here are the most common limits for the **IPTC-IIM (Information Interchange Model)** fields, which are still widely used in image metadata (especially JPEGs):

### Common IPTC-IIM Fields and Max Character Lengths:

| **Field**                    | **Max Characters** |
|-----------------------------|--------------------|
| Object Name (Title)         | 64                 |
| Caption / Abstract          | 2000               |
| Keywords                    | 64 per keyword     |
| Category                    | 3                  |
| Supplemental Categories     | 32 per category    |
| Photographer (By-line)      | 32                 |
| By-line Title               | 32                 |
| Credit                      | 32                 |
| Source                      | 32                 |
| Copyright Notice            | 128                |
| Headline                    | 256                |
| Special Instructions        | 256                |
| City                        | 32                 |
| Province/State              | 32                 |
| Country Name                | 64                 |
| Original Transmission Ref.  | 32                 |

### Notes:
- These are limits set by the **IPTC-IIM standard**, which is often embedded in JPEG files via the legacy format.
- **IPTC Core** (XMP-based, used in modern workflows like in Adobe products) doesn’t always have strict character limits, but compatibility with IIM means many tools still enforce these.

If you’re embedding IPTC metadata using XMP, it's more flexible, but truncation can occur when writing to legacy formats or when viewed in tools expecting IIM constraints.



## IPTC Core/XMP fields  


 Here’s a table for common **IPTC Core (XMP-based)** metadata fields along with practical or recommended character limits. Unlike IPTC-IIM, **IPTC Core (via XMP)** doesn’t have strict character limits defined by the standard, but many tools and best practices impose **practical limits** to maintain compatibility and usability—especially with legacy software and file formats.

### 🧾 IPTC Core (XMP) Metadata Fields and Practical Limits

| **Field**                      | **Practical Max Characters** | **Notes** |
|-------------------------------|-------------------------------|-----------|
| **Title**                     | 64–128                        | Should be short and descriptive; legacy tools limit to 64 |
| **Description (Caption)**     | ~2000                         | No strict limit, but legacy tools and UIs often cut off after 2000 |
| **Creator (Photographer)**    | 255                           | Often shown fully in modern UIs |
| **Creator's Job Title**       | 128                           | Not always displayed |
| **Credit Line**               | 255                           | Sometimes shown as “Courtesy of” |
| **Source**                    | 255                           | Describes original provider |
| **Copyright Notice**          | 255                           | Long statements supported |
| **Usage Terms**               | 255–1000+                     | Recommended to stay concise unless embedded as extended rights info |
| **Headline**                  | 256                           | Treated like a short title |
| **Instructions**              | 255                           | Internal guidance for image use |
| **Date Created**              | ISO 8601 format               | No character limit; format matters |
| **City, State, Country**      | 255 each                      | Flexible in XMP |
| **Location (Sublocation)**    | 255                           | More precise than city/state |
| **Keywords**                  | ~64 per keyword               | Unlimited number of entries, but each keyword should be reasonable |
| **IPTC Subject Code**         | ~3–8 characters per code      | Controlled vocabulary |
| **Contact Info (Email, Phone)**| 255 each                    | Part of extended contact structure |

### Key Differences from IPTC-IIM:
- XMP fields can **support longer strings** and **Unicode characters**.
- Multiple languages are supported through **language alternatives**.
- **Custom fields and namespaces** can be used for extensibility.

⚠️ **Caution:** While modern platforms (like Lightroom, Photoshop, and DAM systems) handle XMP well, images exported to JPEG with embedded **IPTC-IIM for backward compatibility** may cause truncation or loss of long values.


