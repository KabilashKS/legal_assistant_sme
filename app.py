import streamlit as st
import PyPDF2
from docx import Document
import re
import json
import pandas as pd
from datetime import datetime
import tempfile
import os
import sys

# Add current directory to path to import your LLMHandler
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import LLMHandler from your file
try:
    from llm_handler import LLMHandler, LLMConfig  # Your file name
except ImportError:
    # Create a simple fallback if import fails
    class LLMHandler:
        def __init__(self, use_mock=True):
            self.use_mock = use_mock
        
        def explain_clause(self, clause_text):
            return f"This clause appears to be standard. For detailed analysis, add OpenAI API key."

# Page configuration
st.set_page_config(
    page_title="Legal Assistant for SMEs",
    page_icon="⚖️",
    layout="wide"
)

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'contract_text' not in st.session_state:
    st.session_state.contract_text = ""
if 'clauses' not in st.session_state:
    st.session_state.clauses = []
if 'detailed_report' not in st.session_state:
    st.session_state.detailed_report = None

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-high {
        color: #DC2626;
        font-weight: bold;
        padding: 2px 8px;
        border-radius: 4px;
        background-color: #FEE2E2;
    }
    .risk-medium {
        color: #D97706;
        font-weight: bold;
        padding: 2px 8px;
        border-radius: 4px;
        background-color: #FEF3C7;
    }
    .risk-low {
        color: #059669;
        font-weight: bold;
        padding: 2px 8px;
        border-radius: 4px;
        background-color: #D1FAE5;
    }
    .clause-box {
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #F8FAFC;
        border-radius: 0 8px 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# Document Processor Class
class DocumentProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc', '.txt']
    
    def extract_text(self, file_path: str, file_type: str) -> str:
        try:
            if file_type == 'pdf':
                return self._extract_from_pdf(file_path)
            elif file_type in ['docx', 'doc']:
                return self._extract_from_docx(file_path)
            elif file_type == 'txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise ValueError(f"Unsupported format: {file_type}")
        except Exception as e:
            return f"Error extracting text: {str(e)}. Using fallback: you can paste text directly."
    
    def _extract_from_pdf(self, file_path: str) -> str:
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        except:
            text = "Could not extract PDF text. Try converting to text format first."
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except:
            return "Could not extract Word document text. Try saving as .txt first."

# Initialize modules
doc_processor = DocumentProcessor()
llm_handler = LLMHandler(use_mock=True)  # Use mock for demo

# Streamlit UI
st.title("⚖️ Legal Assistant for Small & Medium Businesses")
st.write("AI-powered contract analysis for Indian SMEs")

# Sidebar
with st.sidebar:
    st.title("📋 Legal Assistant")
    
    st.markdown("---")
    
    # Option 1: File upload
    st.subheader("Upload Contract")
    uploaded_file = st.file_uploader(
        "Choose a contract file",
        type=['pdf', 'docx', 'doc', 'txt'],
        help="Upload PDF, Word, or Text files"
    )
    
    # Option 2: Text input
    st.subheader("Or Paste Text")
    text_input = st.text_area(
        "Paste contract text here:",
        height=200,
        placeholder="Paste your contract text here...",
        help="For quick testing, paste contract text directly"
    )
    
    # Process input
    contract_text = ""
    
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp_file:
            tmp_file.write(uploaded_file.read())
            file_path = tmp_file.name
        
        with st.spinner("Processing document..."):
            try:
                file_ext = uploaded_file.name.split('.')[-1].lower()
                contract_text = doc_processor.extract_text(file_path, file_ext)
                os.unlink(file_path)
                st.success("File processed!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    elif text_input:
        contract_text = text_input
        st.success("Text ready for analysis!")
    
    # Store contract text
    if contract_text:
        st.session_state.contract_text = contract_text
        
        # Simple clause segmentation
        paragraphs = [p.strip() for p in contract_text.split('\n\n') if p.strip()]
        clauses = []
        for i, para in enumerate(paragraphs[:15]):
            if para and len(para) > 20:
                clauses.append({
                    "clause_id": i + 1,
                    "title": f"Clause {i + 1}",
                    "text": para[:500],
                    "full_text": para
                })
        st.session_state.clauses = clauses
    
    st.markdown("---")
    
    # API Key input
    st.subheader("API Configuration")
    api_key = st.text_input("OpenAI API Key (optional)", type="password", 
                           help="Add your API key for real AI analysis")
    
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        llm_handler = LLMHandler(use_mock=False)
        st.success("Using real AI analysis!")
    
    st.markdown("---")
    
    # Sample contract
    if st.button("📋 Load Sample Contract", use_container_width=True):
        sample_text = """EMPLOYMENT AGREEMENT

This Employment Agreement is made on January 15, 2024 between:

INNOVATE TECH SOLUTIONS PVT. LTD.
Address: Mumbai, India
(the "Company")

AND

RAJESH SHARMA
Address: Delhi, India
(the "Employee")

1. POSITION AND DUTIES
The Employee shall serve as Senior Developer. Company may terminate at its sole discretion without cause.

2. COMPENSATION
Monthly salary: ₹85,000. Late payment penalty: 5% per month.

3. CONFIDENTIALITY
Employee shall maintain confidentiality of all Company information indefinitely.

4. JURISDICTION
Any disputes shall be subject to exclusive jurisdiction of courts in Singapore.

5. LIABILITY
Employee's liability to Company shall be unlimited for any breach.

6. AUTO-RENEWAL
This Agreement shall automatically renew for additional one-year terms without notice."""
        
        st.session_state.contract_text = sample_text
        paragraphs = [p.strip() for p in sample_text.split('\n\n') if p.strip()]
        clauses = []
        for i, para in enumerate(paragraphs):
            if para and len(para) > 20:
                clauses.append({
                    "clause_id": i + 1,
                    "title": f"Clause {i + 1}",
                    "text": para[:500],
                    "full_text": para
                })
        st.session_state.clauses = clauses
        st.success("Sample contract loaded!")
        st.rerun()
    
    st.markdown("---")
    st.info("💡 **Tip:** Start with the sample contract to see how it works.")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📑 Analysis", "⚠️ Risks", "📄 Report"])

with tab1:
    st.header("Contract Overview")
    
    if st.session_state.contract_text:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Clauses", len(st.session_state.clauses))
        
        with col2:
            word_count = len(st.session_state.contract_text.split())
            st.metric("Word Count", word_count)
        
        with col3:
            # Check for risk indicators
            text_lower = st.session_state.contract_text.lower()
            risk_count = 0
            if 'sole discretion' in text_lower:
                risk_count += 1
            if 'indefinite' in text_lower and 'confidential' in text_lower:
                risk_count += 1
            if 'singapore' in text_lower and ('jurisdiction' in text_lower or 'court' in text_lower):
                risk_count += 1
            if 'unlimited' in text_lower and 'liability' in text_lower:
                risk_count += 1
            
            st.metric("Risk Indicators", risk_count)
        
        # Show contract preview
        with st.expander("📄 View Contract Text"):
            st.text(st.session_state.contract_text[:1500] + ("..." if len(st.session_state.contract_text) > 1500 else ""))
        
        # Analyze button
        if st.button("🔍 Run AI Analysis", type="primary", use_container_width=True):
            with st.spinner("Analyzing contract with AI..."):
                try:
                    analyses = []
                    
                    for i, clause in enumerate(st.session_state.clauses[:10]):
                        # Get AI explanation
                        explanation = llm_handler.explain_clause(clause["text"])
                        
                        # Simple risk detection
                        clause_lower = clause["text"].lower()
                        risk_score = 0
                        
                        if 'sole discretion' in clause_lower:
                            risk_score += 3
                        if 'indefinite' in clause_lower and 'confidential' in clause_lower:
                            risk_score += 3
                        if 'singapore' in clause_lower and ('jurisdiction' in clause_lower or 'court' in clause_lower):
                            risk_score += 3
                        if 'unlimited' in clause_lower and 'liability' in clause_lower:
                            risk_score += 3
                        if '5%' in clause_lower and ('penalty' in clause_lower or 'late' in clause_lower):
                            risk_score += 2
                        
                        # Determine risk level
                        if risk_score >= 3:
                            risk_level = "High"
                        elif risk_score >= 1:
                            risk_level = "Medium"
                        else:
                            risk_level = "Low"
                        
                        analyses.append({
                            "clause_id": clause["clause_id"],
                            "title": clause["title"],
                            "type": "General",
                            "risk_score": risk_score,
                            "risk_level": risk_level,
                            "explanation": explanation,
                            "text_preview": clause["text"][:200] + "..."
                        })
                    
                    # Calculate composite risk
                    high_count = sum(1 for a in analyses if a["risk_level"] == "High")
                    medium_count = sum(1 for a in analyses if a["risk_level"] == "Medium")
                    total_score = sum(a["risk_score"] for a in analyses)
                    avg_score = total_score / len(analyses) if analyses else 0
                    
                    if avg_score >= 2.5:
                        overall_risk = "High"
                    elif avg_score >= 1:
                        overall_risk = "Medium"
                    else:
                        overall_risk = "Low"
                    
                    st.session_state.analysis_results = {
                        "analyses": analyses,
                        "composite_risk": {
                            "overall_risk": overall_risk,
                            "score": round(avg_score, 1),
                            "high_risk_count": high_count,
                            "medium_risk_count": medium_count,
                            "total_clauses": len(analyses)
                        },
                        "summary": f"Analysis complete. Found {high_count} high-risk and {medium_count} medium-risk clauses. {'⚠️ Immediate review recommended.' if high_count > 0 else 'Review suggested before signing.'}",
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    st.success("✅ Analysis complete!")
                    st.balloons()
                    
                    # Show results
                    st.subheader("📈 Analysis Results")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Overall Risk", overall_risk)
                    
                    with col2:
                        st.metric("High Risk Clauses", high_count)
                    
                    with col3:
                        st.metric("Medium Risk Clauses", medium_count)
                    
                except Exception as e:
                    st.error(f"Analysis error: {str(e)}")
    
    else:
        st.info("👈 Upload a contract or paste text in the sidebar to begin.")

# In the analysis section (around line 270), update this part:

with tab2:
    st.header("Clause-by-Clause Analysis")
    
    if st.session_state.analysis_results:
        analyses = st.session_state.analysis_results["analyses"]
        
        for analysis in analyses:
            # Create expander with better styling
            risk_color = {
                "High": "🔴",
                "Medium": "🟡", 
                "Low": "🟢"
            }.get(analysis["risk_level"], "⚪")
            
            with st.expander(f"{risk_color} Clause {analysis['clause_id']}: {analysis['title']} - {analysis['risk_level']} Risk", expanded=False):
                
                # Risk summary
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    risk_level = analysis["risk_level"].lower()
                    risk_html = f'<span class="risk-{risk_level}">{analysis["risk_level"]} Risk</span>'
                    st.markdown(f"**Risk Level:** {risk_html}", unsafe_allow_html=True)
                    st.metric("Risk Score", f"{analysis.get('risk_score', 'N/A')}/10")
                
                with col2:
                    st.write("**📋 Clause Preview:**")
                    st.markdown(f'<div class="clause-box">{analysis["text_preview"]}</div>', unsafe_allow_html=True)
                
                # AI Explanation in detail
                st.markdown("---")
                
                # Summary
                if "summary" in analysis:
                    st.subheader("📌 Summary")
                    st.info(analysis["summary"])
                
                # Legal Issues
                if "legal_issues" in analysis and analysis["legal_issues"]:
                    st.subheader("⚖️ Legal Issues")
                    for issue in analysis["legal_issues"]:
                        st.write(f"• {issue}")
                
                # Business Impact
                if "business_impact" in analysis:
                    st.subheader("💼 Business Impact")
                    st.warning(analysis["business_impact"])
                
                # Recommendations
                if "recommendations" in analysis:
                    st.subheader("✅ Recommendations")
                    for rec in analysis["recommendations"]:
                        st.write(f"• {rec}")
                
                # Alternative Wording
                if "alternative_wording" in analysis:
                    st.subheader("📝 Suggested Improvement")
                    st.success(analysis["alternative_wording"])
                
                # Negotiation Tips
                if "negotiation_tips" in analysis:
                    with st.expander("💡 Negotiation Tips"):
                        for tip in analysis["negotiation_tips"]:
                            st.write(f"• {tip}")
                
                # Indian Law Reference
                if "indian_law_reference" in analysis:
                    with st.expander("📚 Legal References"):
                        st.write(analysis["indian_law_reference"])
    else:
        st.info("Run analysis from the Overview tab first.")
with tab3:
    st.header("Risk Assessment Dashboard")
    
    if st.session_state.analysis_results:
        composite = st.session_state.analysis_results["composite_risk"]
        
        # Risk overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Overall Risk", composite["overall_risk"])
        
        with col2:
            st.metric("High Risk Clauses", composite["high_risk_count"])
        
        with col3:
            st.metric("Medium Risk Clauses", composite["medium_risk_count"])
        
        # Risk distribution chart
        st.subheader("Risk Distribution")
        risk_data = pd.DataFrame({
            "Risk Level": ["High", "Medium", "Low"],
            "Count": [
                composite["high_risk_count"],
                composite["medium_risk_count"],
                composite["total_clauses"] - composite["high_risk_count"] - composite["medium_risk_count"]
            ]
        })
        st.bar_chart(risk_data.set_index("Risk Level"))
        
        # Recommendations
        st.subheader("📋 Recommendations")
        
        if composite["overall_risk"] == "High":
            st.error("""
            **🚨 Immediate Action Required:**
            1. Do NOT sign in current form
            2. Consult with a lawyer immediately
            3. Negotiate all high-risk clauses
            4. Consider alternative options if terms cannot be improved
            """)
        elif composite["overall_risk"] == "Medium":
            st.warning("""
            **⚠️ Proceed with Caution:**
            1. Get legal review for problematic clauses
            2. Negotiate changes before signing
            3. Document all agreed changes in writing
            4. Ensure business terms are clearly specified
            """)
        else:
            st.success("""
            **✅ Generally Acceptable:**
            1. Still recommend final legal review
            2. Verify all terms match your understanding
            3. Ensure proper execution and signatures
            4. Keep signed copy securely
            """)
    else:
        st.info("Run analysis first to see risk assessment.")

with tab4:
    st.header("📊 Comprehensive Analysis Report")
    
    # Initialize detailed report in session state
    if 'detailed_report' not in st.session_state:
        st.session_state.detailed_report = None
    
    if st.session_state.analysis_results:
        composite = st.session_state.analysis_results["composite_risk"]
        analyses = st.session_state.analysis_results["analyses"]
        
        # Helper function to create basic report
        def create_basic_report(composite, analyses):
            return {
                "executive_summary": f"""
                **CONTRACT ANALYSIS REPORT**
                
                This analysis examined {len(analyses)} clauses and found {composite['high_risk_count']} high-risk 
                and {composite['medium_risk_count']} medium-risk issues requiring attention.
                
                **Overall Risk Assessment:** {composite['overall_risk']} (Score: {composite['score']}/10)
                
                {"🚨 IMMEDIATE ACTION REQUIRED: High-risk clauses detected." if composite['high_risk_count'] > 0 else "⚠️ Review recommended before signing."}
                
                For Indian SMEs, it's crucial to review jurisdiction clauses, liability limits, 
                and termination procedures to ensure they align with Indian business practices.
                """,
                "risk_analysis": f"""
                **RISK BREAKDOWN:**
                
                • High Risk Clauses: {composite['high_risk_count']}
                • Medium Risk Clauses: {composite['medium_risk_count']}
                • Low Risk Clauses: {composite['total_clauses'] - composite['high_risk_count'] - composite['medium_risk_count']}
                
                **Key Risk Areas:**
                1. Legal & Compliance Risk
                2. Financial Risk Exposure
                3. Operational Disruption Risk
                4. Business Continuity Risk
                """,
                "critical_issues": [
                    "Complete clause-by-clause analysis recommended",
                    "Review jurisdiction and dispute resolution clauses",
                    "Verify liability limits and penalty terms",
                    "Check termination and renewal procedures"
                ],
                "business_impact_analysis": "Detailed impact analysis requires professional legal review. Key considerations include financial exposure, operational continuity, and compliance requirements.",
                "action_plan": [
                    "IMMEDIATE: Consult with qualified Indian lawyer",
                    "WEEK 1: Document all concerns and required changes",
                    "WEEK 2: Request amendments in writing",
                    "WEEK 3: Negotiate key terms (jurisdiction, liability, termination)",
                    "WEEK 4: Final review and execution"
                ],
                "negotiation_strategy": [
                    "Priority 1: Ensure Indian jurisdiction for all disputes",
                    "Priority 2: Limit liability to reasonable business amounts",
                    "Priority 3: Add reasonable notice periods for termination",
                    "Priority 4: Specify clear payment terms (net 30-45 days)",
                    "Priority 5: Avoid indefinite or perpetual obligations"
                ],
                "legal_compliance_check": {
                    "status": "Professional Review Required",
                    "issues": ["Complete legal review recommended for Indian compliance"],
                    "recommendations": ["Consult with legal professional specializing in Indian contract law"]
                },
                "red_flags": [
                    "⚠️ Professional legal review strongly recommended",
                    f"🚨 {composite['high_risk_count']} high-risk clauses require immediate attention" if composite['high_risk_count'] > 0 else "✅ No critical red flags detected"
                ],
                "industry_benchmarks": "Standard Indian SME contracts typically include: Indian jurisdiction, limited liability, reasonable notice periods, and clear renewal procedures.",
                "cost_implications": "Potential costs include legal fees, dispute resolution expenses, penalty charges, and operational disruptions. Professional review can help mitigate these risks."
            }
        
        # Generate detailed report button
        if st.button("📈 Generate Comprehensive AI Report", type="primary", use_container_width=True):
            with st.spinner("🧠 Generating detailed AI-powered report. This may take a minute..."):
                try:
                    # Try to generate report - if generate_detailed_report exists
                    if hasattr(llm_handler, 'generate_detailed_report'):
                        detailed_report = llm_handler.generate_detailed_report(
                            analyses, 
                            st.session_state.contract_text[:2000]
                        )
                    else:
                        # If method doesn't exist, create a basic report
                        detailed_report = create_basic_report(composite, analyses)
                    
                    # Store in session state
                    st.session_state.detailed_report = detailed_report
                    st.success("✅ Detailed report generated!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Report generation failed: {str(e)}")
                    # Create a simple fallback report
                    detailed_report = create_basic_report(composite, analyses)
                    st.session_state.detailed_report = detailed_report
                    st.warning("⚠️ Basic report generated (fallback mode)")
                    st.rerun()
        
        # Check if we have a detailed report
        if st.session_state.detailed_report:
            detailed_report = st.session_state.detailed_report
            
            # Display report sections
            st.subheader("📋 Executive Summary")
            if "executive_summary" in detailed_report:
                st.markdown(detailed_report["executive_summary"])
            
            st.markdown("---")
            
            st.subheader("⚠️ Risk Analysis")
            if "risk_analysis" in detailed_report:
                st.markdown(detailed_report["risk_analysis"])
            
            if "critical_issues" in detailed_report and detailed_report["critical_issues"]:
                with st.expander("🚨 Critical Issues", expanded=True):
                    for issue in detailed_report["critical_issues"]:
                        if isinstance(issue, str):
                            st.error(f"• {issue}")
            
            if "red_flags" in detailed_report and detailed_report["red_flags"]:
                with st.expander("🚩 Red Flags", expanded=True):
                    for flag in detailed_report["red_flags"]:
                        if isinstance(flag, str):
                            st.warning(flag)
            
            st.markdown("---")
            
            st.subheader("🎯 Action Plan")
            col1, col2 = st.columns(2)
            
            with col1:
                if "action_plan" in detailed_report and detailed_report["action_plan"]:
                    st.info("### 📅 Timeline")
                    for i, action in enumerate(detailed_report["action_plan"], 1):
                        if isinstance(action, str):
                            st.markdown(f"**Step {i}:** {action}")
            
            with col2:
                if "negotiation_strategy" in detailed_report and detailed_report["negotiation_strategy"]:
                    st.success("### 💼 Negotiation Strategy")
                    for strategy in detailed_report["negotiation_strategy"]:
                        if isinstance(strategy, str):
                            st.markdown(f"• {strategy}")
            
            st.markdown("---")
            
            # Additional sections in expanders
            if "business_impact_analysis" in detailed_report:
                with st.expander("📊 Business Impact Analysis", expanded=False):
                    st.markdown(detailed_report["business_impact_analysis"])
            
            if "legal_compliance_check" in detailed_report:
                with st.expander("⚖️ Legal Compliance", expanded=False):
                    compliance = detailed_report["legal_compliance_check"]
                    if isinstance(compliance, dict):
                        st.metric("Compliance Status", compliance.get("status", "To Be Assessed"))
                        if "issues" in compliance and compliance["issues"]:
                            st.warning("**Issues:**")
                            for issue in compliance["issues"]:
                                st.write(f"• {issue}")
                        if "recommendations" in compliance and compliance["recommendations"]:
                            st.success("**Recommendations:**")
                            for rec in compliance["recommendations"]:
                                st.write(f"• {rec}")
            
            if "industry_benchmarks" in detailed_report:
                with st.expander("📈 Industry Standards", expanded=False):
                    st.markdown(detailed_report["industry_benchmarks"])
            
            if "cost_implications" in detailed_report:
                with st.expander("💰 Cost Implications", expanded=False):
                    st.markdown(detailed_report["cost_implications"])
            
            st.markdown("---")
            
            # Generate downloadable report
            st.subheader("📄 Download Report")
            
            # Create full report text
            full_report = f"""
COMPREHENSIVE CONTRACT ANALYSIS REPORT
=======================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Client: Indian SME Business

EXECUTIVE SUMMARY
=================
{detailed_report.get('executive_summary', '')}

CONTRACT METRICS
================
Overall Risk Level: {composite['overall_risk']}
Risk Score: {composite['score']}/10
High Risk Clauses: {composite['high_risk_count']}
Medium Risk Clauses: {composite['medium_risk_count']}
Total Clauses Analyzed: {composite['total_clauses']}

RISK ANALYSIS
=============
{detailed_report.get('risk_analysis', '')}

CRITICAL ISSUES
===============
"""
            
            if "critical_issues" in detailed_report:
                for issue in detailed_report["critical_issues"]:
                    full_report += f"• {issue}\n"
            
            full_report += f"""
BUSINESS IMPACT
===============
{detailed_report.get('business_impact_analysis', '')}

ACTION PLAN
===========
"""
            
            if "action_plan" in detailed_report:
                for i, action in enumerate(detailed_report["action_plan"], 1):
                    full_report += f"{i}. {action}\n"
            
            full_report += f"""
NEGOTIATION STRATEGY
====================
"""
            
            if "negotiation_strategy" in detailed_report:
                for strategy in detailed_report["negotiation_strategy"]:
                    full_report += f"• {strategy}\n"
            
            full_report += f"""
LEGAL COMPLIANCE
================
{detailed_report.get('legal_compliance_check', {}).get('status', 'Professional review required')}

INDUSTRY STANDARDS
==================
{detailed_report.get('industry_benchmarks', '')}

COST IMPLICATIONS
=================
{detailed_report.get('cost_implications', '')}

RECOMMENDATIONS
===============
1. Consult with qualified Indian lawyer before signing
2. Ensure Indian jurisdiction for all disputes
3. Limit liability to reasonable business amounts
4. Add clear notice periods (30-90 days)
5. Avoid indefinite or perpetual obligations
6. Document all changes in writing
7. Keep complete contract records

DISCLAIMER
==========
This report provides guidance only, not legal advice.
Always consult with qualified legal professionals.

Report generated: {datetime.now().strftime('%B %d, %Y')}
"""
            
            # Download buttons
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📥 Download Full Report",
                    data=full_report,
                    file_name=f"contract_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    type="primary"
                )
            
            with col2:
                # Export as JSON
                json_report = {
                    "metadata": {
                        "generated": datetime.now().isoformat(),
                        "analysis_type": "contract_review",
                        "for": "Indian SME"
                    },
                    "summary": {
                        "overall_risk": composite['overall_risk'],
                        "risk_score": composite['score'],
                        "high_risk_clauses": composite['high_risk_count'],
                        "medium_risk_clauses": composite['medium_risk_count'],
                        "total_clauses": composite['total_clauses']
                    },
                    "report": detailed_report
                }
                
                json_data = json.dumps(json_report, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📊 Download JSON Data",
                    data=json_data,
                    file_name=f"analysis_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # Regenerate button
            if st.button("🔄 Generate New Report", use_container_width=True):
                st.session_state.detailed_report = None
                st.rerun()
        
        else:
            st.info("Click 'Generate Comprehensive AI Report' to create a detailed analysis report.")
            
            # Show quick overview
            st.subheader("Quick Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Overall Risk", composite['overall_risk'])
            with col2:
                st.metric("High Risk Clauses", composite['high_risk_count'])
            with col3:
                st.metric("Medium Risk Clauses", composite['medium_risk_count'])
            
            st.info("""
            **What the report will include:**
            • Executive summary with risk assessment
            • Detailed risk analysis by category
            • Action plan with timeline
            • Negotiation strategy
            • Legal compliance check
            • Industry benchmarks
            • Cost implications
            • Downloadable formats
            """)
    
    else:
        st.info("Complete analysis first to generate detailed reports.")