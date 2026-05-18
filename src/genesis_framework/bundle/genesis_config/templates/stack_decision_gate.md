<!-- GENESIS PIPELINE TEMPLATE — Stack Decision Gate (Stage 5) -->
<!-- RENDER RULE: Load this file and display it VERBATIM. Do not summarise,  -->
<!-- shorten, or restructure. Replace {{APP_NAME}} and {{STAGE}} with values. -->
<!-- All sections, bullets, sub-headings, and separators must appear as-is.   -->

## Stack Decision Gate
**{{APP_NAME}}** · Stage {{STAGE}}

{{STACK_CONFLICT_CONTEXT}}

Which stack should Genesis use to build this application?

---

**A. Next.js + Tailwind + shadcn/ui + Framer Motion**
`RECOMMENDED` · `Production Pro-Code` · `Full DevOps Hand-Off Ready`
Full production stack built for patient-facing hospital portals. Next.js handles real page routing, Tailwind + shadcn/ui delivers the clean healthcare-trusted UI the BRD describes, and Framer Motion adds purposeful transitions. UI/UX Pro Max acts as design director. 21st.dev Magic generates every component. Playwright tests run natively against real routes.

**Containerisation**
- `Dockerfile` (multi-stage optimised build) + `.dockerignore`
- `docker-compose.yml` (local dev) + `docker-compose.prod.yml` (staging + production)
- Non-root user, health-check endpoint, memory/CPU limits defined in container

**CI/CD Pipeline** (`/.github/workflows/`)
- `lint.yml` — ESLint, TypeScript, Prettier
- `test.yml` — unit + integration tests with coverage gate (80%+)
- `build.yml` — Docker image build + registry push
- `security.yml` — SAST (Snyk), dependency audit, secrets scan
- `e2e.yml` — Playwright end-to-end browser tests
- `performance.yml` — Lighthouse CI, Core Web Vitals gate
- `accessibility.yml` — axe-core WCAG 2.1 AA check
- `deploy.yml` — staging + production deploy with rollback automation

**Environment & Secrets**
- `.env.local` / `.env.staging` / `.env.production` / `.env.example`
- AWS Secrets Manager or HashiCorp Vault for credentials
- GitHub Secrets for CI/CD pipeline variables
- Startup-time environment variable validation (Zod schema)

**Infrastructure as Code** (`/terraform/`)
- `vpc.tf` — VPC, subnets, security groups
- `rds.tf` — PostgreSQL with encryption at rest, Multi-AZ
- `ecs.tf` — ECS cluster for containerised app
- `alb.tf` — Application Load Balancer + health checks
- `cdn.tf` — CloudFront CDN with SSL/TLS
- `iam.tf` — roles + policies (least privilege)
- `kms.tf` — Key Management for encryption keys
- `secrets.tf` — Secrets Manager integration
- `monitoring.tf` — CloudWatch alarms + dashboards
- `backend.tf` — Terraform state (S3 + DynamoDB lock)

**Security**
- TLS 1.2+ enforced, Let's Encrypt with auto-renewal
- Security headers via `next.config.js` — HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy
- CSRF protection, SameSite cookies, HttpOnly + Secure flags
- Rate limiting — per IP, per user, per route
- WAF rules — SQL injection, XSS, bot control, IP reputation
- AES-256 encryption at rest, TLS 1.3 in transit
- OAuth 2.0 + PKCE, JWT with refresh tokens, MFA for staff
- RBAC, session timeout (15 min for sensitive pages)
- Dependency vulnerability scanning (Snyk + Dependabot)

**CDN & Performance**
- CloudFront CDN with edge caching
- Static assets cached 1 year (immutable, content-hashed filenames)
- Next.js Image optimisation — WebP/AVIF auto-serving, lazy loading
- Bundle analyser, code splitting, tree-shaking, font optimisation
- Redis for server-side caching layer

**Load Balancing & Scaling**
- ALB with health checks, cross-zone load balancing, connection draining
- ECS auto-scaling — CPU 70% threshold, min/max instance counts
- Stateless app design — sessions in Redis, no filesystem dependencies
- SIGTERM graceful shutdown handler

**Database Layer**
- RDS PostgreSQL — Multi-AZ, encryption at rest, Enhanced Monitoring
- PgBouncer connection pooling
- Prisma Migrate for versioned, backward-compatible migrations
- Automated daily backups — 35-day retention, cross-region replication
- Point-in-Time Recovery (PITR) — 5-min RPO
- pgBackRest for large-volume physical backups
- Slow query logging + Index performance monitoring

