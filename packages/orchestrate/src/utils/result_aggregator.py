"""
Result aggregator for consolidating outputs across phases.
Handles merging, conflict detection, and synthesis generation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class ResultAggregator:
    """
    Aggregates and synthesizes results from multiple phases and tasks.
    """
    
    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
        self.conflicts: List[Dict[str, Any]] = []
        
    def add_result(
        self, 
        phase: str, 
        task: str, 
        result: Dict[str, Any]
    ) -> None:
        """Add a task result to the aggregator."""
        if phase not in self.results:
            self.results[phase] = {}
        
        self.results[phase][task] = {
            **result,
            "aggregated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Check for conflicts with existing results
        self._detect_conflicts(phase, task, result)
    
    def _detect_conflicts(
        self, 
        phase: str, 
        task: str, 
        new_result: Dict[str, Any]
    ) -> None:
        """
        Detect potential conflicts between new and existing results.
        Looks for contradictory claims, inconsistent numbers, etc.
        """
        # Skip if no structured data to compare
        new_data = new_result.get("structured_data")
        if not new_data:
            return
        
        # Compare against all existing results
        for existing_phase, tasks in self.results.items():
            for existing_task, existing_result in tasks.items():
                if existing_phase == phase and existing_task == task:
                    continue
                    
                existing_data = existing_result.get("structured_data")
                if not existing_data:
                    continue
                
                # Check for numeric inconsistencies
                conflicts = self._find_numeric_conflicts(
                    new_data, existing_data,
                    f"{phase}/{task}", f"{existing_phase}/{existing_task}"
                )
                self.conflicts.extend(conflicts)
    
    def _find_numeric_conflicts(
        self,
        data1: Dict[str, Any],
        data2: Dict[str, Any],
        source1: str,
        source2: str,
        threshold: float = 0.2  # 20% difference threshold
    ) -> List[Dict[str, Any]]:
        """Find numeric values that differ significantly between results."""
        conflicts = []
        
        def extract_numbers(d: Any, path: str = "") -> Dict[str, float]:
            """Recursively extract numeric values with their paths."""
            numbers = {}
            if isinstance(d, dict):
                for k, v in d.items():
                    new_path = f"{path}.{k}" if path else k
                    numbers.update(extract_numbers(v, new_path))
            elif isinstance(d, (int, float)) and not isinstance(d, bool):
                numbers[path] = float(d)
            elif isinstance(d, list):
                for i, item in enumerate(d):
                    numbers.update(extract_numbers(item, f"{path}[{i}]"))
            return numbers
        
        nums1 = extract_numbers(data1)
        nums2 = extract_numbers(data2)
        
        # Find matching keys and check for significant differences
        common_keys = set(nums1.keys()) & set(nums2.keys())
        for key in common_keys:
            v1, v2 = nums1[key], nums2[key]
            if v1 == 0 and v2 == 0:
                continue
            
            # Calculate relative difference
            avg = (abs(v1) + abs(v2)) / 2
            if avg > 0:
                diff = abs(v1 - v2) / avg
                if diff > threshold:
                    conflicts.append({
                        "type": "numeric_conflict",
                        "key": key,
                        "value1": v1,
                        "source1": source1,
                        "value2": v2,
                        "source2": source2,
                        "difference_percent": round(diff * 100, 1)
                    })
        
        return conflicts
    
    def get_phase_results(self, phase: str) -> Dict[str, Any]:
        """Get all results for a specific phase."""
        return self.results.get(phase, {})
    
    def get_all_results(self) -> Dict[str, Dict[str, Any]]:
        """Get all aggregated results."""
        return self.results
    
    def get_conflicts(self) -> List[Dict[str, Any]]:
        """Get all detected conflicts."""
        return self.conflicts
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of all aggregated results."""
        summary = {
            "phases_completed": list(self.results.keys()),
            "tasks_completed": sum(len(tasks) for tasks in self.results.values()),
            "conflicts_detected": len(self.conflicts),
            "by_phase": {},
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        for phase, tasks in self.results.items():
            phase_summary = {
                "tasks": list(tasks.keys()),
                "success_count": sum(
                    1 for t in tasks.values() 
                    if t.get("status") == "success"
                ),
                "error_count": sum(
                    1 for t in tasks.values() 
                    if t.get("status") == "error"
                )
            }
            summary["by_phase"][phase] = phase_summary
        
        return summary
    
    async def synthesize(
        self, 
        all_results: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> str:
        """
        Generate executive synthesis report from all results.
        
        Args:
            all_results: Override results (uses self.results if not provided)
            
        Returns:
            Markdown formatted synthesis report
        """
        results = all_results or self.results
        
        report_sections = [
            "# Omni-Performative Engine: Executive Synthesis Report",
            f"\n*Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*\n",
            "---\n",
        ]
        
        # Executive Summary
        report_sections.append("## Executive Summary\n")
        summary = self.generate_summary()
        report_sections.append(
            f"This report consolidates findings from **{summary['tasks_completed']} tasks** "
            f"across **{len(summary['phases_completed'])} phases** of the orchestration pipeline.\n"
        )
        
        if self.conflicts:
            report_sections.append(
                f"\n⚠️ **{len(self.conflicts)} conflicts detected** between results. "
                "See Conflicts section below.\n"
            )
        
        # Phase-by-phase findings
        phase_order = [
            ("research_validation", "Phase 1: Research Validation"),
            ("spec_hardening", "Phase 2: Specification Hardening"),
            ("messaging_synthesis", "Phase 3: Messaging Synthesis"),
            ("implementation_planning", "Phase 4: Implementation Planning"),
            ("vulnerability_audit", "Phase 5: Vulnerability Audit"),
        ]
        
        for phase_key, phase_title in phase_order:
            if phase_key in results:
                report_sections.append(f"\n## {phase_title}\n")
                phase_results = results[phase_key]
                
                for task_name, task_result in phase_results.items():
                    report_sections.append(f"\n### {task_name.replace('_', ' ').title()}\n")
                    
                    status = task_result.get("status", "unknown")
                    status_emoji = "✅" if status == "success" else "❌"
                    report_sections.append(f"**Status**: {status_emoji} {status}\n")
                    
                    # Add key findings from structured data
                    structured = task_result.get("structured_data")
                    if structured:
                        # Extract summary if present
                        if "summary" in structured:
                            report_sections.append("\n**Key Findings:**\n")
                            for k, v in structured["summary"].items():
                                if isinstance(v, list):
                                    report_sections.append(f"- {k}: {len(v)} items\n")
                                else:
                                    report_sections.append(f"- {k}: {v}\n")
        
        # Conflicts section
        if self.conflicts:
            report_sections.append("\n## Detected Conflicts\n")
            report_sections.append(
                "The following inconsistencies were found between task outputs:\n"
            )
            for conflict in self.conflicts:
                report_sections.append(
                    f"\n- **{conflict['key']}**: {conflict['value1']} ({conflict['source1']}) "
                    f"vs {conflict['value2']} ({conflict['source2']}) "
                    f"— {conflict['difference_percent']}% difference\n"
                )
        
        # Recommendations
        report_sections.append("\n## Next Steps\n")
        report_sections.append(
            "1. Review any detected conflicts and resolve discrepancies\n"
            "2. Validate critical assumptions identified in Phase 5\n"
            "3. Begin POC development based on Phase 4 timeline\n"
            "4. Submit first grant application based on Phase 3 narratives\n"
        )
        
        return "".join(report_sections)
    
    def save_to_file(self, output_path: Path) -> None:
        """Save aggregated results to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        output = {
            "results": self.results,
            "conflicts": self.conflicts,
            "summary": self.generate_summary()
        }
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        logger.info(f"Saved aggregated results to {output_path}")
    
    @classmethod
    def load_from_file(cls, input_path: Path) -> "ResultAggregator":
        """Load aggregated results from JSON file."""
        with open(input_path, 'r') as f:
            data = json.load(f)
        
        aggregator = cls()
        aggregator.results = data.get("results", {})
        aggregator.conflicts = data.get("conflicts", [])
        
        return aggregator
