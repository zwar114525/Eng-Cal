"""
Main Intake Engine for Civil Engineering Freelance Jobs.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from modules.enums import JobType, Jurisdiction, DeliverableType
from modules.models import (
    CodeResolutionResult, LicensingInfo, ProjectMetadata,
    ClassificationResult, RequirementsResult, RiskAssessmentResult,
    NextActions, ComplianceInfo, ParsedIntake
)
from modules.code_resolver import HybridCodeResolver


class EngineeringIntake:
    """
    Generalized intake processor for civil engineering freelance jobs.
    Hybrid approach: Database + LLM + Human Verification.
    """
    
    # Keyword mappings for fallback (no LLM)
    KEYWORD_MAP = {
        JobType.PILE_FOUNDATION: ["pile", "piling", "deep foundation", "bored pile", "driven pile", "helical pile"],
        JobType.SLAB_BEAM_COLUMN: ["slab", "beam", "column", "frame", "reinforced concrete", "rc design", "rc frame"],
        JobType.RETAINING_WALL: ["retaining wall", "cantilever wall", "sheet pile", "gravity wall", "anchored wall"],
        JobType.DRAINAGE_STORMWATER: ["drainage", "stormwater", "culvert", "swale", "hydrology", "hydraulic", "sewer"],
        JobType.ROAD_HIGHWAY: ["road", "highway", "pavement", "alignment", "geometric design", "flexible pavement"],
        JobType.STRUCTURAL_ANALYSIS_FEM: ["abaqus", "ansys", "fea", "fem", "finite element", "nonlinear analysis", "etabs", "sap2000"],
        JobType.PERMIT_DRAWINGS: ["permit", "submission", "building department", "stamped drawings", "approval", "ahj"],
        JobType.SITE_PLANNING_GRADING: ["site plan", "grading", "earthwork", "cut fill", "topography", "survey"],
        JobType.MATERIAL_TAKEOFF: ["takeoff", "quantity", "boq", "bill of quantities", "material estimate", "cost estimate"],
        JobType.GEOTECHNICAL_ANALYSIS: ["geotechnical", "soil report", "bearing capacity", "settlement", "slope stability"],
        JobType.BRIDGE_STRUCTURE: ["bridge", "span", "girder", "abutment", "pier", "viaduct"],
        JobType.STEEL_STRUCTURE: ["steel", "structural steel", "metal building", "steel frame", "connection design"],
        JobType.PRESTRESSED_CONCRETE: ["prestressed", "pre-tensioned", "post-tensioned", "pt slab", "prestressing"],
        JobType.SEISMIC_RETROFIT: ["seismic", "earthquake", "retrofit", "strengthening", "base isolation"],
    }
    
    JURISDICTION_MAP = {
        Jurisdiction.INDIA_IS: ["is 2911", "is 456", "is 875", "india", "inr", "₹", "mumbai", "delhi", "bangalore"],
        Jurisdiction.USA_ACI: ["aci 318", "asce 7", "ibc", "usa", "usd", "$", "american"],
        Jurisdiction.FLORIDA_FBC: ["florida", "fl", "miami-dade", "hvhz", "florida building code", "palmetto bay"],
        Jurisdiction.EUROCODE: ["eurocode", "en 199", "europe", "€", "ec2", "ec3"],
        Jurisdiction.UK_BS: ["bs 8110", "bs 5950", "uk", "british standard", "london"],
        Jurisdiction.AUSTRALIA_AS: ["as 3600", "as 1170", "australia", "aud", "a$", "sydney"],
        Jurisdiction.CANADA_CS: ["csa", "canada", "cad", "c$", "toronto", "vancouver"],
        Jurisdiction.UAE_SBC: ["uae", "dubai", "abu dhabi", "uae code"],
        Jurisdiction.SINGAPORE_SS: ["singapore", "ss", "sgd", "s$"],
    }
    
    DELIVERABLE_MAP = {
        DeliverableType.DWG_FILE: [".dwg", "autocad", "cad file", "drawing file"],
        DeliverableType.PDF_DRAWING: [".pdf", "pdf drawing", "print ready"],
        DeliverableType.EXCEL_CALCULATIONS: ["excel", ".xlsx", "calculation sheet", "spreadsheet", "calc"],
        DeliverableType.PDF_REPORT: ["report", "design summary", "technical report", "memo"],
        DeliverableType.PE_STAMPED: ["pe stamp", "professional engineer", "sealed", "licensed", "signed and sealed"],
        DeliverableType.INP_FILE: [".inp", "abaqus input", "input file"],
        DeliverableType.ODB_FILE: [".odb", "abaqus output", "results file"],
        DeliverableType.REVIT_MODEL: [".rvt", "revit", "bim model"],
    }
    
    def __init__(self, raw_text: str, llm_client=None, llm_provider: str = "openai", base_url: str = "", model: str = "gpt-4o-mini"):
        self.raw_text = raw_text
        self.job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.llm_client = llm_client
        self.llm_provider = llm_provider
        self.base_url = base_url
        self._model = model
        self._classify_llm_failed = False  # recursion guard: fall back to keyword only
        self._jurisdiction_llm_failed = False
        self.code_resolver = HybridCodeResolver(
            llm_client=llm_client, 
            llm_provider=llm_provider,
            base_url=base_url
        )
        
    # Classification Methods
    
    def _keyword_classify_job_type(self) -> JobType:
        """Keyword-based job type classification (no LLM)."""
        text_lower = self.raw_text.lower()
        best_match = JobType.OTHER
        best_score = 0
        for job_type, keywords in self.KEYWORD_MAP.items():
            score = sum(1 for kw in keywords if kw.lower() in text_lower)
            if score > best_score:
                best_score = score
                best_match = job_type
        return best_match

    def classify_job_type(self) -> JobType:
        """Classify job type. Uses keyword matching only to avoid recursion with LLM fallback."""
        return self._keyword_classify_job_type()

    def _llm_classify_job_type(self) -> JobType:
        """Use LLM for more accurate classification"""
        prompt = f"""You are a civil engineering project classifier. 
