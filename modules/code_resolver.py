"""
Hybrid Code Resolver - Three-layer code identification system.
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from modules.code_database import CodeDatabase
from modules.models import CodeResolutionResult, CodeEntry


class HybridCodeResolver:
    """
    Three-layer code identification system:
    1. Database lookup (fast, reliable)
    2. LLM suggestion (flexible, fallback)
    3. Human verification gate (mandatory)
    """
    
    def __init__(self, llm_client=None, llm_provider: str = "openai", base_url: str = ""):
        self.db = CodeDatabase()
        self.llm = llm_client
        self.llm_provider = llm_provider
        self.base_url = base_url
        self.known_code_ids = self.db.get_all_code_ids()
        
    def resolve_codes(self, jurisdiction: str, job_type: str, 
                     job_text: str, confidence_threshold: float = 0.7) -> CodeResolutionResult:
        """
        Main entry point: return codes with confidence scores and verification flags.
        """
        audit_metadata = {
            "resolved_at": datetime.now().isoformat(),
            "jurisdiction_input": jurisdiction,
            "job_type_input": job_type,
            "confidence_threshold": confidence_threshold,
            "llm_provider": self.llm_provider if self.llm else "none"
        }
        
        # Layer 1: Database Lookup
        db_codes = self.db.get_required_codes(jurisdiction, job_type)
        
        if db_codes and len(db_codes) > 0:
            codes_dict = [self._code_entry_to_dict(c) for c in db_codes]
            result = CodeResolutionResult(
                source="database",
                codes=codes_dict,
                confidence=0.9,
                requires_human_verification=True,
                notes=["Codes matched from curated database"],
                uncertainties=[],
                audit_metadata=audit_metadata
            )
            
            if result.confidence >= confidence_threshold:
                return result
        
        # Layer 2: LLM Fallback
        if self.llm and (not db_codes or len(db_codes) == 0):
            llm_suggestion = self._llm_suggest_codes(jurisdiction, job_type, job_text)
            
            if llm_suggestion.codes and len(llm_suggestion.codes) > 0:
                llm_suggestion.source = "llm_suggestion"
                llm_suggestion.notes.append("Codes suggested by LLM - MUST be verified by licensed engineer")
                llm_suggestion.audit_metadata = audit_metadata
                return llm_suggestion
        
        # Layer 3: No Match
        return CodeResolutionResult(
            source="manual_required",
            codes=[],
            confidence=0.0,
            requires_human_verification=True,
            notes=["No codes identified. Engineer must research applicable standards."],
            uncertainties=["Automated resolver could not identify applicable codes"],
            audit_metadata=audit_metadata
        )
    
    def _code_entry_to_dict(self, entry: CodeEntry) -> dict:
        """Convert CodeEntry to dict with verification flags"""
        return {
            "code_id": entry.code_id,
            "title": entry.title,
            "scope": entry.scope,
            "priority": entry.priority,
            "edition": entry.edition,
            "parts": entry.parts,
            "source_url": entry.source_url,
            "alternatives": entry.alternatives,
            "local_amendments_possible": entry.local_amendments_possible,
            "source": "database",
            "requires_verification": True
        }
    
    def _llm_suggest_codes(self, jurisdiction: str, job_type: str, job_text: str) -> CodeResolutionResult:
        """Use LLM to suggest applicable codes with validation"""
        
        prompt = f"""You are a senior civil engineering standards expert.

TASK: Identify the applicable codes of practice for this freelance engineering job.

JOB CONTEXT:
- Jurisdiction: {jurisdiction}
- Job Type: {job_type}
- Full Job Description:
{job_text[:2500]}

KNOWN CODE IDs (prefer these if applicable):
{', '.join(self.known_code_ids[:30])}... (and more)

INSTRUCTIONS:
1. List ALL applicable codes/standards (primary and secondary)
2. For each code, provide:
   - Official code ID (e.g., "IS_2911", "ACI_318-19", "EN_1992-1-1")
   - Full title
   - Brief scope (what aspect of the job it governs)
   - Priority: "primary", "secondary", or "tertiary"
   - Edition/year if known (e.g., "2000", "2019", "latest")
   - Whether local amendments may apply (boolean)
3. If jurisdiction is unclear, suggest codes for likely regions + note uncertainty
4. Estimate your confidence (0.0-1.0) in this list
5. List any uncertainties or assumptions you made

OUTPUT FORMAT (JSON ONLY):
{{
  "codes": [
    {{
      "code_id": "IS_2911",
      "title": "Design and construction of pile foundations",
      "scope": "Pile capacity calculation, load testing",
      "priority": "primary",
      "edition": "latest",
      "local_amendments_possible": true
    }}
  ],
  "confidence": 0.85,
  "uncertainties": ["Jurisdiction not explicitly stated", "Soil type unknown"]
}}

Return ONLY valid JSON. No markdown, no explanations.
"""
        
        try:
            if self.llm_provider == "openai" and hasattr(self.llm, 'chat'):
                response = self.llm.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                llm_output = json.loads(response.choices[0].message.content)
                
            elif self.llm_provider == "anthropic" and hasattr(self.llm, 'messages'):
                response = self.llm.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                llm_output = json.loads(response.content[0].text)
                
            else:
                raise ValueError("No valid LLM client available")
            
            # Validate and enrich output
            validated_codes = []
            for code in llm_output.get("codes", []):
                code_id = code.get("code_id", "UNKNOWN")
                
                # Check for hallucination red flags
                suspicious_patterns = ["fictional", "placeholder", "example", "tbd", "xxx"]
                if any(pat in code_id.lower() for pat in suspicious_patterns):
                    continue
                
                validated_codes.append({
                    "code_id": code_id,
                    "title": code.get("title", "Title not provided"),
                    "scope": code.get("scope", "Scope not specified"),
                    "priority": code.get("priority", "secondary"),
                    "edition": code.get("edition", "unknown"),
                    "parts": code.get("parts", []),
                    "source_url": code.get("source_url"),
                    "local_amendments_possible": code.get("local_amendments_possible", True),
                    "source": "llm_suggestion",
                    "requires_verification": True,
                    "known_code": code_id in self.known_code_ids
                })
            
            confidence = llm_output.get("confidence", 0.5)
            uncertainties = llm_output.get("uncertainties", [])
            
            # Apply confidence penalties
            if len(validated_codes) == 0:
                confidence = 0.0
            elif not any(c["known_code"] for c in validated_codes):
                confidence *= 0.7  # Penalty if no known codes
            if any("unknown" in str(c.get("edition", "")).lower() for c in validated_codes):
                confidence *= 0.9
            
            return CodeResolutionResult(
                source="llm_suggestion",
                codes=validated_codes,
                confidence=confidence,
                requires_human_verification=True,
                notes=[],
                uncertainties=uncertainties
            )
            
        except Exception as e:
            return CodeResolutionResult(
                source="llm_error",
                codes=[],
                confidence=0.0,
                requires_human_verification=True,
                notes=[f"LLM code suggestion failed: {str(e)}"],
                uncertainties=[f"LLM error: {str(e)}"]
            )
