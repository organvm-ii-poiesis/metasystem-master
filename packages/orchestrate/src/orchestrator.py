#!/usr/bin/env python3
"""
Omni-Performative Engine: Multi-AI Orchestration Tool
Coordinates research, validation, and synthesis across 5 AI services.

Usage:
    python orchestrator.py run --phase all --gates --output-dir ./results
    python orchestrator.py run --phase research-validation --pause-at-gate
    python orchestrator.py status --services all
    python orchestrator.py estimate --phases all
"""

import asyncio
import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
import logging
import yaml

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services import (
    PerplexityHandler, GeminiHandler, ChatGPTHandler, 
    CopilotHandler, GrokHandler
)
from utils import PromptLibrary, ResultAggregator, GateValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("orchestrator")


@dataclass
class PhaseConfig:
    """Configuration for a single phase."""
    name: str
    phase_number: int
    tasks: List[str]
    services: Dict[str, str]  # task_name -> service_name
    gate_required: bool = True
    parallel_limit: int = 2
    timeout_seconds: int = 300


@dataclass
class OrchestratorConfig:
    """Full orchestrator configuration."""
    api_keys: Dict[str, str] = field(default_factory=dict)
    output_dir: str = "./results"
    prompts_dir: str = "./prompts"
    service_config: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    phases: List[PhaseConfig] = field(default_factory=list)


