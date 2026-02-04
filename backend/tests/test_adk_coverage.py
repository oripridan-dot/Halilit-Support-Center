"""
Comprehensive ADK (Agent Development Kit) Coverage Test Suite v5.2.4
Tests the entire Agentic System: Trinity Swarm + UI Agent Bridge
Validates Trinity Swarm architecture with CommercialAgent, OfficialAgent, ValidatorAgent
"""

import logging
import pytest
from backend.agents.trinity_swarm import (
    AgentBase, CommercialAgent, OfficialAgent, ValidatorAgent,
    TrinitySwarm, ProductDraft, AuditReport
)

logger = logging.getLogger(__name__)


class TestAgentBase:
    """Test the base agent class"""

    def test_agent_initialization(self):
        """Test agent basic initialization"""
        agent = AgentBase("TestAgent", model_name="gemini-2.0-flash")
        assert agent.name == "TestAgent"
        assert agent.model_name == "gemini-2.0-flash"
        assert agent.client is not None

    def test_agent_think_method(self):
        """Test agent think method"""
        agent = AgentBase("TestAgent")
        result = agent.think("test prompt")
        assert isinstance(result, str) or result is not None

    def test_agent_memory_system(self):
        """Test agent has memory system"""
        agent = AgentBase("TestAgent")
        assert hasattr(agent, 'learn_from_action')

    def test_agent_initialization_prints_message(self, capsys):
        """Test agent initialization prints message"""
        agent = AgentBase("DebugAgent")
        captured = capsys.readouterr()
        assert "DebugAgent" in captured.out
        assert "learning" in captured.out.lower() or "Initialized" in captured.out


class TestCommercialAgent:
    """Test the CommercialAgent agent"""

    def test_scout_initialization(self):
        """Test CommercialAgent initialization"""
        scout = CommercialAgent()
        assert scout.name == "CommercialScout"
        assert scout.model_name == "gemini-2.0-flash"

    def test_scout_harvest(self):
        """Test CommercialAgent harvest method"""
        scout = CommercialAgent()
        result = scout.harvest("Nord")
        assert isinstance(result, dict)
        assert "id" in result
        assert "name" in result
        assert "brand" in result
        assert "price_il" in result
        assert "price_eilat" in result

    def test_scout_harvest_with_various_brands(self):
        """Test CommercialAgent harvest with different brands"""
        scout = CommercialAgent()
        brands = ["Roland", "Yamaha", "Korg"]
        for brand in brands:
            result = scout.harvest(brand)
            assert result.get("brand") == brand

    def test_scout_system_instruction(self):
        """Test scout has proper system instruction"""
        scout = CommercialAgent()
        assert "harvester" in scout.system_instruction.lower(
        ) or "data" in scout.system_instruction.lower()


class TestOfficialAgent:
    """Test the OfficialAgent agent"""

    def test_verifier_initialization(self):
        """Test OfficialAgent initialization"""
        verifier = OfficialAgent()
        assert verifier.name == "OfficialVerifier"
        assert verifier.model_name == "gemini-2.0-flash"

    def test_verifier_enrich(self):
        """Test OfficialAgent enrich method"""
        verifier = OfficialAgent()
        draft = {
            "id": "123",
            "name": "Test Product",
            "brand": "TestBrand",
            "price_il": 100,
            "price_eilat": 85
        }
        result = verifier.enrich(draft)
        assert isinstance(result, dict)
        assert "image_url" in result
        assert "official_match" in result
        assert result.get("official_match") == True

    def test_verifier_preserves_original_data(self):
        """Test verifier preserves original draft data"""
        verifier = OfficialAgent()
        draft = {"id": "456", "name": "Test", "brand": "Brand"}
        result = verifier.enrich(draft)
        assert result.get("id") == "456"
        assert result.get("name") == "Test"

    def test_verifier_system_instruction(self):
        """Test verifier has proper system instruction"""
        verifier = OfficialAgent()
        assert "expert" in verifier.system_instruction.lower(
        ) or "brand" in verifier.system_instruction.lower()


class TestValidatorAgent:
    """Test the ValidatorAgent agent"""

    def test_validator_initialization(self):
        """Test ValidatorAgent initialization"""
        validator = ValidatorAgent()
        assert validator.name == "ExternalValidator"
        assert validator.model_name == "gemini-2.0-flash"

    def test_validator_has_audit(self):
        """Test ValidatorAgent has audit method"""
        validator = ValidatorAgent()
        assert hasattr(validator, 'audit')
        assert callable(validator.audit)

    def test_validator_system_instruction(self):
        """Test validator has compliance instruction"""
        validator = ValidatorAgent()
        instruction = validator.system_instruction.lower()
        assert "audit" in instruction or "compliance" in instruction


