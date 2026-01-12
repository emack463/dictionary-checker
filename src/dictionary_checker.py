import os
import sqlite3
from typing import List, Dict, Set, Optional
import json


class DictionaryChecker:
    """Check tokens against an English dictionary in SQLite database."""
    
    def __init__(self, db_path: str):
        """Initialize the dictionary checker.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Cache for performance
        self._word_cache: Set[str] = set()
        self._cache_initialized = False
    
    def _initialize_cache(self):
        """Load all dictionary words into memory for faster lookups."""
        if self._cache_initialized:
            return
        
        print("Loading dictionary into memory...")
        self.cursor.execute("SELECT DISTINCT LOWER(word) FROM entries")
        self._word_cache = {row[0] for row in self.cursor.fetchall()}
        self._cache_initialized = True
        print(f"Loaded {len(self._word_cache):,} unique words")
    
    def is_in_dictionary(self, word: str, case_sensitive: bool = False) -> bool:
        """Check if a word exists in the dictionary.
        
        Args:
            word: The word to check
            case_sensitive: Whether to perform case-sensitive lookup
            
        Returns:
            True if word is in dictionary, False otherwise
        """
        self._initialize_cache()
        
        check_word = word if case_sensitive else word.lower()
        return check_word in self._word_cache
    
    def check_tokens(self, tokens: List[str]) -> Dict[str, bool]:
        """Check a list of tokens against the dictionary.
        
        Args:
            tokens: List of tokens to check
            
        Returns:
            Dictionary mapping each unique token to True/False (in dictionary or not)
        """
        self._initialize_cache()
        
        results = {}
        for token in tokens:
            # Check lowercase version
            token_lower = token.lower()
            if token_lower not in results:
                results[token_lower] = token_lower in self._word_cache
        
        return results
    
    def analyze_tokens(self, tokens: List[str]) -> Dict:
        """Analyze tokens and return detailed statistics.
        
        Args:
            tokens: List of tokens to analyze
            
        Returns:
            Dictionary with analysis results
        """
        self._initialize_cache()
        
        found_tokens = []
        not_found_tokens = []
        
        for token in tokens:
            token_lower = token.lower()
            if token_lower in self._word_cache:
                found_tokens.append(token)
            else:
                not_found_tokens.append(token)
        
        # Get unique counts
        unique_found = set(t.lower() for t in found_tokens)
        unique_not_found = set(t.lower() for t in not_found_tokens)
        
        return {
            'total_tokens': len(tokens),
            'found_count': len(found_tokens),
            'not_found_count': len(not_found_tokens),
            'unique_found': len(unique_found),
            'unique_not_found': len(unique_not_found),
            'found_percentage': (len(found_tokens) / len(tokens) * 100) if tokens else 0,
            'found_tokens': found_tokens,
            'not_found_tokens': not_found_tokens,
            'unique_found_list': sorted(unique_found),
            'unique_not_found_list': sorted(unique_not_found)
        }
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def check_tokenized_files(tokenized_json_path: str, db_path: str, output_path: Optional[str] = None) -> Dict:
    """Check all tokenized files against the dictionary.
    
    Args:
        tokenized_json_path: Path to the tokenized summary JSON file
        db_path: Path to the SQLite dictionary database
        output_path: Optional path to save results JSON
        
    Returns:
        Dictionary with complete analysis results
    """
    # Load tokenized data
    print(f"Loading tokenized data from: {tokenized_json_path}")
    with open(tokenized_json_path, 'r', encoding='utf-8') as f:
        tokenized_data = json.load(f)
    
    print(f"Files to process: {tokenized_data['total_files']}")
    print(f"Total tokens: {tokenized_data['total_tokens']:,}\n")
    
    # Initialize dictionary checker
    with DictionaryChecker(db_path) as checker:
        # Initialize cache first to get correct count
        checker._initialize_cache()
        
        results = {
            'summary': {
                'total_files': tokenized_data['total_files'],
                'total_tokens': tokenized_data['total_tokens'],
                'dictionary_words': len(checker._word_cache)
            },
            'files': {}
        }
        
        # Process each file
        file_count = 0
        for filename, file_data in tokenized_data['files'].items():
            file_count += 1
            tokens = file_data['tokens']
            
            # Analyze tokens
            analysis = checker.analyze_tokens(tokens)
            
            # Store results (without full token lists to save space)
            results['files'][filename] = {
                'total_tokens': analysis['total_tokens'],
                'found_count': analysis['found_count'],
                'not_found_count': analysis['not_found_count'],
                'unique_found': analysis['unique_found'],
                'unique_not_found': analysis['unique_not_found'],
                'found_percentage': analysis['found_percentage'],
                'not_found_tokens': analysis['unique_not_found_list']  # Keep list of unknown words
            }
            
            if file_count % 100 == 0:
                print(f"Processed {file_count}/{tokenized_data['total_files']} files...")
        
        # Calculate overall statistics
        total_found = sum(f['found_count'] for f in results['files'].values())
        total_not_found = sum(f['not_found_count'] for f in results['files'].values())
        
        # Collect all unique not-found words across all files
        all_not_found = set()
        for file_data in results['files'].values():
            all_not_found.update(file_data['not_found_tokens'])
        
        results['summary']['total_found'] = total_found
        results['summary']['total_not_found'] = total_not_found
        results['summary']['found_percentage'] = (total_found / (total_found + total_not_found) * 100) if (total_found + total_not_found) > 0 else 0
        results['summary']['unique_not_found_words'] = len(all_not_found)
        results['summary']['all_not_found_words'] = sorted(all_not_found)
    
    # Save results if output path provided
    if output_path:
        print(f"\nSaving results to: {output_path}")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"File size: {os.path.getsize(output_path):,} bytes")
    
    return results


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(here, '..'))
    
    db_path = os.path.join(project_root, 'data', 'dictionary.db')
    tokenized_path = os.path.join(project_root, 'data', 'tokenized_summary.json')
    output_path = os.path.join(project_root, 'data', 'dictionary_check_results.json')
    
    print("="*60)
    print("Dictionary Check")
    print("="*60)
    print()
    
    results = check_tokenized_files(tokenized_path, db_path, output_path)
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"Total tokens checked: {results['summary']['total_tokens']:,}")
    print(f"Tokens found in dictionary: {results['summary']['total_found']:,} ({results['summary']['found_percentage']:.2f}%)")
    print(f"Tokens NOT in dictionary: {results['summary']['total_not_found']:,}")
    print(f"Unique unknown words: {results['summary']['unique_not_found_words']:,}")
    print()
    print("Sample unknown words:")
    for word in results['summary']['all_not_found_words'][:20]:
        print(f"  - {word}")