class OmniOrchestrator:
    """Main orchestration engine."""
    
    # Default phase configurations
    DEFAULT_PHASES = [
        PhaseConfig(
            name="research_validation",
            phase_number=1,
            tasks=["precedent_verification", "funding_landscape"],
            services={
                "precedent_verification": "perplexity",
                "funding_landscape": "perplexity",
            },
            parallel_limit=2,
            timeout_seconds=300,
        ),
        PhaseConfig(
            name="spec_hardening",
            phase_number=2,
            tasks=["edge_case_matrix", "latency_constraints"],
            services={
                "edge_case_matrix": "gemini",
                "latency_constraints": "gemini",
            },
            parallel_limit=2,
            timeout_seconds=600,
        ),
        PhaseConfig(
            name="messaging_synthesis",
            phase_number=3,
            tasks=["grant_narrative_nsf", "grant_narrative_neh", "grant_narrative_ars", "artist_statement"],
            services={
                "grant_narrative_nsf": "chatgpt",
                "grant_narrative_neh": "chatgpt",
                "grant_narrative_ars": "chatgpt",
                "artist_statement": "chatgpt",
            },
            parallel_limit=3,
            timeout_seconds=300,
        ),
        PhaseConfig(
            name="implementation_planning",
            phase_number=4,
            tasks=["code_architecture", "budget_allocation"],
            services={
                "code_architecture": "copilot",
                "budget_allocation": "copilot",
            },
            parallel_limit=2,
            timeout_seconds=300,
        ),
        PhaseConfig(
            name="vulnerability_audit",
            phase_number=5,
            tasks=["assumption_critique", "failure_scenarios"],
            services={
                "assumption_critique": "grok",
                "failure_scenarios": "grok",
            },
            gate_required=False,  # Final phase, synthesized manually
            parallel_limit=2,
            timeout_seconds=300,
        ),
    ]
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize orchestrator with configuration."""
        self.config = self._load_config(config_path)
        self.output_dir = Path(self.config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize prompt library
        self.prompts = PromptLibrary(Path(self.config.prompts_dir))
        
        # Initialize service handlers
        self.services: Dict[str, Any] = {}
        self._initialize_services()
        
        # Initialize utilities
        self.aggregator = ResultAggregator()
        self.gate_validator = GateValidator()
        
        # Track execution state
        self.current_phase: Optional[int] = None
        self.execution_log: List[Dict[str, Any]] = []
    
    def _load_config(self, config_path: Optional[str]) -> OrchestratorConfig:
        """Load configuration from YAML file or environment."""
        config = OrchestratorConfig()
        
        # Try loading from file
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                yaml_config = yaml.safe_load(f)
            
            config.output_dir = yaml_config.get("output_dir", config.output_dir)
            config.prompts_dir = yaml_config.get("prompts_dir", config.prompts_dir)
            config.service_config = yaml_config.get("service_config", {})
            
            # API keys from config file (may reference env vars)
            api_keys = yaml_config.get("api_keys", {})
            for service, key in api_keys.items():
                if isinstance(key, str) and key.startswith("${") and key.endswith("}"):
                    env_var = key[2:-1]
                    config.api_keys[service] = os.environ.get(env_var, "")
                else:
                    config.api_keys[service] = key
        
        # Override with environment variables
        env_mappings = {
            "perplexity": "PERPLEXITY_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "chatgpt": "OPENAI_API_KEY",
            "copilot": "OPENAI_API_KEY",  # Copilot uses OpenAI
            "grok": "GROK_API_KEY",
        }
        
        for service, env_var in env_mappings.items():
            env_key = os.environ.get(env_var)
            if env_key:
                config.api_keys[service] = env_key
        
        return config
    
    def _initialize_services(self) -> None:
        """Initialize all service handlers."""
        service_classes = {
            "perplexity": PerplexityHandler,
            "gemini": GeminiHandler,
            "chatgpt": ChatGPTHandler,
            "copilot": CopilotHandler,
            "grok": GrokHandler,
        }
        
        for name, handler_class in service_classes.items():
            api_key = self.config.api_keys.get(name, "")  # allow-secret
            self.services[name] = handler_class(api_key)
    
    async def run_phase(
        self, 
        phase: PhaseConfig, 
        context: Optional[Dict[str, Any]] = None,
        pause_at_gate: bool = False
    ) -> bool:
        """
        Execute a single phase with parallel task execution.
        
        Args:
            phase: Phase configuration
            context: Optional context to inject into prompts
            pause_at_gate: Whether to pause for human review at gate
            
        Returns:
            True if phase passed gate, False otherwise
        """
        logger.info(f"Starting Phase {phase.phase_number}: {phase.name}")
        self.current_phase = phase.phase_number
        
        # Prepare tasks
        tasks = []
        for task_name in phase.tasks:
            service_name = phase.services[task_name]
            handler = self.services.get(service_name)
            
            if not handler:
                logger.error(f"Service not found: {service_name}")
                continue
            
            if not handler.is_available():
                logger.warning(f"Service {service_name} not configured (missing API key)")
                continue
            
            # Load prompt template
            try:
                prompt = self.prompts.get(
                    self._phase_to_folder(phase.name),
                    task_name,
                    context
                )
            except FileNotFoundError:
                logger.warning(f"Prompt template not found: {phase.name}/{task_name}")
                prompt = f"Execute task: {task_name}"
            
            tasks.append((task_name, service_name, handler, prompt))
        
        # Execute tasks with parallel limit
        semaphore = asyncio.Semaphore(phase.parallel_limit)
        
        async def bounded_execute(task_name, handler, prompt):
            async with semaphore:
                return await handler.execute(
                    prompt=prompt,
                    task_name=task_name,
                    timeout=phase.timeout_seconds
                )
        
        # Run all tasks
        coroutines = [
            bounded_execute(task_name, handler, prompt)
            for task_name, _, handler, prompt in tasks
        ]
        
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Process results
        phase_results = {}
        for (task_name, service_name, _, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Task {task_name} failed with exception: {result}")
                phase_results[task_name] = {
                    "status": "error",
                    "error": str(result),
                    "service": service_name
                }
            else:
                phase_results[task_name] = result
                self._save_result(phase, task_name, result)
                self.aggregator.add_result(phase.name, task_name, result)
        
        # Log execution
        self.execution_log.append({
            "phase": phase.phase_number,
            "name": phase.name,
            "tasks_attempted": len(tasks),
            "tasks_succeeded": sum(
                1 for r in phase_results.values() 
                if r.get("status") == "success"
            ),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        
        # Gate validation
        if phase.gate_required:
            gate_pass = await self._validate_gate(phase, phase_results, pause_at_gate)
            if not gate_pass:
                logger.warning(f"Phase {phase.phase_number} gate not passed")
                return False
        
        logger.info(f"Phase {phase.phase_number} complete")
        return True
    
    def _phase_to_folder(self, phase_name: str) -> str:
        """Convert phase name to folder name."""
        folder_map = {
            "research_validation": "phase1_research",
            "spec_hardening": "phase2_specification",
            "messaging_synthesis": "phase3_messaging",
            "implementation_planning": "phase4_implementation",
            "vulnerability_audit": "phase5_vulnerability",
        }
        return folder_map.get(phase_name, phase_name)
    
    async def _validate_gate(
        self, 
        phase: PhaseConfig, 
        results: Dict[str, Any],
        pause: bool
    ) -> bool:
        """Validate phase gate and optionally pause for review."""
        validation = await self.gate_validator.validate(
            gate_prompt="",  # Using rule-based validation
            phase_results=results,
            gate_number=phase.phase_number
        )
        
        logger.info(f"Gate {phase.phase_number} validation: {validation['status']}")
        
        # Save gate result
        gate_path = self.output_dir / f"phase{phase.phase_number}_{phase.name}" / "gate_result.json"
        gate_path.parent.mkdir(parents=True, exist_ok=True)
        with open(gate_path, 'w') as f:
            json.dump(validation, f, indent=2)
        
        if pause:
            print(f"\n{'='*60}")
            print(f"GATE {phase.phase_number} REVIEW")
            print(f"{'='*60}")
            print(f"Status: {validation['status']}")
            print(f"Output directory: {self.output_dir / f'phase{phase.phase_number}_{phase.name}'}")
            
            if validation.get('recommendations'):
                print("\nRecommendations:")
                for rec in validation['recommendations']:
                    print(f"  - {rec}")
            
            if validation.get('blocking_issues'):
                print("\nBlocking Issues:")
                for issue in validation['blocking_issues']:
                    print(f"  ⚠️  {issue}")
            
            response = input("\nContinue to next phase? [y/n/r(revise)]: ").strip().lower()
            if response == 'r':
                logger.info("User requested revision")
                return False
            elif response != 'y':
                logger.info("User halted pipeline")
                return False
        
        return validation['pass']
    
    def _save_result(self, phase: PhaseConfig, task_name: str, result: Dict[str, Any]) -> None:
        """Save task result to output directory."""
        phase_dir = self.output_dir / f"phase{phase.phase_number}_{phase.name}"
        phase_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_path = phase_dir / f"{task_name}.json"
        with open(json_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        # Save markdown content if present
        content = result.get("content")
        if content:
            md_path = phase_dir / f"{task_name}.md"
            with open(md_path, 'w') as f:
                f.write(content)
        
        logger.info(f"Saved result: {json_path}")
    
    async def run_all_phases(
        self,
        gates: bool = True,
        pause_at_gates: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Execute full orchestration pipeline.
        
        Args:
            gates: Whether to enforce gate validation
            pause_at_gates: Whether to pause for human review at each gate
            context: Optional context to inject into all prompts
            
        Returns:
            True if all phases completed successfully
        """
        phases = self.DEFAULT_PHASES.copy()
        
        # Update gate requirements based on argument
        for phase in phases:
            if not gates:
                phase.gate_required = False
        
        for phase in phases:
            success = await self.run_phase(phase, context, pause_at_gates)
            if not success:
                logger.error(f"Pipeline halted at Phase {phase.phase_number}")
                return False
        
        logger.info("All phases complete. Generating synthesis report...")
        await self._generate_synthesis_report()
        return True
    
    async def run_single_phase(
        self,
        phase_name: str,
        pause_at_gate: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Run a single phase by name."""
        phase_map = {p.name: p for p in self.DEFAULT_PHASES}
        
        if phase_name not in phase_map:
            logger.error(f"Unknown phase: {phase_name}")
            logger.info(f"Available phases: {list(phase_map.keys())}")
            return False
        
        return await self.run_phase(phase_map[phase_name], context, pause_at_gate)
    
    async def _generate_synthesis_report(self) -> None:
        """Generate and save executive synthesis report."""
        report = await self.aggregator.synthesize()
        
        report_path = self.output_dir / "EXECUTIVE_REPORT.md"
        with open(report_path, 'w') as f:
            f.write(report)
        
        # Also save aggregated data
        self.aggregator.save_to_file(self.output_dir / "aggregated_results.json")
        
        logger.info(f"Executive report saved: {report_path}")
    
    def check_service_status(self) -> Dict[str, bool]:
        """Check availability of all services."""
        status = {}
        for name, handler in self.services.items():
            status[name] = handler.is_available()
        return status
    
    def estimate_costs(self) -> Dict[str, Any]:
        """Estimate API costs for full pipeline run."""
        # Rough estimates based on typical usage
        estimates = {
            "perplexity": {"tasks": 2, "tokens_per_task": 3000, "cost_per_1k": 0.002},
            "gemini": {"tasks": 2, "tokens_per_task": 8000, "cost_per_1k": 0.00125},
            "chatgpt": {"tasks": 4, "tokens_per_task": 4000, "cost_per_1k": 0.01},
            "copilot": {"tasks": 2, "tokens_per_task": 3000, "cost_per_1k": 0.01},
            "grok": {"tasks": 2, "tokens_per_task": 3000, "cost_per_1k": 0.005},
        }
        
        total = 0
        breakdown = {}
        
        for service, params in estimates.items():
            tokens = params["tasks"] * params["tokens_per_task"]
            cost = (tokens / 1000) * params["cost_per_1k"]
            breakdown[service] = {
                "tasks": params["tasks"],
                "estimated_tokens": tokens,
                "estimated_cost_usd": round(cost, 2)
            }
            total += cost
        
        return {
            "breakdown": breakdown,
            "total_estimated_usd": round(total, 2),
            "note": "Estimates based on typical usage. Actual costs may vary."
        }
    
    async def cleanup(self) -> None:
        """Close all service connections."""
        for handler in self.services.values():
            if hasattr(handler, 'close'):
                await handler.close()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Omni-Performative Engine: Multi-AI Orchestration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run --phase all --gates --output-dir ./results
  %(prog)s run --phase research-validation --pause-at-gate
  %(prog)s status --services all
  %(prog)s estimate --phases all
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run orchestration pipeline")
    run_parser.add_argument(
        "--phase",
        choices=["all", "research-validation", "spec-hardening", 
                 "messaging-synthesis", "implementation-planning", 
                 "vulnerability-audit"],
        default="all",
        help="Which phase(s) to run"
    )
    run_parser.add_argument(
        "--gates",
        action="store_true",
        default=True,
        help="Enable gate validation between phases"
    )
    run_parser.add_argument(
        "--no-gates",
        action="store_true",
        help="Disable gate validation"
    )
    run_parser.add_argument(
        "--pause-at-gate",
        action="store_true",
        help="Pause for human review at each gate"
    )
    run_parser.add_argument(
        "--output-dir",
        default="./results",
        help="Output directory for results"
    )
    run_parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file"
    )
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check service status")
    status_parser.add_argument(
        "--services",
        default="all",
        help="Which services to check (all or comma-separated list)"
    )
    
    # Estimate command
    estimate_parser = subparsers.add_parser("estimate", help="Estimate API costs")
    estimate_parser.add_argument(
        "--phases",
        default="all",
        help="Which phases to estimate"
    )
    
    # Synthesis command
    synthesis_parser = subparsers.add_parser("synthesis", help="Generate synthesis report")
    synthesis_parser.add_argument(
        "--input-dir",
        required=True,
        help="Directory containing phase results"
    )
    synthesis_parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize orchestrator
    config_path = getattr(args, 'config', 'config.yaml')
    orchestrator = OmniOrchestrator(config_path)
    
    if args.command == "status":
        status = orchestrator.check_service_status()
        print("\nService Status:")
        print("-" * 30)
        for service, available in status.items():
            icon = "✓" if available else "✗"
            print(f"  {icon} {service}")
        print()
        
    elif args.command == "estimate":
        estimates = orchestrator.estimate_costs()
        print("\nCost Estimates:")
        print("-" * 50)
        for service, data in estimates["breakdown"].items():
            print(f"  {service}: ~${data['estimated_cost_usd']:.2f} ({data['tasks']} tasks)")
        print("-" * 50)
        print(f"  Total: ~${estimates['total_estimated_usd']:.2f}")
        print(f"\n  Note: {estimates['note']}\n")
        
    elif args.command == "run":
        # Update output dir from args
        orchestrator.output_dir = Path(args.output_dir)
        orchestrator.output_dir.mkdir(parents=True, exist_ok=True)
        
        gates = not args.no_gates if hasattr(args, 'no_gates') else args.gates
        
        async def run():
            try:
                if args.phase == "all":
                    success = await orchestrator.run_all_phases(
                        gates=gates,
                        pause_at_gates=args.pause_at_gate
                    )
                else:
                    phase_name = args.phase.replace("-", "_")
                    success = await orchestrator.run_single_phase(
                        phase_name,
                        pause_at_gate=args.pause_at_gate
                    )
                
                if success:
                    print(f"\n✓ Pipeline completed successfully")
                    print(f"  Results: {orchestrator.output_dir}")
                else:
                    print(f"\n✗ Pipeline halted")
                    print(f"  Check logs and results in: {orchestrator.output_dir}")
                    
            finally:
                await orchestrator.cleanup()
        
        asyncio.run(run())
        
    elif args.command == "synthesis":
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            print(f"Error: Input directory not found: {input_dir}")
            return
        
        # Load results and generate synthesis
        aggregator = ResultAggregator.load_from_file(
            input_dir / "aggregated_results.json"
        )
        
        async def synthesize():
            report = await aggregator.synthesize()
            if args.format == "markdown":
                print(report)
            else:
                print(json.dumps(aggregator.generate_summary(), indent=2))
        
        asyncio.run(synthesize())


if __name__ == "__main__":
    main()
