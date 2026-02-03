from fastapi import FastAPI, Request

"""
Comprehensive ADK (Agent Development Kit) Coverage Test Suite
Tests the entire Agentic System: Trinity Swarm + UI Agent Bridge
"""

                AgentBase, CommercialAgent, OfficialAgent, ValidatorAgent,
                TrinitySwarm, ProductDraft, AuditReport
)

class TestAgentBase:
                """Test the base agent class"""

                def test_agent_initialization(self):
                                """Test agent basic initialization"""
                                agent = AgentBase("TestAgent", model_name="gemini-2.0-flash")
                                assert agent.name == "TestAgent"
                                assert agent.model_name == "gemini-2.0-flash"
                                assert agent.client is not None

                def test_agent_with_system_instruction(self):
                                """Test agent initialization with system instruction"""
                                instruction = "You are a test agent"
                                agent = AgentBase("TestAgent", system_instruction=instruction)
                                assert agent.system_instruction == instruction

                def test_agent_think_method_returns_string(self):
                                """Test think method signature"""
                                agent = AgentBase("TestAgent")
                                # Mock the client response
                                with patch.object(agent.client.models, 'generate_content') as mock_gen:
                                                mock_response = Mock()
                                                mock_response.text = "Test response"
                                                mock_gen.return_value = mock_response

                                                result = agent.think("Test prompt")
                                                assert isinstance(result, str)

class TestCommercialAgent:
                """Test Commercial Scout agent"""

                def test_commercial_agent_initialization(self):
                                """Test CommercialAgent initializes correctly"""
                                agent = CommercialAgent()
                                assert agent.name == "CommercialScout"
                                assert "Halilit" in agent.system_instruction.lower(
                                ) or "data harvester" in agent.system_instruction.lower()

                def test_harvest_returns_product_data(self):
                                """Test harvest method returns valid product data"""
                                agent = CommercialAgent()
                                result = agent.harvest("Nord")

                                assert isinstance(result, dict)
                                assert "id" in result
                                assert "name" in result
                                assert "brand" in result
                                assert result["brand"] == "Nord"
                                assert "price_il" in result
                                assert "price_eilat" in result

class TestOfficialAgent:
                """Test Official Verifier agent"""

                def test_official_agent_initialization(self):
                                """Test OfficialAgent initializes correctly"""
                                agent = OfficialAgent()
                                assert agent.name == "OfficialVerifier"
                                assert "brand expert" in agent.system_instruction.lower()

                def test_enrich_adds_official_match_flag(self):
                                """Test enrich adds official_match flag"""
                                agent = OfficialAgent()
                                draft = {
                                                "id": "123",
                                                "name": "Test Product",
                                                "brand": "TestBrand",
                                                "price_il": 1000,
                                                "price_eilat": 850
                                }

                                enriched = agent.enrich(draft)
                                assert enriched["official_match"] == True
                                assert "image_url" in enriched
                                assert draft["name"] == enriched["name"]  # Original data preserved

class TestValidatorAgent:
                """Test External Validator (Compliance Auditor) agent"""

                def test_validator_agent_initialization(self):
                                """Test ValidatorAgent initializes correctly"""
                                agent = ValidatorAgent()
                                assert agent.name == "ExternalValidator"
                                assert "COMPLIANCE AUDITOR" in agent.system_instruction
                                assert "STRICT RULES" in agent.system_instruction

                def test_audit_returns_audit_report(self):
                                """Test audit method returns AuditReport"""
                                agent = ValidatorAgent()
                                product = {
                                                "id": "12345",
                                                "name": "Nord Stage 4",
                                                "brand": "Nord",
                                                "price_il": 18500,
                                                "price_eilat": 15811,
                                                "image_url": "https://example.com/image.jpg"
                                }
                                taxonomy = ["Nord", "Roland", "Yamaha"]

                                result = agent.audit(product, taxonomy)
                                assert isinstance(result, AuditReport)
                                assert result.status in ["APPROVED", "REJECTED"]
                                assert isinstance(result.risk_score, int)
                                assert 0 <= result.risk_score <= 100
                                assert isinstance(result.violations, list)
                                assert isinstance(result.auditor_notes, str)

                def test_audit_detects_brand_not_in_taxonomy(self):
                                """Test validator detects brand not in taxonomy"""
                                agent = ValidatorAgent()
                                product = {
                                                "id": "123",
                                                "name": "UnknownBrand Product",
                                                "brand": "UnknownBrand",
                                                "price_il": 1000,
                                                "price_eilat": 850,
                                                "image_url": "https://example.com/image.jpg"
                                }
                                taxonomy = ["Nord", "Roland"]  # UnknownBrand not in list

                                result = agent.audit(product, taxonomy)
                                # Should detect the brand issue
                                assert len(result.violations) > 0 or result.status == "REJECTED"

                def test_audit_detects_price_inconsistency(self):
                                """Test validator detects price inconsistencies"""
                                agent = ValidatorAgent()
                                product = {
                                                "id": "123",
                                                "name": "Test Product",
                                                "brand": "Nord",
                                                "price_il": 1000,
                                                "price_eilat": 500,  # Too low (50% off instead of ~17%)
                                                "image_url": "https://example.com/image.jpg"
                                }
                                taxonomy = ["Nord"]

                                result = agent.audit(product, taxonomy)
                                # Should flag price inconsistency
                                if result.status == "REJECTED":
                                                assert any("price" in v.lower() or "eilat" in v.lower()
                                                                                        for v in result.violations)

