import os
import sys

# allow importing from src
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from src.xml_parser import process_xml_to_output


def main():
    project_root = ROOT
    docs = os.path.join(project_root, 'docs')
    output = os.path.join(project_root, 'output')
    
    if not os.path.isdir(docs):
        print(f'Docs directory not found: {docs}')
        return
    
    # Process all XML files recursively
    total_files = 0
    xml_count = 0
    
    for root, dirs, files in os.walk(docs):
        for name in files:
            if not name.lower().endswith('.xml'):
                continue
            xml_path = os.path.join(root, name)
            xml_count += 1
            
            # Show relative path for better context
            rel_path = os.path.relpath(xml_path, docs)
            print(f"Processing {rel_path}...")
            count = process_xml_to_output(xml_path, output)
            total_files += count
            print(f"  -> Created {count} text files")
    
    print(f"\nProcessed {xml_count} XML file(s)")
    print(f"Total: {total_files} article files written to '{output}'")
    
    # Show a sample of what was created
    if total_files > 0:
        print("\nSample files created:")
        output_files = sorted(os.listdir(output))[:5]
        for fname in output_files:
            fpath = os.path.join(output, fname)
            size = os.path.getsize(fpath)
            print(f"  - {fname} ({size:,} bytes)")


if __name__ == '__main__':
    main()
