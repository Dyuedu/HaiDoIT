"use client";

import { useId, useState } from "react";

import { type SkillRow, type SkillsResult, searchSkills, skillDisplayName } from "@/lib/vocab";

interface SkillSearchProps {
  /** `null` khi đang tải danh sách kỹ năng. */
  vocab: SkillsResult | null;
  owned: ReadonlySet<string>;
  onToggle: (skill: string) => void;
}

/**
 * Ô tìm kỹ năng (#207): lọc `GET /api/v1/skills` theo tên tiếng Việt, tiếng Anh hoặc bí danh, đã bỏ dấu. Mỗi kết quả
 * là một ô tick gốc; tick là thêm vào hồ sơ (#206). Không có kết quả thì nói thành chữ trong `role="status"`.
 */
export function SkillSearch({ vocab, owned, onToggle }: SkillSearchProps) {
  const inputId = useId();
  const [query, setQuery] = useState("");
  const skills: SkillRow[] = vocab?.kind === "ok" ? vocab.skills : [];
  const results = searchSkills(skills, query);
  const searching = query.trim().length > 0;

  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={inputId} className="font-mono text-kicker uppercase text-text-muted">
        Tìm kỹ năng (tiếng Việt hoặc tiếng Anh)
      </label>
      <input
        id={inputId}
        type="search"
        value={query}
        autoComplete="off"
        placeholder="Ví dụ: học máy, React"
        onChange={(event) => setQuery(event.target.value)}
        className="min-h-target min-w-0 rounded-lg border border-border-chip bg-inset px-3 text-body-md text-text placeholder:text-text-muted hover:border-selected"
      />
      {/* Gõ được ngay cả khi danh sách chưa về: kết quả hiện khi danh sách tải xong. */}
      <p role="status" className="m-0 text-caption text-text-muted">
        {vocab?.kind === "unreadable"
          ? "Không tải được danh sách kỹ năng. Tải lại trang để thử lại."
          : searching && vocab === null
            ? "Đang tải danh sách kỹ năng…"
            : searching && results.length === 0
              ? "Không có kỹ năng nào khớp"
              : ""}
      </p>
      {searching && results.length > 0 && (
        <ul aria-label="Kết quả tìm kỹ năng" className="m-0 flex list-none flex-col gap-1 p-0">
          {results.map((skill) => (
            <li key={skill.code}>
              <label className="flex min-h-target cursor-pointer items-center gap-3 rounded-lg px-2 text-body-md text-text hover:bg-inset">
                <input
                  type="checkbox"
                  checked={owned.has(skill.code)}
                  onChange={() => onToggle(skill.code)}
                  className="size-6 shrink-0 cursor-pointer accent-selected"
                />
                <span className="min-w-0 break-words">{skillDisplayName(skill)}</span>
              </label>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
