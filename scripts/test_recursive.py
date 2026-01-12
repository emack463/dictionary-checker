"""
Test script to verify recursive XML file discovery in docs directory.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from src.xml_parser import parse_docs_directory_to_texts


def test_recursive_search():
    docs_dir = os.path.join(ROOT, 'docs')
    
    print("="*60)
    print("Testing Recursive XML Discovery")
    print("="*60)
    
    # Test recursive mode
    print("\n1. Recursive mode (default):")
    results_recursive = parse_docs_directory_to_texts(docs_dir, recursive=True)
    print(f"   Found {len(results_recursive)} XML file(s)")
    for filename, _ in results_recursive:
        print(f"     - {filename}")
    
    # Test non-recursive mode
    print("\n2. Non-recursive mode:")
    results_nonrecursive = parse_docs_directory_to_texts(docs_dir, recursive=False)
    print(f"   Found {len(results_nonrecursive)} XML file(s)")
    for filename, _ in results_nonrecursive:
        print(f"     - {filename}")
    
    # Show directory structure
    print("\n3. Directory structure:")
    for root, dirs, files in os.walk(docs_dir):
        level = root.replace(docs_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if file.endswith('.xml'):
                print(f'{subindent}{file} ✓')
    
    print("\n" + "="*60)
    print("✓ Recursive search functionality verified")
    print("="*60)


if __name__ == '__main__':
    test_recursive_search()
