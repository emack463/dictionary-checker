"""Handle hyphenated words for dictionary validation."""

import re
from typing import Tuple, List, Dict, Optional


class HyphenatedWordHandler:
    """Handle validation of hyphenated compound words."""
    
    def __init__(self, dictionary_checker, stemmer=None):
        """Initialize the handler.
        
        Args:
            dictionary_checker: DictionaryChecker instance
            stemmer: Optional TokenStemmer instance
        """
        self.checker = dictionary_checker
        self.stemmer = stemmer
    
    def is_valid_hyphenated_word(self, word: str) -> Tuple[bool, str, Dict]:
        """Check if a hyphenated word is valid through various strategies.
        
        Args:
            word: The hyphenated word to check
            
        Returns:
            Tuple of (is_valid, match_type, details)
            match_type: 'whole', 'components', 'dehyphenated', 'stem_components', 'none'
            details: Dictionary with validation details
        """
        if '-' not in word:
            return (False, 'none', {'reason': 'not_hyphenated'})
        
        details = {
            'original': word,
            'components': [],
            'valid_components': [],
            'invalid_components': []
        }
        
        # Strategy 1: Check if whole word is in dictionary
        found, match_type = self.checker.is_in_dictionary(word, allow_hyphenated=False)
        if found:
            return (True, 'whole', details)
        
        # Strategy 2: Check as dehyphenated word (remove hyphens)
        dehyphenated = word.replace('-', '')
        if dehyphenated and dehyphenated.isalpha():
            found, match_type = self.checker.is_in_dictionary(dehyphenated, allow_hyphenated=False)
            if found:
                details['dehyphenated'] = dehyphenated
                return (True, 'dehyphenated', details)
        
        # Strategy 3: Split and check individual components
        # Split on hyphens, filter out empty strings and non-alphabetic parts
        components = [part.strip() for part in word.split('-') if part.strip()]
        details['components'] = components
        
        # Ignore if starts/ends with hyphen (likely OCR error)
        if word.startswith('-') or word.endswith('-'):
            details['reason'] = 'edge_hyphen_likely_ocr_error'
            return (False, 'none', details)
        
        # Ignore if any component is too short (single letter) - likely OCR error
        if any(len(part) < 2 for part in components if part.isalpha()):
            details['reason'] = 'short_component_likely_ocr_error'
            return (False, 'none', details)
        
        # Check each alphabetic component
        valid_count = 0
        for part in components:
            if part.isalpha():
                found, match_type = self.checker.is_in_dictionary(part, allow_hyphenated=False)
                if found:
                    details['valid_components'].append(part)
                    valid_count += 1
                else:
                    details['invalid_components'].append(part)
        
        # If all alphabetic components are valid, consider the whole word valid
        alphabetic_components = [p for p in components if p.isalpha()]
        if alphabetic_components and valid_count == len(alphabetic_components):
            details['all_components_valid'] = True
            return (True, 'components', details)
        
        # Strategy 4: Check stems of components (if stemmer available)
        if self.stemmer and alphabetic_components:
            stem_valid_count = 0
            details['stem_components'] = []
            
            for part in alphabetic_components:
                if part not in details['valid_components']:  # Only check invalid ones
                    stem = self.stemmer.stem_token(part)
                    found, match_type = self.checker.is_in_dictionary(stem, allow_hyphenated=False)
                    if found:
                        details['stem_components'].append({'original': part, 'stem': stem})
                        stem_valid_count += 1
            
            # If all components are valid (either original or stem)
            total_valid = valid_count + stem_valid_count
            if total_valid == len(alphabetic_components):
                details['all_components_valid_via_stem'] = True
                return (True, 'stem_components', details)
        
        return (False, 'none', details)
    
    def analyze_hyphenated_words(self, words: List[str]) -> Dict:
        """Analyze a list of hyphenated words.
        
        Args:
            words: List of hyphenated words
            
        Returns:
            Dictionary with analysis results
        """
        results = {
            'total_hyphenated': len(words),
            'valid_whole': [],
            'valid_components': [],
            'valid_dehyphenated': [],
            'valid_stem_components': [],
            'invalid': [],
            'ocr_errors': []
        }
        
        for word in words:
            is_valid, match_type, details = self.is_valid_hyphenated_word(word)
            
            if is_valid:
                if match_type == 'whole':
                    results['valid_whole'].append(word)
                elif match_type == 'components':
                    results['valid_components'].append((word, details))
                elif match_type == 'dehyphenated':
                    results['valid_dehyphenated'].append((word, details))
                elif match_type == 'stem_components':
                    results['valid_stem_components'].append((word, details))
            else:
                if 'ocr_error' in details.get('reason', ''):
                    results['ocr_errors'].append((word, details))
                else:
                    results['invalid'].append((word, details))
        
        # Calculate statistics
        total_valid = (len(results['valid_whole']) + 
                      len(results['valid_components']) + 
                      len(results['valid_dehyphenated']) + 
                      len(results['valid_stem_components']))
        
        results['statistics'] = {
            'total': len(words),
            'valid': total_valid,
            'invalid': len(results['invalid']),
            'ocr_errors': len(results['ocr_errors']),
            'valid_percentage': (total_valid / len(words) * 100) if words else 0,
            'valid_whole_count': len(results['valid_whole']),
            'valid_components_count': len(results['valid_components']),
            'valid_dehyphenated_count': len(results['valid_dehyphenated']),
            'valid_stem_components_count': len(results['valid_stem_components'])
        }
        
        return results


