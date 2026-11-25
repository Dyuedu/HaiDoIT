"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";

import { type Profile } from "@/lib/haido-keys";
import { ROLE_OPTIONS, levelLabel, roleLabel } from "@/lib/labels";
import { type LearningPathResult, fetchLearningPath, learningPathUrl } from "@/lib/learning-path";
import {
  ALL_DONE_TEXT,
  NOT_READY_HINT,
  NOT_READY_TEXT,
  PATH_LEVEL,
  buildLearningPathView,
} from "@/lib/learning-path-view";
import { skillProfileHref } from "@/lib/newcomer-roles-view";
import { getProfileSnapshot, getServerProfileSnapshot, saveProfile, subscribeProfile } from "@/lib/profile-store";
import { GROUP_NOTE, learningPathHref } from "@/lib/skill-profile-view";
import { type SkillsResult, fetchSkills, skillDisplayName } from "@/lib/vocab";

import { FilterSelect } from "../map/filter-select";
import { LoadError } from "../map/load-error";
import { SnapshotCaption } from "../map/snapshot-caption";
import { PathGraph } from "./path-graph";
import { pathNodeId } from "./path-node";
import { SkillPanel } from "./skill-panel";

const LOADING = "Đang tải lộ trình…";
const UNREADABLE = "Không đọc được số liệu. Thử lại sau.";
const INTRO = "Chọn một vai trò để xem nên học gì trước, theo tin tuyển dụng dành cho người mới vào nghề.";

const PATH_ROLES = ROLE_OPTIONS.filter((option) => option.code !== "all");
const ROLE_CODES = new Set(PATH_ROLES.map((option) => option.code));

interface Loaded {
  key: string;
  role: string;
  result: LearningPathResult;
}

interface LearningPathScreenProps {
  /** Vai trò hợp lệ trong URL, hoặc `null`. */
  initialRole: string | null;
  /** Cấp hợp lệ trong URL: chỉ dùng cho liên kết về hồ sơ kỹ năng. Lộ trình luôn ở nhóm mới vào nghề (#134). */
  profileLevel: string;
  /** Kỹ năng đúng định dạng trong URL: mở ngăn ở kỹ năng đó (#153). */
  initialSkill: string | null;
  /** URL có tham số `role` nhưng mã không phải vai trò nào. */
  unknownRole: boolean;
}

/**
 * Màn lộ trình học (#217, story #121), phía trình duyệt. Thứ tự, chặng đang học và số đếm của API (AD-7, AD-22); hồ sơ
 * đọc và ghi qua `profile-store.ts` (AD-23), gửi lên API bằng `have=`. Ô tick phản hồi ngay theo hồ sơ; số cũ ở lại tới
 * khi số mới về.
 */
