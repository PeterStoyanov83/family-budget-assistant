import { NextRequest, NextResponse } from "next/server";

const BACKEND = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function proxy(request: NextRequest, { params }: { params: { path: string[] } }) {
  const path = params.path.join("/");
  const url = `${BACKEND}/${path}${request.nextUrl.search}`;

  const reqHeaders = new Headers(request.headers);
  reqHeaders.delete("host");

  const init: RequestInit & { duplex?: string } = {
    method: request.method,
    headers: reqHeaders,
  };

  if (!["GET", "HEAD"].includes(request.method)) {
    init.duplex = "half";
    init.body = request.body;
  }

  const backendRes = await fetch(url, init);

  return new NextResponse(backendRes.body, {
    status: backendRes.status,
    statusText: backendRes.statusText,
    headers: backendRes.headers,
  });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export const HEAD = proxy;
export const OPTIONS = proxy;
