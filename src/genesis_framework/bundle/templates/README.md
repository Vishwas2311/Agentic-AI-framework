# templates/ — Code Generation Templates

Jinja2 templates used by the scaffold generator (`src/genesis_framework/generation/scaffold.py`) to produce boilerplate output files. These are deterministic — no AI, just template rendering with extracted variables.

```
templates/
├── react/          Next.js / React page template
├── database/       SQL migration template
├── cicd/           GitHub Actions CI/CD template
├── docker/         Dockerfile template
├── java-spring/    Spring Boot entity class template
└── kubernetes/     Kubernetes deployment manifest template
```

---

## Templates

| Template | Output | Variables injected |
|---|---|---|
| `react/page.tsx.jinja2` | Next.js page component | screen_name, components, entities, nav_targets |
| `database/migration.sql.jinja2` | SQL schema migration | entities, fields, types, indexes |
| `cicd/github-actions.yml.jinja2` | GitHub Actions workflow | app_name, stack, test_command, deploy_target |
| `docker/Dockerfile.jinja2` | Production Dockerfile | base_image, port, build_command, start_command |
| `java-spring/entity.java.jinja2` | Spring Boot JPA entity | entity_name, fields, types, annotations |
| `kubernetes/deployment.yaml.jinja2` | K8s deployment + service | app_name, image, port, replicas, resources |

---

## How Templates Are Used

The scaffold generator (`TemplateScaffoldGenerator`) renders these via Jinja2 when the evidence confidence is too low for Claude-generated code, or when boilerplate is deterministic enough that AI generation adds no value.

```python
from genesis_framework.generation.scaffold import TemplateScaffoldGenerator

gen = TemplateScaffoldGenerator(templates_dir=Path("templates"))
gen.render("react/page.tsx.jinja2", output_path, context)
```

---

## Adding a New Template

1. Create a `.jinja2` file in the relevant subfolder
2. Use `{{ variable_name }}` for string interpolation and `{% for %}` for loops
3. Register it in `src/genesis_framework/generation/scaffold.py`
