#!/usr/bin/env python3
"""
Databricks Asset Bundles (DABs) Template Generator
Generates boilerplate Jinja2 pipeline/workflow/governance templates in bundle/
"""

import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
BUNDLE_DIR = PROJECT_ROOT / "bundle"

PIPELINE_BOILERPLATE = """# bundle/pipelines/{name}_pipeline.yml.j2
resources:
  pipelines:
    {name}_dlt_pipeline:
      name: "[{{ environment }}] {title_name} DLT Pipeline"
      catalog: "${var.catalog}"
      target: "${var.schema_prefix}_{name}"

      edition: ADVANCED
      channel: CURRENT
      continuous: false
      development: {% if environment != 'prod' %}true{% else %}false{% endif %}

      # Compute Configuration (Serverless compute enabled)
      serverless: true

      # Libraries & Code Sources (Folder paths via file:)
      libraries:
        - file:
            path: ../../src/models/{name}

      # Runtime Configuration
      configuration:
        bundle.target: "${bundle.target}"
        catalog: "${var.catalog}"
        schema_prefix: "${var.schema_prefix}"

      # Trigger & Schedule
      {% if environment == 'prod' %}
      trigger:
        cron:
{% filter indent(10) %}
{% include "includes/schedule.yml.j2" %}
{% endfilter %}
      {% endif %}

      # Governance, Tags & Permissions
{% filter indent(6) %}
{% include "includes/tags.yml.j2" %}
{% include "includes/permissions.yml.j2" %}
{% endfilter %}

      notifications:
        - email_recipients:
            - dev-alerts@company.com
          alerts:
            - "on-update-failure"
"""

WORKFLOW_BOILERPLATE = """# bundle/workflows/{name}_workflow.yml.j2
resources:
  jobs:
    {name}_workflow:
      name: "[{{ environment }}] {title_name} Workflow"

      # Tasks Execution Graph
      tasks:
        - task_key: run_{name}_task
          notebook_task:
            notebook_path: ../../src/jobs/{name}_job.py

      # Schedule
      {% if environment == 'prod' %}
      schedule:
{% filter indent(8) %}
{% include "includes/schedule.yml.j2" %}
{% endfilter %}
      {% endif %}

      # Governance, Tags & Permissions
{% filter indent(6) %}
{% include "includes/tags.yml.j2" %}
{% include "includes/permissions.yml.j2" %}
{% endfilter %}

      email_notifications:
        on_failure:
          - dev-alerts@company.com
"""

GOVERNANCE_BOILERPLATE = """# bundle/governance/{name}_governance.yml.j2
resources:
  schemas:
    {name}_schema:
      name: "${var.schema_prefix}_{name}"
      catalog_name: "${var.catalog}"
      comment: "Managed schema for {title_name} in {{ environment }} environment"

      {% if environment == 'prod' %}
      grants:
        - principal: "users"
          privileges:
            - "USE_SCHEMA"
            - "SELECT"
      {% else %}
      grants:
        - principal: "${workspace.current_user.userName}"
          privileges:
            - "ALL_PRIVILEGES"
      {% endif %}

  volumes:
    {name}_landing_volume:
      name: "{name}_raw"
      catalog_name: "${var.catalog}"
      schema_name: "${var.schema_prefix}_{name}"
      volume_type: "MANAGED"
      comment: "Managed volume for {title_name} raw files in {{ environment }}"

      {% if environment == 'prod' %}
      grants:
        - principal: "users"
          privileges:
            - "READ_VOLUME"
            - "WRITE_VOLUME"
      {% else %}
      grants:
        - principal: "${workspace.current_user.userName}"
          privileges:
            - "READ_VOLUME"
            - "WRITE_VOLUME"
      {% endif %}
"""


def main():
    parser = argparse.ArgumentParser(description="Create a new Jinja2 template for DABs")
    parser.add_argument("type", choices=["pipeline", "workflow", "governance"], help="Template type (pipeline, workflow, governance)")
    parser.add_argument("name", help="Name of the resource (e.g. sales_analytics)")

    args = parser.parse_args()

    target_type = args.type.lower()
    raw_name = args.name.lower().replace("-", "_").replace(" ", "_")
    title_name = raw_name.replace("_", " ").title()

    if target_type == "pipeline":
        target_dir = BUNDLE_DIR / "pipelines"
        target_file = target_dir / f"{raw_name}_pipeline.yml.j2"
        content = PIPELINE_BOILERPLATE.replace("{name}", raw_name).replace("{title_name}", title_name)
    elif target_type == "workflow":
        target_dir = BUNDLE_DIR / "workflows"
        target_file = target_dir / f"{raw_name}_workflow.yml.j2"
        content = WORKFLOW_BOILERPLATE.replace("{name}", raw_name).replace("{title_name}", title_name)
    else:
        target_dir = BUNDLE_DIR / "governance"
        target_file = target_dir / f"{raw_name}_governance.yml.j2"
        content = GOVERNANCE_BOILERPLATE.replace("{name}", raw_name).replace("{title_name}", title_name)

    target_dir.mkdir(parents=True, exist_ok=True)

    if target_file.exists():
        print(f"❌ Error: File '{target_file.relative_to(PROJECT_ROOT)}' already exists!", file=sys.stderr)
        sys.exit(1)

    target_file.write_text(content, encoding="utf-8")
    print(f"✨ Successfully created new {target_type} template: '{target_file.relative_to(PROJECT_ROOT)}'")
    print(f"💡 Run 'make render' to render all templates into dist_bundle/.\n")


if __name__ == "__main__":
    main()
