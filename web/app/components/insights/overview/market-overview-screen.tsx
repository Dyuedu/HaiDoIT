"use client";

import { useEffect, useRef, useState } from "react";

import { levelLabel } from "@/lib/labels";
import { type MarketOverviewResult, fetchMarketOverview } from "@/lib/market-overview";
import { ALL_LEVELS_KEY, type OverviewView, buildMarketOverviewView } from "@/lib/market-overview-view";

import { LoadError } from "../../map/load-error";
import { SnapshotCaption } from "../../map/snapshot-caption";
import { BarChart, ButterflyChart, ColumnChart, DataTable } from "./charts";
import { PLACE_COLORS, levelColor } from "./palette";
import { Pie3D } from "./pie-3d";

const LOADING = "Đang tải số liệu…";
const UNREADABLE = "Không đọc được số liệu. Thử lại sau.";
const CARD = "flex min-w-0 flex-col gap-3 rounded-xl border border-border bg-panel p-panel";

interface Loaded {
  requestId: number;
  result: MarketOverviewResult;
}

/**
 * Phần toàn cảnh đầu trang Insights (#329, story #326): chỉ số, câu tóm tắt, biểu đồ tròn 3D theo cấp lọc biểu đồ vai
 * trò, cột số năm kinh nghiệm và nơi làm việc, Hà Nội/TP.HCM theo vai trò. Số gọi qua proxy `/api/*` sau khi trang mở.
 */
