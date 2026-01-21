#!/usr/bin/env python3
"""Validate Claude Code plugins structure and configuration."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

PLUGINS_DIR = Path("plugins")
MARKETPLACE_FILE = Path(".claude-plugin/marketplace.json")

REQUIRED_PLUGIN_FIELDS = ("name", "version", "description")
REQUIRED_MARKETPLACE_FIELDS = ("name", "description", "plugins")
REQUIRED_MARKETPLACE_PLUGIN_FIELDS = ("name", "version", "description", "source")


@dataclass
class ValidationResult:
    """Result of a single validation check."""

    plugin: str
    check: str
    passed: bool
    message: str = ""


@dataclass
class ValidationReport:
    """Aggregated validation report."""

    results: list[ValidationResult] = field(default_factory=list)

    def add(
        self,
        plugin: str,
        check: str,
        passed: bool,
        message: str = "",
    ) -> None:
        self.results.append(ValidationResult(plugin, check, passed, message))

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    @property
    def errors(self) -> Sequence[ValidationResult]:
        return [r for r in self.results if not r.passed]

    @property
    def warnings(self) -> Sequence[ValidationResult]:
        return [r for r in self.results if r.passed and r.message.startswith("WARN")]

    def print_summary(self) -> None:
        print("\n" + "=" * 50)
        print("VALIDATION SUMMARY")
        print("=" * 50)

        plugins = {r.plugin for r in self.results if r.plugin != "marketplace"}
        print(f"Plugins validated: {len(plugins)}")

        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for err in self.errors:
                print(f"  [{err.plugin}] {err.check}: {err.message}")

        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warn in self.warnings:
                print(f"  [{warn.plugin}] {warn.check}: {warn.message}")

        if self.passed:
            print("\nAll validations passed!")
        else:
            print(f"\nValidation FAILED with {len(self.errors)} error(s)")


def load_json(path: Path) -> dict | None:
    """Load and parse JSON file, return None on error."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def validate_plugin_json(
    plugin_dir: Path,
    report: ValidationReport,
) -> dict | None:
    """Validate plugin.json exists and has required fields."""
    plugin_name = plugin_dir.name
    manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"

    if not manifest_path.exists():
        report.add(plugin_name, "plugin.json", False, "File not found")
        return None

    data = load_json(manifest_path)
    if data is None:
        report.add(plugin_name, "plugin.json", False, "Invalid JSON syntax")
        return None

    missing = [f for f in REQUIRED_PLUGIN_FIELDS if f not in data]
    if missing:
        report.add(
            plugin_name,
            "plugin.json",
            False,
            f"Missing required fields: {missing}",
        )
        return None

    report.add(plugin_name, "plugin.json", True)
    return data


def validate_readme(plugin_dir: Path, report: ValidationReport) -> None:
    """Validate README.md exists."""
    plugin_name = plugin_dir.name
    readme_path = plugin_dir / "README.md"

    if readme_path.exists():
        report.add(plugin_name, "README.md", True)
    else:
        report.add(plugin_name, "README.md", False, "File not found")


def validate_skill(plugin_dir: Path, report: ValidationReport) -> None:
    """Validate at least one SKILL.md exists."""
    plugin_name = plugin_dir.name
    skills_dir = plugin_dir / "skills"

    if not skills_dir.exists():
        report.add(plugin_name, "SKILL.md", True, "WARNING: No skills directory")
        return

    skill_files = list(skills_dir.glob("*/SKILL.md"))
    if skill_files:
        report.add(plugin_name, "SKILL.md", True)
    else:
        report.add(plugin_name, "SKILL.md", True, "WARNING: No SKILL.md found")


def validate_commands(plugin_dir: Path, report: ValidationReport) -> None:
    """Validate commands directory has .md files."""
    plugin_name = plugin_dir.name
    commands_dir = plugin_dir / "commands"

    if not commands_dir.exists():
        report.add(plugin_name, "commands", True, "WARNING: No commands directory")
        return

    command_files = list(commands_dir.glob("*.md"))
    if command_files:
        report.add(plugin_name, "commands", True)
    else:
        report.add(plugin_name, "commands", True, "WARNING: No command files found")


def validate_marketplace(
    report: ValidationReport,
    plugin_configs: dict[str, dict],
) -> None:
    """Validate marketplace.json exists and is consistent with plugins."""
    if not MARKETPLACE_FILE.exists():
        report.add("marketplace", "marketplace.json", True, "WARNING: File not found")
        return

    data = load_json(MARKETPLACE_FILE)
    if data is None:
        report.add("marketplace", "marketplace.json", False, "Invalid JSON syntax")
        return

    missing = [f for f in REQUIRED_MARKETPLACE_FIELDS if f not in data]
    if missing:
        report.add(
            "marketplace",
            "marketplace.json",
            False,
            f"Missing required fields: {missing}",
        )
        return

    report.add("marketplace", "marketplace.json", True)

    # Validate each plugin entry in marketplace
    for mp_plugin in data.get("plugins", []):
        mp_name = mp_plugin.get("name", "unknown")
        missing_fields = [
            f for f in REQUIRED_MARKETPLACE_PLUGIN_FIELDS if f not in mp_plugin
        ]
        if missing_fields:
            report.add(
                "marketplace",
                f"plugin:{mp_name}",
                False,
                f"Missing fields: {missing_fields}",
            )
            continue

        # Check version consistency
        if mp_name in plugin_configs:
            plugin_version = plugin_configs[mp_name].get("version")
            mp_version = mp_plugin.get("version")
            if plugin_version != mp_version:
                report.add(
                    "marketplace",
                    f"version:{mp_name}",
                    False,
                    f"Version mismatch: plugin.json={plugin_version}, "
                    f"marketplace.json={mp_version}",
                )
            else:
                report.add("marketplace", f"version:{mp_name}", True)


def validate_plugin(plugin_dir: Path, report: ValidationReport) -> dict | None:
    """Run all validations for a single plugin."""
    print(f"Validating {plugin_dir.name}...")

    config = validate_plugin_json(plugin_dir, report)
    validate_readme(plugin_dir, report)
    validate_skill(plugin_dir, report)
    validate_commands(plugin_dir, report)

    return config


def main() -> int:
    """Run all validations and return exit code."""
    report = ValidationReport()
    plugin_configs: dict[str, dict] = {}

    if not PLUGINS_DIR.exists():
        print(f"ERROR: Plugins directory not found: {PLUGINS_DIR}")
        return 1

    plugin_dirs = sorted(PLUGINS_DIR.iterdir())
    plugin_dirs = [d for d in plugin_dirs if d.is_dir()]

    if not plugin_dirs:
        print("ERROR: No plugins found")
        return 1

    # Validate each plugin
    for plugin_dir in plugin_dirs:
        config = validate_plugin(plugin_dir, report)
        if config:
            plugin_configs[plugin_dir.name] = config

    # Validate marketplace
    print("Validating marketplace.json...")
    validate_marketplace(report, plugin_configs)

    report.print_summary()
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