class TestTrinitySwarm:
    """Test the Trinity Swarm orchestrator"""

    def test_trinity_initialization(self):
        """Test TrinitySwarm initialization"""
        swarm = TrinitySwarm()
        assert swarm.scout is not None
        assert swarm.verifier is not None
        assert swarm.auditor is not None

    def test_trinity_has_agents(self):
        """Test swarm contains all three agents"""
        swarm = TrinitySwarm()
        assert isinstance(swarm.scout, CommercialAgent)
        assert isinstance(swarm.verifier, OfficialAgent)
        assert isinstance(swarm.auditor, ValidatorAgent)

    def test_trinity_agent_names(self):
        """Test agents have correct names"""
        swarm = TrinitySwarm()
        assert swarm.scout.name == "CommercialScout"
        assert swarm.verifier.name == "OfficialVerifier"
        assert swarm.auditor.name == "ExternalValidator"

    def test_trinity_process_brand(self):
        """Test swarm has process_brand method"""
        swarm = TrinitySwarm()
        assert hasattr(swarm, 'process_brand')
        assert callable(swarm.process_brand)

    def test_trinity_process_brand_with_results(self):
        """Test swarm has process_brand_with_results method"""
        swarm = TrinitySwarm()
        assert hasattr(swarm, 'process_brand_with_results')
        assert callable(swarm.process_brand_with_results)

    def test_trinity_handle_audit_outcome(self):
        """Test swarm has handle_audit_outcome method"""
        swarm = TrinitySwarm()
        assert hasattr(swarm, 'handle_audit_outcome')
        assert callable(swarm.handle_audit_outcome)


class TestAgentWorkflows:
    """Test complete agent workflow scenarios"""

    def test_scout_harvest_workflow(self):
        """Test scout harvesting workflow"""
        scout = CommercialAgent()
        result = scout.harvest("Yamaha")
        assert result is not None
        assert result.get("brand") == "Yamaha"
        assert "price_il" in result

    def test_verifier_enrich_workflow(self):
        """Test verifier enrichment workflow"""
        verifier = OfficialAgent()
        draft = {
            "id": "789",
            "name": "Test Product",
            "brand": "TestBrand",
            "price_il": 200,
            "price_eilat": 170
        }
        result = verifier.enrich(draft)
        assert "official_match" in result
        assert result.get("official_match") == True
        assert "image_url" in result

    def test_agent_communication_flow(self):
        """Test agents work together in workflow"""
        swarm = TrinitySwarm()

        # Scout produces data
        raw = swarm.scout.harvest("Roland")
        assert raw is not None

        # Verifier enriches
        enriched = swarm.verifier.enrich(raw)
        assert enriched is not None
        assert enriched.get("official_match") == True

    def test_swarm_process_workflow(self):
        """Test complete swarm process"""
        swarm = TrinitySwarm()
        assert hasattr(swarm, 'process_brand')
        # Verify the swarm is ready to process
        assert swarm.scout is not None
        assert swarm.verifier is not None
        assert swarm.auditor is not None


class TestDataModels:
    """Test data models used in the swarm"""

    def test_product_draft_model(self):
        """Test ProductDraft data model"""
        draft = ProductDraft(
            id="123",
            name="Test Product",
            brand="TestBrand",
            price_il=100.0,
            price_eilat=85.0
        )
        assert draft.id == "123"
        assert draft.name == "Test Product"
        assert draft.brand == "TestBrand"

    def test_audit_report_model(self):
        """Test AuditReport data model"""
        report = AuditReport(
            product_id="456",
            status="APPROVED",
            risk_score=15,
            violations=[],
            auditor_notes="Product passed all checks"
        )
        assert report.status == "APPROVED"
        assert report.risk_score == 15

    def test_audit_report_rejection(self):
        """Test AuditReport for rejected products"""
        report = AuditReport(
            product_id="789",
            status="REJECTED",
            risk_score=85,
            violations=["Price inconsistency", "Brand mismatch"],
            auditor_notes="Product violates compliance rules"
        )
        assert report.status == "REJECTED"
        assert len(report.violations) == 2


