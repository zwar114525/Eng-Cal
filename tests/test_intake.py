"""
Tests for the intake module.
"""

import pytest
from modules.intake import EngineeringIntake
from modules.enums import JobType, Jurisdiction


class TestJobClassification:
    """Test job type classification"""
    
    def test_pile_foundation_classification(self):
        """Test pile foundation job classification"""
        job_text = """
        Need pile foundation design for 1300 sft residential slab in Mumbai.
        Soil report available. Must follow IS 2911.
        """
        intake = EngineeringIntake(job_text)
        result = intake.classify_job_type()
        assert result == JobType.PILE_FOUNDATION
    
    def test_fem_job_classification(self):
        """Test FEM analysis job classification"""
        job_text = """
        Abaqus finite element analysis model for structural analysis.
        Need nonlinear analysis with stress results.
        """
        intake = EngineeringIntake(job_text)
        result = intake.classify_job_type()
        assert result == JobType.STRUCTURAL_ANALYSIS_FEM
    
    def test_permit_drawings_classification(self):
        """Test permit drawings job classification"""
        job_text = """
        Need permit-ready patio roof plans for Florida.
        Must be PE stamped.
        """
        intake = EngineeringIntake(job_text)
        result = intake.classify_job_type()
        assert result == JobType.PERMIT_DRAWINGS


class TestJurisdictionDetection:
    """Test jurisdiction detection"""
    
    def test_india_detection(self):
        """Test India jurisdiction detection"""
        job_text = """
        Need pile foundation design in Mumbai.
        Must follow IS 2911. Budget: 8000 INR.
        """
        intake = EngineeringIntake(job_text)
        result = intake.detect_jurisdiction()
        assert result == Jurisdiction.INDIA_IS
    
    def test_florida_detection(self):
        """Test Florida jurisdiction detection"""
        job_text = """
        Need permit-ready plans for Palmetto Bay, FL.
        Florida Building Code applies.
        """
        intake = EngineeringIntake(job_text)
        result = intake.detect_jurisdiction()
        assert result == Jurisdiction.FLORIDA_FBC
    
    def test_usa_detection(self):
        """Test USA jurisdiction detection"""
        job_text = """
        Structural design for building in USA.
        Must follow ACI 318 and ASCE 7.
        """
        intake = EngineeringIntake(job_text)
        result = intake.detect_jurisdiction()
        assert result == Jurisdiction.USA_ACI


class TestDeliverableExtraction:
    """Test deliverable extraction"""
    
    def test_dwg_extraction(self):
        """Test DWG deliverable extraction"""
        job_text = "Need AutoCAD drawings (.dwg) for foundation layout"
        intake = EngineeringIntake(job_text)
        result = intake.extract_deliverables()
        from modules.enums import DeliverableType
        assert DeliverableType.DWG_FILE in result
    
    def test_pe_stamped_extraction(self):
        """Test PE stamped deliverable extraction"""
        job_text = "Need PE stamped drawings for permit submission"
        intake = EngineeringIntake(job_text)
        result = intake.extract_deliverables()
        from modules.enums import DeliverableType
        assert DeliverableType.PE_STAMPED in result


class TestLicensingAssessment:
    """Test licensing requirements assessment"""
    
    def test_license_required_for_permit(self):
        """Test license is required for permit drawings"""
        job_text = "Need permit drawings for Florida building"
        intake = EngineeringIntake(job_text)
        result = intake.assess_licensing_requirements()
        assert result.requires_license == True
    
    def test_license_required_for_structural(self):
        """Test license is required for structural work"""
        job_text = "Need pile foundation design for building"
        intake = EngineeringIntake(job_text)
        result = intake.assess_licensing_requirements()
        assert result.requires_license == True


class TestFullIntake:
    """Test full intake processing"""
    
    def test_full_parse(self):
        """Test full parsing of job"""
        job_text = """
        Need pile foundation design for 1300 sft residential slab in Mumbai.
        Soil report available. Must follow IS 2911.
        Deliverables: DWG layout + Excel calcs.
        """
        intake = EngineeringIntake(job_text)
        result = intake.parse_to_structured()
        
        assert result["classification"]["job_type"] == "pile_foundation"
        assert result["classification"]["jurisdiction"] == "India_IS"
        assert len(result["required_codes"]["codes"]) > 0
        assert result["compliance"]["human_verification_required"] == True
    
    def test_audit_log_creation(self):
        """Test audit log is created"""
        job_text = "Test job for audit log verification"
        intake = EngineeringIntake(job_text)
        log_file = intake.save_intake_log()
        
        from pathlib import Path
        assert Path(log_file).exists()