export function LearningPathScreen({ initialRole, profileLevel, initialSkill, unknownRole }: LearningPathScreenProps) {
  // `undefined`: chưa chọn trên màn này, dùng vai trò mục tiêu đã lưu (FR-14). `null`: không có vai trò.
  const [chosenRole, setChosenRole] = useState<string | null | undefined>(
    initialRole ?? (unknownRole ? null : undefined),
  );
  const [openSkill, setOpenSkill] = useState<string | null>(initialSkill);
  const [vocab, setVocab] = useState<SkillsResult | null>(null);
  const [retry, setRetry] = useState(0);
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const statusRef = useRef<HTMLParagraphElement>(null);
  const scrolledRef = useRef(false);

  const profile: Profile = useSyncExternalStore(subscribeProfile, getProfileSnapshot, getServerProfileSnapshot);
  const skills = profile.skills;
  const savedRole = profile.role !== null && ROLE_CODES.has(profile.role) ? profile.role : null;
  const role = chosenRole === undefined ? savedRole : chosenRole;

  useEffect(() => {
    const controller = new AbortController();
    fetchSkills({ signal: controller.signal }).then((result) => {
      if (!controller.signal.aborted) setVocab(result);
    });
    return () => controller.abort();
  }, []);

  const requestKey = role ? `${learningPathUrl(role, PATH_LEVEL, skills)}#${retry}` : null;

  useEffect(() => {
    if (!role || requestKey === null) return;
    const controller = new AbortController();
    fetchLearningPath(role, PATH_LEVEL, skills, { signal: controller.signal }).then((result) => {
      if (!controller.signal.aborted) setLoaded({ key: requestKey, role, result });
    });
    return () => controller.abort();
    // `requestKey` gộp role, skills và lần thử lại.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [requestKey]);

  useEffect(() => {
    if (role) window.history.replaceState(window.history.state, "", learningPathHref(role, PATH_LEVEL, openSkill));
  }, [role, openSkill]);

  const owned = useMemo(() => new Set(skills), [skills]);
  const nameOf = useMemo(() => {
    const byCode = new Map(vocab?.kind === "ok" ? vocab.skills.map((s) => [s.code, skillDisplayName(s)]) : []);
    return (code: string) => byCode.get(code);
  }, [vocab]);
  const shortNameOf = useMemo(() => {
    const byCode = new Map(vocab?.kind === "ok" ? vocab.skills.map((s) => [s.code, s.name_vi]) : []);
    return (code: string) => byCode.get(code) ?? code;
  }, [vocab]);

  // Số của lần tải đúng vai trò đang chọn. Sau khi tick, giữ số cũ tới khi số mới về để màn không nhảy.
  const current = role && loaded?.role === role ? loaded : null;
  const result = current && (current.key === requestKey || current.result.kind === "ok") ? current.result : null;
  const view = useMemo(
    () => (result?.kind === "ok" ? buildLearningPathView(result.envelope, (code) => nameOf(code) ?? code, shortNameOf) : null),
    [result, nameOf, shortNameOf],
  );
  const openNode = view?.nodes.find((node) => node.skill === openSkill) ?? null;

  // Mở từ liên kết của hồ sơ kỹ năng (#153): cuộn tới đúng kỹ năng, một lần.
  useEffect(() => {
    if (!openNode || scrolledRef.current || openNode.skill !== initialSkill) return;
    scrolledRef.current = true;
    document.getElementById(pathNodeId(openNode.skill))?.scrollIntoView?.({ block: "start" });
  }, [openNode, initialSkill]);

  const toggle = (skill: string) => {
    saveProfile({
      ...profile,
      skills: owned.has(skill) ? skills.filter((code) => code !== skill) : [...skills, skill],
    });
  };

  const chooseRole = (next: string) => {
    if (!ROLE_CODES.has(next)) return;
    setChosenRole(next);
    setOpenSkill(null);
    saveProfile({ ...profile, role: next });
  };

  const close = useCallback(() => {
    setOpenSkill(null);
    if (openSkill) document.getElementById(pathNodeId(openSkill))?.focus();
  }, [openSkill]);

  let content: React.ReactNode = null;
  if (result?.kind === "error") {
    content = (
      <LoadError
        message={result.message}
        snapshotDate={result.snapshotDate}
        onRetry={result.retryable ? () => setRetry((n) => n + 1) : undefined}
      />
    );
  } else if (result?.kind === "unreadable") {
    content = (
      <LoadError
        message={UNREADABLE}
        onRetry={() => {
          setRetry((n) => n + 1);
          statusRef.current?.focus();
        }}
      />
    );
  } else if (view && !view.ready) {
    content = (
      <>
        <div className="rounded-xl border border-border bg-panel p-panel">
          <p data-testid="insight-sentence" className="m-0 text-body-md text-text">
            {NOT_READY_TEXT}
          </p>
          <p data-testid="insight-sentence" className="mt-1 mb-0 max-w-[68ch] text-body-md text-text-quiet">
            {NOT_READY_HINT}
          </p>
        </div>
        <SnapshotCaption caption={view.caption} />
      </>
    );
  } else if (view) {
    const todo = view.current?.nodes.filter((node) => !owned.has(node.skill)) ?? [];
    const missingName = openSkill && !openNode ? nameOf(openSkill) : undefined;
    content = (
      <>
        {view.fallbackText && (
          <div className="rounded-xl border border-amber-deep bg-notice p-panel">
            <p className="m-0 text-body-md text-text">{view.fallbackText}</p>
            {view.nText && <p className="mt-1 mb-0 font-mono text-footer text-text-muted">{view.nText}</p>}
          </div>
        )}
        {missingName && (
          <p data-testid="insight-sentence" className="m-0 text-body-md text-amber-soft">
            {missingName} không nằm trên lộ trình của vai trò này.
          </p>
        )}
        <section aria-labelledby="hoc-tiep" className="flex flex-col gap-3 rounded-xl border border-border bg-panel p-panel">
          <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
            <h2 id="hoc-tiep" className="m-0 text-section text-text">
              Học tiếp
            </h2>
            <p data-testid="path-count" className="m-0 text-body-md text-text-secondary">
              <span className="font-mono text-mono text-text">{view.countText}</span> kỹ năng trên lộ trình bạn đã có
            </p>
          </div>
          {view.allDone ? (
            <p data-testid="insight-sentence" className="m-0 text-body-md text-text">
              {ALL_DONE_TEXT}
            </p>
          ) : (
            <>
              <p className="m-0 flex flex-wrap items-baseline gap-x-2 text-body-md text-text-secondary">
                <span>{view.current?.title}</span>
                {view.current?.chooseOne && <span className="text-caption text-text-muted">Chọn một</span>}
              </p>
              <ul className="m-0 flex list-none flex-wrap gap-2 p-0">
                {todo.map((node) => (
                  <li key={node.skill}>
                    <button
                      type="button"
                      onClick={() => setOpenSkill(node.skill)}
                      className="min-h-target cursor-pointer rounded-md border border-border-chip px-3 text-ui text-text-secondary transition-colors hover:border-selected hover:text-text"
                    >
                      {node.shortName}
                    </button>
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>
        <PathGraph title={roleLabel(role ?? "")} stages={view.stages} owned={owned} selected={openNode} onToggle={toggle} onOpen={setOpenSkill} />
        <p data-testid="insight-sentence" className="m-0 max-w-[68ch] text-caption text-text-quiet">
          {GROUP_NOTE}
        </p>
        <SnapshotCaption caption={view.caption} />
        {openNode && (
          <SkillPanel
            node={openNode}
            have={owned.has(openNode.skill)}
            onToggle={toggle}
            onOpen={setOpenSkill}
            onClose={close}
          />
        )}
      </>
    );
  }

  const roleOptions = role ? PATH_ROLES : [{ code: "", label: "Chọn vai trò" }, ...PATH_ROLES];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <h1 className="m-0 text-title text-text">{role ? `Lộ trình học: ${roleLabel(role)}` : "Cố vấn"}</h1>
        {role ? (
          <p className="m-0 text-body-md text-text-secondary">{levelLabel(PATH_LEVEL)}</p>
        ) : (
          <p data-testid="insight-sentence" className="m-0 max-w-[68ch] text-body-md text-text-quiet">
            {unknownRole ? `Không có vai trò này. ${INTRO}` : INTRO}
          </p>
        )}
      </div>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
        <div className="sm:w-80">
          <FilterSelect label="Vai trò" value={role ?? ""} options={roleOptions} onChange={chooseRole} />
        </div>
        {role && (
          <Link
            href={skillProfileHref(role, role === initialRole ? profileLevel : PATH_LEVEL)}
            className="inline-flex min-h-target items-center justify-center rounded-md border border-border-chip px-4 text-ui text-text-secondary transition-colors hover:border-selected hover:text-text"
          >
            Xem hồ sơ kỹ năng
          </Link>
        )}
      </div>

      {role && (
        <p
          ref={statusRef}
          role="status"
          tabIndex={-1}
          className={result === null ? "m-0 text-body-md text-text-muted" : "sr-only"}
        >
          {result === null ? LOADING : ""}
        </p>
      )}
      {content}
    </div>
  );
}
