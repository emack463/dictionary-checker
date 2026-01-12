import os
from typing import List, Dict
import nltk
from nltk.tokenize import word_tokenize


def ensure_nltk_data():
    """Download required NLTK data if not already present."""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Downloading NLTK punkt tokenizer...")
        nltk.download('punkt', quiet=True)
    
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        try:
            nltk.download('punkt_tab', quiet=True)
        except:
            pass  # punkt_tab may not be available in all versions


def tokenize_file(filepath: str) -> List[str]:
    """Read a text file and return list of tokens.
    
    Args:
        filepath: Path to the text file to tokenize
        
    Returns:
        List of tokens (words)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        tokens = word_tokenize(text)
        return tokens
    except Exception as e:
        print(f"Error tokenizing {filepath}: {e}")
        return []


def tokenize_directory(directory: str) -> Dict[str, List[str]]:
    """Tokenize all text files in a directory.
    
    Args:
        directory: Path to directory containing text files
        
    Returns:
        Dictionary mapping filename to list of tokens
    """
    if not os.path.isdir(directory):
        return {}
    
    results = {}
    files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    
    print(f"Tokenizing {len(files)} files...")
    for i, filename in enumerate(files, 1):
        filepath = os.path.join(directory, filename)
        tokens = tokenize_file(filepath)
        results[filename] = tokens
        
        if i % 100 == 0:
            print(f"  Processed {i}/{len(files)} files...")
    
    return results


def get_token_statistics(tokens: List[str]) -> Dict[str, int]:
    """Calculate basic statistics for a list of tokens.
    
    Returns:
        Dictionary with token count, unique tokens, etc.
    """
    return {
        'total_tokens': len(tokens),
        'unique_tokens': len(set(tokens)),
        'avg_token_length': sum(len(t) for t in tokens) / len(tokens) if tokens else 0
    }


if __name__ == "__main__":
    # Test tokenization
    ensure_nltk_data()
    
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(here, '..'))
    output_dir = os.path.join(project_root, 'output')
    
    print(f"Tokenizing files in: {output_dir}\n")
    results = tokenize_directory(output_dir)
    
    print(f"\nTokenization complete!")
    print(f"Files processed: {len(results)}")
    
    # Show sample statistics
    if results:
        sample_files = list(results.items())[:3]
        print("\nSample token statistics:")
        for filename, tokens in sample_files:
            stats = get_token_statistics(tokens)
            print(f"\n{filename}:")
            print(f"  Total tokens: {stats['total_tokens']:,}")
            print(f"  Unique tokens: {stats['unique_tokens']:,}")
            print(f"  Avg token length: {stats['avg_token_length']:.2f}")
            print(f"  First 10 tokens: {tokens[:10]}")
