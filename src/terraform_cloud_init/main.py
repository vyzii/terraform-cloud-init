#!/usr/bin/env python3
"""Validate action inputs and run `terraform init` for a single backend.

Subcommands:
    validate  Check inputs only (no Terraform needed).
    init      Validate inputs again, then run terraform init.
"""

import argparse
import subprocess
import sys

from terraform_cloud_init.config import Config, load_config
from terraform_cloud_init.terraform import build_init_command
from terraform_cloud_init.validation import ConfigError, validate


def report_errors(errors: list[str]) -> None:
    for error in errors:
        print(f"::error::{error}")


def run_validate(cfg: Config) -> int:
    errors = validate(cfg)
    if errors:
        report_errors(errors)
        return 1

    print("Inputs are valid.")
    return 0


def run_init(cfg: Config) -> int:
    try:
        cmd = build_init_command(cfg)
    except ConfigError as error:
        report_errors(error.errors)
        return 1

    result = subprocess.run(cmd, check=False)
    return result.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate inputs and initialize Terraform."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate", help="Validate action inputs only")
    subparsers.add_parser("init", help="Validate inputs, then run terraform init")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = load_config()

    if args.command == "validate":
        return run_validate(cfg)
    if args.command == "init":
        return run_init(cfg)

    return 1


if __name__ == "__main__":
    sys.exit(main())
