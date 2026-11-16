"use client";

import { useEffect, useState } from "react";

import { fetchSkills, skillDisplayName } from "@/lib/vocab";

/**
 * Câu của trang giữ chỗ Cố vấn (#153): gọi tên kỹ năng mà người dùng chạm trên hồ sơ kỹ năng. Tên lấy từ
 * `GET /api/v1/skills`; mã không có trong danh sách thì không in mã ra như một tên. Câu không chứa số (DEC-6).
 */
export function PathPlaceholder({ skill }: { skill: string | null }) {
  const [name, setName] = useState<string | null>(null);

  useEffect(() => {
    if (!skill) return;
    const controller = new AbortController();
    fetchSkills({ signal: controller.signal }).then((result) => {
      if (controller.signal.aborted || result.kind !== "ok") return;
      const found = result.skills.find((row) => row.code === skill);
      setName(found ? skillDisplayName(found) : null);
    });
    return () => controller.abort();
  }, [skill]);

  return (
    <p data-testid="insight-sentence" className="mt-4 mb-0 max-w-[68ch] text-body-md text-text-quiet">
      {name
        ? `Lộ trình học của vai trò này, mở tại kỹ năng ${name}, sẽ có ở sprint sau.`
        : "Lộ trình học của vai trò này sẽ có ở sprint sau."}
    </p>
  );
}
