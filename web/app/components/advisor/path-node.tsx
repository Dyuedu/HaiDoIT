import type { NodeKind, PathNode } from "@/lib/learning-path-view";

/** `id` của nút mở ngăn, để trả focus khi ngăn đóng. */
export function pathNodeId(skill: string): string {
  return `ky-nang-${skill}`;
}

interface PathNodeCardProps {
  node: PathNode;
  have: boolean;
  selected: boolean;
  /** Kỹ năng nối trực tiếp với kỹ năng đang mở ngăn. */
  related: boolean;
  onToggle: (skill: string) => void;
  onOpen: (skill: string) => void;
}

/** Màu của từng loại ô; chú giải dùng lại. Chữ đi kèm nằm trong cùng lớp để tương phản luôn khớp nền. */
export const NODE_FILL: Readonly<Record<NodeKind | "have", string>> = {
  core: "border-selected bg-band-pale text-primary-ink",
  common: "border-band-mid bg-band-deep text-text",
  foundation: "border-dashed border-amber bg-notice text-amber-softer",
  unknown: "border-border-chip bg-panel text-text",
  have: "border-selected bg-inset text-text-muted",
};

/** Một ô kỹ năng trên lộ trình (#217): ô tick tròn "Đã có …" và nút mở ngăn chi tiết, hai ô bấm riêng. */
export function PathNodeCard({ node, have, selected, related, onToggle, onOpen }: PathNodeCardProps) {
  const ring = selected ? "ring-2 ring-primary" : related ? "ring-2 ring-amber" : "hover:ring-2 hover:ring-selected";
  return (
    <div
      data-skill={node.skill}
      data-have={have}
      data-kind={node.kind}
      className={`flex h-full min-w-0 items-stretch rounded-md border-2 transition-shadow ${NODE_FILL[have ? "have" : node.kind]} ${ring}`}
    >
      <label className="flex min-h-target w-11 shrink-0 cursor-pointer items-center justify-center">
        <input
          type="checkbox"
          checked={have}
          onChange={() => onToggle(node.skill)}
          aria-label={`Đã có ${node.shortName}`}
          className="peer sr-only"
        />
        <span
          aria-hidden="true"
          className={`flex size-5 items-center justify-center rounded-full border-2 text-micro peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-primary ${have ? "border-selected bg-selected text-primary-ink" : "border-current"}`}
        >
          {have ? "✓" : ""}
        </span>
      </label>
      <button
        type="button"
        id={pathNodeId(node.skill)}
        aria-haspopup="dialog"
        aria-expanded={selected}
        onClick={() => onOpen(node.skill)}
        className="flex min-h-target min-w-0 flex-1 scroll-mt-16 cursor-pointer flex-wrap items-baseline justify-between gap-x-2 self-center py-2 pr-3 text-left"
      >
        <span className={`min-w-0 break-words text-ui font-semibold ${have ? "line-through" : ""}`}>{node.shortName}</span>
        <span className={node.shareShown ? "font-mono text-mono-sm" : "text-caption text-amber"}>{node.shareText}</span>
        {have && <span className="sr-only">Đã có</span>}
        {node.groupText && <span className="sr-only">{node.groupText}</span>}
      </button>
    </div>
  );
}
