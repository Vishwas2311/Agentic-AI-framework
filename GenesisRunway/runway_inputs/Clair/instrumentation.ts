// OpenTelemetry for Next.js — loaded by Next.js instrumentation hook
import { registerOTel } from '@vercel/otel'

export function register() {
  registerOTel({
    serviceName: process.env.OTEL_SERVICE_NAME ?? 'genesis-frontend',
  })
}
