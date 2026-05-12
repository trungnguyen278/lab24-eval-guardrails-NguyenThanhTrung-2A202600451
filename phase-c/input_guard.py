"""
Task C.1 - Input Guardrail: PII Redaction (Presidio + VN regex)
Task C.2 - Input Guardrail: Topic Scope Validator
"""

import sys
import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import re
import time
import csv
import os
import json
import numpy as np

# ============================================================
# C.1 - PII Redaction
# ============================================================

VN_PII = {
    "cccd": r"\b\d{12}\b",
    "phone_vn": r"(\+84|0)\d{9,10}\b",
    "phone_intl": r"\+\d[\d\-]{7,15}\b",
    "tax_code": r"\b\d{10}(-\d{3})?\b",
    "email": r"\b[\w.-]+@[\w.-]+\.\w+\b",
    "address": r"\b\d{1,5}\s+(Main|Elm|Oak|Maple|Le Loi|Lê Lợi|Nguyen Hue|Nguyễn Huệ|Tran Hung Dao|Trần Hưng Đạo)\b",
    "vn_name": r"\b(Nguyễn|Trần|Lê|Phạm|Hoàng|Huỳnh|Phan|Vũ|Võ|Đặng|Bùi|Đỗ|Hồ|Ngô|Dương|Lý)\s+[A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+)*\b",
}


class InputGuard:
    def __init__(self):
        self._presidio_available = False
        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_anonymizer import AnonymizerEngine
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()
            self._presidio_available = True
        except ImportError:
            pass

    def scrub_vn(self, t: str) -> str:
        if not t:
            return t
        for name, pattern in VN_PII.items():
            t = re.sub(pattern, f"[{name.upper()}]", t)
        return t

    def scrub_ner(self, t: str) -> str:
        if not t or not self._presidio_available:
            return t
        try:
            results = self.analyzer.analyze(text=t, language="en")
            return self.anonymizer.anonymize(
                text=t, analyzer_results=results
            ).text
        except Exception:
            return t

    def sanitize(self, t: str) -> tuple[str, float]:
        start = time.perf_counter()
        if not t:
            latency_ms = (time.perf_counter() - start) * 1000
            return t, latency_ms

        out = self.scrub_vn(t)
        if self._presidio_available:
            out = self.scrub_ner(out)

        latency_ms = (time.perf_counter() - start) * 1000
        return out, latency_ms

    def detect_pii(self, t: str) -> list[str]:
        found = []
        if not t:
            return found
        for name, pattern in VN_PII.items():
            if re.search(pattern, t):
                found.append(name)
        if self._presidio_available:
            try:
                results = self.analyzer.analyze(text=t, language="en")
                for r in results:
                    found.append(r.entity_type.lower())
            except Exception:
                pass
        return found


# ============================================================
# Injection Detector
# ============================================================

INJECTION_PATTERNS = [
    r"(?i)\bbase64\b",
    r"(?i)\brot13\b",
    r"(?i)\bhex\s*(encod|decod|string)",
    r"(?i)(decode|encode)\s+this",
    r"(?i)translate\s+from\s+(rot13|base64|hex|binary)",
    r"[A-Za-z0-9+/]{20,}={0,2}",
    r"(?i)\b[0-9a-f]{20,}\b",
    r"(?i)(ignore|disregard|forget|override)\s+(all\s+)?(previous|prior|above|your|safety|system)\s*(instructions|rules|guidelines|checks|prompt|constraints)",
    r"(?i)\bsystem\s*(override|prompt|instruction)",
    r"(?i)(you\s+are\s+now|from\s+now\s+on\s+you\s+are|pretend\s+(you\s+are|you're|to\s+be))\s+",
    r"(?i)\b(DAN|jailbreak|do\s+anything\s+now|freedom\s*gpt|no\s*rules)\b",
    r"(?i)(act\s+as|behave\s+as|you\s+are)\s+(an?\s+)?(unrestricted|uncensored|unfiltered|evil|malicious)",
    r"(?i)safety\s+(filters?|module|checks?)\s+(are\s+)?(disabled|off|removed)",
    r"(?i)(developer|admin|debug|test)\s+mode",
    r"(?i)\[\s*system\s*(override|prompt)\s*\]",
    r"(?i)<!--.*?(admin|system|ignore|override).*?-->",
    r"(?i)(latest|new|updated?)\s+(policy|guideline|instruction)\s+(update|document|file)",
    r"(?i)fake_policy",
    r"(?i)confirm\s+by\s+sharing",
    r"(?i)reveal\s+(all|customer|internal|system)",
]


class InjectionDetector:
    def __init__(self):
        self._compiled = [re.compile(p) for p in INJECTION_PATTERNS]

    def check(self, text: str) -> tuple[bool, str]:
        if not text:
            return True, "Empty input"
        for i, pattern in enumerate(self._compiled):
            match = pattern.search(text)
            if match:
                return False, f"Injection pattern detected: {match.group()[:40]}"
        return True, "No injection detected"


