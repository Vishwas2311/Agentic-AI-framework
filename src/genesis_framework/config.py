from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class GenesisPaths:
    root: Path

    @property
    def config_dir(self) -> Path:
        return self.root / ".genesis"

    @property
    def flow_file(self) -> Path:
        return self.config_dir / "genesis.flow.yaml"

    @property
    def tools_file(self) -> Path:
        return self.config_dir / "genesis.tools.yaml"

    @property
    def policy_file(self) -> Path:
        return self.config_dir / "genesis.policy.yaml"

    @property
    def outputs_file(self) -> Path:
        return self.config_dir / "genesis.outputs.yaml"

    @property
    def routing_file(self) -> Path:
        return self.config_dir / "genesis.routing.yaml"

    @property
    def prompting_file(self) -> Path:
        return self.config_dir / "genesis.prompting.yaml"

    @property
    def install_file(self) -> Path:
        return self.config_dir / "genesis.install.yaml"

    @property
    def design_file(self) -> Path:
        return self.config_dir / "genesis.design.yaml"

    @property
    def design_quality_file(self) -> Path:
        return self.config_dir / "genesis.design_quality.yaml"

    @property
    def stack_file(self) -> Path:
        return self.config_dir / "genesis.stack.yaml"

    @property
    def qa_file(self) -> Path:
        return self.config_dir / "genesis.qa.yaml"

    @property
    def agents_file(self) -> Path:
        return self.config_dir / "genesis.agents.yaml"

    @property
    def cost_file(self) -> Path:
        return self.config_dir / "genesis.cost.yaml"

    @property
    def memory_file(self) -> Path:
        return self.config_dir / "genesis.memory.yaml"

    @property
    def capabilities_file(self) -> Path:
        return self.config_dir / "genesis.capabilities.yaml"

    @property
    def deploy_file(self) -> Path:
        return self.config_dir / "genesis.deploy.yaml"


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".genesis" / "genesis.flow.yaml").exists():
            return candidate
    raise FileNotFoundError("Could not find .genesis/genesis.flow.yaml from current directory.")


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required Genesis config: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


def load_all(root: Path) -> dict[str, dict[str, Any]]:
    paths = GenesisPaths(root)
    return {
        "flow": load_yaml(paths.flow_file),
        "tools": load_yaml(paths.tools_file),
        "policy": load_yaml(paths.policy_file),
        "outputs": load_yaml(paths.outputs_file),
        "routing": load_yaml(paths.routing_file),
        "prompting": load_yaml(paths.prompting_file),
        "install": load_yaml(paths.install_file),
        "design": load_yaml(paths.design_file),
        "design_quality": load_yaml(paths.design_quality_file),
        "stack": load_yaml(paths.stack_file),
        "qa": load_yaml(paths.qa_file),
        "agents": load_yaml(paths.agents_file),
        "cost": load_yaml(paths.cost_file),
        "memory": load_yaml(paths.memory_file),
        "capabilities": load_yaml(paths.capabilities_file),
        "deploy": load_yaml(paths.deploy_file),
    }
