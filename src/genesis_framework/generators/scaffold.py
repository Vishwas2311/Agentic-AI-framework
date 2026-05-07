from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from genesis_framework.generators.base import Generator


class TemplateScaffoldGenerator(Generator):
    def __init__(self, template_root: Path) -> None:
        self.template_root = template_root
        self.environment = Environment(loader=FileSystemLoader(str(template_root)))

    def generate(self, canonical_spec: dict[str, Any], output_dir: Path) -> list[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        generated: list[Path] = []
        app = canonical_spec.get("app", {})
        ui_spec = canonical_spec.get("ui_spec", {})
        domain_spec = canonical_spec.get("domain_spec", {})
        deployment_spec = canonical_spec.get("deployment_spec", {})

        app_name = app.get("name", "Generated App")
        route_screens = ui_spec.get("screens", [])[:20]
        entities = domain_spec.get("entities", [])[:20]

        frontend_package = {
            "name": _slug(app_name),
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "echo \"Add eslint later\"",
            },
            "dependencies": {
                "next": "15.0.0",
                "react": "18.3.1",
                "react-dom": "18.3.1",
            },
        }
        generated.append(_write_json(output_dir / "frontend" / "package.json", frontend_package))
        generated.append(_write_text(output_dir / "frontend" / "tsconfig.json", _frontend_tsconfig()))
        generated.append(_write_text(output_dir / "frontend" / "next.config.js", "/** @type {import('next').NextConfig} */\nmodule.exports = {};\n"))
        generated.append(_write_text(output_dir / "frontend" / "app" / "layout.tsx", _layout_tsx(app_name)))
        generated.append(
            _write_text(
                output_dir / "frontend" / "app" / "page.tsx",
                self._render("react/page.tsx.jinja2", component_name="Home", title=f"{app_name} Home"),
            )
        )
        for screen in route_screens:
            screen_name = str(screen.get("name") or "screen")
            route = _slug(screen_name)
            component_name = "".join(part.capitalize() for part in route.split("-")) or "Screen"
            generated.append(
                _write_text(
                    output_dir / "frontend" / "app" / route / "page.tsx",
                    self._render("react/page.tsx.jinja2", component_name=component_name, title=screen_name),
                )
            )
        generated.append(_write_text(output_dir / "frontend" / "components" / "GeneratedNav.tsx", _navigation_component(route_screens)))

        backend_requirements = "fastapi==0.115.0\nuvicorn[standard]==0.30.6\npydantic==2.9.2\n"
        generated.append(_write_text(output_dir / "backend" / "requirements.txt", backend_requirements))
        generated.append(_write_text(output_dir / "backend" / "app" / "__init__.py", ""))
        generated.append(_write_text(output_dir / "backend" / "app" / "main.py", _backend_main(app_name, entities, route_screens)))

        sql_text = "\n".join(
            self._render("database/migration.sql.jinja2", table_name=_slug(entity.get("name", "entity")).replace("-", "_"))
            for entity in entities
        ) or self._render("database/migration.sql.jinja2", table_name="generated_entity")
        generated.append(_write_text(output_dir / "database" / "migration.sql", sql_text))

        docker_command = "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"
        generated.append(
            _write_text(
                output_dir / "deploy" / "Dockerfile",
                self._render("docker/Dockerfile.jinja2", base_image="python:3.11-slim", command=docker_command),
            )
        )
        generated.append(
            _write_text(
                output_dir / ".github" / "workflows" / "genesis-ci.yml",
                self._render("cicd/github-actions.yml.jinja2", verify_command="pytest -q"),
            )
        )

        generated.append(_write_text(output_dir / "tests" / "api" / "test_health.py", _health_test()))
        generated.append(_write_text(output_dir / "tests" / "playwright" / "smoke.spec.ts", _playwright_smoke(route_screens)))
        generated.append(_write_text(output_dir / "docs" / "ARCHITECTURE_SUMMARY.md", _architecture_summary(app_name, canonical_spec)))
        generated.append(
            _write_text(
                output_dir / "run_app.ps1",
                _run_app_script(deployment_spec.get("target_stack") or canonical_spec.get("target_stack", "nextjs_fastapi")),
            )
        )
        generated.append(
            _write_text(
                output_dir / "generated_app" / "README.md",
                f"# {app_name}\n\nThis scaffold was generated from the canonical app spec.\n",
            )
        )
        return generated

    def _render(self, template_name: str, **context: Any) -> str:
        return self.environment.get_template(template_name).render(**context)


