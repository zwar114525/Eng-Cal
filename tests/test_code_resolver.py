"""Tests for code resolver"""

import pytest
from modules.code_resolver import HybridCodeResolver
from modules.code_database import CodeDatabase


class TestCodeDatabase:
    def test_get_code_details(self):
        code = CodeDatabase.get_code_details("IS_2911")
        assert code is not None
        assert code.code_id == "IS_2911"
    
    def test_get_required_codes_india_pile(self):
        codes = CodeDatabase.get_required_codes("India_IS", "pile_foundation")
        assert len(codes) > 0
        assert any(c.code_id == "IS_2911" for c in codes)
    
    def test_get_required_codes_usa_concrete(self):
        codes = CodeDatabase.get_required_codes("USA_ACI", "slab_beam_column")
        assert len(codes) > 0
        assert any(c.code_id == "ACI_318" for c in codes)


class TestHybridResolver:
    def test_database_lookup(self):
        resolver = HybridCodeResolver(llm_client=None)
        result = resolver.resolve_codes("India_IS", "pile_foundation", "test job")
        
        assert result.source == "database"
        assert len(result.codes) > 0
        assert result.confidence > 0.5
    
    def test_no_match_returns_manual(self):
        resolver = HybridCodeResolver(llm_client=None)
        result = resolver.resolve_codes("Other", "other", "test job")
        
        assert result.source in ["manual_required", "llm_suggestion"]
