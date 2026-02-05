from datetime import datetime

class EnhancedReportGenerator:
    def __init__(self):
        pass
    
    def generate_simple_report(self, analysis_data):
        """Generate professional, easy-to-understand report"""
        report = self._create_simple_report(analysis_data)
        return report.encode('utf-8')
    
    def _create_simple_report(self, analysis_data):
        """Create professional business report"""
        comp_risk = analysis_data.get("composite_risk", {})
        analyses = analysis_data.get("analyses", [])
        
        report = f"""
CONTRACT ANALYSIS REPORT
For Business Owners
Generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}
Tool: Legal Assistant for Indian SMEs

================================================================
QUICK SUMMARY FOR BUSINESS OWNERS
================================================================

{self._get_risk_summary(comp_risk)}

TOP WARNINGS:
{self._get_top_warnings(analyses)}

NEXT STEPS:
{self._get_next_steps(comp_risk)}

================================================================
DETAILED ANALYSIS
================================================================

{self._get_detailed_analysis(analyses)}

================================================================
PRACTICAL BUSINESS ADVICE
================================================================

{self._get_business_advice(comp_risk)}

================================================================
WHEN TO CONSULT A LAWYER
================================================================

{self._get_lawyer_advice(comp_risk)}

================================================================
IMPORTANT NOTES:
- This report provides guidance only, not legal advice
- Always consult a qualified lawyer for important contracts
- Keep this report for your records
- Negotiate changes before signing any contract

Your business safety matters. Review carefully before signing.
"""
        return report
    
    def _get_risk_summary(self, comp_risk):
        overall_risk = comp_risk.get("overall_risk", "Unknown")
        score = comp_risk.get("score", 0)
        
        if overall_risk == "High":
            return f"""HIGH RISK - DO NOT SIGN AS IS

Contract Risk Score: {score}/10 (Dangerous)
High-Risk Clauses: {comp_risk.get('high_risk_count', 0)}

What this means: This contract contains serious problems that could 
cause significant financial loss or legal issues for your business."""
        
        elif overall_risk == "Medium":
            return f"""MEDIUM RISK - NEEDS CHANGES

Contract Risk Score: {score}/10 (Needs Improvement)
Problematic Clauses: {comp_risk.get('medium_risk_count', 0) + comp_risk.get('high_risk_count', 0)}

What this means: Several clauses are unfair to your business. 
You should negotiate changes before signing this contract."""
        
        else:
            return f"""LOW RISK - GENERALLY ACCEPTABLE

Contract Risk Score: {score}/10 (Generally Good)
Mostly Safe Clauses: {comp_risk.get('low_risk_count', 0)}

What this means: Most contract terms appear fair. However, 
a quick legal review is still recommended for important contracts."""
    
    def _get_top_warnings(self, analyses):
        warnings = []
        for analysis in analyses:
            if analysis.get("risk_level") in ["High", "Medium"] and analysis.get("issues"):
                clause_type = analysis.get("type", "Unknown")
                issues = analysis.get("issues", [])
                
                if issues:
                    issue_text = issues[0].get("issue", "")
                    simple_issue = self._simplify_issue(issue_text)
                    warnings.append(f"- Clause {analysis.get('clause_id')} ({clause_type}): {simple_issue}")
                    
                    if len(warnings) >= 3:
                        break
        
        if not warnings:
            warnings = ["- No major issues detected"]
        
        return "\n".join(warnings)
    
    def _simplify_issue(self, issue_text):
        simplifications = {
            "unilateral termination rights are unfair": "Other party can terminate anytime without cause",
            "indefinite confidentiality may be unreasonable": "Confidentiality obligations continue forever",
            "foreign jurisdiction increases legal costs": "Legal disputes must be resolved in foreign country",
            "unlimited liability exposes business to catastrophic risk": "No limit on financial liability",
            "excessive penalty rates can be punitive": "Very high penalty rates for late payments",
            "automatic renewal without notice creates lock-in": "Contract renews automatically",
            "broad indemnity covering all losses is dangerous": "Covers all losses including others' mistakes",
            "long non-compete periods may restrict business": "Very long restrictions on future work"
        }
        
        for complex, simple in simplifications.items():
            if complex.lower() in issue_text.lower():
                return simple
        
        return issue_text[:80] + ("..." if len(issue_text) > 80 else "")
    
    def _get_next_steps(self, comp_risk):
        if comp_risk.get("overall_risk") == "High":
            return """1. Consult a lawyer immediately - do not sign as is
2. Negotiate all high-risk clauses
3. Get all changes documented in writing
4. Consider alternative options if terms cannot be improved"""
        
        elif comp_risk.get("overall_risk") == "Medium":
            return """1. Show this report to your lawyer for review
2. Negotiate the problematic clauses
3. Ensure agreement on all changes
4. Keep records of all communications"""
        
        else:
            return """1. Review the contract yourself carefully
2. Verify all amounts, dates, and terms are correct
3. Consider a quick legal check for important contracts
4. File the signed copy securely"""
    
    def _get_detailed_analysis(self, analyses):
        if not analyses:
            return "No detailed analysis available."
        
        details = []
        for analysis in analyses[:5]:
            clause_id = analysis.get("clause_id", "?")
            clause_type = analysis.get("type", "Unknown")
            risk_level = analysis.get("risk_level", "Unknown")
            explanation = analysis.get("explanation", "")
            
            simple_explanation = self._simplify_explanation(explanation)
            
            details.append(f"""
Clause {clause_id} - {clause_type} ({risk_level} Risk Level)

{simple_explanation}
""")
        
        return "\n".join(details)
    
    def _simplify_explanation(self, explanation):
        if len(explanation) > 150:
            sentences = explanation.split('. ')
            if sentences and len(sentences[0]) > 20:
                return sentences[0] + "."
            else:
                return explanation[:120] + "..."
        return explanation
    
    def _get_business_advice(self, comp_risk):
        advice = []
        
        if comp_risk.get("high_risk_count", 0) > 0:
            advice.append("- High-risk clauses could result in significant financial loss")
        
        if comp_risk.get("overall_risk") in ["High", "Medium"]:
            advice.append("- Request a liability cap (maximum amount you can owe)")
            advice.append("- Add reasonable notice periods for termination")
            advice.append("- Specify Indian courts for dispute resolution")
        
        advice.append("- If terms seem unfair, they probably are")
        
        return "\n".join(advice)
    
    def _get_lawyer_advice(self, comp_risk):
        if comp_risk.get("overall_risk") == "High":
            return """Consult a lawyer immediately if:
- Contract value exceeds Rs. 5 lakhs
- Unlimited liability clause is present
- Foreign jurisdiction is specified
- Any part of the contract is unclear"""
        
        elif comp_risk.get("overall_risk") == "Medium":
            return """Show to a lawyer before signing if:
- Contract value exceeds Rs. 10 lakhs
- More than 2 high-risk clauses exist
- Agreement duration is more than 1 year
- Important business relationship is involved"""
        
        else:
            return """Consider a legal review if:
- First time doing business with this party
- Unusual business arrangement
- Large payment is involved
- Intellectual property is included"""