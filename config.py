import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

# File paths
TEMPLATES_DIR = BASE_DIR / "templates"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
AUDIT_LOGS_DIR = BASE_DIR / "audit_logs"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Create directories
for dir_path in [TEMPLATES_DIR, KNOWLEDGE_BASE_DIR, AUDIT_LOGS_DIR, OUTPUTS_DIR]:
    dir_path.mkdir(exist_ok=True)

# Risk categories
RISK_CATEGORIES = {
    "penalty_clauses": ["penalty", "liquidated damages", "fine", "forfeiture"],
    "indemnity_clauses": ["indemnify", "hold harmless", "indemnity"],
    "termination": ["termination", "terminate", "cancel"],
    "jurisdiction": ["jurisdiction", "governing law", "venue"],
    "renewal": ["auto-renew", "automatic renewal", "evergreen"],
    "non_compete": ["non-compete", "non-solicit", "restrictive covenant"],
    "ip_transfer": ["intellectual property", "IP", "assign", "transfer"],
    "liability": ["liability", "warranty", "guarantee"]
}

# Indian legal compliance keywords (basic)
INDIAN_COMPLIANCE_ISSUES = [
    "unfair trade practice",
    "unconscionable",
    "oppressive",
    "one-sided",
    "without cause",
    "sole discretion"
]