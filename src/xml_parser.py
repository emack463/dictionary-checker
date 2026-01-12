import os
from typing import List, Set, Optional, Dict

from lxml import etree


# Metadata elements to exclude from text extraction
EXCLUDED_ELEMENTS: Set[str] = {
    'processing-meta',
    'collection-meta',
    'book-meta',
    'sec-meta',
    'book-id',
    'book-title-group',
    'contrib-group',
    'ext-link',
    'related-object',
    'day',
    'month',
    'year',
}


def extract_text_from_element(elem: etree._Element) -> str:
    """Recursively extract and join text content from an element and its children.

    Skips metadata elements defined in EXCLUDED_ELEMENTS.
    Preserves whitespace between sibling text nodes.
    """
    # Get the local name (without namespace)
    local_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
    
    # Skip this element entirely if it's metadata
    if local_name in EXCLUDED_ELEMENTS:
        return ""
    
    parts: List[str] = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        parts.append(extract_text_from_element(child))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts).strip()


def parse_xml_file_to_text(path: str) -> str:
    """Parse a single XML file and return extracted plain text.

    Uses lxml.etree for robust parsing. Returns an empty string on parse errors.
    """
    try:
        parser = etree.XMLParser(recover=True)
        tree = etree.parse(path, parser)
        root = tree.getroot()
        text = extract_text_from_element(root)
        return text
    except Exception:
        # On any error, return empty string to let caller decide how to handle it.
        return ""


def extract_date_from_section(sec_elem: etree._Element) -> Optional[str]:
    """Extract yyyy-mm date from a section's metadata.
    
    Returns date in 'yyyy-mm' format or None if not found.
    """
    # Look for date elements in sec-meta
    namespaces = {'bits': 'https://jats.nlm.nih.gov/extensions/bits/2.1/xsd/BITS-book2-1.xsd'}
    
    # Try to find year and month in the metadata
    year_elem = sec_elem.find('.//bits:year', namespaces)
    month_elem = sec_elem.find('.//bits:month', namespaces)
    
    if year_elem is not None and month_elem is not None:
        year = year_elem.text
        month = month_elem.text
        if year and month:
            # Ensure month is zero-padded
            month_str = month.zfill(2)
            return f"{year}-{month_str}"
    
    return None


def parse_xml_to_articles(path: str) -> List[Dict[str, str]]:
    """Parse XML file and return list of articles with their metadata.
    
    Each article is a dict with:
    - 'id': section ID
    - 'date': yyyy-mm format (or empty string)
    - 'text': plain text content
    """
    try:
        parser = etree.XMLParser(recover=True)
        tree = etree.parse(path, parser)
        root = tree.getroot()
        
        # Find all section elements
        namespaces = {'bits': 'https://jats.nlm.nih.gov/extensions/bits/2.1/xsd/BITS-book2-1.xsd'}
        sections = root.findall('.//bits:sec', namespaces)
        
        articles = []
        for sec in sections:
            # Extract section ID
            sec_id = sec.get('id', '')
            
            # Extract date
            date_str = extract_date_from_section(sec) or ''
            
            # Extract text
            text = extract_text_from_element(sec)
            
            if text:  # Only include sections with actual content
                articles.append({
                    'id': sec_id,
                    'date': date_str,
                    'text': text
                })
        
        return articles
    except Exception:
        return []


def save_articles_to_files(articles: List[Dict[str, str]], output_dir: str) -> int:
    """Save articles to individual text files in output_dir.
    
    Filenames use pattern: {date}_{id}.txt or just {id}.txt if no date.
    Creates output_dir if it doesn't exist.
    
    Returns count of files written.
    """
    if not articles:
        return 0
    
    os.makedirs(output_dir, exist_ok=True)
    
    count = 0
    for article in articles:
        # Build filename
        if article['date']:
            filename = f"{article['date']}_{article['id']}.txt"
        else:
            filename = f"{article['id']}.txt"
        
        filepath = os.path.join(output_dir, filename)
        
        # Write the text content
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(article['text'])
            count += 1
        except Exception:
            # Skip files that can't be written
            continue
    
    return count


def process_xml_to_output(xml_path: str, output_dir: str) -> int:
    """Process a single XML file and save articles to output directory.
    
    Returns number of files created.
    """
    articles = parse_xml_to_articles(xml_path)
    return save_articles_to_files(articles, output_dir)


def parse_docs_directory_to_texts(docs_dir: str, recursive: bool = True) -> List[tuple]:
    """Find XML files under `docs_dir` and return list of (filename, text).

    Behavior:
    - Walks the directory recursively (if recursive=True) or non-recursively.
    - Only files ending with .xml (case-insensitive) are processed.
    - Returns an empty list if docs_dir doesn't exist or contains no xml files.
    
    Args:
        docs_dir: Directory to search for XML files
        recursive: If True, search subdirectories recursively
    """
    if not os.path.isdir(docs_dir):
        return []

    results: List[tuple] = []
    
    if recursive:
        # Recursively walk through all subdirectories
        for root, dirs, files in os.walk(docs_dir):
            for name in files:
                if not name.lower().endswith('.xml'):
                    continue
                path = os.path.join(root, name)
                text = parse_xml_file_to_text(path)
                # Use relative path from docs_dir for the filename
                rel_path = os.path.relpath(path, docs_dir)
                results.append((rel_path, text))
    else:
        # Only process files directly under docs_dir
        for name in os.listdir(docs_dir):
            if not name.lower().endswith('.xml'):
                continue
            path = os.path.join(docs_dir, name)
            if not os.path.isfile(path):
                continue
            text = parse_xml_file_to_text(path)
            results.append((name, text))

    return results


if __name__ == "__main__":
    # Quick manual test when run as script
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(here, '..'))
    docs = os.path.join(project_root, 'docs')
    output = os.path.join(project_root, 'output')
    
    # Process all XML files in docs directory (recursively)
    total_files = 0
    xml_count = 0
    
    for root, dirs, files in os.walk(docs):
        for name in files:
            if not name.lower().endswith('.xml'):
                continue
            xml_path = os.path.join(root, name)
            xml_count += 1
            
            # Show relative path for clarity
            rel_path = os.path.relpath(xml_path, docs)
            print(f"Processing {rel_path}...")
            count = process_xml_to_output(xml_path, output)
            total_files += count
            print(f"  Created {count} article files")
    
    print(f"\nProcessed {xml_count} XML file(s)")
    print(f"Total: {total_files} article files written to {output}")
