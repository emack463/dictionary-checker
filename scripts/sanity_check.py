import json
import os

# Verify data integrity
data_dir = 'c:/Users/Ed/projects/lexical-checker/data'

print("="*60)
print("SANITY CHECK - Data Integrity")
print("="*60)

# Check dictionary_check_results.json
results_file = os.path.join(data_dir, 'dictionary_check_results.json')
if os.path.exists(results_file):
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    print(f"\n✓ dictionary_check_results.json")
    print(f"  Files: {len(results['files'])}")
    print(f"  Summary keys: {list(results['summary'].keys())}")
    if results['files']:
        first_file = list(results['files'].values())[0]
        print(f"  File entry keys: {list(first_file.keys())}")
else:
    print(f"\n✗ dictionary_check_results.json NOT FOUND")

# Check tokenized_summary.json
tokenized_file = os.path.join(data_dir, 'tokenized_summary.json')
if os.path.exists(tokenized_file):
    with open(tokenized_file, 'r', encoding='utf-8') as f:
        tokenized = json.load(f)
    print(f"\n✓ tokenized_summary.json")
    print(f"  Files: {len(tokenized['files'])}")
    print(f"  Total tokens: {tokenized['total_tokens']:,}")
    if tokenized['files']:
        first_file = list(tokenized['files'].values())[0]
        print(f"  Sample token count: {first_file['token_count']}")
else:
    print(f"\n✗ tokenized_summary.json NOT FOUND")

# Check CSV files
csv_files = [
    'dictionary_results.csv',
    'dictionary_results_summary.csv',
    'unknown_words.csv',
    'unknown_words_categories.csv'
]

print(f"\n{'='*60}")
print("CSV Files")
print("="*60)

for csv_file in csv_files:
    path = os.path.join(data_dir, csv_file)
    if os.path.exists(path):
        size = os.path.getsize(path)
        with open(path, 'r', encoding='utf-8') as f:
            lines = sum(1 for _ in f)
        print(f"✓ {csv_file}: {size:,} bytes, {lines:,} lines")
    else:
        print(f"✗ {csv_file}: NOT FOUND")

# Check output directory
output_dir = 'c:/Users/Ed/projects/lexical-checker/output'
if os.path.exists(output_dir):
    txt_files = [f for f in os.listdir(output_dir) if f.endswith('.txt')]
    total_size = sum(os.path.getsize(os.path.join(output_dir, f)) for f in txt_files)
    print(f"\n{'='*60}")
    print("Output Directory")
    print("="*60)
    print(f"✓ Text files: {len(txt_files)}")
    print(f"  Total size: {total_size:,} bytes")
else:
    print(f"\n✗ Output directory NOT FOUND")

print(f"\n{'='*60}")
print("Data Consistency Check")
print("="*60)

# Verify counts match
if os.path.exists(results_file) and os.path.exists(tokenized_file):
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    with open(tokenized_file, 'r', encoding='utf-8') as f:
        tokenized = json.load(f)
    
    if len(results['files']) == len(tokenized['files']):
        print(f"✓ File counts match: {len(results['files'])}")
    else:
        print(f"✗ File count mismatch!")
        print(f"  Results: {len(results['files'])}")
        print(f"  Tokenized: {len(tokenized['files'])}")
    
    if results['summary']['total_tokens'] == tokenized['total_tokens']:
        print(f"✓ Token counts match: {tokenized['total_tokens']:,}")
    else:
        print(f"✗ Token count mismatch!")
        print(f"  Results: {results['summary']['total_tokens']:,}")
        print(f"  Tokenized: {tokenized['total_tokens']:,}")

print("\n" + "="*60)
print("SANITY CHECK COMPLETE")
print("="*60)