Classify this freelance job posting into ONE category:

JOB TEXT:
{self.raw_text[:3000]}

CATEGORIES:
{', '.join([jt.value for jt in JobType])}

Return ONLY the category name (e.g., "pile_foundation"), nothing else.
"""
        try:
            if hasattr(self.llm_client, 'chat'):
                response = self.llm_client.chat.completions.create(
                    model=self._model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=20
                )
                result = response.choices[0].message.content.strip().lower()
                return JobType(result) if result in [jt.value for jt in JobType] else JobType.OTHER
        except Exception:
            pass
        self._classify_llm_failed = True
        return self._keyword_classify_job_type()
    
    def _keyword_detect_jurisdiction(self) -> Jurisdiction:
        """Keyword-based jurisdiction detection (no LLM)."""
        text_lower = self.raw_text.lower()
        for jurisdiction, keywords in self.JURISDICTION_MAP.items():
            if any(kw.lower() in text_lower for kw in keywords):
                return jurisdiction
        return Jurisdiction.OTHER

    def detect_jurisdiction(self) -> Jurisdiction:
        """Detect jurisdiction. Uses keyword matching only to avoid recursion with LLM fallback."""
        return self._keyword_detect_jurisdiction()

    def _llm_detect_jurisdiction(self) -> Jurisdiction:
        """Use LLM for jurisdiction detection"""
        prompt = f"""Detect the engineering jurisdiction/code system for this job:

JOB TEXT:
{self.raw_text[:3000]}

OPTIONS:
{', '.join([j.value for j in Jurisdiction])}

