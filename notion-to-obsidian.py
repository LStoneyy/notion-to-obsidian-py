#!/usr/bin/env python3
"""
Advanced Notion to Obsidian Migration Tool

This script converts Notion exports to Obsidian-compatible format with comprehensive
file handling, UUID removal, and advanced link conversion.

Features:
- Removes UUIDs from file and folder names
- Converts all file types (PDFs, images, etc.)
- Advanced link conversion for Markdown and CSV files
- Converts CSV databases to Markdown tables
- Preserves folder structure with files next to their MD files

Author: Migration Tool
Version: 2.0
"""

import os
import shutil
import re
import csv
import urllib.parse
from pathlib import Path
from typing import Optional, Tuple, Dict, List
import sys


class AdvancedNotionMigrator:
    def __init__(self):
        self.processed_files = 0
        self.skipped_files = 0
        self.converted_csvs = 0
        self.errors = []
        self.uuid_pattern = re.compile(r'[a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12}', re.IGNORECASE)
        self.short_uuid_pattern = re.compile(r'[a-f0-9]{32}', re.IGNORECASE)
    
    def remove_uuid_from_name(self, name: str) -> str:
        """
        Remove UUID from file/folder names.
        Handles both long UUIDs (with dashes) and short UUIDs (32 chars).
        """
        # Remove long UUIDs (with or without dashes)
        name = re.sub(r'\s+[a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12}', '', name, flags=re.IGNORECASE)
        
        # Remove short UUIDs at the end
        name = re.sub(r'\s+[a-f0-9]{32}', '', name, flags=re.IGNORECASE)
        
        # Remove UUID at the end of filename (before extension)
        name = re.sub(r'_[a-f0-9]{32}(\.[^.]+)$', r'\1', name, flags=re.IGNORECASE)
        name = re.sub(r'_[a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12}(\.[^.]+)$', r'\1', name, flags=re.IGNORECASE)
        
        return name.strip()
    
    def clean_filename(self, filename: str) -> str:
        """
        Clean filename to be Obsidian-compatible.
        Replace illegal characters with spaces and clean up.
        """
        # Replace illegal characters with spaces
        filename = re.sub(r'[*"/\\<>:|?]', ' ', filename)
        # Replace multiple spaces/underscores with single space
        filename = re.sub(r'[_\s]+', ' ', filename)
        # Remove leading/trailing spaces
        filename = filename.strip()
        
        return filename
    
    def is_url(self, text: str) -> bool:
        """Check if text is a URL."""
        # Check for protocol
        if '://' in text:
            return True
        # Check for IP address pattern
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        if re.match(ip_pattern, text):
            return True
        return False
    
    def convert_notion_links(self, content: str, file_path: Path) -> str:
        """
        Convert various types of links in Notion content to Obsidian format.
        """
        # Convert Notion.so links
        def replace_notion_url(match):
            url = match.group(2)
            text = match.group(1)
            
            if 'notion.so' in url:
                # Extract page title from URL
                # Format: https://www.notion.so/The-Page-Title-2d41ab7b61d14cec885357ab17d48536
                url_parts = url.split('/')[-1]  # Get the last part
                page_title = url_parts.split('-')[:-1]  # Remove UUID part
                if page_title:
                    title = ' '.join(page_title).replace('-', ' ')
                    return f'[[{title}]]'
            
            return match.group(0)  # Return original if not a notion.so link
        
        # Convert standard markdown links
        def replace_markdown_link(match):
            text = match.group(1)
            link = match.group(2)
            
            # Don't convert URLs
            if self.is_url(link):
                return match.group(0)
            
            # URL decode the link
            link = urllib.parse.unquote(link)
            
            # Remove .md extension and path
            if link.endswith('.md'):
                page_name = Path(link).stem
                page_name = self.remove_uuid_from_name(page_name)
                page_name = self.clean_filename(page_name)
                
                # If text is same as page name, use simple format
                if text.lower() == page_name.lower():
                    return f'[[{page_name}]]'
                else:
                    return f'[[{page_name}|{text}]]'
            
            return match.group(0)
        
        # Convert image links
        def replace_image_link(match):
            alt_text = match.group(1) if match.group(1) else ''
            image_path = match.group(2)
            
            # URL decode
            image_path = urllib.parse.unquote(image_path)
            
            # Clean up the path - remove UUIDs from folder names
            path_parts = image_path.split('/')
            cleaned_parts = []
            for part in path_parts:
                if part:
                    cleaned_part = self.remove_uuid_from_name(part)
                    cleaned_part = self.clean_filename(cleaned_part)
                    if cleaned_part:
                        cleaned_parts.append(cleaned_part)
            
            if cleaned_parts:
                clean_path = '/'.join(cleaned_parts)
                return f'![{alt_text}]({clean_path})'
            
            return match.group(0)
        
        # Apply conversions
        # 1. Convert Notion.so URLs
        content = re.sub(r'\[([^\]]+)\]\((https://[^)]*notion\.so[^)]*)\)', replace_notion_url, content)
        
        # 2. Convert image links
        content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image_link, content)
        
        # 3. Convert regular markdown links (but not URLs)
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_markdown_link, content)
        
        return content
    
    def convert_csv_links(self, content: str) -> str:
        """Convert CSV cell content links to Obsidian format."""
        def replace_csv_link(match):
            link = match.group(0)
            # URL decode
            link = urllib.parse.unquote(link)
            
            # Remove relative path indicators and .md extension
            if link.endswith('.md'):
                page_name = Path(link).stem
                page_name = self.remove_uuid_from_name(page_name)
                page_name = self.clean_filename(page_name)
                return f'[[{page_name}]]'
            
            return link
        
        # Find relative paths ending in .md
        content = re.sub(r'\.\.\/[^,\n\r]*\.md', replace_csv_link, content)
        return content
    
    def csv_to_markdown_table(self, csv_path: Path) -> str:
        """Convert CSV file to Markdown table format."""
        try:
            with open(csv_path, 'r', encoding='utf-8', errors='ignore') as file:
                # Detect delimiter
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                rows = list(reader)
            
            if not rows:
                return "Empty table"
            
            # Convert links in all cells
            for i, row in enumerate(rows):
                rows[i] = [self.convert_csv_links(cell) for cell in row]
            
            # Create markdown table
            markdown_lines = []
            
            # Header
            if rows:
                headers = rows[0]
                markdown_lines.append('| ' + ' | '.join(headers) + ' |')
                markdown_lines.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
                
                # Data rows
                for row in rows[1:]:
                    # Pad row to match header length
                    while len(row) < len(headers):
                        row.append('')
                    markdown_lines.append('| ' + ' | '.join(row[:len(headers)]) + ' |')
            
            return '\n'.join(markdown_lines)
            
        except Exception as e:
            self.errors.append(f"Error converting CSV to table {csv_path}: {str(e)}")
            return f"Error converting CSV: {str(e)}"
    
    def process_markdown_file(self, src_path: Path, dst_path: Path) -> bool:
        """Process a markdown file with advanced link conversion."""
        try:
            with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Convert links
            content = self.convert_notion_links(content, src_path)
            
            # Ensure destination directory exists
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(dst_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Converted MD: {dst_path.name}")
            return True
            
        except Exception as e:
            error_msg = f"Error processing {src_path}: {str(e)}"
            print(f"✗ {error_msg}")
            self.errors.append(error_msg)
            return False
    
    def process_csv_file(self, src_path: Path, dst_path: Path) -> bool:
        """Process CSV file - copy original and create markdown table version."""
        try:
            # Ensure destination directory exists
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy original CSV
            shutil.copy2(src_path, dst_path)
            
            # Create markdown table version
            md_path = dst_path.with_suffix('.md')
            markdown_content = f"# {dst_path.stem}\n\n"
            markdown_content += self.csv_to_markdown_table(src_path)
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"✓ Converted CSV: {dst_path.name} (+ {md_path.name})")
            self.converted_csvs += 1
            return True
            
        except Exception as e:
            error_msg = f"Error processing CSV {src_path}: {str(e)}"
            print(f"✗ {error_msg}")
            self.errors.append(error_msg)
            return False
    
    def process_other_file(self, src_path: Path, dst_path: Path) -> bool:
        """Process other file types (PDFs, images, etc.) by copying them."""
        try:
            # Ensure destination directory exists
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(src_path, dst_path)
            print(f"✓ Copied: {dst_path.name}")
            return True
            
        except Exception as e:
            error_msg = f"Error copying {src_path}: {str(e)}"
            print(f"✗ {error_msg}")
            self.errors.append(error_msg)
            return False
    
    def clean_path_component(self, name: str) -> str:
        """Clean a single path component (file or directory name)."""
        # Remove UUID
        name = self.remove_uuid_from_name(name)
        # Clean illegal characters
        name = self.clean_filename(name)
        return name
    
    def get_clean_relative_path(self, src_path: Path, base_path: Path) -> Path:
        """Get cleaned relative path with UUIDs removed from all components."""
        rel_path = src_path.relative_to(base_path)
        
        # Clean each path component
        clean_parts = []
        for part in rel_path.parts:
            clean_part = self.clean_path_component(part)
            if clean_part:  # Only add non-empty parts
                clean_parts.append(clean_part)
        
        if clean_parts:
            return Path(*clean_parts)
        else:
            # Fallback to original filename if all parts were removed
            return Path(self.clean_path_component(src_path.name))
    
    def migrate_directory(self, src_dir: Path, dst_dir: Path) -> None:
        """
        Recursively migrate all files from source to destination directory.
        """
        if not src_dir.exists():
            raise FileNotFoundError(f"Source directory does not exist: {src_dir}")
        
        # Create destination directory if it doesn't exist
        dst_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📁 Processing directory: {src_dir.name}")
        
        # Walk through all files and subdirectories
        for root, dirs, files in os.walk(src_dir):
            current_src = Path(root)
            
            # Process files in current directory
            for file in files:
                src_file = current_src / file
                
                # Get clean relative path
                clean_rel_path = self.get_clean_relative_path(src_file, src_dir)
                dst_file = dst_dir / clean_rel_path
                
                # Process based on file type
                if src_file.suffix.lower() == '.md':
                    success = self.process_markdown_file(src_file, dst_file)
                elif src_file.suffix.lower() == '.csv':
                    success = self.process_csv_file(src_file, dst_file)
                else:
                    # Copy all other files (PDFs, images, etc.)
                    success = self.process_other_file(src_file, dst_file)
                
                if success:
                    self.processed_files += 1
                else:
                    self.skipped_files += 1
    
    def print_summary(self) -> None:
        """Print migration summary."""
        print(f"\n{'='*60}")
        print("📊 ADVANCED MIGRATION SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Files processed: {self.processed_files}")
        print(f"📄 CSVs converted to MD tables: {self.converted_csvs}")
        print(f"⊘ Files with errors: {self.skipped_files}")
        print(f"❌ Total errors: {len(self.errors)}")
        
        if self.errors:
            print(f"\n⚠️  ERRORS ENCOUNTERED:")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"   • {error}")
            if len(self.errors) > 10:
                print(f"   ... and {len(self.errors) - 10} more errors")
        
        print(f"\n🎉 Advanced migration completed!")
        print("💡 Features applied:")
        print("   • Removed UUIDs from all file and folder names")
        print("   • Converted Markdown links to Obsidian wikilinks")
        print("   • Converted CSV databases to Markdown tables")
        print("   • Copied all file types (PDFs, images, etc.)")
        print("   • Preserved folder structure with clean names")


