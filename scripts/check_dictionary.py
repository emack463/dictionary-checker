import os
import sys
import json
import re

# allow importing from src
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from src.dictionary_checker import check_tokenized_files


def categorize_unknown_words(unknown_words):
    """Categorize unknown words into different types."""
    categories = {
        'punctuation': [],
        'numbers': [],
        'mixed_alphanumeric': [],
        'hyphenated': [],
        'possessives': [],
        'contractions': [],
        'potential_misspellings': [],
        'other': []
    }
    
    for word in unknown_words:
        # Punctuation only
        if re.match(r'^[^\w]+$', word):
            categories['punctuation'].append(word)
        # Numbers only
        elif re.match(r'^[\d,.\-]+$', word):
            categories['numbers'].append(word)
        # Mixed alphanumeric
        elif re.match(r'^.*\d+.*[a-zA-Z]+.*$', word) or re.match(r'^.*[a-zA-Z]+.*\d+.*$', word):
            categories['mixed_alphanumeric'].append(word)
        # Hyphenated words
        elif '-' in word and any(c.isalpha() for c in word):
            categories['hyphenated'].append(word)
        # Possessives (ends with 's)
        elif word.endswith("'s") or word.endswith("s'"):
            categories['possessives'].append(word)
        # Contractions
        elif "'" in word:
            categories['contractions'].append(word)
        # Potential real misspellings (only letters, longer than 2 chars)
        elif word.isalpha() and len(word) > 2:
            categories['potential_misspellings'].append(word)
        else:
            categories['other'].append(word)
    
    return categories


def main():
    project_root = ROOT
    
    db_path = os.path.join(project_root, 'data', 'dictionary.db')
    tokenized_path = os.path.join(project_root, 'data', 'tokenized_summary.json')
    output_path = os.path.join(project_root, 'data', 'dictionary_check_results.json')
    
    print("="*70)
    print("LEXICAL CHECKER - Dictionary Validation")
    print("="*70)
    print()
    
    # Run dictionary check
    results = check_tokenized_files(tokenized_path, db_path, output_path)
    
    # Display summary
    print("\n" + "="*70)
    print("OVERALL SUMMARY")
    print("="*70)
    print(f"Files processed: {results['summary']['total_files']:,}")
    print(f"Total tokens: {results['summary']['total_tokens']:,}")
    print(f"Dictionary size: {results['summary']['dictionary_words']:,} words")
    print()
    print(f"✓ Found in dictionary: {results['summary']['total_found']:,} ({results['summary']['found_percentage']:.2f}%)")
    print(f"✗ Not found: {results['summary']['total_not_found']:,}")
    print(f"  Unique unknown: {results['summary']['unique_not_found_words']:,}")
    
    # Categorize unknown words
    print("\n" + "="*70)
    print("UNKNOWN WORDS ANALYSIS")
    print("="*70)
    
    categories = categorize_unknown_words(results['summary']['all_not_found_words'])
    
    print("\nBreakdown by category:")
    for category, words in categories.items():
        if words:
            print(f"\n{category.upper().replace('_', ' ')} ({len(words):,} unique):")
            sample = words[:10]
            for word in sample:
                print(f"  - {word}")
            if len(words) > 10:
                print(f"  ... and {len(words) - 10:,} more")
    
    # Show files with most unknown words
    print("\n" + "="*70)
    print("FILES WITH MOST UNKNOWN WORDS")
    print("="*70)
    
    files_sorted = sorted(
        results['files'].items(),
        key=lambda x: x[1]['not_found_count'],
        reverse=True
    )
    
    for i, (filename, data) in enumerate(files_sorted[:10], 1):
        pct = data['found_percentage']
        print(f"{i}. {filename}")
        print(f"   Found: {data['found_count']}/{data['total_tokens']} ({pct:.1f}%)")
        print(f"   Unknown: {data['not_found_count']} ({data['unique_not_found']} unique)")
    
    # Save categorized analysis
    analysis_path = os.path.join(project_root, 'data', 'unknown_words_analysis.json')
    analysis_data = {
        'summary': results['summary'],
        'categories': {k: v for k, v in categories.items()},
        'category_counts': {k: len(v) for k, v in categories.items()}
    }
    
    with open(analysis_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2)
    
    print(f"\nDetailed analysis saved to: {analysis_path}")


if __name__ == '__main__':
    main()