Return ONLY the option name (e.g., "India_IS"), nothing else.
"""
        try:
            if hasattr(self.llm_client, 'chat'):
                response = self.llm_client.chat.completions.create(
                    model=self._model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=20
                )
                result = response.choices[0].message.content.strip()
                return Jurisdiction(result) if result in [j.value for j in Jurisdiction] else Jurisdiction.OTHER
        except Exception:
            pass
        self._jurisdiction_llm_failed = True
        return self._keyword_detect_jurisdiction()
    
    # Requirements Extraction
    
    def extract_deliverables(self) -> List[DeliverableType]:
        """Extract required deliverable types from job text"""
        text_lower = self.raw_text.lower()
        found = []
        
        for del_type, keywords in self.DELIVERABLE_MAP.items():
            if any(kw.lower() in text_lower for kw in keywords):
                found.append(del_type)
        
        # Add common defaults based on job type
        job_type = self._keyword_classify_job_type()
        if job_type == JobType.PERMIT_DRAWINGS and DeliverableType.PE_STAMPED not in found:
            found.append(DeliverableType.PE_STAMPED)
        if job_type == JobType.STRUCTURAL_ANALYSIS_FEM:
            if DeliverableType.INP_FILE not in found:
                found.append(DeliverableType.INP_FILE)
        
        return found if found else [DeliverableType.OTHER]
    
    def extract_required_inputs(self) -> List[str]:
        """Identify what inputs the client should provide"""
        job_type = self._keyword_classify_job_type()
        
        common_inputs = [
            "project location/address",
            "site plan or survey",
            "applicable building codes/local amendments"
        ]
        
        type_specific = {
            JobType.PILE_FOUNDATION: [
                "geotechnical investigation report",
                "column load values (dead/live/wind)",
                "pile type preference (bored/driven/CFA)",
                "groundwater level information"
            ],
            JobType.SLAB_BEAM_COLUMN: [
                "architectural floor plans",
                "live load requirements (occupancy type)",
                "column grid layout",
                "material preferences (concrete grade, steel grade)"
            ],
            JobType.STRUCTURAL_ANALYSIS_FEM: [
                "geometry file (STEP/IGES) or detailed dimensions",
                "material properties (E, nu, yield strength)",
                "boundary conditions & loading scenarios",
                "expected output metrics (stress, displacement, factor of safety)"
            ],
            JobType.PERMIT_DRAWINGS: [
                "existing building drawings (if renovation)",
                "local building department submission requirements",
                "property survey with setbacks",
                "contractor/licensee information for stamping"
            ],
            JobType.DRAINAGE_STORMWATER: [
                "topographic survey",
                "rainfall intensity data (IDF curves)",
                "downstream discharge constraints",
                "soil infiltration rates"
            ],
            JobType.GEOTECHNICAL_ANALYSIS: [
                "soil investigation report",
                "laboratory test results",
                "groundwater conditions",
                "proposed foundation type"
            ],
        }
        
        inputs = common_inputs + type_specific.get(job_type, [])
        
        # Check which inputs are mentioned in job text
        text_lower = self.raw_text.lower()
        provided = [inp for inp in inputs if any(phrase in text_lower for phrase in inp.lower().split())]
        missing = [inp for inp in inputs if inp not in provided]
        
        return missing
    
    # Licensing & Risk Assessment
    
    def assess_licensing_requirements(self) -> LicensingInfo:
        """Determine if professional license is required"""
        jurisdiction = self._keyword_detect_jurisdiction().value
        job_type = self._keyword_classify_job_type()
        deliverables = self.extract_deliverables()
        
        requires_license = False
        
        if DeliverableType.PE_STAMPED in deliverables or job_type == JobType.PERMIT_DRAWINGS:
            requires_license = True
        
        structural_jobs = [
            JobType.PILE_FOUNDATION, JobType.SLAB_BEAM_COLUMN, 
            JobType.RETAINING_WALL, JobType.BRIDGE_STRUCTURE,
            JobType.STEEL_STRUCTURE, JobType.PRESTRESSED_CONCRETE
        ]
        if job_type in structural_jobs:
            requires_license = True
        
        license_map = {
            "Florida_FBC": "Florida Professional Engineer (PE) + Structural Recognition",
            "India_IS": "Registered Structural Engineer (State Council)",
            "USA_ACI": "Professional Engineer (PE) - State Licensed",
            "Eurocode": "Chartered Engineer (CEng) or equivalent",
            "Australia_AS": "Registered Professional Engineer of Queensland (RPEQ) or equivalent",
            "Canada_CS": "Professional Engineer (P.Eng.) - Provincial Licensed",
        }
        license_type = license_map.get(jurisdiction, "Verify with local engineering board")
        
        return LicensingInfo(
            requires_license=requires_license,
            license_type=license_type,
            jurisdiction=jurisdiction,
            note="Verify with local engineering board before bidding"
        )
    
    def assess_risk_flags(self) -> List[str]:
        """Identify potential project risks"""
        flags = []
        text_lower = self.raw_text.lower()
        
        # Budget risk
        budget_match = re.search(r'[\$₹€£]\s*([\d,]+(?:\.\d+)?)\s*(?:–|-)?\s*[\$₹€£]?[\d,]+', text_lower)
        if budget_match:
            budget_text = budget_match.group()
            if any(kw in text_lower for kw in ["pile", "foundation", "structural", "permit"]) and "50" in budget_text:
                flags.append("Budget may be insufficient for scope complexity")
        
        # Scope ambiguity
        if any(phrase in text_lower for phrase in ["not sure", "open to", "flexible", "to be determined"]):
            flags.append("Scope may be ambiguous - clarify deliverables upfront")
        
        # Missing critical inputs
        missing_inputs = self.extract_required_inputs()
        critical_missing = [inp for inp in missing_inputs if "soil" in inp.lower() or "load" in inp.lower()]
        if critical_missing:
            flags.append(f"Missing critical inputs: {', '.join(critical_missing)}")
        
        # Timeline pressure
        if any(phrase in text_lower for phrase in ["urgent", "asap", "24 hours", "tomorrow"]):
            flags.append("Tight timeline may compromise quality/review")
        
        # Licensing
        license_info = self.assess_licensing_requirements()
        if license_info.requires_license:
            flags.append("License required - ensure you hold appropriate credential")
        
        return flags if flags else ["No major risk flags detected"]
    
    # Code Resolution (Hybrid)
    
    def extract_required_codes(self) -> CodeResolutionResult:
        """Hybrid code extraction: database + LLM + verification flag."""
        jurisdiction = self._keyword_detect_jurisdiction().value
        job_type = self._keyword_classify_job_type().value
        
        result = self.code_resolver.resolve_codes(
            jurisdiction=jurisdiction,
            job_type=job_type,
            job_text=self.raw_text
        )
        
        return result
    
    # Clarifying Questions
    
    def generate_clarifying_questions(self) -> List[str]:
        """Generate targeted questions to fill information gaps"""
        job_type = self._keyword_classify_job_type()
        missing_inputs = self.extract_required_inputs()
        
        questions = []
        
        type_questions = {
            JobType.PILE_FOUNDATION: [
                "Do you have a geotechnical report with soil parameters (c, phi, gamma)?",
                "What are the design loads (axial, lateral, moment) at pile head?",
                "Is there a preferred pile installation method (bored, driven, CFA)?",
                "Are there access constraints for pile driving equipment?"
            ],
            JobType.STRUCTURAL_ANALYSIS_FEM: [
                "Will you provide geometry files (STEP/IGES) or should I model from drawings?",
                "What analysis type is needed: static, dynamic, nonlinear, buckling?",
                "What output metrics are critical: stresses, displacements, factor of safety?",
                "Do you need validation against experimental or analytical results?"
            ],
            JobType.PERMIT_DRAWINGS: [
                "Which building department will review these plans?",
                "Do you need the engineer's seal/stamp, or just draft drawings?",
                "Are there local amendments to the base code we should follow?",
                "Will you handle permit submission, or do you need support?"
            ],
            JobType.DRAINAGE_STORMWATER: [
                "What is the design storm return period (10-yr, 25-yr, 100-yr)?",
                "Are there downstream discharge limits or detention requirements?",
                "Do you have existing drainage infrastructure to connect to?",
                "What software format is preferred for hydraulic modeling?"
            ],
            JobType.GEOTECHNICAL_ANALYSIS: [
                "What is the purpose of this analysis (foundation design, slope stability, settlement)?",
                "Do you have laboratory test results (triaxial, consolidation, direct shear)?",
                "What is the groundwater condition during analysis?",
                "Are there specific software requirements (PLAXIS, GeoStudio, etc.)?"
            ],
        }
        
        # Add questions based on missing inputs
        for inp in missing_inputs[:3]:
            if "soil" in inp.lower():
                questions.append("Could you provide the geotechnical report or soil parameters?")
            elif "load" in inp.lower():
                questions.append("What are the design load values (dead/live/wind/seismic)?")
            elif "plan" in inp.lower() or "survey" in inp.lower():
                questions.append("Do you have a site plan or survey showing property lines?")
        
        # Add job-type specific questions
        for q in type_questions.get(job_type, [])[:3]:
            if q not in questions:
                questions.append(q)
        
        return questions if questions else ["No clarifying questions at this time."]
    
    # Main Parsing Method
    
    def parse_to_structured(self) -> Dict[str, Any]:
        """Main method: return standardized JSON output"""
        # Use keyword-based methods directly to avoid recursion issues with LLM
        classification = self._keyword_classify_job_type()
        jurisdiction = self._keyword_detect_jurisdiction()
        
        return {
            "meta": {
                "job_id": self.job_id,
                "parsed_at": datetime.now().isoformat(),
                "parser_version": "2.0.0",
                "llm_provider": self.llm_provider if self.llm_client else "none"
            },
            "classification": {
                "job_type": classification.value,
                "jurisdiction": jurisdiction.value,
                "confidence": "high" if self.llm_client else "medium"
            },
            "required_codes": self.extract_required_codes().model_dump(),
            "requirements": {
                "deliverables": [d.value for d in self.extract_deliverables()],
                "required_inputs_missing": self.extract_required_inputs(),
                "licensing": self.assess_licensing_requirements().model_dump()
            },
            "risk_assessment": {
                "flags": self.assess_risk_flags(),
                "overall_risk": "high" if any("insufficient" in f or "ambiguous" in f for f in self.assess_risk_flags()) else "low"
            },
            "next_actions": {
                "clarifying_questions": self.generate_clarifying_questions(),
                "recommended_first_step": self._recommend_first_step()
            },
            "raw_excerpt": self.raw_text[:500],
            "compliance": {
                "human_verification_required": True,
                "ai_assisted": self.llm_client is not None,
                "disclaimer": "This output is AI-assisted and requires verification by a licensed Professional Engineer before use in any engineering design, permit submission, or construction activity."
            }
        }
    
    def _recommend_first_step(self) -> str:
        """Suggest the most critical next action"""
        missing = self.extract_required_inputs()
        if any("soil" in m.lower() for m in missing):
            return "Request geotechnical report before starting design"
        elif any("load" in m.lower() for m in missing):
            return "Clarify design loads and load combinations"
        elif self.assess_licensing_requirements().requires_license:
            return "Confirm you hold the required professional license for this jurisdiction"
        else:
            return "Send clarifying questions to client to finalize scope"
    
    # Audit Logging
    
    def save_intake_log(self, output_dir: str = "data/logs") -> str:
        """Save parsed result to audit log"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_file = Path(output_dir) / f"intake_{self.job_id}.json"
        
        result = self.parse_to_structured()
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Also append to master log
        master_log = Path(output_dir) / "intake_master.jsonl"
        with open(master_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(result) + "\n")
        
        return str(output_file)
