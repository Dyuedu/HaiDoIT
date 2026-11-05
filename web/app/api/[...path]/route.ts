import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const { path } = await context.params;

  for (const rawSegment of path) {
    let decoded: string;
    try {
      decoded = decodeURIComponent(rawSegment);
    } catch {
      return NextResponse.json(
        {
          error: {
            code: "not_found",
            message: "Không tìm thấy tài nguyên yêu cầu.",
            snapshot_date: null,
          },
        },
        { status: 404, headers: { "content-type": "application/json" } }
      );
    }

    if (
      decoded === "." ||
      decoded === ".." ||
      decoded.includes("/") ||
      decoded.includes("\\") ||
      decoded.includes("?")
    ) {
      return NextResponse.json(
        {
          error: {
            code: "not_found",
            message: "Không tìm thấy tài nguyên yêu cầu.",
            snapshot_date: null,
          },
        },
        { status: 404, headers: { "content-type": "application/json" } }
      );
    }
  }

  const encodedPath = path
    .map((s) => encodeURIComponent(decodeURIComponent(s)))
    .join("/");

  const apiBaseUrl = process.env.API_BASE_URL || "http://localhost:8000";
  const search = request.nextUrl.search;
  const targetUrl = `${apiBaseUrl.replace(/\/$/, "")}/api/${encodedPath}${search}`;

  try {
    const upstreamRes = await fetch(targetUrl, {
      method: "GET",
      headers: {
        accept: request.headers.get("accept") || "application/json",
      },
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });

    const body = await upstreamRes.text();
    const contentType = upstreamRes.headers.get("content-type") || "application/json";

    return new NextResponse(body, {
      status: upstreamRes.status,
      headers: {
        "content-type": contentType,
      },
    });
  } catch (_err) {
    const errorBody = {
      error: {
        code: "api_unavailable",
        message: "Dịch vụ API hiện không phản hồi. Vui lòng thử lại sau.",
        snapshot_date: null,
      },
    };

    return NextResponse.json(errorBody, {
      status: 502,
      headers: {
        "content-type": "application/json",
      },
    });
  }
}
