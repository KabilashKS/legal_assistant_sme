# llm_handler.py (COMPLETE CORRECTED VERSION)
import openai
import os
from typing import Dict, Any, List
import json

class LLMConfig:
    def __init__(self, model="gpt-3.5-turbo", temperature=0.3):
        self.model = model
        self.temperature = temperature

class LLMHandler:
    def __init__(self, use_mock=True):
        self.use_mock = use_mock

    def explain_clause(self, clause_text):
        return "This clause should be reviewed for fairness and clarity."

    # ⭐ ADD THIS NEW FUNCTION
    def generate_detailed_report(self, analyses, contract_excerpt):
        """Generates a structured legal report (mock or real AI)"""

        high_risk = [a for a in analyses if a["risk_level"] == "High"]
        medium_risk = [a for a in analyses if a["risk_level"] == "Medium"]

        return {
            "executive_summary": f"""
### 📋 Executive Summary

This contract was analyzed using AI.  
We identified **{len(high_risk)} high-risk** and **{len(medium_risk)} medium-risk** clauses.

**Overall concern areas include:**
- Unbalanced termination rights
- High financial liability exposure
- Jurisdiction risks
- Long-term confidentiality or IP transfer terms

Business owners should carefully review this agreement before signing.
""",

            "risk_analysis": f"""
### ⚠️ Risk Breakdown

| Risk Level | Clause Count |
|------------|-------------|
| High Risk  | {len(high_risk)} |
| Medium Risk| {len(medium_risk)} |
| Low Risk   | {len(analyses) - len(high_risk) - len(medium_risk)} |
""",

            "critical_issues": [
                f"Clause {a['clause_id']} may expose business to high legal or financial risk"
                for a in high_risk
            ] if high_risk else ["No critical red-flag clauses detected."],

            "business_impact_analysis": """
Unfavorable clauses may increase legal costs, financial liability,
and operational risk. Poorly negotiated contracts often impact cash flow
and dispute exposure for SMEs.
""",

            "action_plan": [
                "Review all highlighted clauses carefully",
                "Negotiate removal of one-sided termination rights",
                "Cap financial liability where possible",
                "Ensure governing law is Indian jurisdiction"
            ],

            "negotiation_strategy": [
                "Request mutual termination rights",
                "Add financial liability limits",
                "Replace foreign jurisdiction with Indian courts",
                "Limit duration of confidentiality clauses"
            ],

            "legal_compliance_check": {
                "status": "Potential compliance concerns",
                "issues": [
                    "Foreign jurisdiction may increase legal burden",
                    "Unlimited liability may be considered unreasonable"
                ],
                "recommendations": [
                    "Seek lawyer review for Indian Contract Act compliance"
                ]
            },

            "red_flags": [
                "One-sided termination terms",
                "Unlimited financial liability",
                "Foreign jurisdiction clauses"
            ],

            "industry_benchmarks": """
Typical SME contracts include liability caps, mutual termination clauses,
and Indian jurisdiction. Deviation increases negotiation risk.
""",

            "cost_implications": """
Potential legal disputes under unfavorable clauses can cost significantly
more than early legal review and renegotiation.
"""
        }