export function MarketOverviewScreen() {
  const [requestId, setRequestId] = useState(0);
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const statusRef = useRef<HTMLParagraphElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetchMarketOverview({ signal: controller.signal }).then((result) => {
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
      <LoadError message={current.message} snapshotDate={current.snapshotDate} onRetry={current.retryable ? retry : undefined} />
    );
  } else if (current?.kind === "unreadable") {
    content = <LoadError message={UNREADABLE} onRetry={retry} />;
  } else if (current?.kind === "ok") {
    content = <Overview view={buildMarketOverviewView(current.envelope)} />;
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

function Overview({ view }: { view: OverviewView }) {
  const [level, setLevel] = useState<string | null>(null);
  const bars = view.roleBars[level ?? ALL_LEVELS_KEY] ?? view.roleBars[ALL_LEVELS_KEY];
  const roleTitle = level ? `Tin cấp ${levelLabel(level)} theo vai trò` : "Số tin theo vai trò";

  return (
    <div className="flex flex-col gap-6">
      <ul aria-label="Chỉ số chính" className="m-0 grid list-none grid-cols-2 gap-3 p-0 lg:grid-cols-4">
        {view.kpis.map((kpi) => (
          <li key={kpi.label} className="flex flex-col gap-1 rounded-xl border border-border bg-panel px-4 py-3">
            <span className="font-mono text-title text-text">{kpi.value}</span>
            <span className="text-caption text-text-secondary">{kpi.label}</span>
            <span className="font-mono text-footer text-text-muted">{kpi.detail}</span>
          </li>
        ))}
      </ul>

      {view.takeaways.length > 0 && (
        <ul data-testid="takeaways" className="m-0 flex max-w-[78ch] list-none flex-col gap-2 p-0">
          {view.takeaways.map((line) => (
            <li key={line} className="grid grid-cols-[14px_minmax(0,1fr)] gap-2 text-body-md text-text-secondary">
              <span aria-hidden="true" className="mt-2 h-2 w-2 rounded-sm bg-primary" />
              {line}
            </li>
          ))}
        </ul>
      )}

      <div className="grid gap-4 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)]">
        <section aria-labelledby="ov-levels" className={CARD}>
          <div>
            <h3 id="ov-levels" className="m-0 text-body-md font-semibold text-text">
              Tin theo cấp bậc
            </h3>
            <p className="m-0 text-caption text-text-muted">Kéo hoặc bấm nút để xoay. Chọn một cấp để lọc biểu đồ vai trò.</p>
          </div>
          <Pie3D slices={view.slices} selected={level} onSelect={setLevel} label="Chọn cấp bậc" />
          <DataTable
            caption="Tin theo cấp bậc"
            head={["Cấp bậc", "Số tin", "Tỷ trọng"]}
            rows={view.slices.map((s) => [s.label, s.countText, s.percent])}
            numeric={[1, 2]}
          />
        </section>
        <section aria-labelledby="ov-roles" className={CARD}>
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <div>
              <h3 id="ov-roles" className="m-0 text-body-md font-semibold text-text">
                {roleTitle}
              </h3>
              <p className="m-0 text-caption text-text-muted">
                {level ? "Lọc theo cấp đã chọn." : "Mọi cấp."} Chọn một vai trò để mở hồ sơ kỹ năng.
              </p>
            </div>
            {level && (
              <button
                type="button"
                onClick={() => setLevel(null)}
                className="min-h-target text-caption text-selected focus-visible:outline-2 focus-visible:outline-selected"
              >
                Bỏ lọc cấp bậc
              </button>
            )}
          </div>
          <BarChart rows={bars} label={roleTitle} color={level ? levelColor(level) : undefined} />
          <DataTable
            caption={roleTitle}
            head={["Vai trò", "Số tin", "Tỷ lệ"]}
            rows={bars.map((b) => [b.label, b.countText, b.note ?? b.shareText])}
            numeric={[1]}
          />
        </section>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <section aria-labelledby="ov-years" className={CARD}>
          <div>
            <h3 id="ov-years" className="m-0 text-body-md font-semibold text-text">
              Số năm kinh nghiệm tin yêu cầu
            </h3>
            <p className="m-0 text-caption text-text-muted">Số năm tối thiểu ghi trong tin.</p>
          </div>
          <ColumnChart
            rows={view.years}
            label="Số tin theo số năm kinh nghiệm"
            colorOf={(key) => (key === "none" ? levelColor("unknown") : PLACE_COLORS.hcm)}
          />
          <DataTable
            caption="Số tin theo số năm kinh nghiệm"
            head={["Số năm tối thiểu", "Số tin", "Tỷ trọng"]}
            rows={view.years.map((y) => [y.label, y.countText, y.percent])}
            numeric={[1, 2]}
          />
        </section>
        <section aria-labelledby="ov-places" className={CARD}>
          <div>
            <h3 id="ov-places" className="m-0 text-body-md font-semibold text-text">
              Nơi làm việc
            </h3>
            <p className="m-0 text-caption text-text-muted">Làm từ xa và nước ngoài tách riêng.</p>
          </div>
          <ColumnChart
            rows={view.places}
            label="Số tin theo nơi làm việc"
            colorOf={(key) => (key === "ha_noi" ? PLACE_COLORS.hn : key === "ho_chi_minh" ? PLACE_COLORS.hcm : PLACE_COLORS.other)}
          />
          <DataTable
            caption="Số tin theo nơi làm việc"
            head={["Nơi làm việc", "Số tin", "Tỷ trọng"]}
            rows={view.places.map((p) => [p.label, p.countText, p.note ? `${p.percent} (${p.note})` : p.percent])}
            numeric={[1, 2]}
          />
        </section>
      </div>

      <section aria-labelledby="ov-cities" className={CARD}>
        <div>
          <h3 id="ov-cities" className="m-0 text-body-md font-semibold text-text">
            Hà Nội hay TP.HCM, theo vai trò
          </h3>
          <p className="m-0 text-caption text-text-muted">Phần trăm tin của mỗi vai trò nằm ở từng thành phố.</p>
        </div>
        <ButterflyChart rows={view.butterfly} />
        <DataTable
          caption="Hà Nội và TP.HCM theo vai trò"
          head={["Vai trò", "Hà Nội", "TP.HCM", "Số tin của vai trò"]}
          rows={view.butterfly.map((b) => [b.label, b.hn.percent, b.hcm.percent, b.totalText])}
          numeric={[1, 2, 3]}
        />
      </section>

      <SnapshotCaption caption={view.caption} />
    </div>
  );
}
