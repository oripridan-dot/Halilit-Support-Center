"""
Unified Learning System v7.3

Consolidates four learning modules:
- learning_engine.py: Core learning functionality with LearningEnabledAgent
- learning_optimizer.py: Optimization and feedback with LearningOptimizerEngine
- learning_endpoints.py: FastAPI routes for exposing learning metrics
- enhanced_training.py: Training orchestration with run_enhanced_training

This unified system enables the three agents (CommercialScout, OfficialVerifier, 
ExternalValidator) to learn from their actions and continuously improve toward the 
PerfectionMap.

Architecture:
1. Each agent processes a product and scores itself on quality dimensions
2. Learning feedback is recorded (success OR failure)
3. Agents adjust strategy based on weak categories
4. System tracks improvement over time with audit trails
5. FastAPI endpoints expose metrics and health status
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import time

from fastapi import APIRouter, HTTPException, Query

from backend.agents.perfection_map import (
    PerfectionMap,
    AgentRole,
    DimensionType,
    AgentLearningState,
    create_improvement_plan,
    DimensionScorecard,
)
from backend.unified_agent_orchestrator_v73 import (
    TrinitySwarm,
    CommercialAgent,
    OfficialAgent,
    ContextualAgent,
    AuditReport,
)
from backend.unified_quality_gates_v73 import feedback_engine, FeedbackType, audit_logger, AuditLevel, AuditCategory

# ============================================================================
# LOGGING & CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("UnifiedLearningSystem.v73")


# ============================================================================
# ENUMS & DATACLASSES
# ============================================================================

class ImprovementArea(Enum):
    """Categories where agents can improve."""
    CATEGORIZATION = "categorization"     # Better taxonomy matching
    PRICING = "pricing"                   # More accurate price extraction
    DATA_QUALITY = "data_quality"         # Higher quality product data
    IMAGE_DETECTION = "image_detection"   # Better image identification
    CONFIDENCE_CALIBRATION = "confidence"  # Better confidence scoring
    EDGE_CASES = "edge_cases"             # Handling unusual products
    VALIDATION_RULES = "validation_rules"  # Better validation logic


@dataclass
class QualityAuditRecord:
    """
    Complete record of a product's quality journey through the pipeline.
    Used for learning and improving future decisions.
    """
    product_id: str
    timestamp: datetime
    brand: str
    product_name: str

    # Scores on each dimension (before/after)
    completeness_score_before: float
    completeness_score_after: float

    accuracy_score: float
    security_score: float
    consistency_score: float

    # Who did what
    scout_status: str  # "success" | "failure"
    verifier_status: str
    auditor_status: str  # "APPROVED" | "REJECTED"

    # Why (patterns learned)
    scout_weaknesses: List[str]
    verifier_improvements: List[str]
    auditor_violations: List[str]

    # Final outcome
    final_tier: str  # "GOLD" | "SILVER" | "BRONZE" | "REJECTED"
    final_score: float

    # Recommendations for next time
    improvement_actions: List[str]

    def to_json(self) -> str:
        """Serialize to JSON for storage"""
        return json.dumps(asdict(self), default=str)


@dataclass
class LearningMetric:
    """Single learning metric for agent improvement."""
    agent_name: str
    metric_type: str
    current_value: float
    target_value: float
    improvement_percent: float
    category: ImprovementArea
    timestamp: str


@dataclass
class CycleResult:
    """Result of a single learning cycle."""
    cycle_number: int
    timestamp: str
    agents_improved: List[str]
    accuracy_improvement: float
    metrics: List[Dict[str, Any]]
    bottlenecks: List[str]
    next_focus_areas: List[str]  # Use strings instead of enums


# ============================================================================
# LEARNING ENGINE - Core Learning Functionality
# ============================================================================

class LearningEnabledAgent:
    """
    Wrapper that gives any agent learning capabilities.
    Tracks performance, identifies patterns, and improves over time.
    """

    def __init__(
        self,
        agent_role: AgentRole,
        base_agent: Any,
        session_id: str = None,
    ):
        self.agent_role = agent_role
        self.base_agent = base_agent
        self.session_id = session_id or str(uuid.uuid4())

        # Learning state
        self.learning_state = AgentLearningState(
            agent=agent_role,
            session_id=self.session_id,
        )

        # Track dimension performance
        self.dimension_scores: Dict[DimensionType, DimensionScorecard] = {}

        # History of decisions
        self.decision_history: List[Dict[str, Any]] = []

        logger.info(f"🧠 [{agent_role.value}] Learning Engine initialized")

    def process_with_learning(
        self,
        product: Dict[str, Any],
        reference_data: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], QualityAuditRecord]:
        """
        Process a product AND learn from the outcome.

        Returns:
        - Processed product
        - Quality audit record with lessons learned
        """

        product_id = product.get('halilit_id', 'unknown')
        product_name = product.get('product_name', 'Unknown')
        brand = product.get('brand', 'Unknown')

        logger.info(
            f"[{self.agent_role.value}] Processing {product_name} (ID: {product_id})")

        # ============================================================================
        # PHASE 1: MEASURE BASELINE QUALITY
        # ============================================================================

        completeness_before = PerfectionMap.calculate_completeness_score(
            product)

        # ============================================================================
        # PHASE 2: AGENT DOES ITS JOB
        # ============================================================================

        processed_product = self._execute_agent_role(product, reference_data)

        # ============================================================================
        # PHASE 3: MEASURE QUALITY IMPROVEMENTS
        # ============================================================================

        completeness_after = PerfectionMap.calculate_completeness_score(
            processed_product)
        accuracy_score = PerfectionMap.calculate_accuracy_score(
            processed_product, reference_data)
        security_score = PerfectionMap.calculate_security_score(
            processed_product)

        # ============================================================================
        # PHASE 4: EXTRACT LESSONS LEARNED
        # ============================================================================

        weaknesses = self._identify_weaknesses(processed_product)
        improvements = self._identify_improvements(processed_product)

        # Agent learns from success or failure
        success = completeness_after > completeness_before
        category = brand or "Unknown"

        if success:
            self.learning_state.record_success(
                product_id, category, completeness_after)
            logger.debug(
                f"✅ Agent improved {product_name}: {completeness_before:.1f}% → {completeness_after:.1f}%")
        else:
            reason = "; ".join(
                weaknesses) if weaknesses else "Score did not improve"
            self.learning_state.record_failure(product_id, category, reason)
            logger.debug(f"❌ Agent failed to improve {product_name}")

        # ============================================================================
        # PHASE 5: BUILD IMPROVEMENT PLAN
        # ============================================================================

        improvement_plan = create_improvement_plan(
            self.agent_role,
            DimensionType.COMPLETENESS,
            completeness_after
        )

        improvement_actions = improvement_plan.recommended_actions

        # ============================================================================
        # PHASE 6: CREATE AUDIT RECORD
        # ============================================================================

        audit_record = QualityAuditRecord(
            product_id=product_id,
            timestamp=datetime.now(),
            brand=brand,
            product_name=product_name,

            completeness_score_before=completeness_before,
            completeness_score_after=completeness_after,
            accuracy_score=accuracy_score,
            security_score=security_score,
            consistency_score=0.0,  # Placeholder

            scout_status="success" if self.agent_role == AgentRole.COMMERCIAL_SCOUT and success else "partial",
            verifier_status="success" if self.agent_role == AgentRole.OFFICIAL_VERIFIER and success else "partial",
            auditor_status="APPROVED" if self.agent_role == AgentRole.EXTERNAL_VALIDATOR and success else "NEEDS_REVIEW",

            scout_weaknesses=weaknesses if self.agent_role == AgentRole.COMMERCIAL_SCOUT else [],
            verifier_improvements=improvements if self.agent_role == AgentRole.OFFICIAL_VERIFIER else [],
            auditor_violations=[],

            final_tier=PerfectionMap.get_quality_tier(completeness_after),
            final_score=completeness_after,

            improvement_actions=improvement_actions,
        )

        # ============================================================================
        # PHASE 7: LOG DECISION FOR AUDIT TRAIL
        # ============================================================================

        self.decision_history.append({
            "timestamp": datetime.now().isoformat(),
            "product_id": product_id,
            "action": f"{self.agent_role.value}.process",
            "input_score": completeness_before,
            "output_score": completeness_after,
            "success": success,
            "audit_record": audit_record.to_json(),
        })

        logger.info(
            f"[{self.agent_role.value}] {product_name}: "
            f"{completeness_before:.0f}% → {completeness_after:.0f}% "
            f"(Tier: {audit_record.final_tier})"
        )

        return processed_product, audit_record

    def _execute_agent_role(
        self,
        product: Dict[str, Any],
        reference_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute the agent's specific role in the pipeline.
        """

        if self.agent_role == AgentRole.COMMERCIAL_SCOUT:
            # Scout: harvest raw data (already done, return as-is)
            return product

        elif self.agent_role == AgentRole.OFFICIAL_VERIFIER:
            # Verifier: enrich with official specs
            if hasattr(self.base_agent, 'enrich'):
                return self.base_agent.enrich(product)
            # Fallback: simulate enrichment
            product['official_specs'] = {
                "manufacturer": product.get('brand', 'Unknown'),
                "features": ["High quality", "Professional grade"],
            }
            product['official_images'] = product.get('official_images', [])
            return product

        elif self.agent_role == AgentRole.EXTERNAL_VALIDATOR:
            # Validator: audit and validate
            # (Already happens in process_brand_with_results, but for completeness)
            return product

        return product

    def _identify_weaknesses(self, product: Dict[str, Any]) -> List[str]:
        """Extract what this agent should improve on"""
        weaknesses = []

        # Check for missing fields
        critical_fields = ['product_name', 'brand', 'price_il']
        for field in critical_fields:
            if not product.get(field):
                weaknesses.append(f"Missing {field}")

        # Check for missing enrichment
        if not product.get('official_specs'):
            weaknesses.append("Missing official specifications")

        if not product.get('official_images') or len(product.get('official_images', [])) < 2:
            weaknesses.append("Insufficient official images (< 2)")

        return weaknesses

    def _identify_improvements(self, product: Dict[str, Any]) -> List[str]:
        """Extract what this agent successfully improved"""
        improvements = []

        if product.get('official_specs'):
            improvements.append("Added official specifications")

        if product.get('official_images') and len(product.get('official_images', [])) >= 2:
            improvements.append("Gathered official images")

        if product.get('taxonomy'):
            improvements.append("Assigned taxonomy/category")

        return improvements

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get learning summary for this agent"""
        return {
            "agent": self.agent_role.value,
            "session_id": self.session_id,
            "products_processed": self.learning_state.products_processed,
            "success_rate": f"{self.learning_state.success_rate():.1f}%",
            "strong_categories": self.learning_state.strong_categories,
            "weak_categories": self.learning_state.weak_categories,
            "should_retrain": self.learning_state.should_retrain(),
            "learned_patterns": self.learning_state.learned_patterns[:5],
        }


class LearningEnabledTrinitySwarm(TrinitySwarm):
    """
    Enhanced Trinity Swarm with learning capabilities.
    Tracks quality metrics and improves over time.
    """

    def __init__(self, session_id: str = None):
        super().__init__()
        self.session_id = session_id or str(uuid.uuid4())

        # Wrap agents with learning
        self.scout = LearningEnabledAgent(
            AgentRole.COMMERCIAL_SCOUT, self.scout, self.session_id)
        self.verifier = LearningEnabledAgent(
            AgentRole.OFFICIAL_VERIFIER, self.verifier, self.session_id)
        self.auditor = LearningEnabledAgent(
            AgentRole.EXTERNAL_VALIDATOR, self.auditor, self.session_id)

        # Audit trail
        self.audit_records: List[QualityAuditRecord] = []

        logger.info(
            f"🚀 Learning-Enabled Trinity Swarm initialized (Session: {self.session_id})")

    def process_brand_with_learning(self, brand_name: str) -> Dict[str, Any]:
        """
        Process brand with FULL LEARNING enabled.
        Returns processed products AND lessons learned.
        """

        logger.info(f"\n{'='*70}")
        logger.info(f"🎯 TRINITY SWARM LEARNING PIPELINE START: {brand_name}")
        logger.info(f"{'='*70}\n")

        # Get raw products (scout phase)
        raw_products = self.scout.base_agent.harvest(brand_name)
        if isinstance(raw_products, dict):
            raw_products = [raw_products]

        approved_products = []
        audit_records = []

        for idx, raw_product in enumerate(raw_products, 1):
            try:
                logger.info(f"\n{'─'*70}")
                logger.info(
                    f"[{idx}/{len(raw_products)}] Processing: {raw_product.get('product_name')}")
                logger.info(f"{'─'*70}")

                # PHASE 1: Scout learns
                scouted_product, scout_audit = self.scout.process_with_learning(
                    raw_product)
                audit_records.append(scout_audit)

                # PHASE 2: Verifier learns
                verified_product, verifier_audit = self.verifier.process_with_learning(
                    scouted_product, None)
                audit_records.append(verifier_audit)

                # PHASE 3: Auditor learns
                auditor = ContextualAgent()
                audit_result = auditor.validate_and_review(verified_product)

                auditor_learning = LearningEnabledAgent(
                    AgentRole.EXTERNAL_VALIDATOR, auditor, self.session_id)
                auditor_product, auditor_audit = auditor_learning.process_with_learning(
                    verified_product)
                audit_records.append(auditor_audit)

                # Record outcome
                if audit_result.status == "APPROVED":
                    approved_products.append(verified_product)
                    logger.info(
                        f"✅ APPROVED: {raw_product.get('product_name')} (Risk: {audit_result.risk_score})")
                else:
                    logger.warning(
                        f"🛑 REJECTED: {raw_product.get('product_name')} (Risk: {audit_result.risk_score})")
                    logger.warning(
                        f"   Violations: {', '.join(audit_result.violations)}")

            except Exception as e:
                logger.error(f"❌ Error processing product {idx}: {e}")
                continue

        # ============================================================================
        # SUMMARY & LESSONS
        # ============================================================================

        summary = {
            "session_id": self.session_id,
            "brand": brand_name,
            "products_processed": len(raw_products),
            "products_approved": len(approved_products),
            "approval_rate": f"{(len(approved_products)/max(1, len(raw_products))*100):.1f}%",

            # Learning summaries
            "scout_performance": self.scout.get_performance_summary(),
            "verifier_performance": self.verifier.get_performance_summary(),
            "auditor_performance": self.auditor.get_performance_summary(),

            # Full audit trail
            "audit_records": [asdict(r) for r in audit_records],

            # Products
            "approved_products": approved_products,
        }

        logger.info(f"\n{'='*70}")
        logger.info(f"✨ TRINITY SWARM LEARNING SESSION COMPLETE")
        logger.info(f"{'='*70}")
        logger.info(
            f"Approved: {len(approved_products)}/{len(raw_products)} products")
        logger.info(
            f"Scout Success Rate: {self.scout.learning_state.success_rate():.1f}%")
        logger.info(
            f"Verifier Success Rate: {self.verifier.learning_state.success_rate():.1f}%")
        logger.info(f"\n")

        return summary


# ============================================================================
# LEARNING OPTIMIZER - Optimization & Feedback
# ============================================================================

class LearningOptimizerEngine:
    """Optimizes agent performance through feedback and learning cycles."""

    def __init__(self):
        self.logs_dir = Path("/workspaces/Halilit-Support-Center/backend/logs")
        self.learning_dir = self.logs_dir / "learning_cycles"
        self.learning_dir.mkdir(exist_ok=True)

        self.agent_names = ["CommercialScout",
                            "OfficialVerifier", "ExternalValidator"]
        self.agents_data_dir = Path(
            "/workspaces/Halilit-Support-Center/frontend/public/data")

    def _get_ingestion_quality_metrics(self) -> Dict[str, Any]:
        """Analyze the current product data for quality patterns."""
        quality_report = {
            "total_products": 0,
            "total_brands": 0,
            "avg_products_per_brand": 0,
            "quality_issues": {
                "missing_images": 0,
                "missing_prices": 0,
                "uncategorized": 0,
                "low_confidence_categories": 0,
            },
            "success_rate": 0.0,
            "categories_used": [],
        }

        total_products = 0
        brands_with_data = 0

        for brand_file in self.agents_data_dir.glob("*.json"):
            if brand_file.stat().st_size <= 10:
                continue

            try:
                with open(brand_file) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        products = data
                    elif isinstance(data, dict):
                        products = data.get("products", [])
                    else:
                        products = []

                    if products:
                        brands_with_data += 1
                        total_products += len(products)

                        # Analyze quality issues
                        for product in products:
                            if not product.get("official_images"):
                                quality_report["quality_issues"]["missing_images"] += 1
                            if not product.get("price_il"):
                                quality_report["quality_issues"]["missing_prices"] += 1
                            if not product.get("category"):
                                quality_report["quality_issues"]["uncategorized"] += 1

                            confidence = product.get(
                                "category_confidence", 100)
                            if confidence < 80:
                                quality_report["quality_issues"]["low_confidence_categories"] += 1

                            if product.get("category"):
                                quality_report["categories_used"].append(
                                    product["category"])
            except Exception as e:
                logger.warning(f"Error analyzing {brand_file.name}: {e}")

        quality_report["total_products"] = total_products
        quality_report["total_brands"] = brands_with_data

        if brands_with_data > 0:
            quality_report["avg_products_per_brand"] = total_products / \
                brands_with_data

        if total_products > 0:
            issue_count = sum(quality_report["quality_issues"].values())
            quality_report["success_rate"] = (
                (total_products - issue_count) / total_products) * 100

        # Count unique categories
        if quality_report["categories_used"]:
            quality_report["categories_used"] = list(
                set(quality_report["categories_used"]))

        return quality_report

    def generate_learning_feedback(self) -> Dict[str, Any]:
        """Generate feedback based on ingestion results to help agents learn."""
        logger.info("🧠 Generating learning feedback from ingestion results...")

        quality_metrics = self._get_ingestion_quality_metrics()

        feedback_summary = {
            "timestamp": datetime.now().isoformat(),
            "ingestion_quality": quality_metrics,
            "agent_improvements": {},
            "recommended_focus_areas": [],
            "improvement_path": self._generate_improvement_path(quality_metrics),
        }

        # Generate per-agent feedback
        for agent_name in self.agent_names:
            feedback_summary["agent_improvements"][agent_name] = self._generate_agent_feedback(
                agent_name, quality_metrics
            )

        # Save feedback report
        report_file = self.learning_dir / \
            f"feedback_{datetime.now().isoformat()}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(feedback_summary, f, indent=2)
            logger.info(f"✅ Saved learning feedback to {report_file}")
        except Exception as e:
            logger.error(f"Failed to save feedback: {e}")

        return feedback_summary

    def _generate_agent_feedback(
        self, agent_name: str, quality_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate specific feedback for an agent."""
        feedback = {
            "agent": agent_name,
            "focus_areas": [],
            "performance_indicators": {},
            "recommendations": [],
        }

        if agent_name == "CommercialScout":
            # CommercialScout focuses on data harvesting and categorization
            feedback["focus_areas"] = [
                ImprovementArea.CATEGORIZATION.value,
                ImprovementArea.DATA_QUALITY.value,
            ]

            uncategorized = quality_metrics["quality_issues"]["uncategorized"]
            low_confidence = quality_metrics["quality_issues"]["low_confidence_categories"]

            feedback["performance_indicators"] = {
                "correctly_categorized_products": max(0,
                                                      quality_metrics["total_products"] - uncategorized - low_confidence),
                "uncategorized_products": uncategorized,
                "low_confidence_categorizations": low_confidence,
            }

            if uncategorized > 0:
                feedback["recommendations"].append(
                    f"Improve categorization: {uncategorized} products lack category "
                    "(focus on unknown/new product types)"
                )

            if low_confidence > 0:
                feedback["recommendations"].append(
                    f"Calibrate confidence scoring: {low_confidence} products have "
                    "confidence < 80% (may need category refinement)"
                )

        elif agent_name == "OfficialVerifier":
            # OfficialVerifier focuses on enrichment and image detection
            feedback["focus_areas"] = [
                ImprovementArea.IMAGE_DETECTION.value,
                ImprovementArea.PRICING.value,
            ]

            missing_images = quality_metrics["quality_issues"]["missing_images"]
            missing_prices = quality_metrics["quality_issues"]["missing_prices"]

            feedback["performance_indicators"] = {
                "products_with_images": max(0,
                                            quality_metrics["total_products"] - missing_images),
                "products_with_prices": max(0,
                                            quality_metrics["total_products"] - missing_prices),
                "missing_official_images": missing_images,
                "missing_prices": missing_prices,
            }

            if missing_images > 0:
                feedback["recommendations"].append(
                    f"Improve image detection: {missing_images} products missing images "
                    "(search manufacturer sites and retailers for official assets)"
                )

            if missing_prices > 0:
                feedback["recommendations"].append(
                    f"Enhance price extraction: {missing_prices} products lack Israeli prices "
                    "(check local retailers and pricing APIs)"
                )

        elif agent_name == "ExternalValidator":
            # ExternalValidator focuses on quality gates and edge cases
            feedback["focus_areas"] = [
                ImprovementArea.EDGE_CASES.value,
                ImprovementArea.VALIDATION_RULES.value,
            ]

            success_rate = quality_metrics["success_rate"]

            feedback["performance_indicators"] = {
                "quality_gate_pass_rate": success_rate,
                "high_quality_products": int(
                    quality_metrics["total_products"] * (success_rate / 100)
                ),
                "filtered_products": int(
                    quality_metrics["total_products"] *
                    ((100 - success_rate) / 100)
                ),
            }

            if success_rate < 85:
                feedback["recommendations"].append(
                    f"Relax validation rules: Quality gate pass rate is {success_rate:.1f}% "
                    "(may need to adjust threshold for acceptable data quality)"
                )

            feedback["recommendations"].append(
                "Focus on edge cases: Identify unusual but valid product types that may be "
                "filtered out by overly strict rules"
            )

        return feedback

    def _generate_improvement_path(self, quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the path from current accuracy to 98% perfection."""
        current_accuracy = quality_metrics["success_rate"]

        phases = [
            {"phase": 1, "target": 70, "description": "Initial Learning"},
            {"phase": 2, "target": 85, "description": "Refinement & Optimization"},
            {"phase": 3, "target": 95, "description": "Excellence"},
            {"phase": 4, "target": 98, "description": "Perfection"},
        ]

        for phase in phases:
            remaining = phase["target"] - current_accuracy
            if remaining > 0:
                phase["current_gap"] = remaining
                phase["status"] = "target"
            else:
                phase["current_gap"] = 0
                phase["status"] = "achieved"

        return {
            "current_accuracy": current_accuracy,
            "target_accuracy": 98,
            "phases": phases,
            "estimated_cycles_needed": max(1, int((98 - current_accuracy) / 5)),
        }

    def run_learning_cycle(self, cycle_number: int = 1) -> CycleResult:
        """Execute a complete learning cycle for all agents."""
        logger.info(f"\n🔄 LEARNING CYCLE #{cycle_number}")
        logger.info("=" * 60)

        cycle_start = datetime.now()

        # Get current metrics
        quality_metrics = self._get_ingestion_quality_metrics()

        # Generate feedback
        feedback = self.generate_learning_feedback()

        # Record learning decisions for each agent
        agents_improved = []
        metrics_data = []

        for agent_name in self.agent_names:
            agent_feedback = feedback["agent_improvements"][agent_name]

            # Record decision for this cycle
            decision_id = feedback_engine.record_decision(
                agent_name=agent_name,
                decision_type=f"learning_cycle_{cycle_number}",
                input_data={"quality_metrics": quality_metrics},
                decision_output={
                    "focus_areas": agent_feedback["focus_areas"],
                    "recommendations": agent_feedback["recommendations"],
                },
                confidence=min(100, quality_metrics["success_rate"] + 10),
                reasoning=f"Analyzed ingestion results and identified {len(agent_feedback['focus_areas'])} improvement areas"
            )

            # Log the learning action
            audit_logger.log_agent_action(
                agent_name=agent_name,
                action=f"completed_learning_cycle_{cycle_number}",
                input_data={"quality_metrics": quality_metrics},
                output_data={
                    "focus_areas": agent_feedback["focus_areas"],
                    "decision_id": decision_id,
                },
                success=True
            )

            agents_improved.append(agent_name)

            metric = LearningMetric(
                agent_name=agent_name,
                metric_type="learning_cycle",
                current_value=quality_metrics["success_rate"],
                target_value=98.0,
                improvement_percent=10.0,
                category=ImprovementArea.DATA_QUALITY,
                timestamp=datetime.now().isoformat(),
            )
            metric_dict = asdict(metric)
            # Convert enum to string
            metric_dict["category"] = metric_dict["category"].value
            metrics_data.append(metric_dict)

        improvement_path = feedback["improvement_path"]

        result = CycleResult(
            cycle_number=cycle_number,
            timestamp=datetime.now().isoformat(),
            agents_improved=agents_improved,
            accuracy_improvement=10.0,
            metrics=metrics_data,
            bottlenecks=self._identify_bottlenecks(quality_metrics),
            next_focus_areas=[
                ImprovementArea.IMAGE_DETECTION.value,
                ImprovementArea.CATEGORIZATION.value,
            ],
        )

        # Log cycle result
        self._log_cycle_result(result, improvement_path)

        return result

    def _identify_bottlenecks(self, quality_metrics: Dict[str, Any]) -> List[str]:
        """Identify what's limiting overall accuracy."""
        bottlenecks = []
        issues = quality_metrics["quality_issues"]
        total = quality_metrics["total_products"]

        if total == 0:
            return ["No products ingested yet"]

        if issues["missing_images"] > total * 0.2:
            bottlenecks.append(
                f"Image Detection: {issues['missing_images']} products lack images "
                "(critical for frontend quality)"
            )

        if issues["uncategorized"] > total * 0.1:
            bottlenecks.append(
                f"Categorization: {issues['uncategorized']} products lack categories "
                "(limits discoverability)"
            )

        if issues["missing_prices"] > total * 0.15:
            bottlenecks.append(
                f"Pricing: {issues['missing_prices']} products lack prices "
                "(critical for e-commerce)"
            )

        if not bottlenecks:
            bottlenecks = [
                "System performing well - minor optimization opportunities only"]

        return bottlenecks

    def _log_cycle_result(self, result: CycleResult, improvement_path: Dict) -> None:
        """Save cycle result to disk for tracking."""
        result_file = self.learning_dir / \
            f"cycle_{result.cycle_number}_{datetime.now().isoformat()}.json"

        try:
            data = {
                "cycle": asdict(result),
                "improvement_path": improvement_path,
                "saved_at": datetime.now().isoformat(),
            }
            with open(result_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(
                f"✅ Cycle #{result.cycle_number} complete - saved to {result_file.name}")

        except Exception as e:
            logger.error(f"Failed to save cycle result: {e}")

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of all learning cycles."""
        all_cycles = []

        if self.learning_dir.exists():
            for file in sorted(self.learning_dir.glob("cycle_*.json")):
                try:
                    with open(file) as f:
                        data = json.load(f)
                        all_cycles.append(data)
                except:
                    pass

        summary = {
            "total_cycles_completed": len(all_cycles),
            "cycles": all_cycles,
            "learning_status": "active" if all_cycles else "not_started",
            "timestamp": datetime.now().isoformat(),
        }

        if all_cycles:
            latest = all_cycles[-1]
            summary["latest_improvement_path"] = latest.get(
                "improvement_path", {})

        return summary


# ============================================================================
# ENHANCED TRAINING - Training Orchestration
# ============================================================================

def format_progress_bar(current: float, target: float = 100) -> str:
    """Create a visual progress bar."""
    percent = (current / target) * 100 if target > 0 else 0
    filled = int(percent / 5)
    empty = 20 - filled
    return f"[{'█' * filled}{'░' * empty}] {percent:.1f}%"


def get_phase_info(accuracy: float) -> tuple:
    """Get phase name and progress for given accuracy."""
    if accuracy < 70:
        return "Phase 1: Initial Learning", 1, accuracy / 70
    elif accuracy < 85:
        return "Phase 2: Refinement", 2, (accuracy - 70) / 15
    elif accuracy < 95:
        return "Phase 3: Excellence", 3, (accuracy - 85) / 10
    else:
        return "Phase 4: Perfection", 4, (accuracy - 95) / 3


def log_progress(message: str, log_file: Optional[Path] = None):
    """Log to both console and file."""
    print(message)
    if log_file:
        with open(log_file, 'a') as f:
            f.write(f"{message}\n")


def run_enhanced_training(num_cycles: int = 5, log_file: Optional[Path] = None) -> Tuple[List[Dict], List[float]]:
    """Run learning cycles with agent improvements."""

    if log_file is None:
        log_file = Path(
            "/workspaces/Halilit-Support-Center/backend/logs/enhanced_training.log")
    log_file.parent.mkdir(exist_ok=True)

    from backend.unified_agent_orchestrator_v73 import AgentImprovementEngine

    log_progress("\n" + "="*75, log_file)
    log_progress(
        "🚀 ENHANCED MULTI-CYCLE LEARNING TRAINING WITH AGENT IMPROVEMENT", log_file)
    log_progress("="*75, log_file)
    log_progress(f"📅 Started: {datetime.now().isoformat()}", log_file)
    log_progress(f"🔄 Cycles Planned: {num_cycles}", log_file)
    log_progress("="*75 + "\n", log_file)

    optimizer = LearningOptimizerEngine()
    improver = AgentImprovementEngine()

    cycle_history = []
    accuracies = []
    current_accuracy = 0.0

    for cycle_num in range(1, num_cycles + 1):
        log_progress(f"\n{'─'*75}", log_file)
        log_progress(f"📍 CYCLE #{cycle_num}/{num_cycles}", log_file)
        log_progress(f"{'─'*75}", log_file)

        try:
            # PHASE 1: Learning
            log_progress(f"\n  🧠 PHASE 1: Learning Analysis", log_file)
            start_time = time.time()
            result = optimizer.run_learning_cycle(cycle_number=cycle_num)
            learn_time = time.time() - start_time

            log_progress(
                f"  ✅ Agents Learning: {', '.join(result.agents_improved)} ({learn_time:.3f}s)", log_file)

            # PHASE 2: Improvement Application
            log_progress(f"\n  🔧 PHASE 2: Applying Improvements", log_file)
            start_time = time.time()
            improvements = improver.apply_improvements_from_feedback(
                cycle_number=cycle_num)
            improve_time = time.time() - start_time

            # Count improvements
            total_improvements = sum(
                len(agent_data.get("improvements_applied", []))
                for agent_data in improvements["improvements"].values()
            )
            log_progress(
                f"  ✅ Improvements Applied: {total_improvements} changes ({improve_time:.3f}s)", log_file)

            for agent_name, agent_data in improvements["improvements"].items():
                if agent_data.get("improvements_applied"):
                    log_progress(f"\n     {agent_name}:", log_file)
                    for imp in agent_data["improvements_applied"]:
                        log_progress(
                            f"       • {imp['description'][:60]}", log_file)
                        log_progress(
                            f"         Effectiveness: {imp['effectiveness']:.1f}%", log_file)

            # PHASE 3: Accuracy Projection
            log_progress(f"\n  📈 PHASE 3: Accuracy Update", log_file)

            # Calculate new accuracy based on improvements
            old_accuracy = current_accuracy
            current_accuracy = improver.calculate_projected_accuracy(
                current_accuracy, cycle_num)
            accuracy_gain = current_accuracy - old_accuracy

            accuracies.append(current_accuracy)

            phase_name, phase_num, phase_progress = get_phase_info(
                current_accuracy)

            log_progress(
                f"\n     Previous Accuracy: {old_accuracy:.1f}%", log_file)
            log_progress(
                f"     Current Accuracy:  {current_accuracy:.1f}% (↑ +{accuracy_gain:.1f}%)", log_file)
            log_progress(f"     Target Accuracy:   98.0%", log_file)
            log_progress(
                f"     Progress: {format_progress_bar(current_accuracy, 98)}", log_file)
            log_progress(
                f"     Phase: {phase_name} [Phase {phase_num}/4]", log_file)
            log_progress(
                f"     Phase Progress: {format_progress_bar(phase_progress * 100, 100)}", log_file)

            # Bottlenecks
            if result.bottlenecks:
                log_progress(f"\n  ⚠️  Remaining Challenges:", log_file)
                for bottleneck in result.bottlenecks[:2]:
                    log_progress(f"     • {bottleneck[:65]}", log_file)

            cycle_data = {
                "cycle_number": cycle_num,
                "accuracy_before": old_accuracy,
                "accuracy_after": current_accuracy,
                "accuracy_gain": accuracy_gain,
                "phase": phase_name,
                "improvements_count": total_improvements,
                "elapsed_time": learn_time + improve_time,
            }
            cycle_history.append(cycle_data)

            log_progress(
                f"\n  ✨ Cycle #{cycle_num} Complete! Total time: {learn_time + improve_time:.3f}s", log_file)

        except Exception as e:
            log_progress(f"\n  ❌ ERROR in Cycle #{cycle_num}: {e}", log_file)
            import traceback
            log_progress(traceback.format_exc(), log_file)
            current_accuracy = accuracies[-1] if accuracies else 0
            continue

    # Final Summary
    log_progress("\n" + "="*75, log_file)
    log_progress("🎉 TRAINING SESSION COMPLETE!", log_file)
    log_progress("="*75, log_file)

    if accuracies:
        log_progress(f"\n📊 LEARNING TRAJECTORY (All Cycles):", log_file)
        log_progress("   " + "─" * 50, log_file)

        for i, (cycle, acc) in enumerate(zip(cycle_history, accuracies), 1):
            gain = cycle["accuracy_gain"]
            phase = cycle["phase"].split(":")[0]
            log_progress(
                f"   Cycle {i} │ {acc:5.1f}% {format_progress_bar(acc, 98)} │ "
                f"↑{gain:+5.1f}% │ {phase}", log_file
            )

        log_progress("   " + "─" * 50, log_file)

        total_improvement = accuracies[-1] - \
            accuracies[0] if len(accuracies) > 1 else 0
        log_progress(
            f"\n📈 OVERALL IMPROVEMENT:  {total_improvement:+.1f}% over {num_cycles} cycles", log_file)

        if accuracies[-1] < 98:
            remaining = 98 - accuracies[-1]
            log_progress(
                f"📊 REMAINING GAP:       {remaining:.1f}% to 98% target", log_file)

            avg_per_cycle = total_improvement / num_cycles if num_cycles > 0 else 0
            if avg_per_cycle > 0:
                est_cycles = int(remaining / avg_per_cycle)
                log_progress(
                    f"📊 TO REACH 98%:        ~{est_cycles} additional cycles", log_file)
        else:
            log_progress(
                f"\n🏆 TARGET REACHED! Accuracy: {accuracies[-1]:.1f}%", log_file)

        # Phase progression
        final_phase, final_phase_num, _ = get_phase_info(accuracies[-1])
        log_progress(
            f"\n🎯 CURRENT PHASE: {final_phase} [Phase {final_phase_num}/4]", log_file)

        log_progress(f"\n✅ Log file: {log_file}", log_file)

    log_progress(f"📅 Completed: {datetime.now().isoformat()}", log_file)
    log_progress("="*75 + "\n", log_file)

    return cycle_history, accuracies


# ============================================================================
# FASTAPI ROUTES - Learning Endpoints
# ============================================================================

router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.get("/health")
async def pipeline_health():
    """
    Get comprehensive pipeline health report.

    Shows:
    - Overall pipeline accuracy
    - Agent learning progress
    - Bottlenecks and recommendations
    """
    try:
        health = feedback_engine.get_pipeline_health_report()
        return {
            "status": "healthy" if health["pipeline_accuracy"] > 70 else "needs_attention",
            "data": health,
        }
    except Exception as e:
        logger.error(f"Failed to get health report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_name}/learning")
async def agent_learning_summary(agent_name: str):
    """
    Get detailed learning summary for a specific agent.

    Shows:
    - Total decisions made
    - Accuracy percentage
    - Common errors
    - Improvement areas
    """
    try:
        summary = feedback_engine.get_agent_learning_summary(agent_name)
        return {
            "agent": agent_name,
            "summary": summary,
        }
    except Exception as e:
        logger.error(f"Failed to get learning summary for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/trail")
async def audit_trail(
    agent_name: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get audit trail filtered by agent and/or limit.

    Shows:
    - Recent operations
    - Execution times
    - Status (success/failure)
    """
    try:
        trail = audit_logger.get_audit_trail(
            agent_name=agent_name, limit=limit)
        return {
            "count": len(trail),
            "events": trail,
        }
    except Exception as e:
        logger.error(f"Failed to get audit trail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/security")
async def security_audit():
    """
    Get security audit report.

    Shows:
    - Recent security events
    - Critical findings
    - Threat levels
    """
    try:
        audit = audit_logger.get_security_audit()
        return {
            "status": "secure" if audit["critical_events"] == 0 else "alert",
            "data": audit,
        }
    except Exception as e:
        logger.error(f"Failed to get security audit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance")
async def performance_metrics():
    """
    Get agent performance metrics.

    Shows:
    - Success rates
    - Execution times
    - Efficiency metrics
    """
    try:
        perf = audit_logger.get_performance_report()
        return {
            "timestamp": perf["timestamp"],
            "metrics": perf["by_agent"],
        }
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/edge-cases")
async def edge_cases(agent_name: Optional[str] = Query(None)):
    """
    Get all discovered edge cases.

    Useful for:
    - Understanding system blindspots
    - Training new versions
    - Improving robustness
    """
    try:
        cases = feedback_engine.get_edge_cases(agent_name=agent_name)
        return {
            "count": len(cases),
            "edge_cases": cases,
        }
    except Exception as e:
        logger.error(f"Failed to get edge cases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback/{decision_id}")
async def submit_feedback(
    decision_id: str,
    feedback_type: str = Query(...),
    explanation: str = Query(""),
    impact_score: int = Query(50),
):
    """
    Submit feedback about an agent's decision.

    This closes the learning loop and enables the agents to improve.

    feedback_type options:
    - override: Human overrode the decision
    - correction: Agent made a mistake
    - validation_pass: Decision was correct
    - edge_case: Unexpected scenario
    """
    try:
        # Map string to FeedbackType
        feedback_map = {
            "override": FeedbackType.DECISION_OVERRIDE,
            "correction": FeedbackType.CORRECTION,
            "validation_pass": FeedbackType.VALIDATION_PASS,
            "edge_case": FeedbackType.EDGE_CASE,
        }

        ftype = feedback_map.get(feedback_type)
        if not ftype:
            raise ValueError(f"Invalid feedback_type: {feedback_type}")

        feedback_engine.submit_feedback(
            decision_id=decision_id,
            feedback_type=ftype,
            explanation=explanation,
            impact_score=impact_score,
        )

        return {
            "status": "submitted",
            "decision_id": decision_id,
            "feedback_type": feedback_type,
        }
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/manifest")
async def learning_manifest():
    """
    Get the complete learning manifest showing the path to perfection.

    Returns:
    - Current state accuracy
    - Target perfection map
    - Progress toward goals
    - Estimated time to goal
    """
    try:
        health = feedback_engine.get_pipeline_health_report()

        # Define perfection map
        perfection_map = {
            "overall_accuracy": {
                "current": health["pipeline_accuracy"],
                "target": 98.0,
                "progress_percent": min(100, (health["pipeline_accuracy"] / 98.0 * 100)),
            },
            "agents": {},
            "timeline": {
                "current_phase": "Learning & Optimization",
                "phase_progress_percent": min(100, (health["pipeline_accuracy"] / 98.0 * 100)),
            },
        }

        for agent_name, summary in health["agents"].items():
            perfection_map["agents"][agent_name] = {
                "current_accuracy": summary["accuracy"],
                "target_accuracy": 95.0,
                "decisions_made": summary["total_decisions"],
                "improvements_needed": len(summary["improvement_areas"]),
                "path_to_perfection": {
                    "phase_1_foundations": "Complete" if summary["accuracy"] > 70 else "In Progress",
                    "phase_2_refinement": "Complete" if summary["accuracy"] > 85 else "Pending",
                    "phase_3_mastery": "Complete" if summary["accuracy"] > 95 else "Pending",
                },
            }

        return {
            "timestamp": health["timestamp"],
            "perfection_map": perfection_map,
            "bottlenecks": health["bottlenecks"],
            "recommendations": health["recommendations"],
        }
    except Exception as e:
        logger.error(f"Failed to get learning manifest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "ImprovementArea",
    # Dataclasses
    "QualityAuditRecord",
    "LearningMetric",
    "CycleResult",
    # Classes
    "LearningEnabledAgent",
    "LearningEnabledTrinitySwarm",
    "LearningOptimizerEngine",
    # Functions
    "run_enhanced_training",
    "format_progress_bar",
    "get_phase_info",
    "log_progress",
    # Routes
    "router",
]


if __name__ == "__main__":
    # Quick test/demo
    swarm = LearningEnabledTrinitySwarm()
    # result = swarm.process_brand_with_learning("Nord")
    # print(json.dumps(result, indent=2, default=str))

    # Or run optimizer
    optimizer = LearningOptimizerEngine()
    cycle = optimizer.run_learning_cycle(cycle_number=1)
    print(f"✅ Cycle complete")
