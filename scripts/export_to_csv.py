import os
import sys
import json
import csv

# allow importing from src
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)


def export_to_csv(results_json_path: str, output_csv_path: str):
    """Export dictionary check results to CSV format.
    
    Args:
        results_json_path: Path to dictionary_check_results.json
        output_csv_path: Path for output CSV file
    """
    print(f"Loading results from: {results_json_path}")
    with open(results_json_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print(f"Exporting {len(results['files'])} files to CSV...")
    
    # Write main results CSV
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'filename',
            'date',
            'article_id',
            'total_tokens',
            'found_count',
            'not_found_count',
            'unique_found',
            'unique_not_found',
            'found_percentage',
            'not_found_words'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for filename, data in sorted(results['files'].items()):
            # Extract date and ID from filename (format: YYYY-MM_ID.txt)
            parts = filename.replace('.txt', '').split('_')
            date = parts[0] if len(parts) > 0 else ''
            article_id = parts[1] if len(parts) > 1 else ''
            
            # Join unknown words with semicolon separator
            not_found_words = '; '.join(data.get('not_found_tokens', []))
            
            writer.writerow({
                'filename': filename,
                'date': date,
                'article_id': article_id,
                'total_tokens': data['total_tokens'],
                'found_count': data['found_count'],
                'not_found_count': data['not_found_count'],
                'unique_found': data['unique_found'],
                'unique_not_found': data['unique_not_found'],
                'found_percentage': round(data['found_percentage'], 2),
                'not_found_words': not_found_words
            })
    
    print(f"✓ Main results exported to: {output_csv_path}")
    print(f"  File size: {os.path.getsize(output_csv_path):,} bytes")
    
    # Create summary CSV
    summary_csv_path = output_csv_path.replace('.csv', '_summary.csv')
    with open(summary_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Files', results['summary']['total_files']])
        writer.writerow(['Total Tokens', results['summary']['total_tokens']])
        writer.writerow(['Tokens Found in Dictionary', results['summary']['total_found']])
        writer.writerow(['Tokens Not Found', results['summary']['total_not_found']])
        writer.writerow(['Found Percentage', f"{results['summary']['found_percentage']:.2f}%"])
        writer.writerow(['Unique Unknown Words', results['summary']['unique_not_found_words']])
    
    print(f"✓ Summary exported to: {summary_csv_path}")
    print(f"  File size: {os.path.getsize(summary_csv_path):,} bytes")


def export_unknown_words_to_csv(analysis_json_path: str, output_csv_path: str):
    """Export categorized unknown words to CSV.
    
    Args:
        analysis_json_path: Path to unknown_words_analysis.json
        output_csv_path: Path for output CSV file
    """
    print(f"\nLoading unknown words analysis from: {analysis_json_path}")
    with open(analysis_json_path, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    # Export categorized words
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['word', 'category']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for category, words in analysis['categories'].items():
            for word in sorted(words):
                writer.writerow({
                    'word': word,
                    'category': category
                })
    
    print(f"✓ Unknown words exported to: {output_csv_path}")
    print(f"  File size: {os.path.getsize(output_csv_path):,} bytes")
    print(f"  Total unique unknown words: {sum(analysis['category_counts'].values()):,}")
    
    # Export category counts
    category_csv_path = output_csv_path.replace('.csv', '_categories.csv')
    with open(category_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Category', 'Count'])
        for category, count in sorted(analysis['category_counts'].items(), key=lambda x: x[1], reverse=True):
            writer.writerow([category.replace('_', ' ').title(), count])
    
    print(f"✓ Category summary exported to: {category_csv_path}")
    print(f"  File size: {os.path.getsize(category_csv_path):,} bytes")


def main():
    project_root = ROOT
    
    results_json = os.path.join(project_root, 'data', 'dictionary_check_results.json')
    analysis_json = os.path.join(project_root, 'data', 'unknown_words_analysis.json')
    
    output_dir = os.path.join(project_root, 'data')
    results_csv = os.path.join(output_dir, 'dictionary_results.csv')
    unknown_words_csv = os.path.join(output_dir, 'unknown_words.csv')
    
    print("="*70)
    print("CSV Export - Dictionary Check Results")
    print("="*70)
    print()
    
    # Check if input files exist
    if not os.path.exists(results_json):
        print(f"Error: {results_json} not found!")
        print("Run check_dictionary.py first to generate results.")
        return
    
    if not os.path.exists(analysis_json):
        print(f"Error: {analysis_json} not found!")
        print("Run check_dictionary.py first to generate analysis.")
        return
    
    # Export results
    export_to_csv(results_json, results_csv)
    
    # Export unknown words analysis
    export_unknown_words_to_csv(analysis_json, unknown_words_csv)
    
    print("\n" + "="*70)
    print("Export Complete!")
    print("="*70)
    print("\nGenerated files:")
    print(f"  1. {results_csv}")
    print(f"  2. {results_csv.replace('.csv', '_summary.csv')}")
    print(f"  3. {unknown_words_csv}")
    print(f"  4. {unknown_words_csv.replace('.csv', '_categories.csv')}")
    print("\nThese files can be opened directly in Excel or imported into other tools.")


if __name__ == '__main__':
    main()
