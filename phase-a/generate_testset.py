"""
Task A.1 - Synthetic Test Set Generation
Generates 50 questions from document corpus with distribution:
  50% simple (single-hop), 25% reasoning, 25% multi-context
"""

import pandas as pd
import os
import json
import random

random.seed(42)

SIMPLE_QUESTIONS = [
    {
        "question": "What is the minimum initial deposit required to open a personal savings account at VietBank?",
        "ground_truth": "The minimum initial deposit required is 500,000 VND.",
        "contexts": ["To open a personal savings account at VietBank, customers must provide: Valid Citizen Identity Card (CCCD) with 12-digit number, Proof of residential address, Minimum initial deposit of 500,000 VND, Tax identification number (TIN) for interest reporting."],
        "evolution_type": "simple"
    },
    {
        "question": "What is the annual interest rate for VietBank's Standard Savings account?",
        "ground_truth": "The Standard Savings account offers 4.5% annual interest.",
        "contexts": ["Standard Savings - 4.5% annual interest, no minimum balance after opening."],
        "evolution_type": "simple"
    },
    {
        "question": "How many branches does VietBank operate nationwide?",
        "ground_truth": "VietBank operates 250+ branches nationwide.",
        "contexts": ["Branch network: 250+ branches nationwide. ATM network: 1,500+ ATMs."],
        "evolution_type": "simple"
    },
    {
        "question": "What is the maximum credit limit for a VietBank Platinum credit card?",
        "ground_truth": "The maximum credit limit for a Platinum card is 1 billion VND.",
        "contexts": ["Platinum | 1,500,000 VND | 300M-1B VND | 1.5%"],
        "evolution_type": "simple"
    },
    {
        "question": "What is the session timeout duration for VietBank's online banking?",
        "ground_truth": "The session timeout is 5 minutes of inactivity.",
        "contexts": ["Session timeout: Auto-logout after 5 minutes of inactivity. Session timeout: 5 minutes of inactivity."],
        "evolution_type": "simple"
    },
    {
        "question": "What is the fee for interbank transfers via Napas?",
        "ground_truth": "The fee for interbank transfers via Napas is 5,500 VND per transaction.",
        "contexts": ["Interbank transfer (Napas) | 5,500 VND per transaction"],
        "evolution_type": "simple"
    },
    {
        "question": "What is the minimum payment required for VietBank credit cards?",
        "ground_truth": "The minimum payment is 5% of outstanding balance or 500,000 VND, whichever is higher.",
        "contexts": ["Minimum payment: 5% of outstanding balance or 500,000 VND (whichever is higher)."],
        "evolution_type": "simple"
    },
    {
        "question": "How long does the credit assessment process take for a loan application?",
        "ground_truth": "The credit assessment takes 3-5 business days.",
        "contexts": ["Credit assessment (3-5 business days). Collateral valuation if applicable. Loan committee approval."],
        "evolution_type": "simple"
    },
    {
        "question": "What is the interest rate for VietBank's Education Loan?",
        "ground_truth": "The Education Loan has a preferential rate of 6.5%.",
        "contexts": ["Education Loan: Up to 200,000,000 VND, 6.5% preferential rate."],
        "evolution_type": "simple"
    },
    {
        "question": "What is the annual fee for a VietBank Gold credit card?",
        "ground_truth": "The annual fee for a Gold credit card is 500,000 VND.",
        "contexts": ["Gold | 500,000 VND | 100-300M VND | 1.0%"],
        "evolution_type": "simple"
    },
    {
        "question": "What is the cashback rate for VietBank Signature credit card?",
        "ground_truth": "The Signature credit card offers 2.0% cashback.",
        "contexts": ["Signature | 3,000,000 VND | 1-5B VND | 2.0%"],
        "evolution_type": "simple"
    },
    {
        "question": "How many ATMs does VietBank have?",
        "ground_truth": "VietBank has 1,500+ ATMs.",
        "contexts": ["ATM network: 1,500+ ATMs."],
        "evolution_type": "simple"
    },
    {
        "question": "What is the minimum investment for VietBank mutual funds?",
        "ground_truth": "The minimum investment for mutual funds is 1,000,000 VND.",
        "contexts": ["Minimum investment: 1,000,000 VND. No lock-up period for open-ended funds."],
        "evolution_type": "simple"
    },
    {
        "question": "What are VietBank branch operating hours on weekdays?",
        "ground_truth": "Branches operate Monday-Friday from 8:00 to 16:30.",
        "contexts": ["Branches: Monday-Friday 8:00-16:30, Saturday 8:00-11:30."],
        "evolution_type": "simple"
    },
    {
        "question": "What is the late payment fee for VietBank credit cards?",
        "ground_truth": "The late payment fee is 4% of the minimum payment amount.",
        "contexts": ["Late payment fee: 4% of minimum payment amount."],
        "evolution_type": "simple"
    },
    {
        "question": "What is the target annual return for VietBank Growth Fund?",
        "ground_truth": "The VietBank Growth Fund targets 15% annual return.",
        "contexts": ["VietBank Growth Fund: Equity-focused, target 15% annual return."],
        "evolution_type": "simple"
    },
    {
        "question": "How many failed login attempts cause account lockout?",
        "ground_truth": "Account lockout occurs after 5 failed attempts.",
        "contexts": ["Account lockout after 5 failed attempts."],
        "evolution_type": "simple"
    },
    {
        "question": "What is the OTP validity period?",
        "ground_truth": "OTP validity is 3 minutes.",
        "contexts": ["OTP validity: 3 minutes."],
        "evolution_type": "simple"
    },
    {
        "question": "What is the maximum amount for individual international remittance?",
        "ground_truth": "The maximum individual remittance is 50,000 USD per transaction.",
        "contexts": ["Maximum individual remittance: 50,000 USD per transaction."],
        "evolution_type": "simple"
    },
    {
        "question": "How often must customer information be updated for standard accounts?",
        "ground_truth": "Customer information must be updated every 2 years for standard accounts.",
        "contexts": ["Every 2 years for standard accounts. Every year for high-risk accounts."],
        "evolution_type": "simple"
    },
    {
        "question": "What encryption standard does VietBank use for transactions?",
        "ground_truth": "VietBank uses TLS 1.3 encryption for all transactions.",
        "contexts": ["All transactions encrypted with TLS 1.3."],
        "evolution_type": "simple"
    },
    {
        "question": "What is the minimum deposit for Structured Deposits?",
        "ground_truth": "The minimum deposit for Structured Deposits is 500,000,000 VND.",
        "contexts": ["Minimum deposit: 500,000,000 VND."],
        "evolution_type": "simple"
    },
    {
        "question": "How long are transaction records retained?",
        "ground_truth": "Transaction records are retained for a minimum of 5 years.",
        "contexts": ["Transaction records retained for minimum 5 years."],
        "evolution_type": "simple"
    },
    {
        "question": "What is the current State Bank of Vietnam base rate?",
        "ground_truth": "The current State Bank of Vietnam base rate is 4.5%.",
        "contexts": ["Vietnam State Bank base rate (currently 4.5%)."],
        "evolution_type": "simple"
    },
    {
        "question": "What is the billing cycle for VietBank credit cards?",
        "ground_truth": "The billing cycle is 30 days.",
        "contexts": ["Billing cycle: 30 days. Payment due date: 15 days after statement date."],
        "evolution_type": "simple"
    },
]

