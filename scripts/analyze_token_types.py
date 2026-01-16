import os
import sys
import json
import csv
import re
from collections import defaultdict, Counter

# allow importing from src
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)


def classify_token(token):
    """Classify a token into a specific type.
    
    Returns:
        Tuple of (main_category, subcategory)
    """
    # Pure punctuation
    if re.match(r'^[^\w]+$', token):
        return ('punctuation', 'symbol_only')
    
    # Pure numbers
    if re.match(r'^\d+$', token):
        return ('numeric', 'integer')
    
    # Decimal/formatted numbers
    if re.match(r'^[\d,.\-]+$', token):
        return ('numeric', 'formatted_number')
    
    # Currency/financial
    if re.match(r'^[$£€]\d+', token) or re.match(r'^\d+[$£€]', token):
        return ('numeric', 'currency')
    
    # Pure alphabetic (normal words)
    if token.isalpha():
        if token.isupper():
            return ('alphabetic', 'all_uppercase')
        elif token[0].isupper():
            return ('alphabetic', 'capitalized')
        else:
            return ('alphabetic', 'lowercase')
    
    # Mixed alphanumeric
    if re.match(r'^.*\d+.*[a-zA-Z]+.*$', token) or re.match(r'^.*[a-zA-Z]+.*\d+.*$', token):
        return ('mixed', 'alphanumeric')
    
    # Hyphenated words (has letters and hyphen)
    if '-' in token and any(c.isalpha() for c in token):
        return ('compound', 'hyphenated')
    
    # Possessives
    if token.endswith("'s") or token.endswith("s'"):
        return ('grammatical', 'possessive')
    
    # Contractions
    if "'" in token and any(c.isalpha() for c in token):
        return ('grammatical', 'contraction')
    
    # URLs/emails
    if '@' in token or 'http' in token.lower() or 'www.' in token.lower():
        return ('special', 'url_email')
    
    # Other
    return ('other', 'unclassified')


def analyze_all_tokens(tokenized_json_path, dict_results_path):
    """Analyze all tokens from the tokenized data."""
    
    print(f"Loading tokenized data from: {tokenized_json_path}")
    with open(tokenized_json_path, 'r', encoding='utf-8') as f:
        tokenized_data = json.load(f)
    
    print(f"Loading dictionary results from: {dict_results_path}")
    with open(dict_results_path, 'r', encoding='utf-8') as f:
        dict_results = json.load(f)
    
    # Create sets for quick lookup
    found_words = set()
    not_found_words = set(dict_results['summary']['all_not_found_words'])
    
    # Statistics collectors
    token_type_counts = defaultdict(int)
    token_subtype_counts = defaultdict(int)
    token_length_distribution = defaultdict(int)
    
    # Category-specific data
    category_examples = defaultdict(list)
    category_unique = defaultdict(set)
    
    # Found vs not found by type
    found_by_type = defaultdict(int)
    not_found_by_type = defaultdict(int)
    
    # Case sensitivity analysis
    case_distribution = defaultdict(int)
    
    print(f"\nProcessing {tokenized_data['total_files']} files...")
    
    all_tokens = []
    file_count = 0
    
    for filename, file_data in tokenized_data['files'].items():
        file_count += 1
        tokens = file_data['tokens']
        all_tokens.extend(tokens)
        
        if file_count % 500 == 0:
            print(f"  Processed {file_count}/{tokenized_data['total_files']} files...")
    
    print(f"\nAnalyzing {len(all_tokens):,} total tokens...")
    
    for token in all_tokens:
        # Classify token
        main_cat, sub_cat = classify_token(token)
        token_type_counts[main_cat] += 1
        token_subtype_counts[f"{main_cat}:{sub_cat}"] += 1
        
        # Track unique tokens per category
        category_unique[main_cat].add(token.lower())
        
        # Store examples (limited)
        if len(category_examples[f"{main_cat}:{sub_cat}"]) < 20:
            if token not in category_examples[f"{main_cat}:{sub_cat}"]:
                category_examples[f"{main_cat}:{sub_cat}"].append(token)
        
        # Length distribution
        token_length_distribution[len(token)] += 1
        
        # Found vs not found
        token_lower = token.lower()
        if token_lower in not_found_words:
            not_found_by_type[main_cat] += 1
        else:
            found_by_type[main_cat] += 1
        
        # Case analysis for alphabetic tokens
        if token.isalpha():
            if token.isupper():
                case_distribution['all_uppercase'] += 1
            elif token.islower():
                case_distribution['all_lowercase'] += 1
            elif token[0].isupper() and token[1:].islower():
                case_distribution['capitalized'] += 1
            else:
                case_distribution['mixed_case'] += 1
    
    return {
        'total_tokens': len(all_tokens),
        'total_files': tokenized_data['total_files'],
        'type_counts': dict(token_type_counts),
        'subtype_counts': dict(token_subtype_counts),
        'length_distribution': dict(token_length_distribution),
        'category_examples': {k: v for k, v in category_examples.items()},
        'category_unique_counts': {k: len(v) for k, v in category_unique.items()},
        'found_by_type': dict(found_by_type),
        'not_found_by_type': dict(not_found_by_type),
        'case_distribution': dict(case_distribution),
        'unique_tokens': len(set(t.lower() for t in all_tokens))
    }