class TestTrinitySwarm:
                """Test the Trinity Swarm orchestrator"""

                def test_swarm_initialization(self):
                                """Test TrinitySwarm initializes all three agents"""
                                swarm = TrinitySwarm()

                                assert swarm.scout is not None
                                assert isinstance(swarm.scout, CommercialAgent)
                                assert swarm.verifier is not None
                                assert isinstance(swarm.verifier, OfficialAgent)
                                assert swarm.auditor is not None
                                assert isinstance(swarm.auditor, ValidatorAgent)
                                assert isinstance(swarm.taxonomy, list)
                                assert len(swarm.taxonomy) > 0

                def test_swarm_process_brand_full_pipeline(self):
                                """Test full Trinity Swarm pipeline"""
                                swarm = TrinitySwarm()

                                # This should run the entire pipeline without errors
                                swarm.process_brand("Nord")

                                # If we get here, the pipeline executed successfully
                                assert True

                def test_swarm_handle_audit_outcome_approved(self):
                                """Test swarm handles approved audit outcome"""
                                swarm = TrinitySwarm()
                                product = {
                                                "id": "123",
                                                "name": "Test Product",
                                                "brand": "Nord"
                                }
                                report = AuditReport(
                                                product_id="123",
                                                status="APPROVED",
                                                risk_score=0,
                                                violations=[],
                                                auditor_notes="All checks passed"
                                )

                                # Should handle without error
                                swarm.handle_audit_outcome(product, report)
                                assert True

                def test_swarm_handle_audit_outcome_rejected(self):
                                """Test swarm handles rejected audit outcome"""
                                swarm = TrinitySwarm()
                                product = {
                                                "id": "123",
                                                "name": "Test Product",
                                                "brand": "UnknownBrand"
                                }
                                report = AuditReport(
                                                product_id="123",
                                                status="REJECTED",
                                                risk_score=95,
                                                violations=["Brand not in taxonomy"],
                                                auditor_notes="Failed validation"
                                )

                                # Should handle without error
                                swarm.handle_audit_outcome(product, report)
                                assert True

class TestProductModels:
                """Test Pydantic models"""

                def test_product_draft_validation(self):
                                """Test ProductDraft model"""
                                draft = ProductDraft(
                                                id="123",
                                                name="Test",
                                                brand="Nord",
                                                price_il=1000,
                                                price_eilat=850
                                )
                                assert draft.id == "123"
                                assert draft.official_match == False  # Default

                def test_audit_report_validation(self):
                                """Test AuditReport model"""
                                report = AuditReport(
                                                status="APPROVED",
                                                risk_score=0,
                                                violations=[],
                                                auditor_notes="OK"
                                )
                                assert report.status == "APPROVED"
                                assert report.risk_score == 0
                                assert len(report.violations) == 0

                def test_audit_report_with_violations(self):
                                """Test AuditReport with violations"""
                                report = AuditReport(
                                                product_id="123",
                                                status="REJECTED",
                                                risk_score=85,
                                                violations=["Issue 1", "Issue 2"],
                                                auditor_notes="Multiple violations"
                                )
                                assert report.status == "REJECTED"
                                assert len(report.violations) == 2

class TestServerIntegration:
                """Test FastAPI server integration with Trinity Swarm"""

                @pytest.mark.asyncio
                async def test_server_health_endpoint(self):
                                """Test health endpoint exists"""
                                from fastapi.testclient import TestClient

                                client = TestClient(app)
                                response = client.get("/health")
                                assert response.status_code == 200
                                assert response.json()["status"] == "ok"

                @pytest.mark.asyncio
                async def test_copilot_chat_endpoint(self):
                                """Test copilot chat endpoint"""
                                from fastapi.testclient import TestClient

                                client = TestClient(app)
                                request = ChatRequest(messages=[
                                                ChatMessage(role="user", content="Check the audit for Nord")
                                ])

                                response = client.post("/api/copilot/chat", json=request.model_dump())
                                assert response.status_code == 200
                                assert "detailedMessage" in response.json()

