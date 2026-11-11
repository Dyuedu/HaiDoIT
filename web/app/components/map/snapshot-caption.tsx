import { useId } from "react";

import type { SnapshotCaption as Caption } from "@/lib/city-shares-view";

/**
 * Chú thích luôn hiện khi có số, kể cả trên điện thoại: bộ lọc đang dùng (vai trò, cấp bậc, số năm; #280), nguồn đúng
 * như API gửi, ngày snapshot, nguồn lỗi khi snapshot `partial`, và mọi câu `coverage_notes` nguyên văn.
 */
export function SnapshotCaption({ caption }: { caption: Caption }) {
  const headingId = useId();
  return (
    <section
      aria-labelledby={headingId}
      className="rounded-xl border border-border bg-panel p-panel"
    >
      <h2 id={headingId} className="m-0 font-mono text-kicker uppercase text-text-muted">
        Nguồn và lưu ý
      </h2>
      <dl className="mt-3 grid grid-cols-[auto_minmax(0,1fr)] gap-x-3 gap-y-1 text-caption">
        <dt className="text-text-muted">Bộ lọc</dt>
        <dd className="m-0 break-words text-text-secondary">{caption.filters}</dd>
        <dt className="text-text-muted">Nguồn</dt>
        <dd className="m-0 font-mono text-footer break-words text-text-secondary">
          {caption.sources.join(", ")}
        </dd>
        <dt className="text-text-muted">Ngày snapshot</dt>
        <dd className="m-0 font-mono text-footer text-text-secondary">{caption.snapshotDate}</dd>
      </dl>
      {caption.failedSources && (
        <p className="mt-2 text-caption text-amber">{caption.failedSources}</p>
      )}
      <ul className="mt-3 list-disc pl-5 text-caption text-text-quiet">
        {caption.notes.map((note) => (
          <li key={note.code}>{note.text}</li>
        ))}
      </ul>
    </section>
  );
}
