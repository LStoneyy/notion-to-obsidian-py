# 🔄 Advanced Notion to Obsidian Migration Tool

A comprehensive Python script that converts Notion exports to Obsidian-compatible format with advanced link conversion, UUID cleanup, and complete file preservation.

## ✨ Features

### 🧹 **Smart Cleanup**
- **UUID Removal**: Automatically removes UUIDs from all file and folder names
- **Illegal Character Handling**: Replaces problematic characters (`*"/\<>:|?`) with spaces
- **Path Normalization**: Cleans up file paths while preserving meaningful names

### 🔗 **Advanced Link Conversion**
- **Markdown Links**: `[Text](Page.md)` → `[[Page|Text]]` (Obsidian wikilinks)
- **Notion URLs**: `https://notion.so/Page-Title-uuid` → `[[Page Title]]`
- **CSV Links**: `../Path/Page%20Title.md` → `[[Page Title]]`
- **Image Links**: Cleans paths and removes UUIDs from image references
- **URL Preservation**: Real URLs (`http://`, `https://`, IPs) remain unchanged

### 📁 **Complete File Support**
- **All File Types**: Copies PDFs, images, videos, and any other attachments
- **Structure Preservation**: Files stay next to their related Markdown files
- **No Root Clutter**: Prevents files from being dumped at vault root

### 📊 **CSV Database Enhancement**
- **Dual Output**: Preserves original CSV + creates Markdown table version
- **Link Conversion**: Converts internal links within CSV cells
- **Table Formatting**: Properly formatted Markdown tables for Obsidian

## 🚀 Quick Start

### Prerequisites
- Python 3.6 or higher
- Notion export (Markdown & CSV format recommended)

### Installation
1. Download the script:
   ```bash
   git clone https://github.com/yourusername/notion-obsidian-migrator
   cd notion-obsidian-migrator
   ```

2. Run the migration:
   ```bash
   python notion_to_obsidian.py
   ```

### Usage
1. **Export from Notion**:
   - Go to Settings & Members → Settings → Export content
   - Choose "Markdown & CSV" format
   - Download and extract the export

2. **Run the script**:
   ```bash
   python notion_to_obsidian.py
   ```

3. **Follow the prompts**:
   - Enter path to your Notion export folder
   - Enter destination path (or press Enter for "Export" folder)
   - Wait for migration to complete

## 📖 How It Works

### Before Migration
```
NotionExport/
├── My Project abc123def456/
│   ├── Overview 789xyz.md
│   ├── Important Document 456def.pdf
│   ├── Task Database 123abc.csv
│   └── Screenshots 999aaa/
│       └── image1 777bbb.png
```

### After Migration
```
Export/
├── My Project/
│   ├── Overview.md                 # Links converted to [[wikilinks]]
│   ├── Important Document.pdf      # Preserved with clean name
│   ├── Task Database.csv           # Original CSV preserved
│   ├── Task Database.md            # Auto-generated Markdown table
│   └── Screenshots/
│       └── image1.png             # Clean filename
```

## 🔧 Conversion Examples

### Link Conversions
| Before | After |
|--------|-------|
| `[Page](Another%20Page%20abc123.md)` | `[[Another Page\|Page]]` |
| `https://notion.so/My-Page-Title-abc123` | `[[My Page Title]]` |
| `[External](https://example.com)` | `[External](https://example.com)` |
| `![Image](folder%20abc123/image.png)` | `![Image](folder/image.png)` |

### File Naming
| Before | After |
|--------|-------|
| `My Document abc123def456.pdf` | `My Document.pdf` |
| `Project Folder 789xyz` | `Project Folder` |
| `Image_file_999aaa.png` | `Image file.png` |

### CSV to Markdown Table
**CSV Input:**
```csv
Task,Status,Link
"Review PR","Done","../Tasks/Review%20abc123.md"
"Update Docs","In Progress","../Tasks/Update%20def456.md"
```

**Markdown Output:**
```markdown
# Task Database

| Task | Status | Link |
| --- | --- | --- |
| Review PR | Done | [[Review]] |
| Update Docs | In Progress | [[Update]] |
```

## 📊 Migration Summary

After completion, you'll see a detailed summary:

```
============================================================
📊 ADVANCED MIGRATION SUMMARY
============================================================
✅ Files processed: 127
📄 CSVs converted to MD tables: 8
⊘ Files with errors: 2
❌ Total errors: 2

🎉 Advanced migration completed!
💡 Features applied:
   • Removed UUIDs from all file and folder names
   • Converted Markdown links to Obsidian wikilinks
   • Converted CSV databases to Markdown tables
   • Copied all file types (PDFs, images, etc.)
   • Preserved folder structure with clean names
```

## ⚠️ Important Notes

### What Gets Converted
- ✅ **Markdown files** (.md) - Links converted to wikilinks
- ✅ **CSV files** (.csv) - Copied + converted to Markdown tables
- ✅ **All other files** - Copied with cleaned names (PDFs, images, videos, etc.)

### What Stays the Same
- ✅ **External URLs** - `https://`, `http://`, `ftp://`, etc.
- ✅ **IP addresses** - `192.168.1.1`, etc.
- ✅ **File contents** - Only links are modified, content preserved
- ✅ **Folder structure** - Hierarchy maintained with clean names

### Limitations
- **Link Resolution**: Some links may not resolve perfectly due to name collisions
- **Complex Databases**: Very complex Notion databases might need manual adjustment
- **Custom Blocks**: Notion-specific blocks (toggles, callouts) remain as-is

## 🛠️ Troubleshooting

### Common Issues

**"Directory does not exist"**
- Ensure you've extracted the Notion export ZIP file
- Use the full path to the extracted folder

**"Files appear in wrong locations"**
- This script fixes the common issue of files being dumped at vault root
- Files will be placed next to their related Markdown files

**"Some links don't work"**
- Due to UUID removal, some links might not resolve perfectly
- Manually check and fix any broken links in Obsidian

### Path Format Examples

**Windows:**
```
C:\Users\YourName\Downloads\NotionExport
"C:\Users\YourName\My Documents\Notion Export"
```

**macOS/Linux:**
```
/Users/YourName/Documents/NotionExport
~/Downloads/NotionExport
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Development
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


**⭐ If this tool helped you migrate successfully, please consider starring the repository!**
