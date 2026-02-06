# language_detector.py
import re
from typing import Dict, Tuple, List

class LanguageDetector:
    def __init__(self):
        # Hindi character ranges (Devanagari script)
        self.hindi_pattern = re.compile(r'[\u0900-\u097F]')
        # Common Hindi words in contracts
        self.hindi_keywords = {
            'समझौता', 'अनुबंध', 'नियम', 'शर्तें', 'पक्ष', 'कंपनी', 'कर्मचारी',
            'भुगतान', 'दायित्व', 'अधिकार', 'कानून', 'न्यायालय', 'मुआवजा',
            'समाप्ति', 'नोटिस', 'अवधि', 'राशि', 'ब्याज', '�ंड', '�ोपनीय'
        }
        
        # English keywords
        self.english_keywords = {
            'agreement', 'contract', 'terms', 'conditions', 'party', 'company', 'employee',
            'payment', 'liability', 'right', 'law', 'court', 'compensation', 'termination',
            'notice', 'period', 'amount', 'interest', 'penalty', 'confidential'
        }
    
    def detect_language(self, text: str) -> Dict[str, any]:
        """Detect language(s) in the text and return analysis"""
        if not text or not text.strip():
            return {"primary_language": "unknown", "is_mixed": False, "hindi_ratio": 0, "english_ratio": 0}
        
        # Count Hindi characters
        hindi_chars = len(self.hindi_pattern.findall(text))
        total_chars = len(re.sub(r'\s', '', text))  # Exclude whitespace
        
        # Count Hindi and English words
        words = re.findall(r'\b\w+\b', text.lower())
        hindi_words = sum(1 for word in words if word in self.hindi_keywords)
        english_words = sum(1 for word in words if word in self.english_keywords)
        
        # Calculate ratios
        hindi_ratio = hindi_chars / total_chars if total_chars > 0 else 0
        english_ratio = (total_chars - hindi_chars) / total_chars if total_chars > 0 else 0
        
        # Determine primary language
        if hindi_ratio > 0.3:  # More than 30% Hindi characters
            primary_language = "hindi"
        elif english_ratio > 0.7:  # More than 70% English characters
            primary_language = "english"
        else:
            primary_language = "mixed"
        
        # Check if mixed language
        is_mixed = (hindi_ratio > 0.1 and english_ratio > 0.1)
        
        return {
            "primary_language": primary_language,
            "is_mixed": is_mixed,
            "hindi_ratio": round(hindi_ratio, 3),
            "english_ratio": round(english_ratio, 3),
            "hindi_word_count": hindi_words,
            "english_word_count": english_words,
            "total_words": len(words)
        }
    
    def extract_hindi_sentences(self, text: str) -> List[str]:
        """Extract sentences containing Hindi text"""
        sentences = re.split(r'[.!?।]', text)  # Include Hindi danda (।)
        hindi_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and self.hindi_pattern.search(sentence):
                hindi_sentences.append(sentence)
        
        return hindi_sentences
    
    def extract_english_sentences(self, text: str) -> List[str]:
        """Extract sentences containing primarily English text"""
        sentences = re.split(r'[.!?।]', text)
        english_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and not self.hindi_pattern.search(sentence):
                english_sentences.append(sentence)
        
        return english_sentences
    
    def get_language_summary(self, text: str) -> str:
        """Get a human-readable language summary"""
        analysis = self.detect_language(text)
        
        if analysis["primary_language"] == "hindi":
            return f"Primarily Hindi ({analysis['hindi_ratio']*100:.1f}% Hindi content)"
        elif analysis["primary_language"] == "english":
            return f"Primarily English ({analysis['english_ratio']*100:.1f}% English content)"
        else:
            return f"Mixed language ({analysis['hindi_ratio']*100:.1f}% Hindi, {analysis['english_ratio']*100:.1f}% English)"
