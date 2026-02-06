#!/usr/bin/env python3
"""
Test script for multilingual contract analysis
Demonstrates English + Hindi contract parsing capabilities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.language_detector import LanguageDetector
from modules.hindi_translator import HindiToEnglishNormalizer

def test_multilingual_features():
    print("🌐 MULTILINGUAL CONTRACT ANALYSIS TEST")
    print("=" * 50)
    
    # Initialize processors
    detector = LanguageDetector()
    translator = HindiToEnglishNormalizer()
    
    # Test samples
    test_samples = {
        "English Only": "This Employment Agreement is made between Tech Company and Employee. Monthly salary: ₹85,000. Company may terminate at sole discretion.",
        "Hindi Only": "यह रोजगारी समझौता टेक कंपनी और कर्मचारी के बीच बनाया गया है। मासिक वेतन: ₹85,000। कंपनी एकतरफा विवेक से समाप्त कर सकती है।",
        "Bilingual": """रोजगारी समझौता - EMPLOYMENT AGREEMENT
कर्मचारी वरिष्ठ डेवलपर के रूप में कार्य करेगा। The Employee shall serve as Senior Developer.
मासिक वेतन: ₹75,000। Monthly salary: ₹75,000.
कर्मचारी सभी कंपनी जानकारी की गोपनीयता अनिश्चित काल के लिए बनाए रखेगा। Employee shall maintain confidentiality indefinitely."""
    }
    
    for test_name, text in test_samples.items():
        print(f"\n📝 {test_name}:")
        print("-" * 30)
        
        # Language detection
        lang_analysis = detector.detect_language(text)
        print(f"Primary Language: {lang_analysis['primary_language'].title()}")
        print(f"Hindi Content: {lang_analysis['hindi_ratio']*100:.1f}%")
        print(f"Is Multilingual: {lang_analysis.get('is_mixed', False)}")
        
        # Translation analysis
        translated_terms = translator.translate_key_terms(text)
        if translated_terms:
            print(f"\n🔄 Translated Terms ({len(translated_terms)}):")
            for hindi, english in list(translated_terms.items())[:5]:
                print(f"  {hindi} → {english}")
        
        # Financial terms
        financial_terms = translator.extract_financial_terms(text)
        if financial_terms:
            print(f"\n💰 Financial Terms:")
            for term in financial_terms:
                print(f"  {term['original']} → {term['normalized']}")
        
        # Simple summary
        summary = translator.get_simple_english_summary(text)
        print(f"\n📋 Simple English Summary:")
        print(f"  {summary}")
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    test_multilingual_features()
    print("\n✅ Multilingual contract analysis test completed!")
    print("🚀 Ready to use with the Streamlit application!")
