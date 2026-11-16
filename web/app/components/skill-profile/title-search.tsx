"use client";

import { useId, useState } from "react";

import { roleLabel } from "@/lib/labels";
import { fetchRoleForTitle } from "@/lib/role-for-title";

export type TitleOutcome =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "matched"; role: string }
  | { kind: "generic" }
  | { kind: "not_it" }
  | { kind: "error" };

interface TitleSearchProps {
  outcome: TitleOutcome;
  onOutcome: (outcome: TitleOutcome) => void;
}

const MESSAGES: Record<"generic" | "not_it" | "error", string> = {
  not_it: "Chức danh này không khớp vai trò IT nào. Chọn một vai trò trong danh sách dưới đây.",
  generic: "Chức danh này chưa chỉ rõ một vai trò, nên không khớp vai trò IT nào cụ thể. Chọn một vai trò trong danh sách dưới đây.",
  error: "Không tìm được vai trò cho chức danh này. Thử lại sau, hoặc chọn vai trò trong ô Vai trò.",
};

/**
 * Ô chức danh (#150): gửi chức danh tới `GET /api/v1/role-for-title` (phép 6) khi bấm "Tìm vai trò", rồi báo vai trò Hải
 * Đồ dùng, hoặc báo không khớp. Không gợi ý theo từng phím gõ: phép 6 cần cả chức danh. Kết quả đọc qua `role="status"`.
 */
export function TitleSearch({ outcome, onOutcome }: TitleSearchProps) {
  const inputId = useId();
  const [title, setTitle] = useState("");

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const cleaned = title.trim();
    if (!cleaned) return;
    onOutcome({ kind: "loading" });
    const result = await fetchRoleForTitle(cleaned);
    onOutcome(result.kind === "unreadable" ? { kind: "error" } : result);
  };

  let message = "";
  if (outcome.kind === "matched") message = `Hải Đồ dùng vai trò ${roleLabel(outcome.role)} cho chức danh này.`;
  else if (outcome.kind === "loading") message = "Đang tìm vai trò…";
  else if (outcome.kind !== "idle") message = MESSAGES[outcome.kind];

  return (
    <form role="search" aria-label="Tìm vai trò theo chức danh" onSubmit={submit} className="flex flex-col gap-1.5">
      <label htmlFor={inputId} className="font-mono text-kicker uppercase text-text-muted">
        Chức danh bạn muốn ứng tuyển
      </label>
      <div className="flex flex-col gap-2 sm:flex-row">
        <input
          id={inputId}
          type="text"
          value={title}
          maxLength={120}
          autoComplete="off"
          placeholder="Ví dụ: Lập trình viên Java"
          onChange={(event) => setTitle(event.target.value)}
          className="min-h-target min-w-0 flex-1 rounded-lg border border-border-chip bg-inset px-3 text-body-md text-text placeholder:text-text-muted hover:border-selected"
        />
        <button
          type="submit"
          className="min-h-target rounded-md border border-border-chip px-4 text-ui text-text-secondary transition-colors hover:border-selected hover:text-text"
        >
          Tìm vai trò
        </button>
      </div>
      <p
        role="status"
        className={
          outcome.kind === "matched" || outcome.kind === "loading"
            ? "m-0 text-body-md text-text-secondary"
            : "m-0 text-body-md text-amber"
        }
      >
        {message}
      </p>
    </form>
  );
}
