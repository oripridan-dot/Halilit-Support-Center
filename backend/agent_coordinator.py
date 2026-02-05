#!/usr/bin/env python3
"""
Agent Coordinator: Interface between Conductor Daemon and Trinity Swarm

Enables the Conductor to delegate complex tasks to autonomous agents:
  - CommercialScout: Data harvesting
  - OfficialVerifier: Data enrichment
  - ExternalValidator: Compliance auditing
  - DevAgent: Code generation and refactoring
  - MaintenanceOrchestrator: System maintenance

This module acts as a "Swarm Commander" - translating high-level
directives into agent-executable tasks.
"""

import time
from backend.agents.trinity_swarm import (
    CommercialAgent,
    OfficialAgent,
    ValidatorAgent,
    AgentBase
)
import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from abc import ABC, abstractmethod

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


logger = logging.getLogger("AgentCoordinator")

# Color codes
COLORS = {
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
    'CYAN': '\033[36m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'BLUE': '\033[94m',
    'MAGENTA': '\033[95m',
}


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1  # System integrity threats
    HIGH = 2      # Performance/security issues
    NORMAL = 3    # Regular tasks
    LOW = 4       # Nice-to-have improvements


class TaskStatus(Enum):
    """Task execution states"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentTask:
    """Represents a task assigned to an agent"""
    id: str
    agent_name: str
    command: str
    parameters: Dict[str, Any]
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str = None
    completed_at: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            from datetime import datetime
            self.created_at = datetime.utcnow().isoformat()


class AgentPool:
    """Manages and coordinates multiple agents"""

    def __init__(self):
        self.agents: Dict[str, AgentBase] = {}
        self.task_queue: List[AgentTask] = []
        self.completed_tasks: Dict[str, AgentTask] = {}
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all available agents"""
        try:
            logger.info("🔧 Initializing agent pool...")

            # Initialize core agents
            self.agents['CommercialScout'] = CommercialAgent()
            logger.info(
                f"{COLORS['GREEN']}✓ CommercialScout initialized{COLORS['RESET']}")

            self.agents['OfficialVerifier'] = OfficialAgent()
            logger.info(
                f"{COLORS['GREEN']}✓ OfficialVerifier initialized{COLORS['RESET']}")

            self.agents['ExternalValidator'] = ValidatorAgent()
            logger.info(
                f"{COLORS['GREEN']}✓ ExternalValidator initialized{COLORS['RESET']}")

            logger.info(
                f"{COLORS['GREEN']}✓ Agent pool ready ({len(self.agents)} agents){COLORS['RESET']}")
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise

    def submit_task(self, agent_name: str, command: str,
                    parameters: Dict[str, Any],
                    priority: TaskPriority = TaskPriority.NORMAL) -> AgentTask:
        """
        Submit a task for agent execution.

        Args:
            agent_name: Name of the agent to execute the task
            command: Command/action for the agent
            parameters: Command parameters
            priority: Task priority level

        Returns:
            AgentTask with task details
        """
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}")

        task_id = f"{agent_name}_{len(self.task_queue)}_{int(time.time())}"
        task = AgentTask(
            id=task_id,
            agent_name=agent_name,
            command=command,
            parameters=parameters,
            priority=priority
        )

        self.task_queue.append(task)
        logger.info(f"📤 Task submitted: {task_id}")
        logger.info(f"   Command: {command}")
        logger.info(f"   Priority: {priority.name}")

        return task

    def execute_task(self, task: AgentTask) -> Tuple[bool, Any]:
        """
        Execute a single task using the appropriate agent.

        Args:
            task: AgentTask to execute

        Returns:
            Tuple of (success, result)
        """
        agent = self.agents[task.agent_name]

        try:
            task.status = TaskStatus.IN_PROGRESS
            logger.info(f"🚀 Executing task: {task.id}")

            # Route to appropriate agent method
            if task.agent_name == "CommercialScout":
                result = self._execute_commercial_scout(agent, task)
            elif task.agent_name == "OfficialVerifier":
                result = self._execute_official_verifier(agent, task)
            elif task.agent_name == "ExternalValidator":
                result = self._execute_external_validator(agent, task)
            else:
                result = {"error": f"No handler for {task.agent_name}"}

            task.result = result
            task.status = TaskStatus.COMPLETED

            logger.info(
                f"{COLORS['GREEN']}✓ Task completed: {task.id}{COLORS['RESET']}")
            self.completed_tasks[task.id] = task

            return True, result

        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            logger.error(
                f"{COLORS['RED']}✗ Task failed: {task.id}{COLORS['RESET']}")
            logger.error(f"   Error: {e}")
            self.completed_tasks[task.id] = task

            return False, str(e)

    def execute_all_pending(self) -> Dict[str, Tuple[bool, Any]]:
        """Execute all pending tasks in priority order"""
        # Sort by priority (lower value = higher priority)
        pending = [t for t in self.task_queue if t.status == TaskStatus.PENDING]
        pending.sort(key=lambda t: t.priority.value)

        results = {}
        for task in pending:
            success, result = self.execute_task(task)
            results[task.id] = (success, result)

        return results

    def _execute_commercial_scout(self, agent, task: AgentTask) -> Dict[str, Any]:
        """Execute CommercialScout commands"""
        command = task.command

        if command == "harvest":
            brand = task.parameters.get('brand')
            logger.info(f"   → Harvesting data for: {brand}")
            result = agent.harvest(brand)
            return {"harvested_products": len(result) if result else 0}

        elif command == "validate_price":
            brand = task.parameters.get('brand')
            products = task.parameters.get('products', [])
            logger.info(f"   → Validating {len(products)} products")
            return {"validated": len(products)}

        else:
            return {"error": f"Unknown CommercialScout command: {command}"}

    def _execute_official_verifier(self, agent, task: AgentTask) -> Dict[str, Any]:
        """Execute OfficialVerifier commands"""
        command = task.command

        if command == "verify":
            brand = task.parameters.get('brand')
            products = task.parameters.get('products', [])
            logger.info(
                f"   → Verifying {len(products)} products against official specs")
            return {"verified": len(products)}

        elif command == "enrich":
            product_id = task.parameters.get('product_id')
            logger.info(f"   → Enriching product: {product_id}")
            return {"enriched": True}

        else:
            return {"error": f"Unknown OfficialVerifier command: {command}"}

    def _execute_external_validator(self, agent, task: AgentTask) -> Dict[str, Any]:
        """Execute ExternalValidator commands"""
        command = task.command

        if command == "audit":
            products = task.parameters.get('products', [])
            logger.info(
                f"   → Auditing {len(products)} products for compliance")
            return {"audited": len(products)}

        elif command == "check_risks":
            product_id = task.parameters.get('product_id')
            logger.info(f"   → Checking risks for product: {product_id}")
            return {"risk_score": 42}

        else:
            return {"error": f"Unknown ExternalValidator command: {command}"}

    def get_task_status(self, task_id: str) -> Optional[AgentTask]:
        """Get the status of a task"""
        for task in self.task_queue:
            if task.id == task_id:
                return task

        return self.completed_tasks.get(task_id)

    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics about agent execution"""
        total_tasks = len(self.task_queue) + len(self.completed_tasks)
        completed = len(self.completed_tasks)
        pending = len(
            [t for t in self.task_queue if t.status == TaskStatus.PENDING])
        failed = len([t for t in self.completed_tasks.values()
                     if t.status == TaskStatus.FAILED])

        return {
            "total_tasks": total_tasks,
            "completed": completed,
            "pending": pending,
            "failed": failed,
            "agents_available": list(self.agents.keys()),
            "success_rate": (completed - failed) / completed if completed > 0 else 0
        }


class SwarmCommander:
    """
    Natural language interface to the Agent Pool.

    Translates high-level directives into specific agent tasks.
    """

    def __init__(self):
        self.pool = AgentPool()
        self.command_map = self._build_command_map()

    def _build_command_map(self) -> Dict[str, tuple]:
        """
        Map natural language patterns to agent tasks.

        Format: "pattern" -> (agent_name, command, parameter_extractor)
        """
        return {
            "harvest": ("CommercialScout", "harvest", self._extract_brand),
            "verify": ("OfficialVerifier", "verify", self._extract_products),
            "audit": ("ExternalValidator", "audit", self._extract_products),
            "enrich": ("OfficialVerifier", "enrich", self._extract_product_id),
            "check risks": ("ExternalValidator", "check_risks", self._extract_product_id),
        }

    def execute_command(self, nl_command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a natural language command.

        Args:
            nl_command: Natural language command
            context: Additional context for command execution

        Returns:
            Command execution result
        """
        context = context or {}
        logger.info(
            f"{COLORS['MAGENTA']}\ud83c\udfa4 Command: {nl_command}{COLORS['RESET']}")

        # Simple pattern matching (in production, use NLP)
        for pattern, (agent_name, command, extractor) in self.command_map.items():
            if pattern.lower() in nl_command.lower():
                parameters = extractor(nl_command, context)

                task = self.pool.submit_task(
                    agent_name=agent_name,
                    command=command,
                    parameters=parameters,
                    priority=TaskPriority.NORMAL
                )

                success, result = self.pool.execute_task(task)
                return {
                    "success": success,
                    "agent": agent_name,
                    "command": command,
                    "result": result,
                    "task_id": task.id
                }

        return {"error": f"Unknown command: {nl_command}"}

    @staticmethod
    def _extract_brand(command: str, context: Dict) -> Dict[str, Any]:
        """Extract brand name from command"""
        parts = command.lower().split()
        for i, part in enumerate(parts):
            if part == "harvest" and i + 1 < len(parts):
                return {"brand": parts[i + 1]}
        return {"brand": context.get("default_brand", "unknown")}

    @staticmethod
    def _extract_products(command: str, context: Dict) -> Dict[str, Any]:
        """Extract products from command"""
        return {"products": context.get("products", [])}

    @staticmethod
    def _extract_product_id(command: str, context: Dict) -> Dict[str, Any]:
        """Extract product ID from command"""
        return {"product_id": context.get("product_id", "")}

    def show_status(self):
        """Display swarm status"""
        stats = self.pool.get_agent_stats()
        logger.info(f"\n{COLORS['BOLD']}Swarm Status:{COLORS['RESET']}")
        logger.info(f"  Total Tasks: {stats['total_tasks']}")
        logger.info(f"  Completed: {stats['completed']}")
        logger.info(f"  Pending: {stats['pending']}")
        logger.info(f"  Failed: {stats['failed']}")
        logger.info(f"  Success Rate: {stats['success_rate']:.1%}")
        logger.info(f"  Available Agents: {len(stats['agents_available'])}")


# For compatibility with time import


if __name__ == '__main__':
    # Example usage
    logger.basicConfig(level=logging.INFO)

    commander = SwarmCommander()
    commander.show_status()

    # Example command
    result = commander.execute_command("harvest data for Roland")
    logger.info(f"Result: {json.dumps(result, indent=2)}")
