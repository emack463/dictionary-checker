import os
import sys
import json

# allow importing from src
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from src.dictionary_checker import check_tokenized_files


def main():
    project_root = ROOT
    
    db_path = os.path.join(project_root, 'data', 'dictionary.db')
    tokenized_path = os.path.join(project_root, 'data', 'tokenized_summary.json')
    output_path = os.path.join(project_root, 'data', 'dictionary_check_results_stemmed.json')
    
    print("="*70)
    print("LEXICAL CHECKER - Dictionary Validation WITH STEMMING")
    print("="*70)
    print()
    
    # Check if input files exist
    if not os.path.exists(tokenized_path):
        print(f"Error: {tokenized_path} not found!")
        print("Run tokenize_files.py first to generate tokenized data.")
        return
    
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found!")
        print("Dictionary database missing.")
        return
    
    # Run dictionary check WITH STEMMING
    # Try different stemming methods to compare
    methods = ['porter', 'snowball', 'lemmatize']
    
    results_comparison = {}
    
    for method in methods:
        print(f"\n{'='*70}")
        print(f"Testing with {method.upper()} method")
        print(f"{'='*70}\n")
        
        method_output_path = output_path.replace('.json', f'_{method}.json')
        
        try:
            results = check_tokenized_files(
                tokenized_path, 
                db_path, 
                method_output_path,
                use_stemming=True,
                stem_method=method
            )
            
            results_comparison[method] = {
                'original_found': results['summary']['total_found'],
                'stem_found': results['summary']['total_stem_found'],
                'combined_found': results['summary']['total_combined_found'],
                'not_found': results['summary']['total_not_found'],
                'original_percentage': results['summary']['found_percentage'],
                'combined_percentage': results['summary']['combined_found_percentage'],
                'stem_contribution': results['summary']['stem_contribution'],
                'unique_stem_found': results['summary']['unique_stem_found_words']
            }
            
            # Display summary
            print("\n" + "="*70)
            print(f"{method.upper()} - SUMMARY")
            print("="*70)
            print(f"Files processed: {results['summary']['total_files']:,}")
            print(f"Total tokens: {results['summary']['total_tokens']:,}")
            print(f"Dictionary size: {results['summary']['dictionary_words']:,} words")
            print()
            print(f"✓ Found (original): {results['summary']['total_found']:,} ({results['summary']['found_percentage']:.2f}%)")
            print(f"✓ Found (via stem): {results['summary']['total_stem_found']:,} ({results['summary']['stem_contribution']:.2f}%)")
            print(f"✓ TOTAL FOUND: {results['summary']['total_combined_found']:,} ({results['summary']['combined_found_percentage']:.2f}%)")
            print(f"✗ Not found: {results['summary']['total_not_found']:,}")
            print()
            print(f"Improvement from stemming: +{results['summary']['stem_contribution']:.2f}%")
            print(f"Unique words found via stem: {results['summary']['unique_stem_found_words']:,}")
            
        except Exception as e:
            print(f"Error with {method} method: {e}")
            import traceback
            traceback.print_exc()
    
    # Print comparison table
    if results_comparison:
        print("\n" + "="*70)
        print("COMPARISON OF STEMMING METHODS")
        print("="*70)
        print(f"{'Method':<15} {'Original %':<15} {'Combined %':<15} {'Improvement':<15}")
        print("-"*70)
        
        for method, stats in results_comparison.items():
            print(f"{method.upper():<15} {stats['original_percentage']:<15.2f} {stats['combined_percentage']:<15.2f} +{stats['stem_contribution']:<14.2f}%")
        
        print("\n" + "="*70)
        print("RECOMMENDATION")
        print("="*70)
        
        # Find best method
        best_method = max(results_comparison.items(), key=lambda x: x[1]['combined_percentage'])
        print(f"\nBest method: {best_method[0].upper()}")
        print(f"  Combined accuracy: {best_method[1]['combined_percentage']:.2f}%")
        print(f"  Improvement: +{best_method[1]['stem_contribution']:.2f}%")
        print(f"  Unique words found via stemming: {best_method[1]['unique_stem_found']:,}")
        
        # Save comparison
        comparison_path = os.path.join(project_root, 'data', 'stemming_comparison.json')
        with open(comparison_path, 'w', encoding='utf-8') as f:
            json.dump(results_comparison, f, indent=2)
        print(f"\nComparison saved to: {comparison_path}")


if __name__ == '__main__':
    main()
