"""
Prompt template library for all orchestration phases.
Loads templates from prompts/ directory and provides substitution utilities.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PromptLibrary:
    """
    Manages prompt templates for all phases.
    Templates are loaded from files and cached.
    """
    
    def __init__(self, prompts_dir: Optional[Path] = None):
        self.prompts_dir = prompts_dir or Path(__file__).parent.parent.parent / "prompts"
        self._cache: Dict[str, str] = {}
        
    def _load_template(self, phase: str, task: str) -> str:
        """Load a template file from disk."""
        # Try multiple extensions
        for ext in [".txt", ".md", ".prompt"]:
            path = self.prompts_dir / phase / f"{task}{ext}"
            if path.exists():
                return path.read_text(encoding="utf-8")
        
        raise FileNotFoundError(
            f"Template not found: {phase}/{task} "
            f"(searched in {self.prompts_dir})"
        )
    
    def get(self, phase: str, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Get a prompt template, optionally with context substitution.
        
        Args:
            phase: Phase name (e.g., "phase1_research")
            task: Task name (e.g., "precedent_verification")
            context: Dictionary of values to substitute
            
        Returns:
            The prompt string, with placeholders filled if context provided
        """
        cache_key = f"{phase}/{task}"
        
        if cache_key not in self._cache:
            self._cache[cache_key] = self._load_template(phase, task)
        
        template = self._cache[cache_key]
        
        if context:
            # Use safe substitution that doesn't fail on missing keys
            for key, value in context.items():
                placeholder = "{" + key + "}"
                template = template.replace(placeholder, str(value))
        
        return template
    
    def get_gate(self, phase_number: int, context: Optional[Dict[str, Any]] = None) -> str:
        """Get a gate validation prompt."""
        return self.get("gates", f"gate_{phase_number}", context)
    
    def list_available(self) -> Dict[str, list[str]]:
        """List all available templates by phase."""
        available = {}
        
        if not self.prompts_dir.exists():
            return available
            
        for phase_dir in self.prompts_dir.iterdir():
            if phase_dir.is_dir():
                templates = []
                for f in phase_dir.iterdir():
                    if f.suffix in [".txt", ".md", ".prompt"]:
                        templates.append(f.stem)
                if templates:
                    available[phase_dir.name] = sorted(templates)
        
        return available
    
    def clear_cache(self) -> None:
        """Clear the template cache."""
        self._cache.clear()


# Pre-built prompt library structure for inline use
# Maps phase -> task -> prompt template
PROMPT_LIBRARY = {
    "research_validation": {
        "precedent_verification": "phase1_research/precedent_verification",
        "funding_landscape": "phase1_research/funding_landscape",
    },
    "spec_hardening": {
        "edge_case_matrix": "phase2_specification/edge_case_matrix",
        "latency_constraints": "phase2_specification/latency_constraints",
    },
    "messaging_synthesis": {
        "grant_narrative_nsf": "phase3_messaging/grant_narrative_nsf",
        "grant_narrative_neh": "phase3_messaging/grant_narrative_neh",
        "grant_narrative_ars": "phase3_messaging/grant_narrative_ars",
        "artist_statement": "phase3_messaging/artist_statement",
    },
    "implementation_planning": {
        "code_architecture": "phase4_implementation/code_architecture",
        "budget_allocation": "phase4_implementation/budget_allocation",
    },
    "vulnerability_audit": {
        "assumption_critique": "phase5_vulnerability/assumption_critique",
        "failure_scenarios": "phase5_vulnerability/failure_scenarios",
    },
    "gates": {
        "phase1_gate": "gates/all_gates",  # Will need parsing
        "phase2_gate": "gates/all_gates",
        "phase3_gate": "gates/all_gates",
        "phase4_gate": "gates/all_gates",
        "phase5_gate": "gates/all_gates",
    }
}


def get_prompt_library(prompts_dir: Optional[Path] = None) -> PromptLibrary:
    """Factory function to get a PromptLibrary instance."""
    return PromptLibrary(prompts_dir)


def load_prompt(
    phase: str, 
    task: str, 
    context: Optional[Dict[str, Any]] = None,
    prompts_dir: Optional[Path] = None
) -> str:
    """
    Convenience function to load a single prompt.
    
    Example:
        prompt = load_prompt(
            "phase1_research", 
            "precedent_verification",
            context={"precedent_claims": claims_list}
        )
    """
    library = PromptLibrary(prompts_dir)
    return library.get(phase, task, context)
