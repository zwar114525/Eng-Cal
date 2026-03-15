"""
Code Database - Curated registry of engineering codes/standards.
"""

from typing import Optional, List, Dict, Tuple
from modules.models import CodeEntry
from modules.enums import JobType, Jurisdiction


class CodeDatabase:
    """
    Centralized registry of engineering codes/standards.
    Organized by jurisdiction -> job_type -> list of codes.
    """
    
    CODES: Dict[str, CodeEntry] = {
        # India (IS Codes)
        "IS_2911": CodeEntry(
            code_id="IS_2911",
            title="Design and construction of pile foundations",
            scope="Pile foundation design, capacity calculation, load testing",
            priority="primary",
            parts=["Part 1: Concrete piles", "Part 2: Under-reamed piles", 
                   "Part 3: Prestressed concrete piles", "Part 4: Load test on piles"],
            source_url="https://bis.gov.in"
        ),
        "IS_456": CodeEntry(
            code_id="IS_456",
            title="Plain and reinforced concrete - Code of practice",
            scope="Concrete design, reinforcement detailing, durability requirements",
            priority="primary",
            edition="2000",
            source_url="https://bis.gov.in"
        ),
        "IS_875": CodeEntry(
            code_id="IS_875",
            title="Code of practice for design loads (other than earthquake)",
            scope="Dead, live, wind, snow load calculations",
            priority="primary",
            parts=["Part 1: Dead loads", "Part 2: Imposed loads", 
                   "Part 3: Wind loads", "Part 4: Snow loads"],
            source_url="https://bis.gov.in"
        ),
        "IS_1893": CodeEntry(
            code_id="IS_1893",
            title="Criteria for earthquake resistant design of structures",
            scope="Seismic design forces, ductility requirements",
            priority="secondary",
            parts=["Part 1: General provisions", "Part 2: Liquid retaining tanks"],
            source_url="https://bis.gov.in"
        ),
        "IS_800": CodeEntry(
            code_id="IS_800",
            title="General construction in steel - Code of practice",
            scope="Steel structure design, connections, stability",
            priority="primary",
            edition="2007",
            source_url="https://bis.gov.in"
        ),
        "IS_1343": CodeEntry(
            code_id="IS_1343",
            title="Prestressed concrete - Code of practice",
            scope="Prestressed concrete design, losses, detailing",
            priority="primary",
            source_url="https://bis.gov.in"
        ),
        "IS_1498": CodeEntry(
            code_id="IS_1498",
            title="Classification and identification of soils for general engineering purposes",
            scope="Soil classification, index properties",
            priority="secondary",
            source_url="https://bis.gov.in"
        ),
        "IS_2720": CodeEntry(
            code_id="IS_2720",
            title="Methods of test for soils",
            scope="Geotechnical laboratory testing procedures",
            priority="secondary",
            source_url="https://bis.gov.in"
        ),
        
        # USA (ACI/ASCE/IBC)
        "ACI_318": CodeEntry(
            code_id="ACI_318",
            title="Building Code Requirements for Structural Concrete",
            scope="Concrete design, reinforcement, durability, seismic provisions",
            priority="primary",
            edition="19",
            source_url="https://www.concrete.org"
        ),
        "ACI_315": CodeEntry(
            code_id="ACI_315",
            title="Details and Detailing of Concrete Reinforcement",
            scope="Reinforcement drafting standards, bar scheduling",
            priority="secondary",
            source_url="https://www.concrete.org"
        ),
        "ASCE_7": CodeEntry(
            code_id="ASCE_7",
            title="Minimum Design Loads and Associated Criteria for Buildings and Other Structures",
            scope="Dead, live, wind, snow, seismic, flood loads",
            priority="primary",
            edition="22",
            source_url="https://ascelibrary.org"
        ),
        "ASCE_20": CodeEntry(
            code_id="ASCE_20",
            title="Standard Guidelines for the Design and Installation of Pile Foundations",
            scope="Pile design, installation, testing, quality control",
            priority="secondary",
            source_url="https://ascelibrary.org"
        ),
        "IBC": CodeEntry(
            code_id="IBC",
            title="International Building Code",
            scope="General building requirements, occupancy, fire safety, structural",
            priority="primary",
            edition="2021",
            source_url="https://codes.iccsafe.org"
        ),
        "AISC_360": CodeEntry(
            code_id="AISC_360",
            title="Specification for Structural Steel Buildings",
            scope="Steel member design, connections, stability",
            priority="primary",
            edition="16",
            source_url="https://www.aisc.org"
        ),
        "AASHTO_LRFD": CodeEntry(
            code_id="AASHTO_LRFD",
            title="LRFD Bridge Design Specifications",
            scope="Bridge structural design, loads, detailing",
            priority="primary",
            source_url="https://transportation.org"
        ),
        
        # Florida Specific
        "FBC_BUILDING": CodeEntry(
            code_id="FBC_BUILDING",
            title="Florida Building Code - Building",
            scope="State-adopted building requirements, amendments to IBC",
            priority="primary",
            edition="2023",
            source_url="https://floridabuilding.org"
        ),
        "FBC_RESIDENTIAL": CodeEntry(
            code_id="FBC_RESIDENTIAL",
            title="Florida Building Code - Residential",
            scope="1-2 family dwellings, townhouses",
            priority="primary",
            edition="2023",
            source_url="https://floridabuilding.org"
        ),
        "FBC_HVHZ": CodeEntry(
            code_id="FBC_HVHZ",
            title="High-Velocity Hurricane Zone Provisions (Miami-Dade & Broward)",
            scope="Enhanced wind, impact, pressure requirements",
            priority="primary",
            source_url="https://www.miamidade.gov/building"
        ),
        "TAS_201": CodeEntry(
            code_id="TAS_201",
            title="Florida Product Approval: Impact Test Procedures",
            scope="HVHZ product testing for wind-borne debris",
            priority="secondary",
            source_url="https://floridabuilding.org"
        ),
        
        # Eurocode
        "EN_1990": CodeEntry(
            code_id="EN_1990",
            title="Eurocode: Basis of structural design",
            scope="Reliability, limit states, combination rules",
            priority="primary",
            source_url="https://www.en-standard.eu"
        ),
        "EN_1992": CodeEntry(
            code_id="EN_1992",
            title="Eurocode 2: Design of concrete structures",
            scope="Concrete member design, detailing, durability",
            priority="primary",
            parts=["Part 1-1: General rules", "Part 1-2: Structural fire design"],
            source_url="https://www.en-standard.eu"
        ),
        "EN_1997": CodeEntry(
            code_id="EN_1997",
            title="Eurocode 7: Geotechnical design",
            scope="Geotechnical analysis, foundation design, soil parameters",
            priority="primary",
            parts=["Part 1: General rules", "Part 2: Ground investigation and testing"],
            source_url="https://www.en-standard.eu"
        ),
        "EN_1998": CodeEntry(
            code_id="EN_1998",
            title="Eurocode 8: Design of structures for earthquake resistance",
            scope="Seismic actions, ductility, capacity design",
            priority="secondary",
            source_url="https://www.en-standard.eu"
        ),
        "EN_1993": CodeEntry(
            code_id="EN_1993",
            title="Eurocode 3: Design of steel structures",
            scope="Steel member design, connections, stability",
            priority="primary",
            source_url="https://www.en-standard.eu"
        ),
        
        # Australia
        "AS_3600": CodeEntry(
            code_id="AS_3600",
            title="Concrete structures",
            scope="Concrete design, reinforcement, durability",
            priority="primary",
            source_url="https://www.standards.org.au"
        ),
        "AS_1170": CodeEntry(
            code_id="AS_1170",
            title="Structural design actions",
            scope="Load determination for Australian conditions",
            priority="primary",
            parts=["Part 1: Permanent/imposed loads", "Part 2: Wind", 
                   "Part 3: Snow", "Part 4: Earthquake"],
            source_url="https://www.standards.org.au"
        ),
        "AS_2159": CodeEntry(
            code_id="AS_2159",
            title="Piling - Design and installation",
            scope="Pile foundation design, testing, installation QA",
            priority="primary",
            source_url="https://www.standards.org.au"
        ),
        
        # Canada
        "CSA_A23_3": CodeEntry(
            code_id="CSA_A23_3",
            title="Design of concrete structures",
            scope="Concrete design, reinforcement, durability",
            priority="primary",
            source_url="https://www.csagroup.org"
        ),
        "CSA_S16": CodeEntry(
            code_id="CSA_S16",
            title="Design of steel structures",
            scope="Steel member design, connections, stability",
            priority="primary",
            source_url="https://www.csagroup.org"
        ),
        "NBC": CodeEntry(
            code_id="NBC",
            title="National Building Code of Canada",
            scope="General building requirements, loads, safety",
            priority="primary",
            edition="2020",
            source_url="https://nrc.canada.ca"
        ),
        
        # International
        "ISO_2394": CodeEntry(
            code_id="ISO_2394",
            title="General principles on reliability for structures",
            scope="Reliability-based design framework",
            priority="tertiary",
            source_url="https://www.iso.org"
        ),
        "FHWA_NHI_16_009": CodeEntry(
            code_id="FHWA_NHI_16_009",
            title="Geotechnical Engineering Circular No. 12: Design of Pile Foundations",
            scope="US federal guidance for pile design methods",
            priority="secondary",
            source_url="https://www.fhwa.dot.gov"
        ),
    }
    
    # Mapping: (jurisdiction, job_type) -> list of code IDs
    CODE_MAPPING: Dict[Tuple[str, str], List[str]] = {
        # India
        ("India_IS", "pile_foundation"): ["IS_2911", "IS_456", "IS_875", "IS_1893", "IS_1498"],
        ("India_IS", "slab_beam_column"): ["IS_456", "IS_875", "IS_1893"],
        ("India_IS", "retaining_wall"): ["IS_456", "IS_875", "IS_1893", "IS_1498"],
        ("India_IS", "steel_structure"): ["IS_800", "IS_875", "IS_1893"],
        ("India_IS", "prestressed_concrete"): ["IS_1343", "IS_456", "IS_875"],
        ("India_IS", "geotechnical_analysis"): ["IS_1498", "IS_2720", "IS_875"],
        ("India_IS", "bridge_structure"): ["IS_456", "IS_800", "IS_1893"],
        
        # USA (ACI)
        ("USA_ACI", "pile_foundation"): ["ACI_318", "ASCE_7", "ASCE_20", "IBC"],
        ("USA_ACI", "slab_beam_column"): ["ACI_318", "ASCE_7", "ACI_315"],
        ("USA_ACI", "retaining_wall"): ["ACI_318", "ASCE_7", "AISC_360"],
        ("USA_ACI", "steel_structure"): ["AISC_360", "ASCE_7", "IBC"],
        ("USA_ACI", "bridge_structure"): ["AASHTO_LRFD", "ASCE_7"],
        ("USA_ACI", "structural_analysis_fem"): ["ACI_318", "AISC_360", "ASCE_7"],
        
        # Florida
        ("Florida_FBC", "permit_drawings"): ["FBC_BUILDING", "FBC_RESIDENTIAL", "ASCE_7", "FBC_HVHZ"],
        ("Florida_FBC", "pile_foundation"): ["FBC_BUILDING", "ACI_318", "ASCE_7", "FBC_HVHZ"],
        ("Florida_FBC", "retaining_wall"): ["FBC_BUILDING", "ACI_318", "ASCE_7", "TAS_201"],
        ("Florida_FBC", "slab_beam_column"): ["FBC_BUILDING", "ACI_318", "ASCE_7"],
        
        # Eurocode
        ("Eurocode", "pile_foundation"): ["EN_1997", "EN_1992", "EN_1990", "EN_1998"],
        ("Eurocode", "slab_beam_column"): ["EN_1992", "EN_1990", "EN_1998"],
        ("Eurocode", "steel_structure"): ["EN_1993", "EN_1990", "EN_1998"],
        ("Eurocode", "geotechnical_analysis"): ["EN_1997", "EN_1990"],
        ("Eurocode", "structural_analysis_fem"): ["EN_1992", "EN_1993", "EN_1990"],
        
        # Australia
        ("Australia_AS", "pile_foundation"): ["AS_2159", "AS_3600", "AS_1170"],
        ("Australia_AS", "slab_beam_column"): ["AS_3600", "AS_1170"],
        
        # Canada
        ("Canada_CS", "slab_beam_column"): ["CSA_A23_3", "NBC", "CSA_S16"],
        ("Canada_CS", "steel_structure"): ["CSA_S16", "NBC"],
        
        # Fallback / Generic
        ("Other", "structural_analysis_fem"): ["ISO_2394"],
        ("Other", "geotechnical_analysis"): ["FHWA_NHI_16_009"],
        ("Other", "pile_foundation"): ["FHWA_NHI_16_009"],
    }
    
    @classmethod
    def get_code_details(cls, code_id: str) -> Optional[CodeEntry]:
        """Retrieve full metadata for a code"""
        return cls.CODES.get(code_id)
    
    @classmethod
    def get_required_codes(cls, jurisdiction: str, job_type: str) -> List[CodeEntry]:
        """Return structured list of codes needed for a job"""
        key = (jurisdiction, job_type)
        code_ids = cls.CODE_MAPPING.get(key, [])
        
        # Fallback: try jurisdiction-agnostic
        if not code_ids:
            fallback_key = ("Other", job_type)
            code_ids = cls.CODE_MAPPING.get(fallback_key, [])
        
        # Build structured output
        result = []
        for idx, code_id in enumerate(code_ids):
            entry = cls.get_code_details(code_id)
            if entry:
                # Override priority based on position
                if idx == 0:
                    entry.priority = "primary"
                elif idx <= 2:
                    entry.priority = "secondary"
                else:
                    entry.priority = "tertiary"
                result.append(entry)
        
        return result
    
    @classmethod
    def get_all_code_ids(cls) -> List[str]:
        """Return list of all known code IDs for LLM validation"""
        return list(cls.CODES.keys())
    
    @classmethod
    def get_all_codes(cls) -> List[CodeEntry]:
        """Return all codes in the database"""
        return list(cls.CODES.values())
    
    @classmethod
    def search_codes(cls, jurisdiction: str = None, job_type: str = None) -> List[CodeEntry]:
        """Search codes by jurisdiction and/or job type"""
        if jurisdiction and job_type:
            return cls.get_required_codes(jurisdiction, job_type)
        elif jurisdiction:
            # Return all codes for this jurisdiction
            codes = []
            for key, code_ids in cls.CODE_MAPPING.items():
                if key[0] == jurisdiction:
                    for code_id in code_ids:
                        entry = cls.get_code_details(code_id)
                        if entry and entry not in codes:
                            codes.append(entry)
            return codes
        else:
            return cls.get_all_codes()
