import os
import sys
import json
import csv
from collections import defaultdict

# allow importing from src
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)


def extract_year_from_filename(filename):
    """Extract year from filename (format: YYYY-MM_ID.txt).
    
    Args:
        filename: The filename to parse
        
    Returns:
        Year as string (e.g., '1817') or 'Unknown'
    """
    try:
        # Expected format: 1817-01_486376978.txt
        parts = filename.split('-')
        if len(parts) > 0 and parts[0].isdigit() and len(parts[0]) == 4:
            return parts[0]
    except:
        pass
    return 'Unknown'


def generate_yearly_summary(results_json_path, output_csv_path):
    """Generate a year-based summary report in CSV format.
    
    Args:
        results_json_path: Path to dictionary_check_results.json
        output_csv_path: Path for output CSV file
    """
    print(f"Loading results from: {results_json_path}")
    with open(results_json_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Aggregate data by year
    yearly_data = defaultdict(lambda: {
        'file_count': 0,
        'total_tokens': 0,
        'found_count': 0,
        'not_found_count': 0,
        'unique_not_found': set()
    })
    
    print(f"Processing {len(results['files'])} files...")
    
    for filename, data in results['files'].items():
        year = extract_year_from_filename(filename)
        
        yearly_data[year]['file_count'] += 1
        yearly_data[year]['total_tokens'] += data['total_tokens']
        yearly_data[year]['found_count'] += data['found_count']
        yearly_data[year]['not_found_count'] += data['not_found_count']
        
        # Track unique unknown words across all files in the year
        if 'not_found_tokens' in data:
            yearly_data[year]['unique_not_found'].update([w.lower() for w in data['not_found_tokens']])
    
    # Write to CSV
    print(f"\nExporting yearly summary to CSV...")
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'year',
            'file_count',
            'total_tokens',
            'found_count',
            'not_found_count',
            'found_percentage',
            'avg_tokens_per_file',
            'unique_not_found_words',
            'error_rate_per_token'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Sort by year
        for year in sorted(yearly_data.keys()):
            data = yearly_data[year]
            
            found_pct = (data['found_count'] / data['total_tokens'] * 100) if data['total_tokens'] > 0 else 0
            avg_tokens = data['total_tokens'] / data['file_count'] if data['file_count'] > 0 else 0
            unique_not_found = len(data['unique_not_found'])
            error_rate = (data['not_found_count'] / data['total_tokens'] * 100) if data['total_tokens'] > 0 else 0
            
            writer.writerow({
                'year': year,
                'file_count': data['file_count'],
                'total_tokens': data['total_tokens'],
                'found_count': data['found_count'],
                'not_found_count': data['not_found_count'],
                'found_percentage': round(found_pct, 2),
                'avg_tokens_per_file': round(avg_tokens, 1),
                'unique_not_found_words': unique_not_found,
                'error_rate_per_token': round(error_rate, 2)
            })
    
    print(f"✓ Yearly summary exported to: {output_csv_path}")
    print(f"  File size: {os.path.getsize(output_csv_path):,} bytes")
    print(f"  Years covered: {len(yearly_data)}")
    
    # Print summary to console
    print(f"\n{'='*80}")
    print("Yearly Summary Report")
    print(f"{'='*80}")
    print(f"{'Year':<8} {'Files':<8} {'Total Tokens':<15} {'Found %':<10} {'Avg/File':<12}")
    print(f"{'-'*80}")
    
    for year in sorted(yearly_data.keys()):
        data = yearly_data[year]
        found_pct = (data['found_count'] / data['total_tokens'] * 100) if data['total_tokens'] > 0 else 0
        avg_tokens = data['total_tokens'] / data['file_count'] if data['file_count'] > 0 else 0
        
        print(f"{year:<8} {data['file_count']:<8} {data['total_tokens']:<15,} {found_pct:<10.2f} {avg_tokens:<12.1f}")
    
    print(f"{'='*80}\n")


def generate_monthly_summary(results_json_path, output_csv_path):
    """Generate a year-month based summary report in CSV format.
    
    Args:
        results_json_path: Path to dictionary_check_results.json
        output_csv_path: Path for output CSV file
    """
    print(f"Loading results from: {results_json_path}")
    with open(results_json_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Aggregate data by year-month
    monthly_data = defaultdict(lambda: {
        'file_count': 0,
        'total_tokens': 0,
        'found_count': 0,
        'not_found_count': 0,
        'unique_not_found': set()
    })
    
    print(f"Processing {len(results['files'])} files...")
    
    for filename, data in results['files'].items():
        try:
            # Expected format: 1817-01_486376978.txt
            date_part = filename.split('_')[0]  # Get "1817-01"
            if '-' in date_part:
                year_month = date_part  # Keep as "1817-01"
            else:
                year_month = 'Unknown'
        except:
            year_month = 'Unknown'
        
        monthly_data[year_month]['file_count'] += 1
        monthly_data[year_month]['total_tokens'] += data['total_tokens']
        monthly_data[year_month]['found_count'] += data['found_count']
        monthly_data[year_month]['not_found_count'] += data['not_found_count']
        
        # Track unique unknown words
        if 'not_found_tokens' in data:
            monthly_data[year_month]['unique_not_found'].update([w.lower() for w in data['not_found_tokens']])
    
    # Write to CSV
    print(f"\nExporting monthly summary to CSV...")
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'year_month',
            'year',
            'month',
            'file_count',
            'total_tokens',
            'found_count',
            'not_found_count',
            'found_percentage',
            'avg_tokens_per_file',
            'unique_not_found_words',
            'error_rate_per_token'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Sort by year-month
        for year_month in sorted(monthly_data.keys()):
            data = monthly_data[year_month]
            
            # Split year and month
            if '-' in year_month and year_month != 'Unknown':
                year, month = year_month.split('-')
            else:
                year, month = year_month, ''
            
            found_pct = (data['found_count'] / data['total_tokens'] * 100) if data['total_tokens'] > 0 else 0
            avg_tokens = data['total_tokens'] / data['file_count'] if data['file_count'] > 0 else 0
            unique_not_found = len(data['unique_not_found'])
            error_rate = (data['not_found_count'] / data['total_tokens'] * 100) if data['total_tokens'] > 0 else 0
            
            writer.writerow({
                'year_month': year_month,
                'year': year,
                'month': month,
                'file_count': data['file_count'],
                'total_tokens': data['total_tokens'],
                'found_count': data['found_count'],
                'not_found_count': data['not_found_count'],
                'found_percentage': round(found_pct, 2),
                'avg_tokens_per_file': round(avg_tokens, 1),
                'unique_not_found_words': unique_not_found,
                'error_rate_per_token': round(error_rate, 2)
            })
    
    print(f"✓ Monthly summary exported to: {output_csv_path}")
    print(f"  File size: {os.path.getsize(output_csv_path):,} bytes")
    print(f"  Periods covered: {len(monthly_data)}")


def main():
    project_root = ROOT
    
    results_json = os.path.join(project_root, 'data', 'dictionary_check_results.json')
    output_dir = os.path.join(project_root, 'data')
    
    yearly_csv = os.path.join(output_dir, 'yearly_summary.csv')
    monthly_csv = os.path.join(output_dir, 'monthly_summary.csv')
    
    print("="*80)
    print("Yearly Summary Report Generator")
    print("="*80)
    print()
    
    # Check if input file exists
    if not os.path.exists(results_json):
        print(f"Error: {results_json} not found!")
        print("Run check_dictionary.py first to generate results.")
        return
    
    # Generate yearly summary
    generate_yearly_summary(results_json, yearly_csv)
    
    print()
    
    # Generate monthly summary
    generate_monthly_summary(results_json, monthly_csv)
    
    print(f"\n{'='*80}")
    print("Export Complete!")
    print(f"{'='*80}")
    print(f"\nGenerated files:")
    print(f"  1. {yearly_csv}")
    print(f"  2. {monthly_csv}")
    print(f"\nYou can now open these files in Excel for analysis.")


if __name__ == "__main__":
    main()
