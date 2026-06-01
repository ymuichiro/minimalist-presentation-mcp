from __future__ import annotations

import argparse
import sys
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from example.communication_compiler.agent.foundry_agent import AGENT_INSTRUCTIONS


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or update the live Communication Compiler Foundry Agent.")
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--agent-name", required=True)
    parser.add_argument("--model-deployment", required=True)
    args = parser.parse_args()

    project = AIProjectClient(endpoint=args.endpoint, credential=DefaultAzureCredential())
    agent = project.agents.create_version(
        agent_name=args.agent_name,
        definition=PromptAgentDefinition(
            model=args.model_deployment,
            instructions=AGENT_INSTRUCTIONS,
            temperature=0.1,
        ),
    )
    print(f"agent_name={agent.name}")
    print(f"agent_id={agent.id}")
    print(f"agent_version={agent.version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