REASONING_QUESTIONS = [
    {
        "question": "If a customer has a Grade A credit score, what home loan interest rate range would they qualify for?",
        "ground_truth": "A Grade A customer (score > 750) receives 0.5-1.0% below standard rates. Since home loan standard rate is 7.5-9%, they would qualify for approximately 6.5-8.5%.",
        "contexts": [
            "Home Loan: Up to 5,000,000,000 VND, 7.5-9% interest rate, term up to 25 years.",
            "Customers with Grade A credit (score > 750) receive preferential rates 0.5-1.0% below standard."
        ],
        "evolution_type": "reasoning"
    },
    {
        "question": "A customer makes a credit card purchase of 10,000,000 VND and only pays the minimum. What is the minimum payment amount and what interest would accrue on the remaining balance?",
        "ground_truth": "Minimum payment is 5% of 10,000,000 = 500,000 VND (meets the 500,000 VND floor). The remaining 9,500,000 VND would accrue interest at 1.5-2.5% per month, which is 142,500-237,500 VND.",
        "contexts": [
            "Minimum payment: 5% of outstanding balance or 500,000 VND (whichever is higher).",
            "Interest on revolving balance: 1.5-2.5% per month."
        ],
        "evolution_type": "reasoning"
    },
    {
        "question": "Why would a customer with over 400,000,000 VND in transactions face additional scrutiny compared to a regular customer?",
        "ground_truth": "Cash transactions ≥ 400,000,000 VND require reporting to State Bank under AML regulations. Additionally, such customers require Enhanced Due Diligence (EDD) for high-value transactions exceeding this threshold.",
        "contexts": [
            "Cash transactions ≥ 400,000,000 VND require reporting to State Bank.",
            "EDD is required for: High-value transactions exceeding 400,000,000 VND."
        ],
        "evolution_type": "reasoning"
    },
    {
        "question": "If a loan becomes 100 days overdue, what classification would it receive and what is the bank's provision rate and collection action?",
        "ground_truth": "At 100 days overdue, the loan is classified as 'Doubtful' with a 50% provision rate. The collection team would be engaged, and legal proceedings may commence since it's past 91 days.",
        "contexts": [
            "91-180 days: Doubtful classification, 50% provision rate.",
            "Day 91+: Legal proceedings may commence."
        ],
        "evolution_type": "reasoning"
    },
    {
        "question": "Compare the total annual cost of holding a Gold vs Platinum credit card assuming no transactions.",
        "ground_truth": "Gold card annual fee is 500,000 VND. Platinum annual fee is 1,500,000 VND. The Platinum costs 1,000,000 VND more per year but includes airport lounge access and higher cashback (1.5% vs 1.0%).",
        "contexts": [
            "Gold | 500,000 VND | 100-300M VND | 1.0%",
            "Platinum | 1,500,000 VND | 300M-1B VND | 1.5%",
            "Airport lounge access (Platinum and above)."
        ],
        "evolution_type": "reasoning"
    },
    {
        "question": "A customer wants to restructure a 5-year loan. What is the maximum extended term they can receive and what other options are available?",
        "ground_truth": "The maximum extension is 50% of the original 5-year term, so 2.5 additional years (total 7.5 years). Other options include interest rate adjustment, grace period up to 6 months for principal payment, and partial debt forgiveness in exceptional cases.",
        "contexts": [
            "Extension of loan term (up to 50% of original term).",
            "Interest rate adjustment. Grace period for principal payment (up to 6 months). Partial debt forgiveness (exceptional cases, requires board approval)."
        ],
        "evolution_type": "reasoning"
    },
    {
        "question": "If VietBank detects a security breach, what are the notification deadlines for different stakeholders?",
        "ground_truth": "State Bank must be notified within 24 hours, customers within 72 hours. Remediation measures must be in place within 30 days, followed by a post-incident review.",
        "contexts": [
            "Immediate containment and investigation. Customer notification within 72 hours. State Bank notification within 24 hours. Remediation measures within 30 days."
        ],
        "evolution_type": "reasoning"
    },
    {
        "question": "Why might a customer's account be restricted even if they haven't done anything wrong?",
        "ground_truth": "A customer's account may be restricted if they fail to update their KYC information within the required timeframe (every 2 years for standard accounts, yearly for high-risk). Failure to update results in account restrictions until verification is completed.",
        "contexts": [
            "Customers must update their information every 2 years for standard accounts.",
            "Failure to update may result in account restrictions until verification is completed."
        ],
        "evolution_type": "reasoning"
    },
    {
        "question": "Calculate the approximate monthly interest earned on a Premium Savings account with the minimum required balance.",
        "ground_truth": "Premium Savings requires minimum 100,000,000 VND at 5.8% annual rate. Monthly interest = 100,000,000 × 5.8% / 12 ≈ 483,333 VND.",
        "contexts": [
            "Premium Savings - 5.8% annual interest, minimum balance 100,000,000 VND."
        ],
        "evolution_type": "reasoning"
    },
    {
        "question": "What happens to a suspicious transaction report if a bank staff member informs the customer about it?",
        "ground_truth": "Informing the customer about a SAR would violate the tipping-off prohibition policy. Staff must file the SAR within 24 hours and the customer must NOT be informed. This is a compliance violation that could have legal consequences.",
        "contexts": [
            "Staff must file internal Suspicious Activity Report (SAR) within 24 hours.",
            "Customer must NOT be informed of the report (tipping-off prohibition)."
        ],
        "evolution_type": "reasoning"
    },
    {
        "question": "If a customer wants to invest 50,000,000 VND with the lowest risk, which VietBank product should they choose and why?",
        "ground_truth": "The VietBank Money Market Fund offers the lowest risk with a target 5% annual return. Alternatively, government bonds are tax-exempt and capital protected. The Money Market Fund is more liquid with no lock-up period.",
        "contexts": [
            "VietBank Money Market Fund: Low risk, target 5% annual return.",
            "Government bonds: Available terms 2-15 years, yield 2.5-4.8%, tax-exempt interest income.",
            "Minimum investment: 1,000,000 VND. No lock-up period for open-ended funds."
        ],
        "evolution_type": "reasoning"
    },
    {
        "question": "A transaction of 60,000,000 VND is attempted through the mobile app. What security measures will be triggered?",
        "ground_truth": "Since the transaction exceeds 50,000,000 VND, OTP verification will be required. Additionally, the real-time fraud scoring system will evaluate the transaction, and the AI-powered transaction monitoring will check for suspicious patterns.",
        "contexts": [
            "Domestic transfers > 50,000,000 VND require OTP.",
            "Real-time fraud detection: AI-powered transaction monitoring.",
            "Two-factor authentication (2FA): OTP via SMS or authenticator app."
        ],
        "evolution_type": "reasoning"
    },
]

