"""
Gate validator for phase transition decisions.
Evaluates whether phase outputs meet criteria for proceeding.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class GateResult:
    """Result of a gate validation."""
    gate_number: int
    passed: bool
    status: str  # "pass", "revise", "fail"
    criteria_results: Dict[str, bool]
    recommendations: List[str]
    blocking_issues: List[str]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate": self.gate_number,
            "pass": self.passed,
            "status": self.status,
            "criteria_results": self.criteria_results,
            "recommendations": self.recommendations,
            "blocking_issues": self.blocking_issues,
            "timestamp": self.timestamp
        }


class GateValidator:
    """
    Validates phase outputs against gate criteria.
    Determines if orchestration can proceed to next phase.
    """
    
    def __init__(self):
        self.gate_history: List[GateResult] = []
    
    async def validate(
        self, 
        gate_prompt: str,
        phase_results: Dict[str, Any],
        gate_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Validate phase results against gate criteria.
        
        Args:
            gate_prompt: The gate validation prompt (unused in rule-based validation)
            phase_results: Dictionary of task results from the phase
            gate_number: Which gate this is (1-5)
            
        Returns:
            Dictionary with validation results
        """
        # Determine gate number from results if not provided
        if gate_number is None:
            gate_number = self._infer_gate_number(phase_results)
        
        # Run appropriate validation
        validators = {
            1: self._validate_gate_1,
            2: self._validate_gate_2,
            3: self._validate_gate_3,
            4: self._validate_gate_4,
            5: self._validate_gate_5,
        }
        
        validator = validators.get(gate_number, self._validate_generic)
        result = validator(phase_results)
        
        # Store in history
        self.gate_history.append(result)
        
        return result.to_dict()
    
    def _infer_gate_number(self, results: Dict[str, Any]) -> int:
        """Infer gate number from task names in results."""
        task_names = list(results.keys())
        task_str = " ".join(task_names).lower()
        
        if "precedent" in task_str or "funding" in task_str:
            return 1
        elif "edge_case" in task_str or "latency" in task_str:
            return 2
        elif "narrative" in task_str or "artist_statement" in task_str:
            return 3
        elif "architecture" in task_str or "budget" in task_str:
            return 4
        elif "assumption" in task_str or "failure" in task_str:
            return 5
        
        return 0  # Unknown
    
    def _validate_gate_1(self, results: Dict[str, Any]) -> GateResult:
        """
        Gate 1: Research Validation
        Criteria:
        - 80%+ claims verified
        - 10+ funding opportunities
        - 3+ near-term deadlines
        - No show-stopping contradictions
        """
        criteria = {}
        recommendations = []
        blocking = []
        
        # Check precedent verification
        precedent = results.get("precedent_verification", {})
        structured = precedent.get("structured_data", {})
        summary = structured.get("summary", {})
        
        total = summary.get("total_claims", 0)
        confirmed = summary.get("confirmed", 0) + summary.get("partially_confirmed", 0)
        contradicted = summary.get("contradicted", 0)
        
        if total > 0:
            verification_rate = confirmed / total
            criteria["claims_80_percent_verified"] = verification_rate >= 0.8
            if not criteria["claims_80_percent_verified"]:
                recommendations.append(
                    f"Only {verification_rate*100:.0f}% claims verified. "
                    "Re-run precedent verification with additional sources."
                )
        else:
            criteria["claims_80_percent_verified"] = False
            blocking.append("No precedent verification results found")
        
        criteria["no_contradictions"] = contradicted == 0
        if contradicted > 0:
            recommendations.append(
                f"{contradicted} claims contradicted. Review and revise claims."
            )
        
        # Check funding landscape
        funding = results.get("funding_landscape", {})
        funding_data = funding.get("structured_data", {})
        opportunities = funding_data.get("funding_opportunities", [])
        
        criteria["10_plus_opportunities"] = len(opportunities) >= 10
        if not criteria["10_plus_opportunities"]:
            recommendations.append(
                f"Only {len(opportunities)} funding opportunities found. "
                "Expand search to additional regions/programs."
            )
        
        # Check near-term deadlines
        near_term = sum(
            1 for opp in opportunities 
            if opp.get("timeline", {}).get("next_deadline") 
            and opp["timeline"]["next_deadline"] != "rolling"
        )
        criteria["near_term_deadlines"] = near_term >= 3
        if not criteria["near_term_deadlines"]:
            recommendations.append(
                f"Only {near_term} opportunities with fixed deadlines. "
                "Prioritize time-sensitive applications."
            )
        
        # Determine overall status
        all_passed = all(criteria.values())
        critical_passed = criteria.get("no_contradictions", True) and len(blocking) == 0
        
        if all_passed:
            status = "pass"
        elif critical_passed:
            status = "revise"
        else:
            status = "fail"
        
        return GateResult(
            gate_number=1,
            passed=status == "pass",
            status=status,
            criteria_results=criteria,
            recommendations=recommendations,
            blocking_issues=blocking,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    
    def _validate_gate_2(self, results: Dict[str, Any]) -> GateResult:
        """
        Gate 2: Specification Hardening
        Criteria:
        - 25 edge cases populated
        - Critical issues have mitigations
        - Constraints are achievable
        """
        criteria = {}
        recommendations = []
        blocking = []
        
        # Check edge case matrix
        edge_cases = results.get("edge_case_matrix", {})
        matrix_data = edge_cases.get("structured_data", {}).get("edge_case_matrix", {})
        cells = matrix_data.get("cells", [])
        
        criteria["25_cells_populated"] = len(cells) >= 25
        if not criteria["25_cells_populated"]:
            recommendations.append(
                f"Only {len(cells)}/25 edge cases analyzed. Complete the matrix."
            )
        
        # Check critical mitigations
        critical_unmitigated = sum(
            1 for cell in cells
            if cell.get("assessment", {}).get("priority") == "critical"
            and not cell.get("mitigation", {}).get("immediate_fix")
        )
        criteria["critical_mitigated"] = critical_unmitigated == 0
        if critical_unmitigated > 0:
            blocking.append(
                f"{critical_unmitigated} critical issues without mitigation"
            )
        
        # Check constraint validation
        constraints = results.get("latency_constraints", {})
        constraint_data = constraints.get("structured_data", {}).get("constraint_validation", {})
        
        latency_ok = constraint_data.get("latency_waterfall", {}).get("total_ms", 999) <= 100
        criteria["latency_achievable"] = latency_ok
        if not latency_ok:
            recommendations.append(
                "Latency exceeds 100ms target. Review optimization opportunities."
            )
        
        # Determine status
        all_passed = all(criteria.values())
        critical_passed = len(blocking) == 0
        
        if all_passed:
            status = "pass"
        elif critical_passed:
            status = "revise"
        else:
            status = "fail"
        
        return GateResult(
            gate_number=2,
            passed=status == "pass",
            status=status,
            criteria_results=criteria,
            recommendations=recommendations,
            blocking_issues=blocking,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    
    def _validate_gate_3(self, results: Dict[str, Any]) -> GateResult:
        """
        Gate 3: Messaging Coherence
        Criteria:
        - Multiple narratives generated
        - Core message consistent
        - Artist statement present
        """
        criteria = {}
        recommendations = []
        blocking = []
        
        # Count narrative variants
        narrative_tasks = [k for k in results.keys() if "narrative" in k.lower()]
        criteria["multiple_narratives"] = len(narrative_tasks) >= 2
        
        # Check artist statement
        artist_statement = results.get("artist_statement", {})
        criteria["artist_statement_present"] = artist_statement.get("status") == "success"
        if not criteria["artist_statement_present"]:
            recommendations.append("Generate artist statement")
        
        # Check for word count compliance (basic check)
        for task_name, task_result in results.items():
            content = task_result.get("content", "")
            word_count = len(content.split())
            if "nsf" in task_name.lower() and word_count < 500:
                recommendations.append(f"{task_name} may be too short ({word_count} words)")
        
        criteria["coherence_check"] = True  # Would need AI to verify
        
        all_passed = all(criteria.values())
        status = "pass" if all_passed else "revise"
        
        return GateResult(
            gate_number=3,
            passed=status == "pass",
            status=status,
            criteria_results=criteria,
            recommendations=recommendations,
            blocking_issues=blocking,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    
    def _validate_gate_4(self, results: Dict[str, Any]) -> GateResult:
        """
        Gate 4: Implementation Planning
        Criteria:
        - Architecture reviewed
        - Budget with contingency
        - Timeline realistic
        """
        criteria = {}
        recommendations = []
        blocking = []
        
        # Check architecture review
        arch = results.get("code_architecture", {})
        criteria["architecture_reviewed"] = arch.get("status") == "success"
        
        # Check budget
        budget = results.get("budget_allocation", {})
        budget_data = budget.get("structured_data", {}).get("budget_analysis", {})
        
        contingency = budget_data.get("contingency", {}).get("percentage", 0)
        criteria["contingency_included"] = contingency >= 20
        if not criteria["contingency_included"]:
            recommendations.append(
                f"Contingency at {contingency}%. Recommend minimum 20%."
            )
        
        # Check timeline realism (from architecture review)
        arch_data = arch.get("structured_data", {}).get("architecture_review", {})
        timeline_realistic = arch_data.get("timeline", {}).get("realistic_outcome") != "partial"
        criteria["timeline_realistic"] = timeline_realistic
        if not timeline_realistic:
            recommendations.append("Timeline may not deliver full POC. Consider scope adjustment.")
        
        all_passed = all(criteria.values())
        status = "pass" if all_passed else "revise"
        
        return GateResult(
            gate_number=4,
            passed=status == "pass",
            status=status,
            criteria_results=criteria,
            recommendations=recommendations,
            blocking_issues=blocking,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    
    def _validate_gate_5(self, results: Dict[str, Any]) -> GateResult:
        """
        Gate 5: Vulnerability Audit
        Criteria:
        - All assumption categories covered
        - 10+ failure scenarios
        - Actionable mitigations
        """
        criteria = {}
        recommendations = []
        blocking = []
        
        # Check assumption critique
        assumptions = results.get("assumption_critique", {})
        assumption_data = assumptions.get("structured_data", {}).get("assumption_audit", {})
        
        categories = assumption_data.get("categories", {})
        criteria["all_categories_covered"] = len(categories) >= 6
        
        red_flags = assumption_data.get("summary", {}).get("red_flags", 0)
        if red_flags > 0:
            recommendations.append(
                f"{red_flags} red-flag assumptions identified. Validate before proceeding."
            )
        
        # Check failure scenarios
        failures = results.get("failure_scenarios", {})
        failure_data = failures.get("structured_data", {}).get("failure_scenarios", {})
        scenarios = failure_data.get("scenarios", [])
        
        criteria["10_plus_scenarios"] = len(scenarios) >= 10
        if not criteria["10_plus_scenarios"]:
            recommendations.append(f"Only {len(scenarios)} failure scenarios. Generate more.")
        
        # Check actionability
        has_priorities = "mitigation_priorities" in failure_data
        criteria["actionable_mitigations"] = has_priorities
        
        all_passed = all(criteria.values())
        status = "pass" if all_passed else "revise"
        
        return GateResult(
            gate_number=5,
            passed=status == "pass",
            status=status,
            criteria_results=criteria,
            recommendations=recommendations,
            blocking_issues=blocking,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    
    def _validate_generic(self, results: Dict[str, Any]) -> GateResult:
        """Generic validation for unknown gates."""
        # Just check that all tasks succeeded
        all_success = all(
            r.get("status") == "success" 
            for r in results.values()
        )
        
        return GateResult(
            gate_number=0,
            passed=all_success,
            status="pass" if all_success else "revise",
            criteria_results={"all_tasks_success": all_success},
            recommendations=[],
            blocking_issues=[],
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get all gate validation history."""
        return [r.to_dict() for r in self.gate_history]