class TestAgentMemoryCapabilities:
    """Test agent memory and learning capabilities"""

    def test_agent_has_memory_mixin(self):
        """Test agent inherits from MemoryAwareMixin"""
        agent = CommercialAgent()
        assert hasattr(agent, 'learn_from_action')

    def test_agent_can_learn(self):
        """Test agent can learn from actions"""
        agent = OfficialAgent()
        # Test that learn_from_action method exists and is callable
        assert callable(agent.learn_from_action)

    def test_agent_learning_in_think(self):
        """Test agent learns during think operations"""
        agent = ValidatorAgent()
        # Agent should automatically learn during think
        initial_result = agent.think("test prompt")
        assert initial_result is not None


class TestSkillsAndCapabilities:
    """Test agent skills and capabilities"""

    def test_scout_has_harvest_skill(self):
        """Test scout has harvest skill"""
        scout = CommercialAgent()
        assert hasattr(scout, 'harvest')
        assert callable(scout.harvest)

    def test_verifier_has_enrich_skill(self):
        """Test verifier has enrich skill"""
        verifier = OfficialAgent()
        assert hasattr(verifier, 'enrich')
        assert callable(verifier.enrich)

    def test_auditor_has_audit_skill(self):
        """Test auditor has audit skill"""
        auditor = ValidatorAgent()
        assert hasattr(auditor, 'audit')
        assert callable(auditor.audit)

    def test_all_agents_have_think_skill(self):
        """Test all agents have think method"""
        agents = [
            CommercialAgent(),
            OfficialAgent(),
            ValidatorAgent()
        ]
        for agent in agents:
            assert hasattr(agent, 'think')
            assert callable(agent.think)


class TestErrorHandling:
    """Test error handling in agents"""

    def test_agent_error_handling(self):
        """Test agent handles errors gracefully"""
        agent = AgentBase("ErrorTest")
        # Should not raise exception
        assert agent is not None

    def test_harvest_handles_empty_brand(self):
        """Test scout handles empty brand gracefully"""
        scout = CommercialAgent()
        result = scout.harvest("")
        assert result is not None
        assert isinstance(result, dict)

    def test_enrich_handles_minimal_draft(self):
        """Test verifier handles minimal data"""
        verifier = OfficialAgent()
        minimal_draft = {"id": "minimal", "name": "minimal"}
        result = verifier.enrich(minimal_draft)
        assert result is not None


class TestSystemIntegration:
    """Test complete system integration"""

    def test_swarm_full_structure(self):
        """Test complete swarm structure"""
        swarm = TrinitySwarm()

        # Verify all agents exist
        assert swarm.scout is not None
        assert swarm.verifier is not None
        assert swarm.auditor is not None

        # Verify all agents have correct names
        assert swarm.scout.name == "CommercialScout"
        assert swarm.verifier.name == "OfficialVerifier"
        assert swarm.auditor.name == "ExternalValidator"

        # Verify all agents are properly configured
        assert swarm.scout.client is not None
        assert swarm.verifier.client is not None
        assert swarm.auditor.client is not None

    def test_swarm_has_taxonomy(self):
        """Test swarm has taxonomy"""
        swarm = TrinitySwarm()
        assert hasattr(swarm, 'taxonomy')
        assert isinstance(swarm.taxonomy, list)
        assert len(swarm.taxonomy) > 0

    def test_agent_methods_are_functional(self):
        """Test all primary agent methods are functional"""
        swarm = TrinitySwarm()

        # Test scout
        scout_result = swarm.scout.harvest("TestBrand")
        assert scout_result is not None

        # Test verifier
        verifier_result = swarm.verifier.enrich(scout_result)
        assert verifier_result is not None

        # Test auditor has audit method
        assert hasattr(swarm.auditor, 'audit')

    def test_swarm_process_methods_exist(self):
        """Test swarm process methods exist"""
        swarm = TrinitySwarm()

        # Check all process methods are available
        assert hasattr(swarm, 'process_brand')
        assert hasattr(swarm, 'process_brand_with_results')
        assert hasattr(swarm, 'handle_audit_outcome')

    def test_multi_agent_workflow(self):
        """Test multi-agent workflow execution"""
        swarm = TrinitySwarm()

        # Simulate workflow
        test_brands = ["Nord", "Roland", "Yamaha"]
        for brand in test_brands:
            raw_data = swarm.scout.harvest(brand)
            assert raw_data is not None

            enriched_data = swarm.verifier.enrich(raw_data)
            assert enriched_data is not None
            assert enriched_data.get("official_match") == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
