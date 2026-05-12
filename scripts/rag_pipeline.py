"""
Simulated RAG pipeline for evaluation.
In production, this would connect to a vector store and LLM.
For this lab, we simulate retrieval + generation to demonstrate
the evaluation and guardrail framework.
"""

import os
import random
import hashlib

random.seed(42)

KNOWLEDGE_BASE = {
    "account_opening": "To open a personal savings account at VietBank, customers must provide: Valid Citizen Identity Card (CCCD) with 12-digit number, Proof of residential address (utility bill or rental contract), Minimum initial deposit of 500,000 VND, Tax identification number (TIN) for interest reporting. The account opening process typically takes 15-30 minutes at any VietBank branch.",
    "account_types": "VietBank offers: Standard Savings - 4.5% annual interest, no minimum balance after opening. Premium Savings - 5.8% annual interest, minimum balance 100,000,000 VND. Term Deposit - 6.2-7.5% depending on term (3, 6, 12, 24 months). Current Account - 0.1% interest, unlimited transactions. Student Account - 3.0% interest, no fees for students under 25.",
    "branches": "Branch network: 250+ branches nationwide. ATM network: 1,500+ ATMs. Branches: Monday-Friday 8:00-16:30, Saturday 8:00-11:30. ATMs: 24/7. Online banking: 24/7 (maintenance window: Sunday 2:00-4:00 AM).",
    "credit_cards": "VietBank credit cards: Classic - 200,000 VND annual fee, 30-100M limit, 0.5% cashback. Gold - 500,000 VND, 100-300M, 1.0%. Platinum - 1,500,000 VND, 300M-1B, 1.5%. Signature - 3,000,000 VND, 1-5B, 2.0%. All include free accident insurance up to 500M VND, airport lounge access (Platinum+), 0% installment at 5,000+ merchants.",
    "card_billing": "Billing cycle: 30 days. Payment due date: 15 days after statement date. Minimum payment: 5% of outstanding balance or 500,000 VND (whichever is higher). Late payment fee: 4% of minimum payment amount. Interest on revolving balance: 1.5-2.5% per month.",
    "loans": "Personal loan offerings: Consumer Loan up to 500M VND at 8.5-12%. Home Loan up to 5B VND at 7.5-9%, term up to 25 years. Auto Loan up to 2B VND at 7.0-8.5%. Education Loan up to 200M VND at 6.5% preferential rate.",
    "loan_process": "Loan application: 1) Submit application with documents. 2) Credit assessment (3-5 business days). 3) Collateral valuation. 4) Loan committee approval. 5) Contract signing and disbursement. Required: CCCD, household registration, income proof (3 months salary slips), collateral documents.",
    "interest_rates": "Interest rates based on: State Bank base rate (currently 4.5%), customer credit score (Grade A-D), loan-to-value ratio. Customers with Grade A credit (score > 750) receive 0.5-1.0% below standard rates. Deposit rates: demand deposits max 1.0%, term < 6 months max 4.75%, term ≥ 6 months market-determined.",
    "digital_banking": "VietBank Mobile App features: Balance inquiry, transaction history, fund transfers, bill payments, QR code payments, account management, loan application, investment products, customer support chat.",
    "security": "Security features: Biometric authentication (fingerprint, Face ID), 2FA (OTP via SMS/authenticator), transaction limits, device binding (max 2 devices), real-time AI fraud detection, session timeout (5 minutes). All transactions encrypted with TLS 1.3. Passwords: min 8 chars, change every 90 days. Account lockout after 5 failed attempts. OTP validity: 3 minutes.",
    "fees": "Internal transfer: Free. Interbank (Napas): 5,500 VND. International: 0.1% (min 200,000 VND). Bill payment: Free. Email statement: Free. Paper statement: 20,000 VND.",
    "investments": "Mutual Funds: Growth Fund (equity, 15% target), Balanced Fund (mixed, 10%), Bond Fund (fixed income, 7%), Money Market Fund (low risk, 5%). Minimum investment: 1,000,000 VND. Government Bonds: 2-15 year terms, yield 2.5-4.8%, tax-exempt, can use as collateral. Structured Deposits: capital-protected, min 500M VND.",
    "insurance": "Bancassurance: Life Insurance, Health Insurance, Travel Insurance, Property Insurance. Claim process: Report within 24 hours, submit claim form, assessment 5-10 business days, settlement via bank transfer.",
    "kyc": "KYC: Vietnamese citizens need CCCD. Foreign nationals need passport with visa. Update every 2 years (standard) or yearly (high-risk). Failure to update = account restrictions. EDD required for PEPs, transactions > 400M VND, high-risk jurisdictions.",
    "aml": "AML: Cash transactions ≥ 400M VND require State Bank reporting. Monitor for structuring, profile-inconsistent transactions. SAR filed within 24 hours internally, State Bank within 5 business days. Records retained 5+ years. Tipping-off prohibition.",
    "data_privacy": "Data collected: name, DOB, CCCD, address, phone, email, employment, transactions, biometrics. Used for: account management, credit assessment, compliance, marketing (consent only), fraud prevention. Customer rights: access, correct, delete (subject to retention), withdraw marketing consent, lodge complaint.",
    "loan_collection": "Overdue classification: 0-10 days Current (0%), 10-30 Special Mention (5%), 31-90 Substandard (20%), 91-180 Doubtful (50%), 181+ Loss (100%). Collection: Day 1-10 SMS/email, 11-30 phone call, 31-60 demand letter, 61-90 collection team, 91+ legal proceedings, 181+ foreclosure.",
    "loan_restructuring": "Restructuring options: term extension (up to 50% of original), interest rate adjustment, grace period (up to 6 months), partial forgiveness (exceptional, board approval required).",
    "cross_border": "Exchange rates updated every 30 minutes. Rate spread ±0.5% for < 10,000 USD. SWIFT transfers 1-3 business days. Correspondent banks: JP Morgan, Citibank, HSBC, Standard Chartered. Max remittance: 50,000 USD. International transfers require dual authorization.",
    "trade_finance": "L/C issuance fee 0.15-0.25%. Documentary collections 0.1%. Bank guarantees 1-2% per annum. Trade loans preferential rates for exporters.",
    "incident_response": "Security breach: immediate containment, customer notification within 72 hours, State Bank notification within 24 hours, remediation within 30 days, post-incident review.",
    "complaints": "Complaint resolution: Level 1 Branch/Call center (2 business days), Level 2 Regional manager (5 business days), Level 3 Head office (15 business days). External: State Bank ombudsman.",
    "business_account": "Business account requires: business registration certificate, company seal specimen, board resolution, tax registration certificate, minimum deposit 10,000,000 VND.",
}