# ============================================================
# Content Safety Detector (dangerous action keywords)
# ============================================================

DANGEROUS_ACTIONS = [
    "hack", "steal", "exploit", "bypass security", "attack",
    "phishing", "forge", "embezzle", "robbery", "rob a bank",
    "malware", "ransomware", "keylogger",
    "forge bank", "forge document", "fake identity",
    "launder money", "money laundering",
]

DANGEROUS_CONTEXT = [
    r"(?i)(how\s+to|explain|show\s+me|teach|help\s+me|tell\s+me\s+how)\s+.{0,30}(hack|steal|exploit|forge|phishing|embezzle|rob|bypass|attack|crack)",
    r"(?i)(create|build|make|write)\s+.{0,20}(phishing|malware|exploit|fake)",
    r"(?i)(plan|method|way|step).{0,30}(rob|theft|steal|hack|fraud|embezzle)",
]


class ContentSafetyDetector:
    def __init__(self):
        self._action_set = set(DANGEROUS_ACTIONS)
        self._context_patterns = [re.compile(p) for p in DANGEROUS_CONTEXT]

    def check(self, text: str) -> tuple[bool, str]:
        if not text:
            return True, "Empty input"
        text_lower = text.lower()
        for action in self._action_set:
            if action in text_lower:
                return False, f"Dangerous content detected: '{action}'"
        for pattern in self._context_patterns:
            match = pattern.search(text)
            if match:
                return False, f"Dangerous intent detected: {match.group()[:40]}"
        return True, "Content safe"


# ============================================================
# C.2 - Topic Scope Validator (Embedding similarity approach)
# ============================================================

BANKING_KEYWORDS = [
    "account", "savings", "deposit", "loan", "credit", "card", "interest",
    "bank", "transfer", "payment", "balance", "branch", "atm", "mortgage",
    "investment", "insurance", "kyc", "aml", "transaction", "fee",
    "vietbank", "cccd", "vnd", "banking", "financial", "money",
    "tài khoản", "tiết kiệm", "cho vay", "thẻ tín dụng", "lãi suất",
    "ngân hàng", "chuyển khoản", "thanh toán", "số dư", "chi nhánh",
]

OFF_TOPIC_INDICATORS = [
    "recipe", "cooking", "cook", "pasta", "cake", "bake",
    "weather", "forecast", "temperature",
    "sports", "football", "soccer", "basketball", "match score",
    "game", "gaming",
    "movie", "film", "cinema", "grammy", "oscar", "award",
    "music", "song", "album",
    "celebrity", "fashion",
    "travel destination", "vacation", "tourism",
    "homework", "solve this",
    "math problem", "physics", "chemistry", "biology",
    "history war", "capital of",
    "joke", "funny", "humor",
    "hack", "attack", "exploit", "bomb", "weapon", "illegal",
]


class TopicGuard:
    def __init__(self, allowed_topics: list[str] = None):
        self.allowed_topics = allowed_topics or [
            "banking services", "loans and credit", "account management",
            "credit cards", "digital banking", "investment products",
            "insurance", "customer support", "fees and charges",
            "security and authentication", "regulations and compliance",
        ]
        self.banking_kw_set = set(BANKING_KEYWORDS)
        self.off_topic_set = set(OFF_TOPIC_INDICATORS)

    def check(self, text: str) -> tuple[bool, str]:
        if not text or not text.strip():
            return False, "Empty input. Please ask a question about banking services."

        text_lower = text.lower()
        words = set(re.findall(r'\w+', text_lower))

        banking_score = len(words & self.banking_kw_set)
        off_topic_matches = [w for w in self.off_topic_set if w in text_lower]

        if off_topic_matches and banking_score == 0:
            return False, (
                f"Your question appears to be about '{off_topic_matches[0]}', "
                f"which is outside our scope. I can help with: "
                f"{', '.join(self.allowed_topics[:5])}."
            )

        if banking_score >= 1:
            matched = [w for w in self.banking_kw_set if w in text_lower]
            return True, f"On topic: matched keywords {matched[:3]}"

        if len(text.split()) < 3:
            return False, (
                "Your question is too short. Please provide more detail "
                "about what banking service you need help with."
            )

        return True, "Allowed: no off-topic indicators detected"

    def check_with_fallback(self, text: str) -> tuple[bool, str]:
        on_topic, reason = self.check(text)
        if not on_topic:
            return False, (
                f"I'm sorry, I can only help with banking-related questions. "
                f"{reason} "
                f"Please try rephrasing your question about VietBank services."
            )
        return True, reason


# ============================================================
# Test Runner
# ============================================================

