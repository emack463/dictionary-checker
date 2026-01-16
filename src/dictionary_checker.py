import os
import sqlite3
from typing import List, Dict, Set, Optional, Tuple
import json


class DictionaryChecker:
    """Check tokens against an English dictionary in SQLite database."""
    
    def __init__(self, db_path: str, use_stemming: bool = False, stemmer=None, handle_hyphenated: bool = True):
        """Initialize the dictionary checker.
        
        Args:
            db_path: Path to the SQLite database file
            use_stemming: Whether to check stem forms if original not found
            stemmer: Optional TokenStemmer instance for stem checking
            handle_hyphenated: Whether to use special handling for hyphenated words
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.use_stemming = use_stemming
        self.stemmer = stemmer
        self.handle_hyphenated = handle_hyphenated
        
        # Cache for performance
        self._word_cache: Set[str] = set()
        self._cache_initialized = False
        
        # Statistics for stem-based matches
        self.stem_match_stats = {
            'original_matches': 0,
            'stem_matches': 0,
            'hyphenated_matches': 0,
            'no_matches': 0
        }
        
        # Hyphenated word handler (lazy initialization)
        self._hyphenated_handler = None
    
    def _initialize_cache(self):
        """Load all dictionary words into memory for faster lookups."""
        if self._cache_initialized:
            return
        
        print("Loading dictionary into memory...")
        self.cursor.execute("SELECT DISTINCT LOWER(word) FROM entries")
        self._word_cache = {row[0] for row in self.cursor.fetchall()}
        self._cache_initialized = True
        print(f"Loaded {len(self._word_cache):,} unique words")
    
    def get_dictionary_size(self) -> int:
        """Get the number of unique words in the dictionary."""
        self._initialize_cache()
        return len(self._word_cache)
    
    def is_in_dictionary(self, word: str, case_sensitive: bool = False, allow_hyphenated: bool = True) -> Tuple[bool, str]:
        """Check if a word exists in the dictionary.
        
        Args:
            word: The word to check
            case_sensitive: Whether to perform a case-sensitive check
            
        Returns:
            Tuple of (bool, match_type) where match_type is one of:
            'original' - matched as-is
            'stem' - matched via stemming
            'hyphenated_{type}' - matched via hyphenated word handling
            'none' - no match found
        """
        self._initialize_cache()
        
        # Check hyphenated words if enabled (guard against recursion)
        if allow_hyphenated and self.handle_hyphenated and '-' in word:
            if self._hyphenated_handler is None:
                # Lazy initialization
                import sys
                import os
                here = os.path.dirname(os.path.abspath(__file__))
                if here not in sys.path:
                    sys.path.insert(0, here)
                from hyphenated_handler import HyphenatedWordHandler
                self._hyphenated_handler = HyphenatedWordHandler(self, self.stemmer)
            
            is_valid, match_type, details = self._hyphenated_handler.is_valid_hyphenated_word(word)
            if is_valid:
                self.stem_match_stats['hyphenated_matches'] += 1
                return (True, f'hyphenated_{match_type}')
        
        check_word = word if case_sensitive else word.lower()
        
        # Check original form first
        if check_word in self._word_cache:
            self.stem_match_stats['original_matches'] += 1
            return (True, 'original')
        
        # Check stem form if enabled
        if self.use_stemming and self.stemmer:
            stem_form = self.stemmer.stem_token(word)
            stem_check = stem_form if case_sensitive else stem_form.lower()
            if stem_check != check_word and stem_check in self._word_cache:
                self.stem_match_stats['stem_matches'] += 1
                return (True, 'stem')
        
        self.stem_match_stats['no_matches'] += 1
        return (False, 'none')
    
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
                found, _ = self.is_in_dictionary(token_lower)
                results[token_lower] = found
        
        return results
    
    def analyze_tokens(self, tokens: List[str]) -> Dict:
        """Analyze tokens and categorize them by dictionary status.
        
        Args:
            tokens: List of tokens to analyze
            
        Returns:
            Dictionary with counts and lists of found/not-found tokens
        """
        self._initialize_cache()
        
        found_tokens = []  # Found in original form
        stem_found_tokens = []  # Found via stemming
        hyphenated_found_tokens = []  # Found via hyphenated word handling
        not_found_tokens = []
        
        # Track match types
        match_details = []
        
        for token in tokens:
            token_lower = token.lower()
            
            # Check original form first
            if token_lower in self._word_cache:
                found_tokens.append(token)
                match_details.append({'token': token, 'match_type': 'original', 'stem': None})
            else:
                # Check hyphenated word handling
                hyphenated_matched = False
                if self.handle_hyphenated and '-' in token:
                    if self._hyphenated_handler is None:
                        # Lazy initialization
                        import sys
                        import os
                        here = os.path.dirname(os.path.abspath(__file__))
                        if here not in sys.path:
                            sys.path.insert(0, here)
                        from hyphenated_handler import HyphenatedWordHandler
                        self._hyphenated_handler = HyphenatedWordHandler(self, self.stemmer)
                    
                    is_valid, match_type, details = self._hyphenated_handler.is_valid_hyphenated_word(token)
                    if is_valid:
                        hyphenated_found_tokens.append(token)
                        match_details.append({'token': token, 'match_type': f'hyphenated_{match_type}', 'details': details})
                        hyphenated_matched = True
                
                # Check stem form if not found via hyphenation
                if not hyphenated_matched:
                    stem_matched = False
                    stem_form = None
                    
                    if self.use_stemming and self.stemmer:
                        stem_form = self.stemmer.stem_token(token)
                        if stem_form != token_lower and stem_form in self._word_cache:
                            stem_found_tokens.append(token)
                            match_details.append({'token': token, 'match_type': 'stem', 'stem': stem_form})
                            stem_matched = True
                    
                    if not stem_matched:
                        not_found_tokens.append(token)
        
        # Calculate unique sets (case-insensitive)
        unique_found = set(t.lower() for t in found_tokens)
        unique_stem_found = set(t.lower() for t in stem_found_tokens)
        unique_hyphenated_found = set(t.lower() for t in hyphenated_found_tokens)
        unique_not_found = set(t.lower() for t in not_found_tokens)
        
        # Combined found (original + stem + hyphenated)
        all_found = found_tokens + stem_found_tokens + hyphenated_found_tokens
        unique_all_found = unique_found | unique_stem_found | unique_hyphenated_found
        
        result = {
            'total_tokens': len(tokens),
            'found_count': len(found_tokens),
            'stem_found_count': len(stem_found_tokens),
            'hyphenated_found_count': len(hyphenated_found_tokens),
            'combined_found_count': len(all_found),
            'not_found_count': len(not_found_tokens),
            'unique_found': len(unique_found),
            'unique_stem_found': len(unique_stem_found),
            'unique_hyphenated_found': len(unique_hyphenated_found),
            'unique_combined_found': len(unique_all_found),
            'unique_not_found': len(unique_not_found),
            'found_percentage': (len(found_tokens) / len(tokens) * 100) if tokens else 0,
            'combined_found_percentage': (len(all_found) / len(tokens) * 100) if tokens else 0,
            'stem_contribution': (len(stem_found_tokens) / len(tokens) * 100) if tokens else 0,
            'hyphenated_contribution': (len(hyphenated_found_tokens) / len(tokens) * 100) if tokens else 0,
            'found_tokens': found_tokens,
            'stem_found_tokens': stem_found_tokens,
            'hyphenated_found_tokens': hyphenated_found_tokens,
            'not_found_tokens': not_found_tokens,
            'unique_found_list': sorted(unique_found),
            'unique_stem_found_list': sorted(unique_stem_found),
            'unique_hyphenated_found_list': sorted(unique_hyphenated_found),
            'unique_not_found_list': sorted(unique_not_found),
            'match_details': match_details
        }
        
        # Add stemming stats if enabled
        if self.use_stemming or self.handle_hyphenated:
            result['stemming_stats'] = self.stem_match_stats.copy()
        
        return result
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def check_tokenized_files(tokenized_json_path: str, db_path: str, output_path: Optional[str] = None, 
                         use_stemming: bool = False, stem_method: str = 'snowball') -> Dict:
    """Check all tokenized files against the dictionary.
    
    Args:
        tokenized_json_path: Path to the tokenized summary JSON file
        db_path: Path to the SQLite dictionary database
        output_path: Optional path to save results JSON
        use_stemming: Whether to use stemming for dictionary lookups (default: False)
        stem_method: Stemming method - 'snowball' (default), 'porter', or 'lemmatize'
        
    Returns:
        Dictionary containing results for all files and summary statistics
    """
    # Load tokenized data
    print(f"Loading tokenized data from {tokenized_json_path}...")
    with open(tokenized_json_path, 'r', encoding='utf-8') as f:
        tokenized_data = json.load(f)
    
    # Initialize stemmer if requested
    stemmer = None
    if use_stemming:
        import sys
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path:
            sys.path.insert(0, here)
        from stemmer import TokenStemmer
        stemmer = TokenStemmer(method=stem_method)
        print(f"Using {stem_method} stemming method")
    
    # Create checker
    checker = DictionaryChecker(db_path, use_stemming=use_stemming, stemmer=stemmer, handle_hyphenated=True)
    dict_size = checker.get_dictionary_size()
    
    print(f"\nProcessing {len(tokenized_data['files']):,} files...")
    
    results = {
        'files': {},
        'summary': {
            'total_files': len(tokenized_data['files']),
            'total_tokens': tokenized_data['total_tokens'],
            'dictionary_words': dict_size,
            'stemming_enabled': use_stemming,
            'stem_method': stem_method if use_stemming else None
        }
    }
    
    # Process each file
    total_found = 0
    total_not_found = 0
    all_not_found_words = set()
    
    for i, (filepath, file_data) in enumerate(tokenized_data['files'].items(), 1):
        if i % 100 == 0:
            print(f"  Processed {i}/{len(tokenized_data['files'])} files...")
        
        tokens = file_data['tokens']
        analysis = checker.analyze_tokens(tokens)
        
        # Store file results
        file_results = {
            'total_tokens': analysis['total_tokens'],
            'found_count': analysis['found_count'],
            'not_found_count': analysis['not_found_count'],
            'found_percentage': analysis['found_percentage'],
            'unique_not_found': analysis['unique_not_found'],
            'not_found_tokens': analysis['unique_not_found_list']
        }
        
        # Add stemming-specific results if enabled
        if use_stemming or checker.handle_hyphenated:
            if 'stem_found_count' in analysis:
                file_results['stem_found_count'] = analysis['stem_found_count']
            if 'hyphenated_found_count' in analysis:
                file_results['hyphenated_found_count'] = analysis['hyphenated_found_count']
            if 'combined_found_count' in analysis:
                file_results['combined_found_count'] = analysis['combined_found_count']
                file_results['combined_found_percentage'] = analysis['combined_found_percentage']
            if 'stem_contribution' in analysis:
                file_results['stem_contribution'] = analysis['stem_contribution']
            if 'hyphenated_contribution' in analysis:
                file_results['hyphenated_contribution'] = analysis['hyphenated_contribution']
            if 'unique_stem_found' in analysis:
                file_results['unique_stem_found'] = analysis['unique_stem_found']
                file_results['stem_found_tokens'] = analysis['unique_stem_found_list']
            if 'unique_hyphenated_found' in analysis:
                file_results['unique_hyphenated_found'] = analysis['unique_hyphenated_found']
                file_results['hyphenated_found_tokens'] = analysis['unique_hyphenated_found_list']
        
        results['files'][filepath] = file_results
        
        # Aggregate counts
        total_found += analysis['found_count']
        total_not_found += analysis['not_found_count']
        all_not_found_words.update(analysis['unique_not_found_list'])
    
    # Calculate summary statistics
    results['summary']['total_found'] = total_found
    results['summary']['total_not_found'] = total_not_found
    results['summary']['found_percentage'] = (total_found / (total_found + total_not_found) * 100) if (total_found + total_not_found) > 0 else 0
    results['summary']['unique_not_found_words'] = len(all_not_found_words)
    results['summary']['all_not_found_words'] = sorted(all_not_found_words)
    
    # Add stemming and hyphenated summary stats
    if use_stemming or checker.handle_hyphenated:
        total_stem_found = sum(f.get('stem_found_count', 0) for f in results['files'].values())
        total_hyphenated_found = sum(f.get('hyphenated_found_count', 0) for f in results['files'].values())
        total_combined_found = sum(f.get('combined_found_count', 0) for f in results['files'].values())
        
        all_stem_found = set()
        all_hyphenated_found = set()
        for file_data in results['files'].values():
            if 'stem_found_tokens' in file_data:
                all_stem_found.update(file_data['stem_found_tokens'])
            if 'hyphenated_found_tokens' in file_data:
                all_hyphenated_found.update(file_data['hyphenated_found_tokens'])
        
        if total_stem_found > 0:
            results['summary']['total_stem_found'] = total_stem_found
            results['summary']['stem_contribution'] = (total_stem_found / tokenized_data['total_tokens'] * 100)
            results['summary']['unique_stem_found_words'] = len(all_stem_found)
        
        if total_hyphenated_found > 0:
            results['summary']['total_hyphenated_found'] = total_hyphenated_found
            results['summary']['hyphenated_contribution'] = (total_hyphenated_found / tokenized_data['total_tokens'] * 100)
            results['summary']['unique_hyphenated_found_words'] = len(all_hyphenated_found)
        
        if total_combined_found > 0:
            results['summary']['total_combined_found'] = total_combined_found
            results['summary']['combined_found_percentage'] = (total_combined_found / (total_combined_found + total_not_found) * 100) if (total_combined_found + total_not_found) > 0 else 0
        
        results['summary']['stemming_stats'] = checker.stem_match_stats.copy()
    
    # Save results if output path specified
    if output_path:
        print(f"\nSaving results to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print("Results saved successfully!")
    
    # Close database connection
    checker.close()
    
    return results


if __name__ == '__main__':
    # Example usage
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, 'data', 'dictionary.db')
    tokenized_path = os.path.join(project_root, 'data', 'tokenized_summary.json')
    output_path = os.path.join(project_root, 'data', 'dictionary_check_results.json')
    
    results = check_tokenized_files(tokenized_path, db_path, output_path, use_stemming=True, stem_method='snowball')
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Files processed: {results['summary']['total_files']:,}")
    print(f"Total tokens: {results['summary']['total_tokens']:,}")
    print(f"Found in dictionary: {results['summary']['total_found']:,} ({results['summary']['found_percentage']:.2f}%)")
    if results['summary'].get('stemming_enabled'):
        print(f"Found via stemming: {results['summary'].get('total_stem_found', 0):,}")
        print(f"TOTAL FOUND: {results['summary'].get('total_combined_found', 0):,} ({results['summary'].get('combined_found_percentage', 0):.2f}%)")
    print(f"Not found: {results['summary']['total_not_found']:,}")
    print(f"Unique unknown words: {results['summary']['unique_not_found_words']:,}")
