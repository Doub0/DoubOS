#!/usr/bin/env python3
"""Extract and read copilot_info documents"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

def extract_docx_text(docx_path):
    """Extract all text from DOCX file"""
    try:
        with zipfile.ZipFile(docx_path, 'r') as zip_ref:
            xml_content = zip_ref.read('word/document.xml')
            root = ET.fromstring(xml_content)
            
            # Get all text elements
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            text_elements = root.findall('.//w:t', ns)
            
            # Join all text with proper spacing
            text_parts = []
            for elem in text_elements:
                if elem.text:
                    text_parts.append(elem.text)
            
            return '\n'.join(text_parts)
    except Exception as e:
        return f'Error reading {docx_path}: {e}'

# Extract both documents
storyline_path = Path('copilot_info/Croptopia - Storyline.docx')
ideaboard_path = Path('copilot_info/croptopia ideaboard.docx')

if storyline_path.exists():
    storyline = extract_docx_text(storyline_path)
    print('=' * 80)
    print('CROPTOPIA STORYLINE')
    print('=' * 80)
    print(storyline)
    print()

if ideaboard_path.exists():
    ideaboard = extract_docx_text(ideaboard_path)
    print('=' * 80)
    print('CROPTOPIA IDEABOARD')
    print('=' * 80)
    print(ideaboard)
