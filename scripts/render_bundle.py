#!/usr/bin/env python3
"""
Databricks Asset Bundles (DABs) Jinja2 Pre-render Script
Reads template files from bundle/ and renders them into dist_bundle/
"""

import os
import sys
import re
import shutil
from pathlib import Path

# Add user site-packages if available on macOS/Linux
user_site = os.path.expanduser("~/Library/Python/3.9/lib/python/site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

from jinja2 import Environment, FileSystemLoader

PROJECT_ROOT = Path(__file__).parent.parent
BUNDLE_DIR = PROJECT_ROOT / "bundle"
OUTPUT_DIR = PROJECT_ROOT / "dist_bundle" / "resources"


def clean_output_dir(output_dir: Path) -> None:
    """Clean and recreate the output directory."""
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def get_target_environment() -> str:
    """Extract BUNDLE_TARGET environment variable."""
    target = os.getenv("BUNDLE_TARGET", "dev").lower()
    valid_targets = {"dev", "staging", "prod"}
    if target not in valid_targets:
        print(f"Error: BUNDLE_TARGET must be one of {valid_targets}, got '{target}'", file=sys.stderr)
        sys.exit(1)
    return target


def glob_files(pattern: str) -> list:
    """Discover files using glob pattern relative to PROJECT_ROOT."""
    matched = sorted(PROJECT_ROOT.glob(pattern))
    return [p.relative_to(PROJECT_ROOT).as_posix() for p in matched if p.is_file()]


def render_templates() -> None:
    """Discover and render all Jinja2 template files."""
    target_env = get_target_environment()
    print(f"🚀 Rendering DAB Jinja2 templates for environment: [{target_env}]...")

    clean_output_dir(OUTPUT_DIR)

    # Initialize Jinja2 Environment
    jinja_env = Environment(
        loader=FileSystemLoader(str(BUNDLE_DIR)),
        trim_blocks=False,
        lstrip_blocks=False
    )
    # Register helper functions
    jinja_env.globals["glob_files"] = glob_files

    context = {
        "environment": target_env,
        "is_prod": target_env == "prod",
    }

    rendered_count = 0
    for template_path in BUNDLE_DIR.rglob("*.yml.j2"):
        relative_path = template_path.relative_to(BUNDLE_DIR)
        if relative_path.parts[0] == "includes":
            continue

        print(f"  └─ Rendering {relative_path}...")
        template = jinja_env.get_template(str(relative_path.as_posix()))
        rendered_content = template.render(context)

        # Post-process:
        # 1. Clean up lines containing only spaces or tabs
        clean_content = re.sub(r'^[ \t]+$', '', rendered_content, flags=re.MULTILINE)
        # 2. Collapse 3+ consecutive newlines into a single blank line (max 1 empty line between blocks)
        clean_content = re.sub(r'\n{3,}', '\n\n', clean_content).strip() + "\n"

        output_filename = template_path.stem
        destination = OUTPUT_DIR / output_filename
        destination.write_text(clean_content, encoding="utf-8")
        rendered_count += 1

    print(f"✅ Successfully rendered {rendered_count} DAB YAML resources to '{OUTPUT_DIR.relative_to(PROJECT_ROOT)}'.\n")


if __name__ == "__main__":
    render_templates()