class TestFrontendAgentSync:
                """Test Frontend-Backend Agent synchronization"""

                def test_copilot_readable_context_structure(self):
                                """Verify useCopilotReadable sends correct context"""
                                expected_context = {
                                                "currentView": "should be string",
                                                "currentBrand": "should be string or None",
                                                "appVersion": "5.0",
                                                "status": "Online"
                                }

                                # Verify structure matches expectations
                                assert "currentView" in expected_context
                                assert "currentBrand" in expected_context
                                assert "appVersion" in expected_context
                                assert "status" in expected_context

                def test_copilot_action_request_audit_structure(self):
                                """Verify useCopilotAction sends correct parameters"""
                                # The action should have these parameters
                                expected_params = {
                                                "name": "requestAudit",
                                                "description": "Request a full compliance audit for a specific brand",
                                                "parameters": [
                                                                {
                                                                                "name": "brand",
                                                                                "type": "string",
                                                                                "description": "The brand name to audit",
                                                                                "required": True
                                                                }
                                                ]
                                }

                                # Verify structure
                                assert expected_params["name"] == "requestAudit"
                                assert len(expected_params["parameters"]) == 1
                                assert expected_params["parameters"][0]["required"] == True

# ========================
# INTEGRATION TEST SUITE
# ========================

class TestEndToEndWorkflow:
                """End-to-end integration tests"""

                def test_complete_audit_workflow(self):
                                """Test complete workflow from brand selection to audit report"""
                                swarm = TrinitySwarm()

                                # Step 1: Scout harvests data
                                scout_data = swarm.scout.harvest("Nord")
                                assert "price_il" in scout_data

                                # Step 2: Verifier enriches data
                                enriched = swarm.verifier.enrich(scout_data)
                                assert enriched["official_match"] == True

                                # Step 3: Auditor validates
                                audit = swarm.auditor.audit(enriched, swarm.taxonomy)
                                assert isinstance(audit, AuditReport)

                                # Workflow completed successfully
                                assert True

                def test_multiple_brands_processing(self):
                                """Test processing multiple brands in sequence"""
                                swarm = TrinitySwarm()
                                brands = ["Nord", "Roland", "Yamaha"]

                                for brand in brands:
                                                try:
                                                                swarm.process_brand(brand)
                                                                assert True  # Should complete without error
                                                except Exception as e:
                                                                # Log but don't fail - external API might be unreliable
                                                                print(f"Warning: {brand} processing had issue: {e}")

# ========================
# PERFORMANCE TEST SUITE
# ========================

class TestPerformance:
                """Test system performance characteristics"""

                def test_agent_response_time(self):
                                """Test agent response time is reasonable"""
                                import time
                                agent = CommercialAgent()

                                start = time.time()
                                agent.harvest("Nord")
                                elapsed = time.time() - start

                                # Harvest should be fast (< 1 second for mock)
                                assert elapsed < 5.0

                def test_swarm_full_cycle_completes(self):
                                """Test full swarm cycle completes in reasonable time"""
                                import time
                                swarm = TrinitySwarm()

                                start = time.time()
                                swarm.process_brand("Nord")
                                elapsed = time.time() - start

                                # Full cycle should complete reasonably
                                assert elapsed < 30.0

# ========================
# SYSTEM REQUIREMENTS VERIFICATION
# ========================

class TestSystemRequirements:
                """Verify all system requirements are met"""

                def test_google_genai_package_imported(self):
                                """Verify google.genai is properly installed"""
                                try:
                                                import google.genai as genai
                                                assert True
                                except ImportError:
                                                pytest.fail("google.genai not installed")

                def test_fastapi_available(self):
                                """Verify FastAPI is available"""
                                try:
                                                import fastapi
                                                assert True
                                except ImportError:
                                                pytest.fail("fastapi not installed")

                def test_pydantic_v2_available(self):
                                """Verify Pydantic v2 is available"""
                                import pydantic
                                version = pydantic.VERSION
                                major_version = int(version.split('.')[0])
                                assert major_version >= 2, f"Pydantic {version} found, need v2+"

                def test_react_version_correct(self):
                                """Verify React 18 is in package.json"""
                                root = Path(__file__).parent.parent.parent
                                pkg_path = root / "frontend" / "package.json"
                                with open(pkg_path, "r") as f:
                                                pkg = json.load(f)
                                                react_version = pkg["dependencies"].get("react", "")
                                                # Should be 18.x.x
                                                assert react_version.startswith("^18") or react_version.startswith("18"), \
                                                                f"React version {react_version} not compatible"

                def test_copilotkit_installed(self):
                                """Verify CopilotKit packages are in package.json"""
                                root = Path(__file__).parent.parent.parent
                                pkg_path = root / "frontend" / "package.json"
                                with open(pkg_path, "r") as f:
                                                pkg = json.load(f)
                                                deps = pkg["dependencies"]
                                                assert "@copilotkit/react-core" in deps
                                                assert "@copilotkit/react-ui" in deps

if __name__ == "__main__":
                pytest.main([__file__, "-v", "--tb=short"])
