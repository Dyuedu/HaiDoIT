import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

function resolveTargetUrl(
  path: string[],
  search: string
): { targetUrl: string } | { error: NextResponse } {
  for (const rawSegment of path) {
    let decoded: string;
    try {
      decoded = decodeURIComponent(rawSegment);
    } catch {
      return {
        error: NextResponse.json(
          {
            error: {
              code: "not_found",
              message: "Không tìm thấy tài nguyên yêu cầu.",
              snapshot_date: null,
            },
          },
          { status: 404, headers: { "content-type": "application/json" } }
        ),
      };
    }

    if (
      decoded === "." ||
      decoded === ".." ||
      decoded.includes("/") ||
      decoded.includes("\\") ||
      decoded.includes("?")
    ) {
      return {
        error: NextResponse.json(
          {
            error: {
              code: "not_found",
              message: "Không tìm thấy tài nguyên yêu cầu.",
              snapshot_date: null,
            },
          },
          { status: 404, headers: { "content-type": "application/json" } }
        ),
      };
    }
  }

  const encodedPath = path
    .map((s) => encodeURIComponent(decodeURIComponent(s)))
    .join("/");

  const apiBaseUrl = process.env.API_BASE_URL || "http://localhost:8000";
  return {
    targetUrl: `${apiBaseUrl.replace(/\/$/, "")}/api/${encodedPath}${search}`,
  };
}

async function forwardRequest(
  targetUrl: string,
  init: RequestInit
): Promise<NextResponse> {
  try {
    const upstreamRes = await fetch(targetUrl, init);
    const body = await upstreamRes.text();
    const contentType =
      upstreamRes.headers.get("content-type") || "application/json";

    return new NextResponse(body, {
      status: upstreamRes.status,
      headers: {
        "content-type": contentType,
      },
    });
  } catch (_err) {
    return NextResponse.json(
      {
        error: {
          code: "api_unavailable",
          message: "Dịch vụ API hiện không phản hồi. Vui lòng thử lại sau.",
          snapshot_date: null,
        },
      },
      {
        status: 502,
        headers: {
          "content-type": "application/json",
        },
      }
    );
  }
}

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const { path } = await context.params;
  const resolved = resolveTargetUrl(path, request.nextUrl.search);
  if ("error" in resolved) return resolved.error;

  return forwardRequest(resolved.targetUrl, {
    method: "GET",
    headers: {
      accept: request.headers.get("accept") || "application/json",
    },
    cache: "no-store",
    signal: AbortSignal.timeout(10000),
  });
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const { path } = await context.params;
  const resolved = resolveTargetUrl(path, request.nextUrl.search);
  if ("error" in resolved) return resolved.error;

  const headers: Record<string, string> = {
    accept: request.headers.get("accept") || "application/json",
  };
  const contentType = request.headers.get("content-type");
  if (contentType) headers["content-type"] = contentType;

  const rawBody = new Uint8Array(await request.arrayBuffer());
  return forwardRequest(resolved.targetUrl, {
    method: "POST",
    headers,
    body: rawBody,
    cache: "no-store",
    signal: AbortSignal.timeout(45000),
  });
}