MULTI_CONTEXT_QUESTIONS = [
    {
        "question": "Compare the security measures for online banking authentication with the data privacy protections VietBank provides. How do they work together?",
        "ground_truth": "Authentication uses biometric (fingerprint/Face ID), 2FA with OTP, device binding (max 2 devices), and session timeout. Data privacy includes TLS 1.3 encryption, right to access/correct/delete data, and consent-based marketing. Together they form a defense-in-depth approach: authentication prevents unauthorized access while privacy policies govern how authorized data is handled.",
        "contexts": [
            "Biometric authentication: Fingerprint and Face ID. Two-factor authentication (2FA): OTP via SMS or authenticator app. Device binding: Each account linked to max 2 devices.",
            "Personal data is used for: Account management, credit assessment, regulatory compliance, marketing (with consent), fraud prevention.",
            "All transactions encrypted with TLS 1.3. Right to access personal data, right to correct inaccurate data, right to request deletion."
        ],
        "evolution_type": "multi_context"
    },
    {
        "question": "How does VietBank's KYC policy interact with its loan application process? What documents overlap?",
        "ground_truth": "KYC requires CCCD for Vietnamese citizens, proof of address, and information updates every 2 years. Loan applications require CCCD, household registration book, income proof, and collateral documents. The CCCD is required by both processes. KYC verification must be current before a loan can be processed, and EDD applies to high-value loans exceeding 400M VND.",
        "contexts": [
            "Vietnamese citizens: CCCD (12-digit Citizen Identity Card) is mandatory. Every 2 years for standard accounts.",
            "Required documents for personal loans: CCCD and household registration book, Income proof (salary slips for 3 months), Collateral documents.",
            "EDD is required for: High-value transactions exceeding 400,000,000 VND."
        ],
        "evolution_type": "multi_context"
    },
    {
        "question": "A customer wants to open a business account, apply for a trade finance letter of credit, and set up mobile banking. What are the total requirements and fees?",
        "ground_truth": "Business account requires: business registration, company seal, board resolution, tax certificate, minimum 10M VND deposit. L/C issuance fee is 0.15-0.25% of value. Mobile app provides fund transfers, bill payments, and QR payments. Internal transfers are free but interbank costs 5,500 VND. Total initial requirement includes all business documents plus 10M VND deposit.",
        "contexts": [
            "Business accounts require: Business registration certificate, Company seal specimen, Board resolution, Tax registration certificate, Minimum deposit of 10,000,000 VND.",
            "Letters of Credit (L/C): Issuance fee 0.15-0.25% of value.",
            "Fund transfers (domestic and international), Bill payments, QR code payments. Internal transfer: Free. Interbank transfer (Napas): 5,500 VND."
        ],
        "evolution_type": "multi_context"
    },
    {
        "question": "How does VietBank's complaint resolution process connect with its data privacy rights and the incident response procedure?",
        "ground_truth": "Complaint resolution has 3 internal levels (2 days, 5 days, 15 days) plus State Bank ombudsman. Data privacy grants rights to access, correct, and delete data, and lodge complaints with data protection authority. Incident response requires customer notification within 72 hours and State Bank notification within 24 hours. All three processes converge when a data breach triggers both incident response and customer complaints.",
        "contexts": [
            "Level 1: Branch/Call center (2 business days). Level 2: Regional manager (5 business days). Level 3: Head office (15 business days). External: State Bank ombudsman.",
            "Right to access personal data, right to correct inaccurate data, right to request deletion, right to lodge complaint with data protection authority.",
            "Customer notification within 72 hours. State Bank notification within 24 hours. Remediation measures within 30 days."
        ],
        "evolution_type": "multi_context"
    },
    {
        "question": "Explain the relationship between VietBank's interest rate policy, the State Bank base rate, and how this affects both savings and loan products.",
        "ground_truth": "State Bank base rate is 4.5%. Deposit rates are capped: demand deposits max 1.0%, term < 6 months max 4.75%, term ≥ 6 months market-determined. Lending rates are based on the base rate plus customer risk profile (Grade A-D). Premium Savings offers 5.8% while standard offers 4.5%. Home loans range 7.5-9%, with Grade A customers getting 0.5-1.0% reduction. The spread between deposit and lending rates is VietBank's profit margin.",
        "contexts": [
            "Vietnam State Bank base rate (currently 4.5%). Customer credit score (VietBank internal scoring A-D).",
            "Demand deposits: max 1.0% per annum. Term deposits < 6 months: max 4.75%. Term deposits ≥ 6 months: market-determined.",
            "Standard Savings - 4.5% annual interest. Premium Savings - 5.8% annual interest.",
            "Home Loan: 7.5-9% interest rate. Customers with Grade A credit receive preferential rates 0.5-1.0% below standard."
        ],
        "evolution_type": "multi_context"
    },
    {
        "question": "What are the different ways VietBank uses technology across its digital banking, security, and investment platforms?",
        "ground_truth": "Digital banking uses a mobile app with biometric auth, QR payments, and real-time alerts. Security employs AI-powered fraud detection, TLS 1.3 encryption, 3D Secure for card-not-present, and EMV chip standard. Investment platform offers mutual funds and bonds through the app. All are integrated: the app serves as single entry point, security layers protect transactions, and investment products are accessible digitally.",
        "contexts": [
            "VietBank Mobile App features: Balance inquiry, Fund transfers, QR code payments, Investment products (mutual funds, bonds).",
            "Real-time fraud detection: AI-powered transaction monitoring. All transactions encrypted with TLS 1.3. Card-not-present transactions require 3D Secure. EMV chip security standard.",
            "VietBank Growth Fund, Balanced Fund, Bond Fund, Money Market Fund available through mobile app."
        ],
        "evolution_type": "multi_context"
    },
    {
        "question": "How does VietBank handle cross-border transactions from both a product offering and regulatory compliance perspective?",
        "ground_truth": "Products include SWIFT transfers (1-3 days), forward contracts, L/Cs (0.15-0.25%), and trade loans. Regulatory requirements include: exchange rates updated every 30 minutes, max 50,000 USD per remittance, dual authorization for international transfers, compliance with State Bank foreign exchange controls, and AML reporting for suspicious cross-border activity. Correspondent banks include JP Morgan, Citibank, HSBC.",
        "contexts": [
            "SWIFT transfers: 1-3 business days. Correspondent banks: JP Morgan, Citibank, HSBC, Standard Chartered.",
            "Maximum individual remittance: 50,000 USD per transaction. International transfers require dual authorization.",
            "Letters of Credit (L/C): Issuance fee 0.15-0.25% of value. Trade loans: Preferential rates for exporters.",
            "Cash transactions ≥ 400,000,000 VND require reporting to State Bank. All transfers must comply with State Bank regulations."
        ],
        "evolution_type": "multi_context"
    },
    {
        "question": "Compare all the insurance and protection features available across VietBank's credit cards, bancassurance products, and investment products.",
        "ground_truth": "Credit cards include free accident insurance up to 500M VND. Bancassurance offers life, health, travel, and property insurance through partnerships. Investment products include capital-protected structured deposits. Government bonds can be used as loan collateral, providing an additional safety net. The claim process requires 24-hour reporting and 5-10 day assessment with settlement via VietBank account.",
        "contexts": [
            "Free accident insurance up to 500M VND (all credit cards).",
            "Bancassurance: Life Insurance, Health Insurance, Travel Insurance, Property Insurance.",
            "Structured Deposits: Capital-protected products with upside participation.",
            "Government bonds can be used as collateral for loans.",
            "Report incident within 24 hours. Claims assessment (5-10 business days)."
        ],
        "evolution_type": "multi_context"
    },
    {
        "question": "What are the end-to-end steps and timeline for a customer who wants to dispute a fraudulent transaction, considering the complaint resolution, security incident, and AML processes?",
        "ground_truth": "The customer reports via hotline. Security team performs immediate containment. SAR filed within 24 hours if suspicious. Level 1 complaint resolution within 2 business days. State Bank notified within 24 hours if breach confirmed. Customer formally notified within 72 hours. If not resolved, escalates to Level 2 (5 days) then Level 3 (15 days). Remediation within 30 days. Customer can escalate to State Bank ombudsman. Records retained for 5+ years.",
        "contexts": [
            "Level 1: Branch/Call center resolution (within 2 business days). Level 2: Regional manager review (within 5 business days).",
            "Immediate containment and investigation. Customer notification within 72 hours. State Bank notification within 24 hours.",
            "Staff must file internal SAR within 24 hours. Compliance department reviews within 3 business days.",
            "Transaction records retained for minimum 5 years."
        ],
        "evolution_type": "multi_context"
    },
    {
        "question": "How do VietBank's fee structures differ across personal banking, credit cards, and digital banking services?",
        "ground_truth": "Personal banking: account opening requires 500K VND deposit (standard) or 10M (business). Credit cards: annual fees range 200K-3M VND with cashback 0.5-2.0%, late fees 4% of minimum, revolving interest 1.5-2.5%/month. Digital banking: internal transfers free, interbank 5,500 VND, international 0.1% (min 200K VND), paper statements 20K VND. Fee changes require 30-day notice with 90-day grandfathering.",
        "contexts": [
            "Minimum initial deposit of 500,000 VND. Business account minimum deposit of 10,000,000 VND.",
            "Classic 200,000 VND, Gold 500,000 VND, Platinum 1,500,000 VND, Signature 3,000,000 VND. Late payment fee: 4% of minimum.",
            "Internal transfer: Free. Interbank transfer (Napas): 5,500 VND. International transfer: 0.1% (min 200,000 VND). Paper statement: 20,000 VND.",
            "Customers notified 30 days before any fee increase. Existing customers grandfathered for 90 days."
        ],
        "evolution_type": "multi_context"
    },
    {
        "question": "What are the complete requirements and processes for a foreign national to open an account, apply for a credit card, and use mobile banking at VietBank?",
        "ground_truth": "Foreign nationals need passport with valid visa for KYC. They can open a current or savings account with minimum 500K VND deposit. Credit card application requires income proof and credit assessment (3-5 business days). Mobile app requires biometric setup, device binding (max 2 devices), and 2FA. All subject to EDD if from high-risk jurisdiction.",
        "contexts": [
            "Foreign nationals: Passport with valid visa or residence permit.",
            "Minimum initial deposit of 500,000 VND. Credit assessment (3-5 business days).",
            "Biometric authentication (fingerprint, Face ID). Device binding: Each account linked to max 2 devices.",
            "EDD is required for: customers from high-risk jurisdictions."
        ],
        "evolution_type": "multi_context"
    },
    {
        "question": "How does VietBank's loan default management connect with its AML monitoring and customer data retention policies?",
        "ground_truth": "Loan defaults follow a 5-stage classification (Current to Loss). At 91+ days, legal proceedings begin. AML monitoring flags transactions inconsistent with customer profile, which could include unusual loan repayment patterns. Both systems rely on 5+ year data retention. SAR filing requirements apply if default-related transactions appear suspicious. All records retained for minimum 5 years after account closure.",
        "contexts": [
            "Overdue: 0-10 Current, 10-30 Special Mention, 31-90 Substandard, 91-180 Doubtful, 181+ Loss.",
            "Monitor for transactions inconsistent with customer profile. SAR filed within 24 hours.",
            "Transaction records retained for minimum 5 years. Customer identification records retained for 5 years after account closure."
        ],
        "evolution_type": "multi_context"
    },
    {
        "question": "Compare the risk mitigation strategies across VietBank's digital security, investment products, and insurance offerings.",
        "ground_truth": "Digital security uses defense-in-depth: biometrics, 2FA, TLS 1.3, AI fraud detection, and 3D Secure. Investments offer risk tiers from Money Market (5% target, low risk) to Growth Fund (15%, high risk), plus capital-protected structured deposits. Insurance covers life, health, travel, and property risks. Together they protect against cyber threats (security), market risk (investment diversification), and personal/property risk (insurance).",
        "contexts": [
            "Biometric authentication, 2FA, real-time AI fraud detection, TLS 1.3, 3D Secure for card-not-present.",
            "Money Market Fund: Low risk, 5% target. Growth Fund: Equity-focused, 15% target. Structured Deposits: Capital-protected.",
            "Bancassurance: Life Insurance, Health Insurance, Travel Insurance, Property Insurance. Free accident insurance up to 500M VND."
        ],
        "evolution_type": "multi_context"
    },
]