def _write_json(path: Path, data: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def _write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _slug(value: str) -> str:
    slug = "".join(character.lower() if character.isalnum() else "-" for character in value)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "generated-app"


def _frontend_tsconfig() -> str:
    return json.dumps(
        {
            "compilerOptions": {
                "target": "ES2020",
                "lib": ["dom", "dom.iterable", "es2020"],
                "allowJs": False,
                "skipLibCheck": True,
                "strict": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "bundler",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
            },
            "include": ["**/*.ts", "**/*.tsx"],
        },
        indent=2,
    )


def _layout_tsx(app_name: str) -> str:
    return (
        "import React from \"react\";\n\n"
        "export default function RootLayout({ children }: { children: React.ReactNode }) {\n"
        "  return (\n"
        "    <html lang=\"en\">\n"
        "      <body>\n"
        f"        <div data-app-name=\"{app_name}\">{{children}}</div>\n"
        "      </body>\n"
        "    </html>\n"
        "  );\n"
        "}\n"
    )


def _navigation_component(route_screens: list[dict[str, Any]]) -> str:
    links = route_screens or [{"name": "Home"}]
    rendered_links = "\n".join(
        f'        <li><a href="/{_slug(str(item.get("name") or "home"))}">{str(item.get("name") or "Home")}</a></li>'
        for item in links
    )
    return (
        "import React from \"react\";\n\n"
        "export function GeneratedNav() {\n"
        "  return (\n"
        "    <nav>\n"
        "      <ul>\n"
        f"{rendered_links}\n"
        "      </ul>\n"
        "    </nav>\n"
        "  );\n"
        "}\n"
    )


def _backend_main(app_name: str, entities: list[dict[str, Any]], screens: list[dict[str, Any]]) -> str:
    entity_payload = json.dumps([entity.get("name") for entity in entities], indent=2)
    screen_payload = json.dumps([screen.get("name") for screen in screens], indent=2)
    return (
        "from fastapi import FastAPI\n\n"
        f"app = FastAPI(title={app_name!r})\n\n"
        "@app.get(\"/health\")\n"
        "def health() -> dict[str, str]:\n"
        "    return {\"status\": \"ok\"}\n\n"
        "@app.get(\"/migration/summary\")\n"
        "def migration_summary() -> dict[str, object]:\n"
        f"    return {{\"app\": {app_name!r}, \"entities\": {entity_payload}, \"screens\": {screen_payload}}}\n"
    )


def _health_test() -> str:
    return (
        "from fastapi.testclient import TestClient\n\n"
        "from backend.app.main import app\n\n"
        "client = TestClient(app)\n\n"
        "def test_health() -> None:\n"
        "    response = client.get('/health')\n"
        "    assert response.status_code == 200\n"
        "    assert response.json()['status'] == 'ok'\n"
    )


def _playwright_smoke(route_screens: list[dict[str, Any]]) -> str:
    first_route = _slug(str((route_screens[0] if route_screens else {"name": "home"}).get("name") or "home"))
    return (
        "import { test, expect } from '@playwright/test';\n\n"
        "test('smoke route placeholder', async ({ page }) => {\n"
        f"  await page.goto('http://localhost:3000/{first_route}');\n"
        "  await expect(page).toHaveTitle(/.*/);\n"
        "});\n"
    )


def _architecture_summary(app_name: str, canonical_spec: dict[str, Any]) -> str:
    target_stack = canonical_spec.get("target_stack") or canonical_spec.get("selected_target_stack")
    acceptance = canonical_spec.get("acceptance_criteria", [])
    rendered = "\n".join(f"- {item}" for item in acceptance) or "- Preserve core workflows\n- Preserve role behavior\n"
    return (
        f"# {app_name} Architecture Summary\n\n"
        f"- Target stack: {target_stack}\n"
        f"- Delivery mode: {canonical_spec.get('deployment_spec', {}).get('delivery_mode')}\n\n"
        "## Acceptance Criteria\n"
        f"{rendered}\n"
    )


def _run_app_script(target_stack: str) -> str:
    return (
        "Write-Host \"Generated scaffold summary\"\n"
        f"Write-Host \"Target stack: {target_stack}\"\n"
        "Write-Host \"Start backend after installing requirements with: python -m uvicorn backend.app.main:app --reload\"\n"
        "Write-Host \"Start frontend after installing dependencies with: npm install && npm run dev\"\n"
    )