def get_hyphenated_words_from_tokens(tokens: List[str]) -> List[str]:
    """Extract hyphenated words from a list of tokens.
    
    Args:
        tokens: List of tokens
        
    Returns:
        List of hyphenated words
    """
    return [token for token in tokens if '-' in token and any(c.isalpha() for c in token)]


if __name__ == "__main__":
    import os
    import sys
    
    # Test with sample hyphenated words
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(here, '..'))
    sys.path.insert(0, project_root)
    
    from src.dictionary_checker import DictionaryChecker
    from src.stemmer import TokenStemmer
    
    db_path = os.path.join(project_root, 'data', 'dictionary.db')
    
    test_words = [
        'well-known',        # Valid compound
        'Basket-making',     # Valid compound
        'self-evident',      # Valid compound
        'Lignt-honse',       # OCR error (should be lighthouse)
        'D-',                # OCR error
        '-Bacon',            # OCR error
        'an-',               # OCR error
        'Sciences-BAKING',   # Mixed (partial OCR error)
        'twenty-one',        # Valid compound
        'forty-five',        # Valid compound
        'pre-existing',      # Valid compound
    ]
    
    print("Testing Hyphenated Word Handler")
    print("="*70)
    
    with DictionaryChecker(db_path) as checker:
        checker._initialize_cache()
        stemmer = TokenStemmer(method='snowball')
        handler = HyphenatedWordHandler(checker, stemmer)
        
        print(f"\nTesting {len(test_words)} hyphenated words:\n")
        
        for word in test_words:
            is_valid, match_type, details = handler.is_valid_hyphenated_word(word)
            status = "VALID" if is_valid else "INVALID"
            print(f"{word:20} -> {status:7} ({match_type})")
            
            if match_type == 'components':
                print(f"{'':20}    Valid parts: {', '.join(details.get('valid_components', []))}")
            elif match_type == 'dehyphenated':
                print(f"{'':20}    As: {details.get('dehyphenated', '')}")
            elif match_type == 'stem_components':
                stems = details.get('stem_components', [])
                if stems:
                    stem_info = ', '.join([f"{s['original']}→{s['stem']}" for s in stems])
                    print(f"{'':20}    Stem matches: {stem_info}")
            elif not is_valid and details.get('reason'):
                print(f"{'':20}    Reason: {details['reason']}")
        
        # Analyze all test words
        print("\n" + "="*70)
        print("Analysis Summary")
        print("="*70)
        
        analysis = handler.analyze_hyphenated_words(test_words)
        stats = analysis['statistics']
        
        print(f"\nTotal hyphenated words: {stats['total']}")
        print(f"Valid: {stats['valid']} ({stats['valid_percentage']:.1f}%)")
        print(f"  - Whole word: {stats['valid_whole_count']}")
        print(f"  - Valid components: {stats['valid_components_count']}")
        print(f"  - Dehyphenated: {stats['valid_dehyphenated_count']}")
        print(f"  - Stem components: {stats['valid_stem_components_count']}")
        print(f"Invalid: {stats['invalid']}")
        print(f"OCR errors: {stats['ocr_errors']}")
