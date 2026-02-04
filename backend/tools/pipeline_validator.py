"""
Pipeline Validator - Production-ready v5.2.4
"""

#!/usr/bin/env python3
"""
Pipeline Validator & Enhancer - Conductor Module
Validates data ingestion, transformation, and population pipeline for reliability
Status: Production v5.2.4
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
import inspect
import json

logger = logging.getLogger(__name__)


class PipelineValidator:
    """Validates data pipeline for reliability, maintainability, and operability"""

    def __init__(self, project_root: str = '/workspaces/Halilit-Support-Center'):
        self.project_root = Path(project_root)
        self.backend = self.project_root / 'backend'
        self.pipeline_dir = self.backend / 'pipeline'
        self.validation_report = {
            'architecture': {},
            'data_flow': {},
            'error_handling': {},
            'monitoring': {},
            'maintainability': {},
            'operability': {},
            'recommendations': []
        }

    def print_section(self, title: str, width: int = 70):
        """Print formatted section header"""
        logger.info("")
        logger.info("-" * width)
        logger.info(f"  {title}")
        logger.info("-" * width)

    # =========================================================================
    # ARCHITECTURE VALIDATION
    # =========================================================================

    def validate_architecture(self) -> Dict[str, Any]:
        """Validate pipeline architecture and structure"""
        self.print_section("PIPELINE ARCHITECTURE VALIDATION")

        architecture = {
            'modules': {},
            'design_patterns': [],
            'issues': []
        }

        # Check for required pipeline modules
        required_modules = [
            ('data_refinery.py', 'Core data transformation'),
            ('__init__.py', 'Package initialization'),
        ]

        for module_name, description in required_modules:
            module_path = self.pipeline_dir / module_name
            if module_path.exists():
                logger.info(f"  ✓ {module_name}: {description}")
                architecture['modules'][module_name] = 'PRESENT'
            else:
                logger.warning(f"  ⚠ {module_name}: MISSING")
                architecture['issues'].append(f"Missing module: {module_name}")

        # Analyze data_refinery.py for design patterns
        refinery_file = self.pipeline_dir / 'data_refinery.py'
        if refinery_file.exists():
            content = refinery_file.read_text()

            # Check for key methods
            methods = {
                'ingest_raw_data': 'Data ingestion interface',
                '_refine_item': 'Data transformation',
                '_validate_item': 'Data validation',
                'export_golden_json': 'Data export',
            }

            logger.info("\n  Data Refinery Methods:")
            for method, purpose in methods.items():
                if f"def {method}" in content:
                    logger.info(f"    ✓ {method}(): {purpose}")
                    architecture['design_patterns'].append(method)
                else:
                    logger.warning(f"    ⚠ {method}(): MISSING")
                    architecture['issues'].append(f"Missing method: {method}")

            # Check for deduplication logic
            if 'seen_ids' in content or 'deduplication' in content.lower():
                logger.info("    ✓ Deduplication logic: PRESENT")
                architecture['design_patterns'].append('deduplication')
            else:
                logger.warning("    ⚠ Deduplication logic: MISSING")
                architecture['issues'].append("No deduplication logic found")

        self.validation_report['architecture'] = architecture
        return architecture

    # =========================================================================
    # DATA FLOW VALIDATION
    # =========================================================================

    def validate_data_flow(self) -> Dict[str, Any]:
        """Validate data flow and transformation stages"""
        self.print_section("DATA FLOW & TRANSFORMATION VALIDATION")

        data_flow = {
            'stages': [],
            'transformations': [],
            'issues': []
        }

        refinery_file = self.pipeline_dir / 'data_refinery.py'
        if refinery_file.exists():
            content = refinery_file.read_text()

            # Define expected transformation stages
            stages = {
                'Commercial Data Flattening': 'commercial' in content,
                'Brand Normalization': '_normalize_brand' in content,
                'Price Parsing': '_parse_price' in content,
                'Category Mapping': 'category' in content,
                'Specification Flattening': 'specs' in content and 'final_specs' in content,
                'Search Token Generation': '_generate_search_tokens' in content,
                'Tier Determination': '_determine_tier' in content,
            }

            logger.info("\n  Transformation Stages:")
            for stage, present in stages.items():
                if present:
                    logger.info(f"    ✓ {stage}: IMPLEMENTED")
                    data_flow['transformations'].append(stage)
                else:
                    logger.warning(f"    ⚠ {stage}: MISSING")
                    data_flow['issues'].append(
                        f"Missing transformation: {stage}")

            # Check for data validation
            logger.info("\n  Data Validation:")
            if '_validate_item' in content:
                logger.info("    ✓ Item validation: IMPLEMENTED")
                data_flow['stages'].append('validation')

                # Check for specific validation rules
                validations = {
                    'Required fields': 'name' in content and 'brand' in content,
                    'Price validation': 'price' in content,
                    'Brand validation': 'brand' in content,
                    'Error tracking': 'validation_errors' in content,
                }

                for validation, present in validations.items():
                    if present:
                        logger.info(f"      ✓ {validation}")
                    else:
                        logger.warning(f"      ⚠ {validation}")
                        data_flow['issues'].append(
                            f"Missing validation: {validation}")

        self.validation_report['data_flow'] = data_flow
        return data_flow

    # =========================================================================
    # ERROR HANDLING VALIDATION
    # =========================================================================

    def validate_error_handling(self) -> Dict[str, Any]:
        """Validate error handling and recovery mechanisms"""
        self.print_section("ERROR HANDLING & RECOVERY VALIDATION")

        error_handling = {
            'mechanisms': [],
            'logging': [],
            'issues': []
        }

        refinery_file = self.pipeline_dir / 'data_refinery.py'
        if refinery_file.exists():
            content = refinery_file.read_text()

            # Check error handling patterns
            logger.info("\n  Error Handling Mechanisms:")

            patterns = {
                'Try-Except Blocks': 'try:' in content and 'except' in content,
                'Error Logging': 'logger.error' in content or 'logger.warning' in content,
                'Validation Errors': 'validation_errors' in content,
                'Validation Warnings': 'validation_warnings' in content,
                'Item Skipping': 'skip' in content.lower() or 'continue' in content,
                'Error Recovery': 'except' in content,
            }

            for pattern, present in patterns.items():
                if present:
                    logger.info(f"    ✓ {pattern}: IMPLEMENTED")
                    error_handling['mechanisms'].append(pattern)
                else:
                    logger.warning(f"    ⚠ {pattern}: MISSING")
                    error_handling['issues'].append(
                        f"Missing error handling: {pattern}")

            # Check logging quality
            logger.info("\n  Logging Quality:")

            if 'logging.basicConfig' in content or 'logger = logging.getLogger' in content:
                logger.info("    ✓ Logging configured: YES")
                error_handling['logging'].append('configuration')

            if 'logger.info' in content:
                logger.info("    ✓ Info logs: PRESENT")
                error_handling['logging'].append('info')

            if 'logger.warning' in content:
                logger.info("    ✓ Warning logs: PRESENT")
                error_handling['logging'].append('warning')

            if 'logger.error' in content:
                logger.info("    ✓ Error logs: PRESENT")
                error_handling['logging'].append('error')
            else:
                logger.warning("    ⚠ Error logs: MISSING")
                error_handling['issues'].append("No error logging")

        self.validation_report['error_handling'] = error_handling
        return error_handling

    # =========================================================================
    # MONITORING & OBSERVABILITY
    # =========================================================================

    def validate_monitoring(self) -> Dict[str, Any]:
        """Validate monitoring and observability capabilities"""
        self.print_section("MONITORING & OBSERVABILITY VALIDATION")

        monitoring = {
            'metrics': [],
            'tracking': [],
            'issues': []
        }

        refinery_file = self.pipeline_dir / 'data_refinery.py'
        if refinery_file.exists():
            content = refinery_file.read_text()

            logger.info("\n  Observable Metrics:")

            metrics = {
                'Ingestion Count': 'count' in content and 'ingested' in content.lower(),
                'Validation Failures': 'validation_errors' in content,
                'Duplicate Detection': 'seen_ids' in content or 'dup' in content.lower(),
                'Processing Time': 'time' in content,
                'Item Status Tracking': 'status' in content,
                'Error Reporting': 'validation_errors' in content or 'validation_warnings' in content,
            }

            for metric, present in metrics.items():
                if present:
                    logger.info(f"    ✓ {metric}: TRACKABLE")
                    monitoring['metrics'].append(metric)
                else:
                    logger.warning(f"    ⚠ {metric}: NOT TRACKABLE")
                    monitoring['issues'].append(
                        f"Metric not tracked: {metric}")

        self.validation_report['monitoring'] = monitoring
        return monitoring

    # =========================================================================
    # MAINTAINABILITY VALIDATION
    # =========================================================================

    def validate_maintainability(self) -> Dict[str, Any]:
        """Validate code maintainability and quality"""
        self.print_section("MAINTAINABILITY VALIDATION")

        maintainability = {
            'documentation': [],
            'code_organization': [],
            'issues': []
        }

        refinery_file = self.pipeline_dir / 'data_refinery.py'
        if refinery_file.exists():
            content = refinery_file.read_text()

            # Check for docstrings
            logger.info("\n  Documentation:")

            if '"""' in content:
                logger.info("    ✓ Module docstring: PRESENT")
                maintainability['documentation'].append('module_docstring')
            else:
                logger.warning("    ⚠ Module docstring: MISSING")
                maintainability['issues'].append("Missing module docstring")

            # Count docstring frequency
            docstring_count = content.count('"""')
            logger.info(f"    ✓ Total docstrings: {docstring_count // 2}")
            maintainability['documentation'].append(
                f'docstring_count:{docstring_count // 2}')

            # Check code organization
            logger.info("\n  Code Organization:")

            organization = {
                'Class-based structure': 'class DataRefinery' in content,
                'Method separation': 'def ' in content,
                'Private method naming': '_' in content and 'def _' in content,
                'Type hints': 'List[' in content or 'Dict[' in content,
                'Constants/Config': 'brand_map' in content or 'self.' in content,
            }

            for org_item, present in organization.items():
                if present:
                    logger.info(f"    ✓ {org_item}: YES")
                    maintainability['code_organization'].append(org_item)
                else:
                    logger.warning(f"    ⚠ {org_item}: NO")
                    maintainability['issues'].append(f"Missing: {org_item}")

        self.validation_report['maintainability'] = maintainability
        return maintainability

    # =========================================================================
    # OPERABILITY VALIDATION
    # =========================================================================

    def validate_operability(self) -> Dict[str, Any]:
        """Validate pipeline operability and deployment readiness"""
        self.print_section("OPERABILITY & DEPLOYMENT VALIDATION")

        operability = {
            'configuration': [],
            'deployment_ready': False,
            'issues': []
        }

        # Check for __main__ entrypoint
        refinery_file = self.pipeline_dir / 'data_refinery.py'
        if refinery_file.exists():
            content = refinery_file.read_text()

            logger.info("\n  Operational Features:")

            features = {
                'CLI Entrypoint': 'if __name__' in content,
                'Configurable input path': 'argparse' in content and '--input' in content,
            }

            for feature, present in features.items():
                if present:
                    logger.info(f"    ✓ {feature}: PRESENT")
                    operability['configuration'].append(feature)
                else:
                    logger.warning(f"    ⚠ {feature}: MISSING")
                    operability['issues'].append(f"Missing: {feature}")

            # Check deployment readiness
            all_present = all(present for present in features.values())
            operability['deployment_ready'] = all_present and len(
                operability['issues']) == 0

            if operability['deployment_ready']:
                logger.info("\n  ✅ Deployment Ready: YES")
            else:
                logger.info("\n  ⚠️  Deployment Ready: PENDING FIXES")

        self.validation_report['operability'] = operability
        return operability

    # =========================================================================
    # RECOMMENDATIONS
    # =========================================================================

    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations for pipeline improvement"""
        self.print_section("IMPROVEMENT RECOMMENDATIONS")

        recommendations = []

        # Architecture recommendations
        arch_issues = self.validation_report['architecture'].get('issues', [])
        if arch_issues:
            recommendations.append(
                "🏗️  ARCHITECTURE: " + "; ".join(arch_issues))

        # Data flow recommendations
        flow_issues = self.validation_report['data_flow'].get('issues', [])
        if flow_issues:
            recommendations.append(
                "📊 DATA FLOW: " + "; ".join(flow_issues[:3]))

        # Error handling recommendations
        error_issues = self.validation_report['error_handling'].get(
            'issues', [])
        if error_issues:
            recommendations.append(
                "🛡️  ERROR HANDLING: " + "; ".join(error_issues[:2]))

        # Monitoring recommendations
        monitor_issues = self.validation_report['monitoring'].get('issues', [])
        if monitor_issues:
            recommendations.append("📈 MONITORING: Add metrics for " + ", ".join(
                [issue.replace("Metric not tracked: ", "") for issue in monitor_issues[:2]]))

        # Maintainability recommendations
        maint_issues = self.validation_report['maintainability'].get(
            'issues', [])
        if maint_issues:
            recommendations.append(
                "📚 MAINTAINABILITY: " + "; ".join(maint_issues[:2]))

        # Operability recommendations
        oper_issues = self.validation_report['operability'].get('issues', [])
        if oper_issues:
            recommendations.append("🚀 OPERABILITY: " +
                                   "; ".join(oper_issues[:2]))

        # Add general recommendations
        if not recommendations:
            recommendations.append(
                "✨ OPTIMIZATION: Consider adding performance metrics collection")
            recommendations.append(
                "📝 DOCUMENTATION: Create pipeline operation runbook")
            recommendations.append(
                "🔒 SECURITY: Add data sanitization validation")

        logger.info("\n  Priority Improvements:")
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"    {i}. {rec}")

        self.validation_report['recommendations'] = recommendations
        return recommendations

    # =========================================================================
    # EXECUTION
    # =========================================================================

    def execute_full_validation(self) -> Dict[str, Any]:
        """Execute comprehensive pipeline validation"""
        logger.info("")
        logger.info("=" * 70)
        logger.info("🔍 PIPELINE VALIDATION & ENHANCEMENT ANALYSIS")
        logger.info("=" * 70)

        try:
            # Run all validations
            self.validate_architecture()
            self.validate_data_flow()
            self.validate_error_handling()
            self.validate_monitoring()
            self.validate_maintainability()
            self.validate_operability()
            self.generate_recommendations()

            # Generate summary
            self.print_section("VALIDATION SUMMARY", width=70)

            arch = self.validation_report['architecture']
            data_flow = self.validation_report['data_flow']
            error = self.validation_report['error_handling']
            monitor = self.validation_report['monitoring']
            maint = self.validation_report['maintainability']
            oper = self.validation_report['operability']

            logger.info(
                f"\n  Architecture Issues:     {len(arch.get('issues', []))} issues")
            logger.info(
                f"  Data Flow Issues:        {len(data_flow.get('issues', []))} issues")
            logger.info(
                f"  Error Handling Issues:   {len(error.get('issues', []))} issues")
            logger.info(
                f"  Monitoring Issues:       {len(monitor.get('issues', []))} issues")
            logger.info(
                f"  Maintainability Issues:  {len(maint.get('issues', []))} issues")
            logger.info(
                f"  Operability Issues:      {len(oper.get('issues', []))} issues")

            total_issues = sum(len(v.get('issues', [])) for v in [
                               arch, data_flow, error, monitor, maint, oper])

            logger.info(f"\n  📊 Total Issues Found: {total_issues}")
            logger.info(
                f"  ✅ Deployment Ready: {oper.get('deployment_ready', False)}")

            self.print_section("VALIDATION COMPLETE", width=70)
            logger.info("")

            return self.validation_report

        except Exception as e:
            logger.error(f"❌ Pipeline validation failed: {e}", exc_info=True)
            raise
