import spacy
import nltk
from typing import List, Dict, Any
import re
from nltk.tokenize import sent_tokenize
from collections import defaultdict
import sys

# Import new multilingual modules
from .language_detector import LanguageDetector
from .hindi_translator import HindiToEnglishNormalizer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
    except:
        pass

class NLPProcessor:
    def __init__(self):
        # Load spaCy model (use en_core_web_sm for speed)
        self.nlp = None
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Model not available - will use fallback mode
            self.nlp = None
        
        # Initialize multilingual processors
        self.language_detector = LanguageDetector()
        self.hindi_normalizer = HindiToEnglishNormalizer()
        
        # Legal terms patterns (expanded for bilingual)
        self.legal_patterns = {
            "definition": r'(?i)"([^"]+)"\s+means\s+([^.,]+)|"([^"]+)"\s+का\s+अर्थ\s+([^.,]+)',
            "obligation": r'shall\s+(?:provide|deliver|perform|ensure|maintain|pay)|करेगा|करेगी|होगा|होगी',
            "right": r'(?:entitled to|right to|may|cannot be prevented from)|अधिकार|हक',
            "prohibition": r'shall not|must not|cannot|prohibited from|नहीं करेगा|नहीं करेगी|नहीं होगा|नहीं होगी',
            "condition": r'provided that|subject to|condition precedent|शर्त|बशर्ते',
            "termination": r'termination|terminate|expiration|end of term|समाप्ति|समाप्त'
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities using spaCy"""
        entities = defaultdict(list)
        
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                entities[ent.label_].append(ent.text)
        
        # Custom extraction for legal entities
        entities["DATES"] = self._extract_dates_custom(text)
        entities["MONEY"] = self._extract_money(text)
        entities["PARTIES"] = self._extract_parties_custom(text)
        
        return dict(entities)
    
    def _extract_dates_custom(self, text: str) -> List[str]:
        date_patterns = [
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}'
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        return dates
    
    def _extract_money(self, text: str) -> List[str]:
        patterns = [
            r'(?:USD|INR|₹|$|£|€)\s*\d+(?:,\d{3})*(?:\.\d{2})?',
            r'\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|INR|dollars|rupees|euros)'
        ]
        amounts = []
        for pattern in patterns:
            amounts.extend(re.findall(pattern, text, re.IGNORECASE))
        return amounts
    
    def _extract_parties_custom(self, text: str) -> List[str]:
        patterns = [
            r'between\s+([^,]+?)\s+\(.*?\)\s+and\s+([^,]+?)\s+\(.*?\)',
            r'party\s+A:\s*([^\n(]+)',
            r'party\s+B:\s*([^\n(]+)'
        ]
        parties = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    parties.extend([m.strip() for m in match])
                else:
                    parties.append(match.strip())
        return list(set(parties))
    
    def classify_clause_type(self, clause_text: str) -> str:
        """Classify clause type based on content"""
        clause_text_lower = clause_text.lower()
        
        if re.search(r'indemnif|hold harmless', clause_text_lower):
            return "Indemnity"
        elif re.search(r'confidential|nda|non-disclosure', clause_text_lower):
            return "Confidentiality"
        elif re.search(r'terminat|expir|cancel', clause_text_lower):
            return "Termination"
        elif re.search(r'jurisdiction|governing law|venue', clause_text_lower):
            return "Jurisdiction"
        elif re.search(r'intellectual property|ip|copyright|patent', clause_text_lower):
            return "Intellectual Property"
        elif re.search(r'warrant|represent', clause_text_lower):
            return "Warranties"
        elif re.search(r'liability|limitation of liability', clause_text_lower):
            return "Liability"
        elif re.search(r'payment|fee|consideration', clause_text_lower):
            return "Payment"
        elif re.search(r'force majeure', clause_text_lower):
            return "Force Majeure"
        elif re.search(r'dispute|arbitration|mediation', clause_text_lower):
            return "Dispute Resolution"
        else:
            return "General"
    
    def identify_legal_concepts(self, text: str) -> Dict[str, List[str]]:
        """Identify legal concepts in text"""
        concepts = defaultdict(list)
        
        for concept, pattern in self.legal_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                concepts[concept].extend(matches)
        
        # Sentence-level analysis
        sentences = sent_tokenize(text)
        for sentence in sentences:
            if re.search(self.legal_patterns["obligation"], sentence, re.IGNORECASE):
                concepts["obligation_sentences"].append(sentence[:200])
            elif re.search(self.legal_patterns["right"], sentence, re.IGNORECASE):
                concepts["right_sentences"].append(sentence[:200])
            elif re.search(self.legal_patterns["prohibition"], sentence, re.IGNORECASE):
                concepts["prohibition_sentences"].append(sentence[:200])
        
        return dict(concepts)
    
    def detect_ambiguity(self, text: str) -> List[Dict]:
        """Detect ambiguous language"""
        ambiguity_patterns = [
            (r'reasonable', "Subjective term 'reasonable' may be ambiguous"),
            (r'substantial', "Subjective term 'substantial' lacks clarity"),
            (r'as soon as practicable', "Vague timeline 'as soon as practicable'"),
            (r'material breach', "'Material breach' is often undefined"),
            (r'sole discretion', "Unilateral discretion may be unfair"),
            (r'best efforts', "'Best efforts' is ambiguous standard"),
            (r'mutually agreeable', "Requires future agreement - may be unenforceable")
        ]
        
        ambiguities = []
        for pattern, explanation in ambiguity_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                ambiguities.append({
                    "term": match.group(),
                    "explanation": explanation,
                    "context": context,
                    "severity": "Medium"
                })
        
        return ambiguities
    
    def process_multilingual_text(self, text: str) -> Dict[str, Any]:
        """Process text with language detection and normalization"""
        # Detect language
        lang_analysis = self.language_detector.detect_language(text)
        
        # Extract Hindi and English sentences
        hindi_sentences = self.language_detector.extract_hindi_sentences(text)
        english_sentences = self.language_detector.extract_english_sentences(text)
        
        # Normalize Hindi text for processing
        normalized_text = self.hindi_normalizer.normalize_text(text)
        
        # Get translated terms
        translated_terms = self.hindi_normalizer.translate_key_terms(text)
        
        # Extract financial terms from Hindi
        hindi_financial_terms = self.hindi_normalizer.extract_financial_terms(text)
        
        return {
            "language_analysis": lang_analysis,
            "hindi_sentences": hindi_sentences,
            "english_sentences": english_sentences,
            "normalized_text": normalized_text,
            "translated_terms": translated_terms,
            "hindi_financial_terms": hindi_financial_terms,
            "is_multilingual": lang_analysis["is_mixed"] or lang_analysis["primary_language"] == "hindi"
        }
    
    def extract_entities_multilingual(self, text: str) -> Dict[str, List[str]]:
        """Extract entities with multilingual support"""
        # First process multilingual aspects
        multilingual_data = self.process_multilingual_text(text)
        
        # Use normalized text for entity extraction
        normalized_text = multilingual_data["normalized_text"]
        
        entities = defaultdict(list)
        
        # Extract from normalized text using existing logic
        if self.nlp:
            doc = self.nlp(normalized_text)
            for ent in doc.ents:
                entities[ent.label_].append(ent.text)
        
        # Custom extraction for legal entities
        entities["DATES"].extend(self._extract_dates_custom(normalized_text))
        entities["MONEY"].extend(self._extract_money(normalized_text))
        entities["PARTIES"].extend(self._extract_parties_custom(normalized_text))
        
        # Add Hindi-specific entities
        if multilingual_data["hindi_financial_terms"]:
            for term_data in multilingual_data["hindi_financial_terms"]:
                if term_data["type"] == "amount":
                    entities["MONEY"].append(term_data["normalized"])
                elif term_data["type"] == "percentage":
                    entities["PERCENTAGE"].append(term_data["normalized"])
        
        # Add translated terms as entities
        if multilingual_data["translated_terms"]:
            entities["TRANSLATED_TERMS"] = list(multilingual_data["translated_terms"].keys())
        
        return dict(entities)
    
    def classify_clause_type_multilingual(self, clause_text: str) -> str:
        """Classify clause type with multilingual support"""
        # Normalize text first
        normalized_text = self.hindi_normalizer.normalize_text(clause_text)
        
        # Use both original and normalized text for classification
        text_to_analyze = f"{clause_text} {normalized_text}".lower()
        
        # Expanded patterns for bilingual classification
        if re.search(r'indemnif|hold harmless|मुआवजा|हर्जाना', text_to_analyze):
            return "Indemnity"
        elif re.search(r'confidential|nda|non-disclosure|गोपनीय|गुप्त', text_to_analyze):
            return "Confidentiality"
        elif re.search(r'terminat|expir|cancel|समाप्ति|रद्द', text_to_analyze):
            return "Termination"
        elif re.search(r'jurisdiction|governing law|venue|न्यायालय|कानून', text_to_analyze):
            return "Jurisdiction"
        elif re.search(r'intellectual property|ip|copyright|patent|बौद्धिक संपदा', text_to_analyze):
            return "Intellectual Property"
        elif re.search(r'warrant|represent|वारंटी|गारंटी', text_to_analyze):
            return "Warranties"
        elif re.search(r'liability|limitation of liability|दायित्व|जिम्मेदारी', text_to_analyze):
            return "Liability"
        elif re.search(r'payment|fee|consideration|भुगतान|शुल्क', text_to_analyze):
            return "Payment"
        elif re.search(r'force majeure|अचल बल', text_to_analyze):
            return "Force Majeure"
        elif re.search(r'dispute|arbitration|mediation|विवाद|मध्यस्थता', text_to_analyze):
            return "Dispute Resolution"
        else:
            return "General"
    
    def generate_simple_english_summary(self, text: str) -> str:
        """Generate simple business English summary for any language text"""
        # Process multilingual text
        multilingual_data = self.process_multilingual_text(text)
        
        # Get basic clause classification
        clause_type = self.classify_clause_type_multilingual(text)
        
        # Extract key entities
        entities = self.extract_entities_multilingual(text)
        
        # Build summary
        summary_parts = []
        
        # Add clause type
        summary_parts.append(f"This is a {clause_type.lower()} clause.")
        
        # Add language information
        if multilingual_data["is_multilingual"]:
            summary_parts.append("This clause contains both Hindi and English text.")
        elif multilingual_data["language_analysis"]["primary_language"] == "hindi":
            summary_parts.append("This clause is primarily in Hindi.")
        
        # Add key financial information
        if entities.get("MONEY"):
            amounts = list(set(entities["MONEY"]))[:3]  # Limit to first 3
            summary_parts.append(f"It mentions financial amounts: {', '.join(amounts)}.")
        
        if entities.get("PERCENTAGE"):
            percentages = list(set(entities["PERCENTAGE"]))[:2]
            summary_parts.append(f"It includes percentages: {', '.join(percentages)}.")
        
        # Add party information
        if entities.get("PARTIES"):
            parties = list(set(entities["PARTIES"]))[:2]
            summary_parts.append(f"It involves parties: {', '.join(parties)}.")
        
        # Add translated terms if any
        if multilingual_data["translated_terms"]:
            term_count = len(multilingual_data["translated_terms"])
            summary_parts.append(f"It contains {term_count} key legal terms in Hindi.")
        
        # Add risk assessment
        risk_indicators = self._assess_simple_risks(text)
        if risk_indicators:
            summary_parts.append(f"Risk indicators: {', '.join(risk_indicators)}.")
        
        # Combine into final summary
        if len(summary_parts) == 1:
            summary = summary_parts[0] + " This clause requires professional legal review."
        else:
            summary = " ".join(summary_parts[:-1]) + " " + summary_parts[-1]
            summary += " Professional legal review is recommended."
        
        return summary
    
    def _assess_simple_risks(self, text: str) -> List[str]:
        """Assess simple risk indicators"""
        risks = []
        text_lower = text.lower()
        normalized_lower = self.hindi_normalizer.normalize_text(text).lower()
        
        # Check for common risk indicators in both languages
        risk_patterns = [
            (r'sole discretion|एकतरफा विवेक', 'unilateral discretion'),
            (r'unlimited liability|असीमित दायित्व', 'unlimited liability'),
            (r'foreign jurisdiction|विदेशी न्यायालय', 'foreign jurisdiction'),
            (r'automatic renewal|स्वचालित नवीनीकरण', 'auto-renewal'),
            (r'indefinite term|अनिश्चित अवधि', 'indefinite duration')
        ]
        
        for pattern, description in risk_patterns:
            if re.search(pattern, text_lower) or re.search(pattern, normalized_lower):
                risks.append(description)
        
        return risks