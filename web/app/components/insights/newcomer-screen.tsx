"use client";

import { useEffect, useRef, useState } from "react";

import { type NewcomerRolesResult, fetchNewcomerRoles } from "@/lib/newcomer-roles";
import { buildNewcomerView } from "@/lib/newcomer-roles-view";

import { LoadError } from "../map/load-error";
import { SnapshotCaption } from "../map/snapshot-caption";
import { NewcomerList } from "./newcomer-list";

const LOADING = "Đang tải số liệu…";
const UNREADABLE = "Không đọc được số liệu. Thử lại sau.";

interface Loaded {
  requestId: number;
  result: NewcomerRolesResult;
}

/**
 * Màn người mới, phía trình duyệt (#147). Server chỉ render khung; số gọi qua proxy `/api/*` sau khi trang mở, cùng
 * cách với màn Bản đồ, nên `next build` không gọi API và không đóng băng số.
 */
export function NewcomerScreen() {
  const [requestId, setRequestId] = useState(0);
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const statusRef = useRef<HTMLParagraphElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetchNewcomerRoles({ signal: controller.signal }).then((result) => {
      if (!controller.signal.aborted) setLoaded({ requestId, result });
    });
    return () => controller.abort();
  }, [requestId]);

  const current = loaded?.requestId === requestId ? loaded.result : null;
  const retry = () => {
    setRequestId((id) => id + 1);
    statusRef.current?.focus();
  };

  let content: React.ReactNode = null;
  if (current?.kind === "error") {
    content = (
      <LoadError
        message={current.message}
        snapshotDate={current.snapshotDate}
        onRetry={current.retryable ? retry : undefined}
      />
    );
  } else if (current?.kind === "unreadable") {
    content = <LoadError message={UNREADABLE} onRetry={retry} />;
  } else if (current?.kind === "ok") {
    const view = buildNewcomerView(current.envelope);
    content = (
      <>
        <NewcomerList lines={view.lines} />
        <SnapshotCaption caption={view.caption} />
      </>
    );
  }

  return (
    <div className="mt-4 flex flex-col gap-4">
      <p
        ref={statusRef}
        role="status"
        tabIndex={-1}
        className={current === null ? "m-0 text-body-md text-text-muted" : "sr-only"}
      >
        {current === null ? LOADING : ""}
      </p>
      {content}
    </div>
  );
}
