import spacy
import nltk
from typing import List, Dict, Any
import re
from nltk.tokenize import sent_tokenize
from collections import defaultdict
import sys

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
        
        # Legal terms patterns
        self.legal_patterns = {
            "definition": r'(?i)"([^"]+)"\s+means\s+([^.,]+)',
            "obligation": r'shall\s+(?:provide|deliver|perform|ensure|maintain|pay)',
            "right": r'(?:entitled to|right to|may|cannot be prevented from)',
            "prohibition": r'shall not|must not|cannot|prohibited from',
            "condition": r'provided that|subject to|condition precedent',
            "termination": r'termination|terminate|expiration|end of term'
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