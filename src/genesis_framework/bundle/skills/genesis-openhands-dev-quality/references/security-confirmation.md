# Security Confirmation

Use this reference for repair, dependency install, deploy, PR delivery, and any action that touches secrets, filesystem boundaries, or external systems.

Classify actions before execution:

| Risk | Examples | Behavior |
|---|---|---|
| Low | read files, run tests, inspect reports | execute and record |
| Medium | install dependencies, start local server, run build | execute when the stage allows it |
| High | delete files, deploy, push PR, publish package, expose credentials | require a gate or explicit approval |
| Blocked | write outside output sandbox, fake QA evidence, leak secrets, destructive root delete | stop pipeline |

Genesis should write `action_risk_report.json` and block final approval on any blocked action or high-risk action without gate evidence.

Security checks are defensive only:

- auth protection;
- API authorization;
- secret leakage;
- safe error responses;
- dependency vulnerability evidence;
- XSS escaping checks;
- IDOR/BOLA prevention for local test data.
