import { type PathNode, type PathSide, type PathStageView, type StageState, connectorPath } from "@/lib/learning-path-view";

import { NODE_FILL, PathNodeCard } from "./path-node";

interface PathGraphProps {
  /** Tên vai trò, đặt ở đầu trục. */
  title: string;
  stages: PathStageView[];
  /** Mã kỹ năng trong hồ sơ (chỉ để hiện tick, không đếm). */
  owned: ReadonlySet<string>;
  selected: PathNode | null;
  onToggle: (skill: string) => void;
  onOpen: (skill: string) => void;
}

const TOPIC_BOX: Readonly<Record<StageState, string>> = {
  done: "border-selected bg-inset text-selected",
  current: "border-primary bg-primary text-primary-ink ring-4 ring-primary/30",
  later: "border-primary bg-primary text-primary-ink",
};

const STAGE_NOTE: Readonly<Record<StageState, string | null>> = {
  done: "Đã xong",
  current: "Đang học",
  later: null,
};

const LEGEND = [
  { kind: "core", text: "Cốt lõi" },
  { kind: "common", text: "Thường gặp" },
  { kind: "foundation", text: "Nền tảng" },
  { kind: "have", text: "Đã có" },
] as const;

/** Số cột của cụm từ `sm`: cụm một kỹ năng chỉ có một cột. */
const COLUMNS = 2;

/**
 * Lộ trình kiểu roadmap.sh (#217): trục giữa là các chủ đề theo thứ tự học, mỗi chủ đề có một cụm ô kỹ năng ở một bên,
 * nối bằng đường chấm. Cụm "chọn một" nằm trong khung. Dưới `lg` đường nối ẩn và mọi thứ xếp thành một danh sách (AC của
 * #217). Một DOM cho cả hai: thứ tự đọc luôn là thứ tự API. Các hàng của một cụm cao bằng nhau nên đường nối không đo DOM.
 */
export function PathGraph({ title, stages, owned, selected, onToggle, onOpen }: PathGraphProps) {
  const related = new Set(selected ? [...selected.needs, ...selected.unlocks].map((link) => link.skill) : []);

  const connector = (side: PathSide, rows: number, done: boolean) => (
    <div aria-hidden="true" className="relative hidden w-14 shrink-0 lg:block xl:w-20">
      <svg
        data-connector={side}
        aria-hidden="true"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        className="absolute inset-0 hidden h-full w-full lg:block"
        fill="none"
      >
        {Array.from({ length: rows }, (_, row) => (
          <path
            key={row}
            d={connectorPath(side, row, rows)}
            vectorEffect="non-scaling-stroke"
            strokeWidth="3"
            strokeDasharray={done ? undefined : "0.5 7"}
            strokeLinecap="round"
            className="stroke-selected"
          />
        ))}
      </svg>
    </div>
  );

  const cluster = ({ stage, title: topic, chooseOne, state, side, nodes }: PathStageView) => {
    const single = nodes.length === 1;
    const cells = (
      <ol
        aria-label={`Chặng ${stage}: ${topic}`}
        className={`m-0 grid min-w-0 flex-1 list-none grid-cols-[minmax(0,1fr)] p-0 lg:auto-rows-fr ${single ? "lg:max-w-60" : "sm:grid-cols-[repeat(2,minmax(0,1fr))]"}`}
      >
        {nodes.map((node) => (
          <li key={node.skill} className={`p-[3px] ${single ? "" : "sm:last:odd:col-span-2"}`}>
            <PathNodeCard
              node={node}
              have={owned.has(node.skill)}
              selected={selected?.skill === node.skill}
              related={related.has(node.skill)}
              onToggle={onToggle}
              onOpen={onOpen}
            />
          </li>
        ))}
      </ol>
    );
    return (
      <div
        className={`flex min-w-0 items-stretch lg:row-start-1 ${side === "left" ? "lg:col-start-1 lg:justify-end" : "lg:col-start-3 lg:flex-row-reverse lg:justify-end"}`}
      >
        {chooseOne ? (
          <div className="min-w-0 flex-1 rounded-lg border-2 border-slate bg-panel p-1.5">
            <p className="m-0 px-1 pb-1 text-center text-caption text-text-muted">Chọn một</p>
            {cells}
          </div>
        ) : (
          cells
        )}
        {connector(side, chooseOne ? 1 : Math.ceil(nodes.length / COLUMNS), state === "done")}
      </div>
    );
  };

  return (
    <div className="flex flex-col gap-4">
      <ul aria-label="Chú giải" className="m-0 flex list-none flex-wrap gap-x-4 gap-y-2 p-0">
        {LEGEND.map(({ kind, text }) => (
          <li key={kind} className="flex items-center gap-2 text-caption text-text-secondary">
            <span aria-hidden="true" className={`h-4 w-7 rounded-sm border-2 ${NODE_FILL[kind]}`} />
            {text}
          </li>
        ))}
      </ul>
      <p aria-hidden="true" className="m-0 hidden text-center text-section text-text lg:block">
        {title}
      </p>
      <ol aria-label="Các chặng của lộ trình học" className="m-0 flex list-none flex-col p-0">
        {stages.map((view) => (
          <li
            key={view.stage}
            aria-current={view.state === "current" ? "step" : undefined}
            className="relative grid grid-cols-[minmax(0,1fr)] py-2 lg:grid-cols-[minmax(0,1fr)_13rem_minmax(0,1fr)] lg:items-center lg:py-1.5"
          >
            <span aria-hidden="true" className="absolute inset-y-0 left-1/2 hidden w-[3px] -translate-x-1/2 bg-selected lg:block" />
            <div
              className={`relative mb-2 flex min-h-target flex-col items-center justify-center rounded-md border-2 px-3 py-1.5 text-center lg:col-start-2 lg:row-start-1 lg:mb-0 ${TOPIC_BOX[view.state]}`}
            >
              <h2 className="m-0 text-ui font-bold">
                <span className="block font-mono text-micro font-semibold opacity-75">Chặng {view.stage}</span>
                {view.title}
              </h2>
              {STAGE_NOTE[view.state] && <p className="m-0 text-micro">{STAGE_NOTE[view.state]}</p>}
            </div>
            {cluster(view)}
          </li>
        ))}
      </ol>
    </div>
  );
}