def get_user_input() -> Tuple[Path, Path]:
    """Get source and destination paths from user input."""
    print("🚀 ADVANCED NOTION TO OBSIDIAN MIGRATION TOOL")
    print("="*60)
    print("This tool provides comprehensive Notion to Obsidian migration:")
    print("• Removes UUIDs from file and folder names")
    print("• Converts all file types (MD, CSV, PDF, images, etc.)")
    print("• Advanced link conversion and CSV to Markdown tables")
    print("• Preserves folder structure with files in correct locations")
    print()
    
    # Get source directory
    while True:
        src_input = input("📂 Enter path to your Notion export directory: ").strip('"\'')
        if not src_input:
            print("❌ Please enter a valid path.")
            continue
        
        src_path = Path(src_input).expanduser().resolve()
        if not src_path.exists():
            print(f"❌ Directory does not exist: {src_path}")
            continue
        
        if not src_path.is_dir():
            print(f"❌ Path is not a directory: {src_path}")
            continue
        
        break
    
    # Get destination directory
    dst_input = input("📁 Enter destination path (press Enter for 'Export' folder): ").strip('"\'')
    
    if not dst_input:
        # Create Export folder in current directory
        dst_path = Path.cwd() / "Export"
        print(f"💡 No destination specified. Using: {dst_path}")
    else:
        dst_path = Path(dst_input).expanduser().resolve()
    
    # Confirm if destination exists and is not empty
    if dst_path.exists() and any(dst_path.iterdir()):
        print(f"\n⚠️  Destination directory exists and is not empty: {dst_path}")
        confirm = input("Continue anyway? (y/N): ").lower().strip()
        if confirm not in ['y', 'yes']:
            print("❌ Migration cancelled.")
            sys.exit(0)
    
    return src_path, dst_path


def main():
    """Main function to run the advanced migration."""
    try:
        # Get user input
        src_path, dst_path = get_user_input()
        
        print(f"\n🚀 Starting advanced migration...")
        print(f"📂 Source: {src_path}")
        print(f"📁 Destination: {dst_path}")
        print()
        
        # Create migrator and run migration
        migrator = AdvancedNotionMigrator()
        migrator.migrate_directory(src_path, dst_path)
        
        # Print summary
        migrator.print_summary()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Migration interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()