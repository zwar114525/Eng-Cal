"""
Enums for civil engineering intake module.
"""

from enum import Enum


class JobType(Enum):
    """Taxonomy of civil/structural engineering job types"""
    PILE_FOUNDATION = "pile_foundation"
    SLAB_BEAM_COLUMN = "slab_beam_column"
    RETAINING_WALL = "retaining_wall"
    DRAINAGE_STORMWATER = "drainage_stormwater"
    ROAD_HIGHWAY = "road_highway"
    STRUCTURAL_ANALYSIS_FEM = "structural_analysis_fem"
    PERMIT_DRAWINGS = "permit_drawings"
    SITE_PLANNING_GRADING = "site_planning_grading"
    MATERIAL_TAKEOFF = "material_takeoff"
    CONSTRUCTION_SUPERVISION = "construction_supervision"
    GEOTECHNICAL_ANALYSIS = "geotechnical_analysis"
    BRIDGE_STRUCTURE = "bridge_structure"
    STEEL_STRUCTURE = "steel_structure"
    PRESTRESSED_CONCRETE = "prestressed_concrete"
    SEISMIC_RETROFIT = "seismic_retrofit"
    OTHER = "other"


class Jurisdiction(Enum):
    """Common engineering jurisdictions & code systems"""
    INDIA_IS = "India_IS"
    USA_ACI = "USA_ACI"
    FLORIDA_FBC = "Florida_FBC"
    EUROCODE = "Eurocode"
    UK_BS = "UK_BS"
    AUSTRALIA_AS = "Australia_AS"
    CANADA_CS = "Canada_CS"
    UAE_SBC = "UAE_SBC"
    SINGAPORE_SS = "Singapore_SS"
    OTHER = "Other"


class DeliverableType(Enum):
    """Standard deliverable types"""
    DWG_FILE = "dwg_file"
    PDF_DRAWING = "pdf_drawing"
    EXCEL_CALCULATIONS = "excel_calculations"
    PDF_REPORT = "pdf_report"
    PE_STAMPED = "pe_stamped"
    INP_FILE = "inp_file"
    ODB_FILE = "odb_file"
    WORD_SPEC = "word_spec"
    REVIT_MODEL = "revit_model"
    OTHER = "other"


class CodePriority(Enum):
    """Code importance ranking"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