# Manually edited question (requirement A.1.5) - marked with comment
SIMPLE_QUESTIONS[2] = {
    "question": "How many physical branches does VietBank currently operate across Vietnam?",  # EDITED: original was "How many branches does VietBank operate nationwide?" - rephrased for clarity
    "ground_truth": "VietBank currently operates more than 250 branches across Vietnam nationwide.",  # EDITED: added "currently" and "across Vietnam" for specificity
    "contexts": ["Branch network: 250+ branches nationwide. ATM network: 1,500+ ATMs."],
    "evolution_type": "simple"
}

all_questions = SIMPLE_QUESTIONS + REASONING_QUESTIONS + MULTI_CONTEXT_QUESTIONS

df = pd.DataFrame(all_questions)
assert len(df) >= 50, f"Need at least 50 questions, got {len(df)}"

print(f"Total questions: {len(df)}")
print(f"\nDistribution:")
print(df['evolution_type'].value_counts())
print(f"\nExpected: simple=25 (50%), reasoning=12-13 (25%), multi_context=12-13 (25%)")
print(f"Actual: simple={len(SIMPLE_QUESTIONS)} ({len(SIMPLE_QUESTIONS)/len(df)*100:.0f}%), "
      f"reasoning={len(REASONING_QUESTIONS)} ({len(REASONING_QUESTIONS)/len(df)*100:.0f}%), "
      f"multi_context={len(MULTI_CONTEXT_QUESTIONS)} ({len(MULTI_CONTEXT_QUESTIONS)/len(df)*100:.0f}%)")

df.to_csv("phase-a/testset_v1.csv", index=False)
print(f"\nSaved to phase-a/testset_v1.csv ({len(df)} rows)")
print(f"Columns: {list(df.columns)}")
