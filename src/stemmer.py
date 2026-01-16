import nltk
from nltk.stem import PorterStemmer, SnowballStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from typing import List, Dict, Tuple, Optional
import re


def ensure_stemmer_data():
    """Download required NLTK data for stemming/lemmatization."""
    required_data = [
        ('corpora/wordnet', 'wordnet'),
        ('corpora/omw-1.4', 'omw-1.4'),
        ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger'),
    ]
    
    for path, name in required_data:
        try:
            nltk.data.find(path)
        except LookupError:
            print(f"Downloading NLTK {name}...")
            try:
                nltk.download(name, quiet=True)
            except:
                print(f"  Warning: Could not download {name}")


def get_wordnet_pos(treebank_tag):
    """Convert treebank POS tag to WordNet POS tag.
    
    Args:
        treebank_tag: Penn Treebank POS tag
        
    Returns:
        WordNet POS tag
    """
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN  # default to noun


class TokenStemmer:
    """Handle stemming and lemmatization of tokens."""
    
    def __init__(self, method: str = 'snowball'):
        """Initialize the stemmer.
        
        Args:
            method: Stemming method - 'snowball' (default), 'porter', or 'lemmatize'
        """
        self.method = method
        
        if method == 'porter':
            self.stemmer = PorterStemmer()
        elif method == 'snowball':
            self.stemmer = SnowballStemmer('english')
        elif method == 'lemmatize':
            ensure_stemmer_data()
            self.lemmatizer = WordNetLemmatizer()
        else:
            raise ValueError(f"Unknown stemming method: {method}")
    
    def stem_token(self, token: str, pos_tag: Optional[str] = None) -> str:
        """Stem a single token.
        
        Args:
            token: The token to stem
            pos_tag: Optional POS tag for lemmatization
            
        Returns:
            Stemmed/lemmatized form of the token
        """
        # Only stem alphabetic tokens
        if not re.match(r'^[a-zA-Z]+$', token):
            return token.lower()
        
        token_lower = token.lower()
        
        if self.method in ['porter', 'snowball']:
            return self.stemmer.stem(token_lower)
        elif self.method == 'lemmatize':
            if pos_tag:
                wordnet_pos = get_wordnet_pos(pos_tag)
                return self.lemmatizer.lemmatize(token_lower, pos=wordnet_pos)
            else:
                return self.lemmatizer.lemmatize(token_lower)
        
        return token_lower
    
    def stem_tokens(self, tokens: List[str]) -> List[Dict[str, str]]:
        """Stem a list of tokens.
        
        Args:
            tokens: List of tokens to stem
            
        Returns:
            List of dictionaries with original, stem, and metadata
        """
        # For lemmatization, get POS tags first
        pos_tags = None
        if self.method == 'lemmatize':
            try:
                pos_tags = nltk.pos_tag(tokens)
            except:
                print("Warning: POS tagging failed, using default POS")
        
        results = []
        for i, token in enumerate(tokens):
            pos_tag = pos_tags[i][1] if pos_tags else None
            stem = self.stem_token(token, pos_tag)
            
            results.append({
                'original': token,
                'stem': stem,
                'pos': pos_tag if pos_tags else None
            })
        
        return results
    
    def stem_tokens_simple(self, tokens: List[str]) -> List[Tuple[str, str]]:
        """Stem tokens and return simple (original, stem) tuples.
        
        Args:
            tokens: List of tokens to stem
            
        Returns:
            List of (original, stem) tuples
        """
        # For lemmatization, get POS tags first
        pos_tags = None
        if self.method == 'lemmatize':
            try:
                pos_tags = nltk.pos_tag(tokens)
            except:
                pass
        
        results = []
        for i, token in enumerate(tokens):
            pos_tag = pos_tags[i][1] if pos_tags else None
            stem = self.stem_token(token, pos_tag)
            results.append((token, stem))
        
        return results


def get_stem_statistics(stemmed_data: List[Dict[str, str]]) -> Dict:
    """Calculate statistics about stemming results.
    
    Args:
        stemmed_data: List of stemmed token dictionaries
        
    Returns:
        Dictionary with stemming statistics
    """
    total_tokens = len(stemmed_data)
    
    # Count tokens that changed after stemming
    changed = sum(1 for item in stemmed_data if item['original'].lower() != item['stem'])
    
    # Count unique original vs unique stems
    unique_original = len(set(item['original'].lower() for item in stemmed_data))
    unique_stems = len(set(item['stem'] for item in stemmed_data))
    
    # Find most common stem reductions
    stem_groups = {}
    for item in stemmed_data:
        stem = item['stem']
        if stem not in stem_groups:
            stem_groups[stem] = set()
        stem_groups[stem].add(item['original'].lower())
    
    # Find stems with multiple source words
    multi_word_stems = {stem: words for stem, words in stem_groups.items() if len(words) > 1}
    
    return {
        'total_tokens': total_tokens,
        'tokens_changed': changed,
        'change_percentage': (changed / total_tokens * 100) if total_tokens > 0 else 0,
        'unique_original': unique_original,
        'unique_stems': unique_stems,
        'reduction_rate': ((unique_original - unique_stems) / unique_original * 100) if unique_original > 0 else 0,
        'multi_word_stems_count': len(multi_word_stems),
        'top_multi_word_stems': sorted(
            [(stem, list(words)[:5]) for stem, words in multi_word_stems.items()],
            key=lambda x: len(multi_word_stems[x[0]]),
            reverse=True
        )[:10]
    }


if __name__ == "__main__":
    # Test stemming
    test_tokens = [
        "running", "runs", "ran", "runner",
        "better", "best", "good",
        "organized", "organizing", "organization",
        "quickly", "quick", "quicker"
    ]
    
    print("Testing different stemming methods:\n")
    
    for method in ['porter', 'snowball', 'lemmatize']:
        print(f"\n{method.upper()} Method:")
        print("-" * 50)
        stemmer = TokenStemmer(method=method)
        results = stemmer.stem_tokens(test_tokens)
        
        for item in results:
            print(f"  {item['original']:20} -> {item['stem']:20} [{item.get('pos', 'N/A')}]")
        
        stats = get_stem_statistics(results)
        print(f"\nStatistics:")
        print(f"  Tokens changed: {stats['tokens_changed']}/{stats['total_tokens']} ({stats['change_percentage']:.1f}%)")
        print(f"  Unique reduction: {stats['unique_original']} -> {stats['unique_stems']} ({stats['reduction_rate']:.1f}%)")
