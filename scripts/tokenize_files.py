import os
import sys
import json

# allow importing from src
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from src.tokenizer import ensure_nltk_data, tokenize_directory, get_token_statistics


def main():
    project_root = ROOT
    output_dir = os.path.join(project_root, 'output')
    
    if not os.path.isdir(output_dir):
        print(f'Output directory not found: {output_dir}')
        print('Run the XML parser first to generate text files.')
        return
    
    # Ensure NLTK data is available
    ensure_nltk_data()
    
    print(f"Tokenizing all text files in: {output_dir}\n")
    
    # Tokenize all files
    results = tokenize_directory(output_dir)
    
    if not results:
        print("No files to tokenize.")
        return
    
    print(f"\n{'='*60}")
    print(f"Tokenization Summary")
    print(f"{'='*60}")
    print(f"Total files processed: {len(results)}")
    
    # Calculate overall statistics
    total_tokens = sum(len(tokens) for tokens in results.values())
    all_unique_tokens = set()
    for tokens in results.values():
        all_unique_tokens.update(tokens)
    
    print(f"Total tokens across all files: {total_tokens:,}")
    print(f"Unique tokens across all files: {len(all_unique_tokens):,}")
    print(f"Average tokens per file: {total_tokens / len(results):.1f}")
    
    # Show statistics for a few sample files
    print(f"\n{'='*60}")
    print("Sample File Statistics")
    print(f"{'='*60}")
    
    sample_files = sorted(results.items())[:5]
    for filename, tokens in sample_files:
        stats = get_token_statistics(tokens)
        print(f"\n{filename}:")
        print(f"  Total tokens: {stats['total_tokens']:,}")
        print(f"  Unique tokens: {stats['unique_tokens']:,}")
        print(f"  Avg token length: {stats['avg_token_length']:.2f} chars")
        print(f"  Sample tokens: {', '.join(tokens[:15])}")
    
    # Option to save tokenized data
    print(f"\n{'='*60}")
    save_path = os.path.join(project_root, 'data', 'tokenized_summary.json')
    
    # Create summary data
    summary = {
        'total_files': len(results),
        'total_tokens': total_tokens,
        'unique_tokens': len(all_unique_tokens),
        'files': {}
    }
    
    for filename, tokens in results.items():
        summary['files'][filename] = {
            'token_count': len(tokens),
            'unique_count': len(set(tokens)),
            'tokens': tokens  # Include full token list
        }
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Tokenized data saved to: {save_path}")
    print(f"File size: {os.path.getsize(save_path):,} bytes")


if __name__ == '__main__':
    main()
