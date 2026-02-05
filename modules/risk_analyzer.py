from typing import Dict, List, Any, Tuple
import re
from collections import defaultdict

class RiskAnalyzer:
    def __init__(self):
        # Risk patterns database
        self.risk_patterns = {
            "high_risk": [
                (r'unlimited liability', "Unlimited liability exposes business to catastrophic risk"),
                (r'indemnify.*for.*negligence', "Indemnifying for others' negligence is extremely risky"),
                (r'penalty.*\d+%.*per month', "High penalty rates can be punitive"),
                (r'sole discretion.*terminate', "Unilateral termination rights are unfair"),
                (r'automatic renewal.*without notice', "Auto-renewal without notice creates lock-in"),
                (r'jurisdiction.*foreign country', "Foreign jurisdiction increases legal costs"),
                (r'assign.*without consent', "Assignment without consent may transfer obligations unfairly")
            ],
            "medium_risk": [
                (r'confidentiality.*indefinite', "Indefinite confidentiality may be unreasonable"),
                (r'non-compete.*\d+ years', "Long non-compete periods may restrict business"),
                (r'force majeure.*exclusive remedy', "Limited force majeure protection"),
                (r'governing law.*another state', "Different state law increases complexity"),
                (r'payment terms.*\d+ days', "Long payment terms affect cash flow"),
                (r'warranty.*as is', "'As is' warranty provides no protection")
            ],
            "low_risk": [
                (r'notice.*in writing', "Written notice requirement is standard"),
                (r'entire agreement', "Entire agreement clause is standard"),
                (r'severability', "Severability clause is protective"),
                (r'counterparts', "Counterparts clause is standard")
            ]
        }
        
        # SME-friendly alternative suggestions
        self.alternatives = {
            "unlimited liability": "Suggest capping liability to contract value or insurance limits",
            "sole discretion": "Suggest requiring 'reasonable grounds' or mutual agreement",
            "automatic renewal": "Suggest requiring 30-60 day notice before renewal",
            "foreign jurisdiction": "Suggest local jurisdiction or neutral arbitration venue",
            "indefinite confidentiality": "Suggest 2-5 year term after contract end"
        }
    
    def analyze_clause_risk(self, clause_text: str, clause_type: str) -> Dict:
        """Calculate risk score for a clause"""
        risk_score = 0
        issues = []
        suggestions = []
        
        # Check against risk patterns
        for risk_level, patterns in self.risk_patterns.items():
            for pattern, explanation in patterns:
                if re.search(pattern, clause_text, re.IGNORECASE):
                    if risk_level == "high_risk":
                        risk_score += 3
                    elif risk_level == "medium_risk":
                        risk_score += 2
                    elif risk_level == "low_risk":
                        risk_score += 1
                    
                    issues.append({
                        "issue": explanation,
                        "risk_level": risk_level.split('_')[0].capitalize(),
                        "context": self._extract_context(clause_text, pattern)
                    })
        
        # Clause type specific risks
        type_risks = self._get_clause_type_risks(clause_type, clause_text)
        risk_score += type_risks.get("additional_risk", 0)
        issues.extend(type_risks.get("issues", []))
        
        # Generate suggestions
        for issue in issues:
            suggestion = self._generate_suggestion(issue["issue"])
            if suggestion:
                suggestions.append(suggestion)
        
        # Normalize risk score to 0-10
        normalized_score = min(10, risk_score)
        
        return {
            "risk_score": normalized_score,
            "risk_level": self._score_to_level(normalized_score),
            "issues": issues[:5],  # Top 5 issues
            "suggestions": suggestions[:3],  # Top 3 suggestions
            "clause_type": clause_type
        }
    
    def _get_clause_type_risks(self, clause_type: str, clause_text: str) -> Dict:
        """Get risks specific to clause type"""
        risks = {"additional_risk": 0, "issues": []}
        
        if clause_type == "Indemnity":
            risks["additional_risk"] += 2
            if re.search(r'indemnify.*all', clause_text, re.IGNORECASE):
                risks["issues"].append({
                    "issue": "Broad 'all losses' indemnity may include indirect/consequential damages",
                    "risk_level": "High",
                    "context": "Indemnity clause scope"
                })
        
        elif clause_type == "Termination":
            if re.search(r'without cause', clause_text, re.IGNORECASE):
                risks["additional_risk"] += 3
                risks["issues"].append({
                    "issue": "'Without cause' termination provides no stability",
                    "risk_level": "High",
                    "context": "Termination conditions"
                })
        
        elif clause_type == "Jurisdiction":
            if re.search(r'delhi|mumbai|bangalore', clause_text, re.IGNORECASE):
                risks["additional_risk"] -= 1  # Local jurisdiction is better
                risks["issues"].append({
                    "issue": "Local Indian jurisdiction is preferable for SMEs",
                    "risk_level": "Low",
                    "context": "Jurisdiction specification"
                })
        
        return risks
    
    def _extract_context(self, text: str, pattern: str) -> str:
        """Extract context around pattern match"""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            return text[start:end]
        return ""
    
    def _generate_suggestion(self, issue: str) -> str:
        """Generate suggestion for an issue"""
        for key, suggestion in self.alternatives.items():
            if key in issue.lower():
                return suggestion
        return ""
    
    def _score_to_level(self, score: int) -> str:
        if score >= 7:
            return "High"
        elif score >= 4:
            return "Medium"
        else:
            return "Low"
    
    def calculate_composite_risk(self, clause_analyses: List[Dict]) -> Dict:
        """Calculate composite risk for entire contract"""
        if not clause_analyses:
            return {"overall_risk": "Low", "score": 0}
        
        total_score = sum(analysis.get("risk_score", 0) for analysis in clause_analyses)
        avg_score = total_score / len(clause_analyses)
        
        high_risk_clauses = [c for c in clause_analyses if c.get("risk_level") == "High"]
        medium_risk_clauses = [c for c in clause_analyses if c.get("risk_level") == "Medium"]
        
        return {
            "overall_risk": self._score_to_level(avg_score * 2),  # Weighted
            "score": round(avg_score, 1),
            "high_risk_count": len(high_risk_clauses),
            "medium_risk_count": len(medium_risk_clauses),
            "total_clauses": len(clause_analyses),
            "risk_distribution": {
                "high": len(high_risk_clauses),
                "medium": len(medium_risk_clauses),
                "low": len(clause_analyses) - len(high_risk_clauses) - len(medium_risk_clauses)
            }
        }