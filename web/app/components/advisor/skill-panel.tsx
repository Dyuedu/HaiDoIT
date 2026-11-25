"use client";

import { useEffect, useId, useRef } from "react";

import type { PathNode, SkillLink } from "@/lib/learning-path-view";

interface SkillPanelProps {
  node: PathNode;
  have: boolean;
  onToggle: (skill: string) => void;
  onOpen: (skill: string) => void;
  onClose: () => void;
}

function SkillLinks({ title, links, onOpen }: { title: string; links: SkillLink[]; onOpen: (skill: string) => void }) {
  const id = useId();
  if (links.length === 0) return null;
  return (
    <section>
      <h3 id={id} className="m-0 font-mono text-kicker uppercase text-text-muted">
        {title}
      </h3>
      <ul aria-labelledby={id} className="mt-2 mb-0 flex list-none flex-wrap gap-2 p-0">
        {links.map((link) => (
          <li key={link.skill}>
            <button
              type="button"
              onClick={() => onOpen(link.skill)}
              className="min-h-target cursor-pointer rounded-md border border-border-chip px-3 text-ui text-text-secondary transition-colors hover:border-selected hover:text-text"
            >
              {link.name}
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}

/**
 * Ngăn chi tiết một kỹ năng (FR-23, #217): số ở ô riêng, lời dẫn viết sẵn không có số, kỹ năng trước và sau, một tài liệu
 * miễn phí. Mở ngăn không gọi API hay mô hình. Không chặn phần còn lại của màn (không modal); Escape hay nút Đóng để đóng.
 */
export function SkillPanel({ node, have, onToggle, onOpen, onClose }: SkillPanelProps) {
  const titleId = useId();
  const headingRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    headingRef.current?.focus({ preventScroll: true });
  }, [node.skill]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div
      role="dialog"
      aria-labelledby={titleId}
      className="fixed inset-x-0 bottom-0 z-40 flex max-h-[75vh] flex-col gap-5 overflow-y-auto overscroll-contain rounded-t-xl border border-border-strong bg-panel p-panel lg:inset-y-0 lg:right-0 lg:left-auto lg:max-h-none lg:w-[26rem] lg:rounded-none lg:border-y-0 lg:border-r-0"
    >
      <div className="flex items-start justify-between gap-3">
        <h2 id={titleId} ref={headingRef} tabIndex={-1} className="m-0 min-w-0 break-words text-title-sm text-text">
          {node.name}
        </h2>
        <button
          type="button"
          onClick={onClose}
          className="min-h-target shrink-0 cursor-pointer rounded-md border border-border-chip px-4 text-ui text-text-secondary transition-colors hover:border-selected hover:text-text"
        >
          Đóng
        </button>
      </div>

      <label className="flex min-h-target cursor-pointer items-center gap-3 rounded-lg border border-border-chip bg-inset px-4 text-body-md text-text">
        <input type="checkbox" checked={have} onChange={() => onToggle(node.skill)} className="size-5 accent-selected" />
        Tôi đã có kỹ năng này
      </label>

      <dl className="m-0 grid grid-cols-[auto_minmax(0,1fr)] items-baseline gap-x-4 gap-y-1 text-body-md">
        <dt className="text-text-muted">Tin yêu cầu</dt>
        <dd className={node.shareShown ? "m-0 font-mono text-mono-lg text-text" : "m-0 text-amber"}>{node.shareText}</dd>
        {node.groupText && (
          <>
            <dt className="text-text-muted">Nhóm</dt>
            <dd className="m-0 text-text-secondary">{node.groupText}</dd>
          </>
        )}
      </dl>

      <p className="m-0 text-body text-text-doc">{node.blurb}</p>

      <SkillLinks title="Lựa chọn thay thế" links={node.alternatives} onOpen={onOpen} />
      <SkillLinks title="Cần học trước" links={node.needs} onOpen={onOpen} />
      <SkillLinks title="Học xong thì học được" links={node.unlocks} onOpen={onOpen} />

      <section>
        <h3 className="m-0 font-mono text-kicker uppercase text-text-muted">Tài liệu miễn phí</h3>
        <a
          href={node.resource.url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-2 inline-flex min-h-target items-center text-body-md text-primary underline underline-offset-4 hover:text-link-hover"
        >
          {node.resource.title}
          <span className="sr-only"> (mở tab mới)</span>
        </a>
      </section>
    </div>
  );
}
