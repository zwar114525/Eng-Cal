"""
Pydantic models for civil engineering intake module.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class CodeEntry(BaseModel):
    """Structured code metadata"""
    code_id: str
    title: str
    scope: str
    priority: str = "primary"
    edition: str = "latest"
    parts: List[str] = Field(default_factory=list)
    source_url: Optional[str] = None
    alternatives: List[str] = Field(default_factory=list)
    local_amendments_possible: bool = True


class CodeResolutionResult(BaseModel):
    """Structured output from hybrid code resolver"""
    source: str
    codes: List[Dict[str, Any]]
    confidence: float
    requires_human_verification: bool = True
    notes: List[str] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)
    audit_metadata: Optional[Dict[str, Any]] = None


class LicensingInfo(BaseModel):
    """Licensing requirements for a project"""
    requires_license: bool
    license_type: str
    jurisdiction: str
    note: str = ""


class RiskFlag(BaseModel):
    """Project risk flag"""
    flag: str
    severity: str = "medium"


class ProjectMetadata(BaseModel):
    """Project metadata"""
    job_id: str
    parsed_at: str
    parser_version: str = "2.0.0"
    llm_provider: str = "none"


class ClassificationResult(BaseModel):
    """Job classification result"""
    job_type: str
    jurisdiction: str
    confidence: str = "medium"


class RequirementsResult(BaseModel):
    """Project requirements"""
    deliverables: List[str]
    required_inputs_missing: List[str]
    licensing: LicensingInfo


class RiskAssessmentResult(BaseModel):
    """Risk assessment result"""
    flags: List[str]
    overall_risk: str = "low"


class NextActions(BaseModel):
    """Recommended next actions"""
    clarifying_questions: List[str]
    recommended_first_step: str


class ComplianceInfo(BaseModel):
    """Compliance information"""
    human_verification_required: bool = True
    ai_assisted: bool = False
    disclaimer: str = ""


class ParsedIntake(BaseModel):
    """Complete parsed intake result"""
    meta: ProjectMetadata
    classification: ClassificationResult
    required_codes: CodeResolutionResult
    requirements: RequirementsResult
    risk_assessment: RiskAssessmentResult
    next_actions: NextActions
    raw_excerpt: str = ""
    compliance: ComplianceInfo
