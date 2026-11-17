"use client";

import { useId, useState } from "react";

import { type SkillRow, type SkillsResult, searchSkills, skillDisplayName } from "@/lib/vocab";

interface SkillPickerProps {
  vocab: SkillsResult | null;
  /** Mã kỹ năng đang chọn, hoặc `null`. */
  selected: string | null;
  /** Mã kỹ năng trong hồ sơ trình duyệt (#206), để chọn nhanh. */
  profileSkills: readonly string[];
  onSelect: (skill: string) => void;
}

const BUTTON =
  "min-h-target rounded-md border px-3 text-left text-ui transition-colors hover:border-selected hover:text-text aria-pressed:border-selected aria-pressed:text-text";

/**
 * Chọn đúng một kỹ năng (#167): ô tìm song ngữ dùng `searchSkills` của #207, kết quả là nút chọn một (`aria-pressed`),
 * cộng hàng chọn nhanh từ hồ sơ trình duyệt. Không có kết quả thì nói thành chữ trong `role="status"`.
 */
export function SkillPicker({ vocab, selected, profileSkills, onSelect }: SkillPickerProps) {
  const inputId = useId();
  const [query, setQuery] = useState("");
  const skills: SkillRow[] = vocab?.kind === "ok" ? vocab.skills : [];
  const results = searchSkills(skills, query);
  const searching = query.trim().length > 0;
  const byCode = new Map(skills.map((skill) => [skill.code, skill]));
  const quick = profileSkills.filter((code) => byCode.has(code));

  return (
    <div className="flex flex-col gap-3">
      {quick.length > 0 && (
        <ul aria-label="Kỹ năng trong hồ sơ của bạn" className="m-0 flex list-none flex-wrap gap-2 p-0">
          {quick.map((code) => (
            <li key={code}>
              <button
                type="button"
                aria-pressed={selected === code}
                onClick={() => onSelect(code)}
                className={`${BUTTON} border-border-chip text-text-secondary`}
              >
                {skillDisplayName(byCode.get(code) as SkillRow)}
              </button>
            </li>
          ))}
        </ul>
      )}
      <div className="flex flex-col gap-1.5">
        <label htmlFor={inputId} className="font-mono text-kicker uppercase text-text-muted">
          Tìm kỹ năng (tiếng Việt hoặc tiếng Anh)
        </label>
        <input
          id={inputId}
          type="search"
          value={query}
          autoComplete="off"
          placeholder="Ví dụ: học máy, Python"
          onChange={(event) => setQuery(event.target.value)}
          className="min-h-target min-w-0 rounded-lg border border-border-chip bg-inset px-3 text-body-md text-text placeholder:text-text-muted hover:border-selected"
        />
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
                <button
                  type="button"
                  aria-pressed={selected === skill.code}
                  onClick={() => onSelect(skill.code)}
                  className={`${BUTTON} w-full border-transparent text-text`}
                >
                  {skillDisplayName(skill)}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
