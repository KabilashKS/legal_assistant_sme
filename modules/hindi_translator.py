# hindi_translator.py
import re
from typing import Dict, List, Optional

class HindiToEnglishNormalizer:
    def __init__(self):
        # Common Hindi legal terms and their English equivalents
        self.legal_terms_dict = {
            # Contract terms
            'समझौता': 'agreement',
            'अनुबंध': 'contract',
            'नियम': 'terms',
            'शर्तें': 'conditions',
            'पक्ष': 'party',
            'पक्षकार': 'party',
            'कंपनी': 'company',
            'फर्म': 'firm',
            'संस्था': 'organization',
            'रोजगारी': 'employment',
            
            # People/roles
            'कर्मचारी': 'employee',
            'व्यक्ति': 'person',
            'निदेशक': 'director',
            'प्रबंधक': 'manager',
            'मालिक': 'owner',
            'वरिष्ठ': 'senior',
            'डेवलपर': 'developer',
            
            # Financial terms
            'भुगतान': 'payment',
            'राशि': 'amount',
            'दायित्व': 'liability',
            'जिम्मेदारी': 'responsibility',
            'ब्याज': 'interest',
            'जुर्माना': 'penalty',
            'मुआवजा': 'compensation',
            'हर्जाना': 'damages',
            'वेतन': 'salary',
            'मासिक': 'monthly',
            
            # Legal terms
            'अधिकार': 'right',
            'कर्तव्य': 'duty',
            'बाध्य': 'obliged',
            'शर्त': 'condition',
            'प्रावधान': 'provision',
            'धारा': 'clause',
            'अनुच्छेद': 'section',
            
            # Actions
            'समाप्ति': 'termination',
            'रद्द': 'cancel',
            'समाप्त': 'terminate',
            'विस्तार': 'extension',
            'नवीनीकरण': 'renewal',
            'कार्य': 'work',
            'करेगा': 'shall',
            
            # Time periods
            'अवधि': 'period',
            'समय': 'time',
            'मियाद': 'term',
            'नोटिस': 'notice',
            'सूचना': 'notification',
            'अनिश्चित': 'indefinite',
            
            # Legal concepts
            'कानून': 'law',
            'न्यायालय': 'court',
            'न्यायाधीश': 'judge',
            'फैसला': 'judgment',
            'आदेश': 'order',
            'विधि': 'act',
            
            # Property/Intellectual
            'संपत्ति': 'property',
            'बौद्धिक संपदा': 'intellectual property',
            'गोपनीय': 'confidential',
            'गुप्त': 'secret',
            'प्रकटीकरण': 'disclosure',
            'गोपनीयता': 'confidentiality',
            'जानकारी': 'information',
            
            # Common verbs
            'होगा': 'shall be',
            'होगी': 'shall be',
            'करेगा': 'shall',
            'करेगी': 'shall',
            'नहीं करेगा': 'shall not',
            'नहीं करेगी': 'shall not',
            'करना होगा': 'must',
            'करना चाहिए': 'should',
            'रखेगा': 'shall maintain',
            'बनाए रखेगा': 'shall maintain',
            
            # Numbers and quantities
            'हज़ार': 'thousand',
            'लाख': 'lakh',
            'करोड़': 'crore',
            'प्रतिशत': 'percent',
            'फीसदी': 'percent',
            'प्रतिमाह': 'per month',
            
            # Common risk terms
            'एकतरफा': 'unilateral',
            'विवेक': 'discretion',
            'असीमित': 'unlimited',
            'विदेशी': 'foreign',
            'स्वचालित': 'automatic',
            'नवीनीकरण': 'renewal'
        }
        
        # Common patterns in Hindi contracts
        self.patterns = [
            # Date patterns
            (r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', r'\1/\2/\3'),
            # Currency patterns
            (r'रुपये|₹', 'INR'),
            (r'(\d+(?:,\d{3})*)\s*रुपये', r'INR \1'),
            # Percentage patterns
            (r'(\d+(?:\.\d+)?)\s*प्रतिशत', r'\1%'),
            (r'(\d+(?:\.\d+)?)\s*फीसदी', r'\1%'),
        ]
        
        # Hindi numerals to English numerals
        self.hindi_numerals = {
            '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
            '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalize Hindi text to English for NLP processing"""
        if not text:
            return text
        
        normalized = text
        
        # Convert Hindi numerals to English
        for hindi_num, english_num in self.hindi_numerals.items():
            normalized = normalized.replace(hindi_num, english_num)
        
        # Apply pattern replacements
        for pattern, replacement in self.patterns:
            normalized = re.sub(pattern, replacement, normalized)
        
        # Replace legal terms
        for hindi_term, english_term in self.legal_terms_dict.items():
            # Word boundary to avoid partial matches
            pattern = r'\b' + re.escape(hindi_term) + r'\b'
            normalized = re.sub(pattern, english_term, normalized, flags=re.IGNORECASE)
        
        return normalized
    
    def translate_key_terms(self, text: str) -> Dict[str, str]:
        """Extract and translate key legal terms from Hindi text"""
        found_terms = {}
        
        for hindi_term, english_term in self.legal_terms_dict.items():
            pattern = r'\b' + re.escape(hindi_term) + r'\b'
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                found_terms[hindi_term] = english_term
        
        return found_terms
    
    def create_bilingual_summary(self, original_text: str) -> Dict[str, str]:
        """Create a bilingual summary with original and normalized text"""
        normalized_text = self.normalize_text(original_text)
        translated_terms = self.translate_key_terms(original_text)
        
        return {
            "original_text": original_text,
            "normalized_text": normalized_text,
            "translated_terms": translated_terms,
            "translation_summary": f"Translated {len(translated_terms)} key terms from Hindi to English"
        }
    
    def extract_financial_terms(self, text: str) -> List[Dict[str, str]]:
        """Extract and normalize financial terms from Hindi text"""
        financial_patterns = [
            (r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:रुपये|₹)', 'amount'),
            (r'(\d+(?:\.\d+)?)\s*(?:प्रतिशत|फीसदी)', 'percentage'),
            (r'(\d+)\s*(?:हज़ार|लाख|करोड़)', 'amount_in_words')
        ]
        
        extracted = []
        
        for pattern, term_type in financial_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                original = match.group(0)
                normalized = self.normalize_text(original)
                extracted.append({
                    "original": original,
                    "normalized": normalized,
                    "type": term_type,
                    "context": text[max(0, match.start()-20):match.end()+20]
                })
        
        return extracted
    
    def get_simple_english_summary(self, clause_text: str) -> str:
        """Generate a simple English summary of Hindi clause"""
        # First normalize the text
        normalized = self.normalize_text(clause_text)
        
        # Extract key terms
        terms = self.translate_key_terms(clause_text)
        
        # Create a basic summary
        if not terms:
            return "This clause contains standard legal provisions that require professional review."
        
        summary_parts = []
        for hindi_term, english_term in terms.items():
            summary_parts.append(f"Contains {english_term} provisions")
        
        summary = "This clause deals with: " + ", ".join(summary_parts[:3])
        if len(summary_parts) > 3:
            summary += f" and {len(summary_parts) - 3} other legal aspects."
        
        return summary + " Professional legal review is recommended."
