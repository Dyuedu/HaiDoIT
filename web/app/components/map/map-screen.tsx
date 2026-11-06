"use client";

import { useEffect, useRef, useState } from "react";

import { type CitySharesResult, fetchCityShares } from "@/lib/city-shares";
import { buildCitySharesView } from "@/lib/city-shares-view";
import { DEFAULT_ROLE } from "@/lib/labels";

import { LoadError } from "./load-error";
import { RoleChips } from "./role-chips";
import { ShareBars } from "./share-bars";
import { ShareTable } from "./share-table";
import { SnapshotCaption } from "./snapshot-caption";
import { type ViewMode, ViewSwitch } from "./view-switch";

const LOADING = "Đang tải số liệu…";
const UNREADABLE = "Không đọc được số liệu. Thử lại sau.";

/** Một lượt gọi API. `id` tăng mỗi lần đổi vai trò hoặc thử lại. */
interface Request {
  id: number;
  role: string;
}

/** Kết quả của một lượt gọi, kèm `id` của lượt đã sinh ra nó. */
interface Loaded {
  requestId: number;
  result: CitySharesResult;
}

/**
 * Màn Bản đồ, phía trình duyệt. Server chỉ render khung và "Đang tải số liệu…": số được gọi
 * qua proxy `/api/*` sau khi trang mở, nên `next build` không gọi API và không đóng băng số.
 */
export function MapScreen() {
  const [request, setRequest] = useState<Request>({ id: 0, role: DEFAULT_ROLE });
  const [mode, setMode] = useState<ViewMode>("2d");
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const statusRef = useRef<HTMLParagraphElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetchCityShares(request.role, { signal: controller.signal }).then((result) => {
      // Đã có lượt gọi mới: bỏ response về muộn.
      if (!controller.signal.aborted) setLoaded({ requestId: request.id, result });
    });
    return () => controller.abort();
  }, [request]);

  // Chỉ dùng kết quả của lượt gọi mới nhất; còn lại là đang tải, kể cả khi quay lại một vai
  // trò đã tải trước đó.
  const current = loaded?.requestId === request.id ? loaded.result : null;
  const changeRole = (role: string) =>
    setRequest((prev) => (prev.role === role ? prev : { id: prev.id + 1, role }));
  const retry = () => {
    setRequest((prev) => ({ id: prev.id + 1, role: prev.role }));
    // Nút "Thử lại" sắp biến mất: đưa focus về vùng trạng thái thay vì để rơi về <body>.
    statusRef.current?.focus();
  };

  // Đang tải (`current === null`) thì không có nội dung; chỉ vùng trạng thái có chữ.
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
    const view = buildCitySharesView(current.envelope);
    content = (
      <>
        {mode === "2d" ? <ShareBars view={view} /> : <ShareTable view={view} />}
        <SnapshotCaption caption={view.caption} />
      </>
    );
  }

  return (
    <div className="mt-6 flex flex-col gap-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <RoleChips value={request.role} onChange={changeRole} />
        <ViewSwitch value={mode} onChange={setMode} />
      </div>
      <p className="m-0 text-caption text-text-muted sm:hidden">
        Mở trên máy tính để xem bản đồ đầy đủ.
      </p>
      {/* Một vùng trạng thái sống suốt màn, chỉ đổi chữ, để trình đọc màn hình đọc được. */}
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