**DNS & Domain**
- Route53 — A, AAAA, CNAME, MX, TXT (SPF, DKIM, DMARC), CAA records
- Wildcard SSL or SAN certificate with auto-renewal
- DNSSEC signing
- Health-check based DNS failover

**Monitoring & Observability**
- Datadog or New Relic APM — latency, error rate, throughput
- Structured JSON logging — ELK stack or CloudWatch Logs
- Log retention 6 years (HIPAA minimum)
- Sensitive data redaction from logs
- `/health` (liveness) + `/health/ready` (readiness) endpoints
- Alerts — high error rate, high latency, DB pool exhaustion, disk space, cert expiry
- Real-time dashboards — system health, business metrics, HIPAA compliance

**Testing**
- Unit tests — Jest, 80%+ coverage gate
- Integration tests — API endpoints, auth flows, DB interactions
- E2E tests — Playwright for all patient journeys
- Performance tests — k6 load testing, Lighthouse CI (score 90+)
- Accessibility tests — axe-core WCAG 2.1 AA
- Security tests — SAST, DAST, OWASP Top 10, annual penetration test

**HIPAA Compliance** *(healthcare-specific)*
- PHI data mapping + data classification scheme
- Audit logs for all PHI access — immutable, encrypted, 6-year retention
- Business Associate Agreements (BAA) with all vendors
- HIPAA Security Risk Analysis (HRA) document
- Annual vulnerability assessment + penetration test
- Breach notification procedure (60-day reporting timeline)
- DR plan — RTO ≤ 15 min, RPO ≤ 5 min

**Backup & Disaster Recovery**
- Daily automated backups — 7 daily, 4 weekly, 12 monthly, 7-year archive
- Cross-region S3 replication for long-term storage
- Monthly restore testing + quarterly DR drills
- Secondary region standby + automated DNS failover

**Documentation delivered to DevOps team**
- `README.md` — setup, run, deploy
- `ARCHITECTURE.md` — system design + data flow diagrams
- `DEPLOYMENT_RUNBOOK.md` — step-by-step deploy + rollback guide
- `INCIDENT_RESPONSE.md` — alert handling + escalation
- `DISASTER_RECOVERY_PLAN.md` — failover + failback procedures
- `HIPAA_COMPLIANCE.md` — controls checklist + audit evidence
- `SECURITY_POLICY.md` — security standards + procedures
- `CHANGELOG.md` — version history + migration guides
- OpenAPI / Swagger spec for all API endpoints

---

**B. Streamlit → Next.js Hybrid Pilot**
`Hybrid Tech` · `Dual Deliverable` · `Sprint 1 Demo + Sprint 2 Production`
Working Streamlit app delivered immediately for the hospital operations demo. A parallel Next.js migration spec, component map, and CI/CD template generated alongside it so the DevOps and engineering teams can begin the production build next sprint without starting from scratch. Includes `Dockerfile` for Streamlit demo + Next.js project scaffold for production sprint.

---

**C. React + FastAPI + PostgreSQL**
`Full Stack` · `API-First` · `Hospital System Integration Ready`
Decoupled frontend and backend with a real relational database. React handles the portal UI, FastAPI serves a typed REST API with auto-generated OpenAPI docs, PostgreSQL stores consultations and prescriptions. Includes `docker-compose.yml` (3-service stack), Alembic migrations, Kubernetes manifests, and full CI/CD pipeline. Best if the portal must connect to real hospital HIS or EHR systems.

---

**D. Polished Streamlit**
`BRD Exact Match` · `Demo Only` · `Internal Showcase`
Multi-page Streamlit app with custom CSS and session state. Honors the BRD stack request exactly. Includes `requirements.txt`, `Dockerfile`, and local run `README.md`. No CI/CD pipeline, no production deployment manifests, no DevOps hand-off package. Suitable for internal hospital operations team demo only.

---

**E. I will specify my own stack**
`Custom Override` · `Manual Input`
Tell Genesis the exact framework, language, database, and toolchain. Genesis validates the choice against BRD requirements and generates all code, tests, CI/CD pipeline, and deployment manifests matched to your specified stack and target cloud.

---

Which stack? **(A / B / C / D / E)**