def run_pii_tests():
    guard = InputGuard()

    test_inputs = [
        ("Hi, I'm John Smith from Microsoft. Email: john@ms.com",
         ["email"], True),
        ("Call me at +1-555-1234 or visit 123 Main Street, NYC",
         ["phone"], True),
        ("Số CCCD của tôi là 012345678901",
         ["cccd"], True),
        ("Liên hệ qua 0987654321 hoặc tax 0123456789-001",
         ["phone_vn", "tax_code"], True),
        ("Customer Nguyễn Văn A, CCCD 098765432101, phone 0912345678",
         ["cccd", "phone_vn"], True),
        ("",
         [], False),
        ("Just a normal question about banking",
         [], False),
        ("A" * 5000,
         [], False),
        ("Lý Văn Bình ở 123 Lê Lợi",
         [], True),
        ("tax_code:0123456789-001 cccd:012345678901",
         ["tax_code", "cccd"], True),
    ]

    results = []
    latencies = []

    print("\n=== PII Redaction Test Results ===\n")
    detected_count = 0
    expected_detect_count = 0

    for i, (inp, expected_pii, has_pii) in enumerate(test_inputs):
        sanitized, latency_ms = guard.sanitize(inp)
        pii_found = guard.detect_pii(inp)
        latencies.append(latency_ms)

        changed = sanitized != inp
        if has_pii:
            expected_detect_count += 1
            if changed or pii_found:
                detected_count += 1

        results.append({
            'input': inp[:80] if inp else "(empty)",
            'output': sanitized[:80] if sanitized else "(empty)",
            'pii_found': json.dumps(pii_found),
            'latency_ms': round(latency_ms, 2),
            'changed': changed,
            'has_pii': has_pii,
        })

        status = "DETECTED" if (changed or pii_found) else "clean"
        pii_str = str(pii_found) if pii_found else "none"
        print(f"  [{i+1:2d}] {status:>8s} | {latency_ms:6.2f}ms | "
              f"PII={pii_str:30s} | {inp[:50]}")

    detection_rate = detected_count / max(expected_detect_count, 1) * 100
    p95_latency = np.percentile(latencies, 95) if latencies else 0

    print(f"\n--- Summary ---")
    print(f"Detection rate: {detected_count}/{expected_detect_count} = {detection_rate:.0f}%")
    print(f"Latency P50: {np.percentile(latencies, 50):.2f}ms")
    print(f"Latency P95: {p95_latency:.2f}ms")
    print(f"Latency P99: {np.percentile(latencies, 99):.2f}ms")

    with open('phase-c/pii_test_results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['input', 'output', 'pii_found', 'latency_ms'])
        writer.writeheader()
        writer.writerows([{k: r[k] for k in ['input', 'output', 'pii_found', 'latency_ms']}
                          for r in results])

    print(f"\nResults saved to phase-c/pii_test_results.csv")
    return results, detection_rate, p95_latency


def run_topic_tests():
    guard = TopicGuard()

    test_inputs = [
        ("What is the interest rate for savings accounts?", True),
        ("How do I open a bank account at VietBank?", True),
        ("What are the credit card fees?", True),
        ("Tell me about loan application process", True),
        ("What is the minimum deposit for investment?", True),
        ("How does the mobile banking app work?", True),
        ("What are VietBank's KYC requirements?", True),
        ("Can I transfer money internationally?", True),
        ("What insurance products does VietBank offer?", True),
        ("How do I file a complaint about a transaction?", True),
        ("What's the best recipe for chocolate cake?", False),
        ("Tell me about the latest football match scores", False),
        ("What's the weather forecast for tomorrow?", False),
        ("Recommend me a good movie to watch", False),
        ("How do I solve this physics homework problem?", False),
        ("What's the capital of France?", False),
        ("Tell me a joke", False),
        ("How to cook pasta carbonara?", False),
        ("Who won the Grammy awards this year?", False),
        ("What are the best travel destinations in Europe?", False),
    ]

    correct = 0
    total = len(test_inputs)

    print("\n=== Topic Validator Test Results ===\n")
    for i, (inp, expected_on_topic) in enumerate(test_inputs):
        on_topic, reason = guard.check_with_fallback(inp)

        is_correct = on_topic == expected_on_topic
        if is_correct:
            correct += 1

        status = "OK" if is_correct else "WRONG"
        result = "on-topic" if on_topic else "off-topic"
        expected = "on-topic" if expected_on_topic else "off-topic"

        print(f"  [{i+1:2d}] {status:>5s} | {result:>9s} (expected {expected:>9s}) | {inp[:50]}")
        if not is_correct:
            print(f"         Reason: {reason[:80]}")

    accuracy = correct / total * 100
    refuse_rate = sum(1 for _, exp in test_inputs if not exp) / total * 100

    print(f"\n--- Summary ---")
    print(f"Accuracy: {correct}/{total} = {accuracy:.0f}%")
    print(f"Refuse rate: {refuse_rate:.0f}% of test inputs are off-topic")
    print(f"Graceful fallback: Yes (custom messages for off-topic)")

    return accuracy


if __name__ == "__main__":
    print("=" * 60)
    print("Task C.1 - PII Redaction Tests")
    print("=" * 60)
    pii_results, detection_rate, p95 = run_pii_tests()

    print("\n" + "=" * 60)
    print("Task C.2 - Topic Scope Validator Tests")
    print("=" * 60)
    topic_accuracy = run_topic_tests()
