import { NextRequest, NextResponse } from "next/server";

const SESSION_COOKIE = "clair_demo_session";
const PROTECTED_PAGE_PREFIXES = ["/dashboard", "/triage", "/navigator", "/documents", "/emergency", "/safety"];
const PROTECTED_API_PREFIXES = ["/api/documents", "/api/triage", "/api/providers"];

function startsWithAny(pathname: string, prefixes: string[]) {
  return prefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const requiresPageSession = startsWithAny(pathname, PROTECTED_PAGE_PREFIXES);
  const requiresApiSession = startsWithAny(pathname, PROTECTED_API_PREFIXES);

  if (!requiresPageSession && !requiresApiSession) {
    return NextResponse.next();
  }

  if (request.cookies.has(SESSION_COOKIE)) {
    return NextResponse.next();
  }

  if (requiresApiSession) {
    return NextResponse.json({ message: "Authentication is required." }, { status: 401 });
  }

  const loginUrl = new URL("/login", request.url);
  loginUrl.searchParams.set("next", pathname);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/triage/:path*",
    "/navigator/:path*",
    "/documents/:path*",
    "/emergency/:path*",
    "/safety/:path*",
    "/api/documents/:path*",
    "/api/triage/:path*",
    "/api/providers/:path*",
  ],
};