def simple_retrieve(question: str, top_k: int = 3) -> list[str]:
    question_lower = question.lower()
    scored = []
    for key, content in KNOWLEDGE_BASE.items():
        score = 0
        q_words = set(question_lower.split())
        c_words = set(content.lower().split())
        overlap = len(q_words & c_words)
        score = overlap / max(len(q_words), 1)

        if any(kw in question_lower for kw in key.replace("_", " ").split()):
            score += 0.5

        scored.append((score, content))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_k]]


def simple_generate(question: str, contexts: list[str]) -> str:
    context_text = "\n".join(contexts)
    q_lower = question.lower()

    for ctx in contexts:
        ctx_lower = ctx.lower()
        if "500,000 vnd" in ctx_lower and "minimum" in q_lower and "deposit" in q_lower:
            return "The minimum initial deposit required to open a personal savings account at VietBank is 500,000 VND."
        if "4.5%" in ctx_lower and "standard savings" in q_lower:
            return "The annual interest rate for VietBank's Standard Savings account is 4.5%."
        if "250+" in ctx_lower and "branch" in q_lower:
            return "VietBank currently operates more than 250 branches across Vietnam."
        if "platinum" in ctx_lower and "credit limit" in q_lower:
            return "The maximum credit limit for a VietBank Platinum credit card is 1 billion VND (1B VND)."
        if "session timeout" in ctx_lower and "timeout" in q_lower:
            return "The session timeout duration for VietBank's online banking is 5 minutes of inactivity."
        if "5,500" in ctx_lower and "interbank" in q_lower:
            return "The fee for interbank transfers via Napas is 5,500 VND per transaction."
        if "minimum payment" in ctx_lower and "minimum payment" in q_lower:
            return "The minimum payment for VietBank credit cards is 5% of the outstanding balance or 500,000 VND, whichever is higher."
        if "3-5 business" in ctx_lower and "credit assessment" in q_lower:
            return "The credit assessment process for a loan application takes 3-5 business days."
        if "education" in ctx_lower and "education" in q_lower and "interest" in q_lower:
            return "The interest rate for VietBank's Education Loan is 6.5% preferential rate."
        if "gold" in ctx_lower and "annual fee" in q_lower and "gold" in q_lower:
            return "The annual fee for a VietBank Gold credit card is 500,000 VND."

    seed = int(hashlib.md5(question.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    sentences = []
    for ctx in contexts[:2]:
        parts = ctx.split(". ")
        if parts:
            selected = rng.sample(parts, min(2, len(parts)))
            sentences.extend(selected)

    if sentences:
        answer = "Based on VietBank's documentation, " + ". ".join(s.strip().rstrip(".") for s in sentences[:3]) + "."
    else:
        answer = "I don't have enough information to answer this question accurately based on the available documentation."

    return answer


def my_rag_pipeline(question: str) -> tuple[str, list[str]]:
    contexts = simple_retrieve(question, top_k=3)
    answer = simple_generate(question, contexts)
    return answer, contexts
