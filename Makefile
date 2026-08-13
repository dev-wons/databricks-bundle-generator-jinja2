TARGET ?= dev
TYPE ?= pipeline
NAME ?= sample

.PHONY: help render validate deploy create clean

help:
	@echo "Databricks Asset Bundle (DAB) Jinja2 Build Automation"
	@echo "-----------------------------------------------------"
	@echo "  make render TARGET=dev             - Render Jinja2 templates into dist_bundle/ for target"
	@echo "  make validate TARGET=dev           - Render and run 'databricks bundle validate'"
	@echo "  make deploy TARGET=dev             - Render and run 'databricks bundle deploy'"
	@echo "  make create TYPE=pipeline NAME=foo - Generate template (TYPE=pipeline|workflow|governance)"
	@echo "  make clean                         - Remove dist_bundle directory"

create:
	@python3 scripts/create_template.py $(TYPE) $(NAME)

render:
	@echo "🔨 Building DAB templates for TARGET=$(TARGET)..."
	BUNDLE_TARGET=$(TARGET) python3 scripts/render_bundle.py

validate: render
	@echo "🔍 Validating Databricks Asset Bundle for TARGET=$(TARGET)..."
	databricks bundle validate -t $(TARGET)

deploy: validate
	@echo "🚀 Deploying Databricks Asset Bundle for TARGET=$(TARGET)..."
	databricks bundle deploy -t $(TARGET)

clean:
	@echo "🧹 Cleaning dist_bundle directory..."
	rm -rf dist_bundle
