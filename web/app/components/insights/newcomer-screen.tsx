"use client";

import { useEffect, useRef, useState } from "react";

import { levelLabel } from "@/lib/labels";
import { type MarketOverviewEnvelope, fetchMarketOverview } from "@/lib/market-overview";
import { buildLevelMixRows } from "@/lib/market-overview-view";
import { type NewcomerRolesResult, fetchNewcomerRoles } from "@/lib/newcomer-roles";
import { buildNewcomerView } from "@/lib/newcomer-roles-view";

import { LoadError } from "../map/load-error";
import { SnapshotCaption } from "../map/snapshot-caption";
import { LevelMixChart } from "./level-mix-chart";
import { NewcomerList } from "./newcomer-list";
import { DataTable } from "./overview/charts";

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
  // Cơ cấu cấp bậc từng vai trò (#330) lấy tỷ lệ cấp của market-overview; lỗi thì chỉ thiếu biểu đồ này.
  const [overview, setOverview] = useState<MarketOverviewEnvelope | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetchMarketOverview({ signal: controller.signal }).then((result) => {
      if (!controller.signal.aborted && result.kind === "ok") setOverview(result.envelope);
    });
    return () => controller.abort();
  }, []);

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
    const mix = overview ? buildLevelMixRows(overview, view.lines.map((l) => l.role)) : [];
    content = (
      <>
        {view.takeaways.length > 0 && (
          <ul data-testid="newcomer-takeaways" className="m-0 flex max-w-[78ch] list-none flex-col gap-2 p-0">
            {view.takeaways.map((line) => (
              <li key={line} className="grid grid-cols-[14px_minmax(0,1fr)] gap-2 text-body-md text-text-secondary">
                <span aria-hidden="true" className="mt-2 h-2 w-2 rounded-sm bg-primary" />
                {line}
              </li>
            ))}
          </ul>
        )}
        <NewcomerList lines={view.lines} />
        <DataTable
          caption="Tỷ lệ tin cho người mới theo vai trò"
          head={["Vai trò", "Tỷ lệ", "Số tin"]}
          rows={view.lines.map((l) => [l.label, l.shareText, l.entryText ?? "Chưa có tin nào"])}
          numeric={[]}
        />
        {mix.length > 0 && overview && (
          <section aria-labelledby="co-cau-cap" className="flex flex-col gap-3 rounded-xl border border-border bg-panel p-panel">
            <div>
              <h3 id="co-cau-cap" className="m-0 text-body-md font-semibold text-text">
                Cơ cấu cấp bậc của từng vai trò
              </h3>
              <p className="m-0 text-caption text-text-muted">Cùng thứ tự với danh sách trên. Màu nhạt là cấp mới vào nghề.</p>
            </div>
            <LevelMixChart rows={mix} levels={overview.data.levels.map((code) => ({ code, label: levelLabel(code) }))} />
            <DataTable
              caption="Cơ cấu cấp bậc của từng vai trò"
              head={["Vai trò", ...overview.data.levels.map(levelLabel)]}
              rows={mix.map((r) => [
                r.label,
                ...overview.data.levels.map((lv) => r.note ?? r.segments.find((s) => s.code === lv)?.percent ?? "0,0%"),
              ])}
              numeric={overview.data.levels.map((_, i) => i + 1)}
            />
          </section>
        )}
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