def export_token_type_summary(analysis_data, output_csv_path):
    """Export token type analysis to CSV."""
    
    print(f"\nExporting token type summary to CSV...")
    
    # Main summary CSV
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'token_type',
            'token_count',
            'percentage',
            'unique_count',
            'found_in_dict',
            'not_found_in_dict',
            'accuracy_rate'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        total_tokens = analysis_data['total_tokens']
        
        for token_type in sorted(analysis_data['type_counts'].keys()):
            count = analysis_data['type_counts'][token_type]
            unique_count = analysis_data['category_unique_counts'].get(token_type, 0)
            found = analysis_data['found_by_type'].get(token_type, 0)
            not_found = analysis_data['not_found_by_type'].get(token_type, 0)
            
            accuracy = (found / (found + not_found) * 100) if (found + not_found) > 0 else 0
            
            writer.writerow({
                'token_type': token_type.title(),
                'token_count': count,
                'percentage': round(count / total_tokens * 100, 2),
                'unique_count': unique_count,
                'found_in_dict': found,
                'not_found_in_dict': not_found,
                'accuracy_rate': round(accuracy, 2)
            })
    
    print(f"✓ Token type summary exported to: {output_csv_path}")
    print(f"  File size: {os.path.getsize(output_csv_path):,} bytes")
    
    # Subtype detail CSV
    subtype_csv = output_csv_path.replace('.csv', '_detailed.csv')
    with open(subtype_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'main_type',
            'subtype',
            'token_count',
            'percentage',
            'examples'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        total_tokens = analysis_data['total_tokens']
        
        for subtype_key in sorted(analysis_data['subtype_counts'].keys()):
            main_type, subtype = subtype_key.split(':', 1)
            count = analysis_data['subtype_counts'][subtype_key]
            examples = analysis_data['category_examples'].get(subtype_key, [])
            
            writer.writerow({
                'main_type': main_type.title(),
                'subtype': subtype.replace('_', ' ').title(),
                'token_count': count,
                'percentage': round(count / total_tokens * 100, 2),
                'examples': '; '.join(examples[:10])
            })
    
    print(f"✓ Detailed subtype analysis exported to: {subtype_csv}")
    print(f"  File size: {os.path.getsize(subtype_csv):,} bytes")
    
    # Length distribution CSV
    length_csv = output_csv_path.replace('.csv', '_length_distribution.csv')
    with open(length_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Token Length', 'Count', 'Percentage'])
        
        total_tokens = analysis_data['total_tokens']
        
        for length in sorted(analysis_data['length_distribution'].keys()):
            count = analysis_data['length_distribution'][length]
            writer.writerow([
                length,
                count,
                round(count / total_tokens * 100, 2)
            ])
    
    print(f"✓ Length distribution exported to: {length_csv}")
    print(f"  File size: {os.path.getsize(length_csv):,} bytes")
    
    # Case distribution CSV (for alphabetic tokens)
    case_csv = output_csv_path.replace('.csv', '_case_distribution.csv')
    with open(case_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Case Type', 'Count', 'Percentage'])
        
        total_case_tokens = sum(analysis_data['case_distribution'].values())
        
        for case_type in sorted(analysis_data['case_distribution'].keys()):
            count = analysis_data['case_distribution'][case_type]
            writer.writerow([
                case_type.replace('_', ' ').title(),
                count,
                round(count / total_case_tokens * 100, 2) if total_case_tokens > 0 else 0
            ])
    
    print(f"✓ Case distribution exported to: {case_csv}")
    print(f"  File size: {os.path.getsize(case_csv):,} bytes")


def print_summary_report(analysis_data):
    """Print a formatted summary report to console."""
    
    print("\n" + "="*80)
    print("TOKEN TYPE ANALYSIS SUMMARY")
    print("="*80)
    print(f"\nTotal Files Analyzed: {analysis_data['total_files']:,}")
    print(f"Total Tokens: {analysis_data['total_tokens']:,}")
    print(f"Unique Tokens (case-insensitive): {analysis_data['unique_tokens']:,}")
    
    print("\n" + "-"*80)
    print("TOKEN TYPE DISTRIBUTION")
    print("-"*80)
    print(f"{'Type':<20} {'Count':<15} {'Percentage':<12} {'Unique':<12}")
    print("-"*80)
    
    total = analysis_data['total_tokens']
    for token_type in sorted(analysis_data['type_counts'].keys(), 
                            key=lambda x: analysis_data['type_counts'][x], 
                            reverse=True):
        count = analysis_data['type_counts'][token_type]
        unique = analysis_data['category_unique_counts'].get(token_type, 0)
        pct = count / total * 100
        print(f"{token_type.title():<20} {count:<15,} {pct:<12.2f} {unique:<12,}")
    
    print("\n" + "-"*80)
    print("DICTIONARY MATCH RATES BY TYPE")
    print("-"*80)
    print(f"{'Type':<20} {'Found':<15} {'Not Found':<15} {'Accuracy %':<12}")
    print("-"*80)
    
    for token_type in sorted(analysis_data['type_counts'].keys()):
        found = analysis_data['found_by_type'].get(token_type, 0)
        not_found = analysis_data['not_found_by_type'].get(token_type, 0)
        total_type = found + not_found
        accuracy = (found / total_type * 100) if total_type > 0 else 0
        
        print(f"{token_type.title():<20} {found:<15,} {not_found:<15,} {accuracy:<12.2f}")
    
    print("\n" + "-"*80)
    print("CASE DISTRIBUTION (Alphabetic Tokens Only)")
    print("-"*80)
    
    total_case = sum(analysis_data['case_distribution'].values())
    for case_type, count in sorted(analysis_data['case_distribution'].items(), 
                                   key=lambda x: x[1], 
                                   reverse=True):
        pct = count / total_case * 100 if total_case > 0 else 0
        print(f"{case_type.replace('_', ' ').title():<20} {count:<15,} {pct:<12.2f}%")
    
    print("\n" + "-"*80)
    print("TOP SUBTYPES")
    print("-"*80)
    
    sorted_subtypes = sorted(analysis_data['subtype_counts'].items(), 
                            key=lambda x: x[1], 
                            reverse=True)[:15]
    
    for subtype_key, count in sorted_subtypes:
        main_type, subtype = subtype_key.split(':', 1)
        pct = count / total * 100
        examples = analysis_data['category_examples'].get(subtype_key, [])
        print(f"\n{main_type.title()}: {subtype.replace('_', ' ').title()}")
        print(f"  Count: {count:,} ({pct:.2f}%)")
        if examples:
            print(f"  Examples: {', '.join(examples[:8])}")
    
    print("\n" + "="*80)


def main():
    project_root = ROOT
    
    tokenized_json = os.path.join(project_root, 'data', 'tokenized_summary.json')
    dict_results = os.path.join(project_root, 'data', 'dictionary_check_results.json')
    output_dir = os.path.join(project_root, 'data')
    
    output_csv = os.path.join(output_dir, 'token_type_summary.csv')
    analysis_json = os.path.join(output_dir, 'token_type_analysis.json')
    
    print("="*80)
    print("COMPLETE TOKEN TYPE ANALYSIS")
    print("="*80)
    print()
    
    # Check if input files exist
    if not os.path.exists(tokenized_json):
        print(f"Error: {tokenized_json} not found!")
        print("Run tokenize_files.py first to generate tokenized data.")
        return
    
    if not os.path.exists(dict_results):
        print(f"Error: {dict_results} not found!")
        print("Run check_dictionary.py first to generate dictionary results.")
        return
    
    # Perform analysis
    analysis_data = analyze_all_tokens(tokenized_json, dict_results)
    
    # Save analysis to JSON
    print(f"\nSaving detailed analysis to: {analysis_json}")
    with open(analysis_json, 'w', encoding='utf-8') as f:
        # Don't save category_examples in JSON (too large), just counts
        save_data = {k: v for k, v in analysis_data.items() if k != 'category_examples'}
        json.dump(save_data, f, indent=2)
    print(f"  File size: {os.path.getsize(analysis_json):,} bytes")
    
    # Export to CSV
    export_token_type_summary(analysis_data, output_csv)
    
    # Print summary report
    print_summary_report(analysis_data)
    
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"\nGenerated files:")
    print(f"  1. {output_csv}")
    print(f"  2. {output_csv.replace('.csv', '_detailed.csv')}")
    print(f"  3. {output_csv.replace('.csv', '_length_distribution.csv')}")
    print(f"  4. {output_csv.replace('.csv', '_case_distribution.csv')}")
    print(f"  5. {analysis_json}")
    print(f"\nAll files are ready to open in Excel for analysis.")


if __name__ == "__main__":
    main()
