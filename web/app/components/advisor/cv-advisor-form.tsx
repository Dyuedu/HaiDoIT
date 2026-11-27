"use client";

import { useEffect, useId, useRef, useState } from "react";

import {
  type AdvisorRoadmapData,
  type AdvisorRoadmapEnvelope,
  CV_ACCEPT_ATTR,
  postAdvisorRoadmap,
  validateCvFile,
} from "@/lib/advisor-roadmap";
import { levelLabel, roleLabel } from "@/lib/labels";

interface CvAdvisorFormProps {
  role: string | null;
  level: string;
  haveSkills: readonly string[];
  skillName: (code: string) => string;
  advisorData: AdvisorRoadmapData | null;
  ownedSkills: ReadonlySet<string>;
  onSuccess: (envelope: AdvisorRoadmapEnvelope) => void;
  onResetAdvisor?: () => void;
}

export function CvAdvisorForm({
  role,
  level,
  haveSkills,
  skillName,
  advisorData,
  ownedSkills,
  onSuccess,
  onResetAdvisor,
}: CvAdvisorFormProps) {
  const fileId = useId();
  const consentId = useId();
  const [file, setFile] = useState<File | null>(null);
  const [consent, setConsent] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    return () => abortRef.current?.abort();
  }, []);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const picked = event.target.files?.[0] ?? null;
    if (!picked) {
      setFile(null);
      setError(null);
      return;
    }
    const validationError = validateCvFile(picked);
    if (validationError) {
      setFile(null);
      setError(validationError);
      return;
    }
    setFile(picked);
    setError(null);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!role) {
      setError("Vui lòng chọn vai trò mục tiêu ở trên trước khi tải CV.");
      return;
    }
    if (!file) {
      setError("Vui lòng chọn tệp CV định dạng PDF hoặc DOCX (tối đa 5 MB).");
      return;
    }
    const validationError = validateCvFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }
    if (!consent) {
      setError("Vui lòng đánh dấu đồng ý gửi nội dung CV để phân tích trước khi tạo lộ trình.");
      return;
    }

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setError(null);
    setSubmitting(true);
    try {
      const result = await postAdvisorRoadmap({
        file,
        role,
        level,
        consent: true,
        have: haveSkills,
        signal: controller.signal,
      });
      if (controller.signal.aborted) return;

      if (result.kind === "ok") {
        onSuccess(result.envelope);
      } else if (result.kind === "error") {
        setError(result.message);
      } else {
        setError("Không nhận được lộ trình phản hồi hợp lệ từ máy chủ. Vui lòng thử lại sau.");
      }
    } finally {
      if (!controller.signal.aborted) setSubmitting(false);
    }
  };

  const remainingCore = advisorData
    ? advisorData.missing_core_skills.filter((code) => !ownedSkills.has(code))
    : [];
  const remainingCommon = advisorData
    ? advisorData.missing_common_skills.filter((code) => !ownedSkills.has(code))
    : [];

  return (
    <section
      aria-labelledby="cv-advisor-heading"
      className="flex flex-col gap-4 rounded-xl border border-border bg-panel p-panel"
    >
      <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <h2 id="cv-advisor-heading" className="m-0 text-section text-text">
          Cá nhân hóa lộ trình từ CV của bạn
        </h2>
        <span className="text-caption text-text-muted">PDF hoặc DOCX · Tối đa 5 MB · Không lưu tệp CV</span>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3" noValidate>
        <div className="flex flex-col gap-1.5">
          <label htmlFor={fileId} className="font-mono text-kicker uppercase text-text-muted">
            Tệp CV (PDF hoặc DOCX, tối đa 5 MB)
          </label>
          <input
            id={fileId}
            type="file"
            accept={CV_ACCEPT_ATTR}
            onChange={handleFileChange}
            className="min-h-target w-full cursor-pointer rounded-lg border border-border-chip bg-inset px-3 py-2 text-body-md text-text file:mr-3 file:cursor-pointer file:rounded-md file:border file:border-border-chip file:bg-panel file:px-3 file:py-1.5 file:text-ui file:text-text-secondary hover:border-selected"
          />
          {file && (
            <p className="m-0 text-caption text-text-secondary">
              Đã chọn: <span className="font-mono text-text">{file.name}</span>
            </p>
          )}
        </div>

        <label
          htmlFor={consentId}
          className="flex min-h-target cursor-pointer items-start gap-3 rounded-lg border border-border-chip bg-inset px-3 py-2.5 text-caption text-text-secondary transition-colors hover:border-selected"
        >
          <input
            id={consentId}
            type="checkbox"
            checked={consent}
            onChange={(event) => {
              setConsent(event.target.checked);
              if (event.target.checked && error) setError(null);
            }}
            className="mt-0.5 size-4 shrink-0 cursor-pointer accent-selected"
          />
          <span>
            Tôi đồng ý gửi nội dung CV để phân tích lộ trình học (hệ thống đọc văn bản trên RAM để đối chiếu với yêu
            cầu tuyển dụng và có thể gửi tới LLM khi bật khóa API; không lưu bản gốc hay nội dung hồ sơ lên máy chủ).
          </span>
        </label>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="submit"
            disabled={submitting}
            className="inline-flex min-h-target cursor-pointer items-center justify-center rounded-md border border-selected bg-notice px-4 text-ui font-medium text-text transition-colors hover:bg-inset disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submitting ? "Đang tạo lộ trình…" : "Tạo lộ trình từ CV"}
          </button>
          {advisorData && onResetAdvisor && (
            <button
              type="button"
              onClick={onResetAdvisor}
              className="inline-flex min-h-target cursor-pointer items-center justify-center rounded-md border border-border-chip px-4 text-ui text-text-secondary transition-colors hover:border-selected hover:text-text"
            >
              Quay lại lộ trình mặc định
            </button>
          )}
        </div>
      </form>

      {submitting && role && (
        <div
          role="status"
          aria-label="Tiến trình phân tích CV"
          className="flex flex-col gap-1 rounded-lg border border-border-chip bg-inset p-3 text-caption text-text-secondary"
        >
          <p className="m-0 text-text">Đang phân tích CV và đối chiếu dữ liệu JD…</p>
          <p className="m-0">
            Vai trò <strong className="text-text">{roleLabel(role)}</strong> · Cấp bậc{" "}
            <strong className="text-text">{levelLabel(level)}</strong> · Đang dựng lộ trình từng chặng kiểu
            roadmap.sh
          </p>
        </div>
      )}

      {error && (
        <div role="alert" className="rounded-xl border border-amber-deep bg-notice p-3 text-body-md text-text">
          {error}
        </div>
      )}

      {advisorData && (
        <section
          aria-labelledby="cv-gap-summary-heading"
          className="flex flex-col gap-3 rounded-lg border border-border-chip bg-inset p-4"
        >
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h3 id="cv-gap-summary-heading" className="m-0 text-ui font-medium text-text">
              Phân tích CV theo yêu cầu tuyển dụng
            </h3>
            <span className="rounded-md border border-border-chip bg-panel px-2.5 py-0.5 text-caption text-text-secondary">
              {advisorData.generation_mode === "llm"
                ? "Phân tích bằng AI + dữ liệu JD"
                : "Tổng hợp từ dữ liệu JD thị trường"}
            </span>
          </div>

          <p className="m-0 max-w-[75ch] text-body-md text-text-secondary">{advisorData.advisor_summary}</p>

          <div className="grid gap-3 sm:grid-cols-3">
            <div className="flex flex-col gap-1.5">
              <span className="font-mono text-kicker uppercase text-text-muted">Kỹ năng thấy trong CV</span>
              {advisorData.cv_skills.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {advisorData.cv_skills.map((code) => (
                    <span
                      key={code}
                      className="rounded-md border border-border-chip bg-panel px-2 py-0.5 text-caption text-text"
                    >
                      {skillName(code)}
                    </span>
                  ))}
                </div>
              ) : (
                <span className="text-caption text-text-muted">Chưa nhận diện được kỹ năng trùng khớp từ khóa.</span>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <span className="font-mono text-kicker uppercase text-amber-soft">Cốt lõi JD cần bổ sung</span>
              {remainingCore.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {remainingCore.map((code) => (
                    <span
                      key={code}
                      className="rounded-md border border-amber-deep bg-notice px-2 py-0.5 text-caption text-text"
                    >
                      {skillName(code)}
                    </span>
                  ))}
                </div>
              ) : (
                <span className="text-caption text-text-secondary">Đã phủ nhóm kỹ năng cốt lõi đang theo dõi.</span>
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <span className="font-mono text-kicker uppercase text-text-muted">Thường gặp JD cần bổ sung</span>
              {remainingCommon.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {remainingCommon.map((code) => (
                    <span
                      key={code}
                      className="rounded-md border border-border-chip bg-panel px-2 py-0.5 text-caption text-text-secondary"
                    >
                      {skillName(code)}
                    </span>
                  ))}
                </div>
              ) : (
                <span className="text-caption text-text-secondary">Đã phủ nhóm kỹ năng thường gặp hiện tại.</span>
              )}
            </div>
          </div>
        </section>
      )}
    </section>
  );
}
