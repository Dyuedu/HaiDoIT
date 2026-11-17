"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";

import { type CitySharesResult, fetchCityShares } from "@/lib/city-shares";
import { getCss3dSnapshot, getServerCss3dSnapshot, subscribeCss3d } from "@/lib/css3d";
import { buildCitySharesView } from "@/lib/city-shares-view";
import {
  DEFAULT_LEVEL,
  DEFAULT_ROLE,
  DEFAULT_YEARS,
  LEVEL_ENTRY_NOTE,
  LEVEL_OPTIONS,
  ROLE_OPTIONS,
  YEARS_OPTIONS,
} from "@/lib/labels";
import { getServerWideSnapshot, getWideSnapshot, subscribeWide } from "@/lib/viewport";

import { FilterSelect } from "./filter-select";
import { LoadError } from "./load-error";
import { Map3D } from "./map-3d";
import { MapSummary } from "./map-summary";
import { ShareBars } from "./share-bars";
import { ShareTable } from "./share-table";
import { SnapshotCaption } from "./snapshot-caption";
import { type ViewMode, ViewSwitch } from "./view-switch";

const LOADING = "Đang tải số liệu…";
const UNREADABLE = "Không đọc được số liệu. Thử lại sau.";

/** Một lượt gọi API. `id` tăng mỗi lần đổi vai trò, cấp bậc, số năm hoặc thử lại. */
interface Request {
  id: number;
  role: string;
  level: string;
  years: string;
}

/** Kết quả của một lượt gọi, kèm `id` của lượt đã sinh ra nó. */
interface Loaded {
  requestId: number;
  result: CitySharesResult;
}

/**
 * Màn Bản đồ, phía trình duyệt. Server chỉ render khung và "Đang tải số liệu…": số được gọi
 * qua proxy `/api/*` sau khi trang mở, nên `next build` không gọi API và không đóng băng số.
 *
 * Lối xem (#314, #316): màn rộng dựng được CSS 3D thì mở lối 3D (UX-DR39); điện thoại mở lối 2D (NFR-12) nhưng vẫn chọn
 * được 3D; không dựng được CSS 3D thì lối 2D và nút 3D nói vì sao (FR-36). Server trả "không" nên HTML tĩnh là lối 2D;
 * trình duyệt chuyển sang 3D sau khi hydrate. Panel bên phải (tóm tắt từng nơi, nguồn và lưu ý) có ở cả ba lối.
 */
export function MapScreen() {
  const [request, setRequest] = useState<Request>({
    id: 0,
    role: DEFAULT_ROLE,
    level: DEFAULT_LEVEL,
    years: DEFAULT_YEARS,
  });
  // `null`: người dùng chưa chọn lối, dùng lối mặc định theo WebGL.
  const [chosenMode, setChosenMode] = useState<ViewMode | null>(null);
  const css3d = useSyncExternalStore(subscribeCss3d, getCss3dSnapshot, getServerCss3dSnapshot);
  const wide = useSyncExternalStore(subscribeWide, getWideSnapshot, getServerWideSnapshot);
  const can3d = css3d;
  const wanted = chosenMode ?? (can3d && wide ? "3d" : "2d");
  const mode: ViewMode = wanted === "3d" && !can3d ? "2d" : wanted;
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const statusRef = useRef<HTMLParagraphElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    const options = { level: request.level, years: request.years, signal: controller.signal };
    fetchCityShares(request.role, options).then((result) => {
      // Đã có lượt gọi mới: bỏ response về muộn.
      if (!controller.signal.aborted) setLoaded({ requestId: request.id, result });
    });
    return () => controller.abort();
  }, [request]);

  // Chỉ dùng kết quả của lượt gọi mới nhất; còn lại là đang tải, kể cả khi quay lại một vai
  // trò hoặc cấp bậc đã tải trước đó. Thanh và bảng cùng dựng từ một envelope nên không thể lệch nhau.
  const current = loaded?.requestId === request.id ? loaded.result : null;
  const changeRole = (role: string) =>
    setRequest((prev) => (prev.role === role ? prev : { ...prev, id: prev.id + 1, role }));
  const changeLevel = (level: string) =>
    setRequest((prev) => (prev.level === level ? prev : { ...prev, id: prev.id + 1, level }));
  const changeYears = (years: string) =>
    setRequest((prev) => (prev.years === years ? prev : { ...prev, id: prev.id + 1, years }));
  const retry = () => {
    setRequest((prev) => ({ ...prev, id: prev.id + 1 }));
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
      <div className="grid grid-cols-1 items-start gap-5 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="flex min-w-0 flex-col gap-5">
          {mode === "3d" ? <Map3D view={view} /> : mode === "2d" ? <ShareBars view={view} /> : <ShareTable view={view} />}
          {view.unstatedNote && <p className="m-0 text-caption text-text-secondary">{view.unstatedNote}</p>}
        </div>
        <aside className="flex min-w-0 flex-col gap-4">
          <MapSummary view={view} />
          <SnapshotCaption caption={view.caption} />
        </aside>
      </div>
    );
  }

  return (
    <div className="mt-6 flex flex-col gap-5">
      <div className="grid grid-cols-1 items-start gap-3 sm:grid-cols-3">
        <FilterSelect label="Vai trò" value={request.role} options={ROLE_OPTIONS} onChange={changeRole} />
        <FilterSelect
          label="Cấp bậc"
          value={request.level}
          options={LEVEL_OPTIONS}
          onChange={changeLevel}
          note={LEVEL_ENTRY_NOTE}
        />
        <FilterSelect
          label="Số năm kinh nghiệm"
          value={request.years}
          options={YEARS_OPTIONS}
          onChange={changeYears}
          note="Tính theo số năm tối thiểu tin yêu cầu."
        />
      </div>
      <ViewSwitch value={mode} onChange={setChosenMode} can3d={can3d} />
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
