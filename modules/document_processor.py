import PyPDF2
from docx import Document
import re
from typing import Dict, List, Tuple, Optional
import hashlib

class DocumentProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc', '.txt']
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from different file formats"""
        try:
            if file_type == 'pdf':
                return self._extract_from_pdf(file_path)
            elif file_type in ['docx', 'doc']:
                return self._extract_from_docx(file_path)
            elif file_type == 'txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise ValueError(f"Unsupported file format: {file_type}")
        except Exception as e:
            raise Exception(f"Error extracting text: {str(e)}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def detect_language(self, text: str) -> str:
        """Simple language detection (English vs Hindi)"""
        hindi_char_pattern = re.compile(r'[\u0900-\u097F]')
        if hindi_char_pattern.search(text):
            return 'hindi'
        return 'english'
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,;:()\-&$%]', ' ', text)
        return text.strip()
    
    def extract_metadata(self, text: str) -> Dict:
        """Extract basic metadata from contract"""
        metadata = {
            "parties": self._extract_parties(text),
            "dates": self._extract_dates(text),
            "financial_terms": self._extract_financial_terms(text),
            "duration": self._extract_duration(text)
        }
        return metadata
    
    def _extract_parties(self, text: str) -> List[str]:
        # Simple pattern for parties (can be enhanced)
        parties = []
        patterns = [
            r'between\s+([^,]+)\s+and\s+([^,]+)',
            r'party\s+A:\s*([^\n]+)',
            r'party\s+B:\s*([^\n]+)',
            r'this agreement is made between\s+([^,]+)\s+and\s+([^,]+)'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    parties.extend([m.strip() for m in match])
                else:
                    parties.append(match.strip())
        return list(set(parties))[:2]  # Return unique parties, max 2
    
    def _extract_dates(self, text: str) -> List[str]:
        date_patterns = [
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}',
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}'
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        return list(set(dates))
    
    def _extract_financial_terms(self, text: str) -> List[str]:
        patterns = [
            r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?',
            r'₹\s*\d+(?:,\d{3})*(?:\.\d{2})?',
            r'INR\s*\d+(?:,\d{3})*(?:\.\d{2})?',
            r'amount.*?\d+(?:,\d{3})*(?:\.\d{2})?',
            r'consideration.*?\d+(?:,\d{3})*(?:\.\d{2})?'
        ]
        financials = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            financials.extend(matches)
        return financials
    
    def _extract_duration(self, text: str) -> Optional[str]:
        patterns = [
            r'term.*?(\d+)\s*(?:year|month|day|week)s?',
            r'duration.*?(\d+)\s*(?:year|month|day|week)s?',
            r'period.*?(\d+)\s*(?:year|month|day|week)s?'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None
    
    def segment_clauses(self, text: str) -> List[Dict]:
        """Segment contract into clauses"""
        clauses = []
        # Split by common clause markers
        clause_patterns = [
            r'\n\s*\d+\.\s+',  # 1. Clause
            r'\n\s*\([a-z]\)\s+',  # (a) Sub-clause
            r'\n\s*[A-Z][A-Z\s]+\s*:\s*\n',  # SECTION HEADER:
            r'\n\s*ARTICLE\s+\w+\s*\n',  # ARTICLE I
        ]
        
        # Use the first pattern that gives reasonable segmentation
        for pattern in clause_patterns:
            segments = re.split(pattern, text)
            if len(segments) > 3:  # Good segmentation
                for i, segment in enumerate(segments[1:], 1):
                    if segment.strip():
                        clauses.append({
                            "clause_id": i,
                            "title": f"Clause {i}",
                            "text": segment.strip()[:500],  # Limit length
                            "full_text": segment.strip()
                        })
                break
        
        # Fallback: simple paragraph splitting
        if not clauses:
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            for i, para in enumerate(paragraphs[:20]):  # Limit to first 20
                clauses.append({
                    "clause_id": i + 1,
                    "title": f"Paragraph {i + 1}",
                    "text": para[:500],
                    "full_text": para
                })
        
        return clauses