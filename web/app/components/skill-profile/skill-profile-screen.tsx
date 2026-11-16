"use client";

import { useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";

import { type Profile, PROFILE_VERSION } from "@/lib/haido-keys";
import { LEVEL_ENTRY_NOTE, LEVEL_OPTIONS, ROLE_OPTIONS, levelLabel, roleLabel } from "@/lib/labels";
import { skillProfileHref } from "@/lib/newcomer-roles-view";
import { getProfileSnapshot, getServerProfileSnapshot, saveProfile, subscribeProfile } from "@/lib/profile-store";
import { GROUP_NOTE, buildSkillProfileView } from "@/lib/skill-profile-view";
import { type SkillRatesResult, fetchSkillRates, skillRatesUrl } from "@/lib/skill-rates";
import { type SkillsResult, fetchSkills, skillDisplayName } from "@/lib/vocab";

import { FilterSelect } from "../map/filter-select";
import { LoadError } from "../map/load-error";
import { SnapshotCaption } from "../map/snapshot-caption";
import { SkillList } from "./skill-list";
import { SkillSearch } from "./skill-search";
import { type TitleOutcome, TitleSearch } from "./title-search";

const LOADING = "Đang tải số liệu…";
const UNREADABLE = "Không đọc được số liệu. Thử lại sau.";
const PICK_ROLE = "Gõ chức danh hoặc chọn một vai trò để xem kỹ năng mà tin tuyển dụng của vai trò đó yêu cầu.";

/** Vai trò chọn được: mọi vai trò của `config/rules.toml`, không có `all`. */
export const PROFILE_ROLES = ROLE_OPTIONS.filter((option) => option.code !== "all");
const ROLE_CODES = new Set(PROFILE_ROLES.map((option) => option.code));
const LEVEL_CODES = new Set(LEVEL_OPTIONS.map((option) => option.code));

interface Loaded {
  key: string;
  role: string;
  level: string;
  result: SkillRatesResult;
}

interface SkillProfileScreenProps {
  /** Vai trò hợp lệ trong URL, hoặc `null`. */
  initialRole: string | null;
  /** Cấp hợp lệ trong URL, hoặc cấp mặc định `entry` (#134). */
  initialLevel: string;
  /** URL có tham số `role` nhưng mã không phải vai trò nào. */
  unknownRole: boolean;
}

/**
 * Hồ sơ kỹ năng, phía trình duyệt (#111): ô chức danh (#150), ô Vai trò và Cấp bậc, danh sách kỹ năng có tick (#152),
 * liên kết lộ trình (#153), ô tìm kỹ năng (#207). Hồ sơ đọc và ghi qua `haido-keys.ts` (#206, AD-23); gửi lên API bằng
 * `have=` (AD-22). Số gọi qua proxy `/api/*` sau khi trang mở, như màn người mới.
 */
export function SkillProfileScreen({ initialRole, initialLevel, unknownRole }: SkillProfileScreenProps) {
  // `undefined`: người dùng chưa chọn trên màn này, dùng vai trò mục tiêu đã lưu (FR-14). `null`: không có vai trò.
  const [chosenRole, setChosenRole] = useState<string | null | undefined>(
    initialRole ?? (unknownRole ? null : undefined),
  );
  const [level, setLevel] = useState(initialLevel);
  const [vocab, setVocab] = useState<SkillsResult | null>(null);
  const [title, setTitle] = useState<TitleOutcome>({ kind: "idle" });
  const [retry, setRetry] = useState(0);
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const statusRef = useRef<HTMLParagraphElement>(null);

  // Hồ sơ trình duyệt (#206): server và lần hydrate đầu thấy hồ sơ rỗng, trình duyệt thấy hồ sơ đã lưu.
  const profile = useSyncExternalStore(subscribeProfile, getProfileSnapshot, getServerProfileSnapshot);
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

  const requestKey = role ? `${skillRatesUrl(role, level, skills)}#${retry}` : null;

  useEffect(() => {
    if (!role || requestKey === null) return;
    const controller = new AbortController();
    fetchSkillRates({ role, level, have: skills, signal: controller.signal }).then((result) => {
      if (!controller.signal.aborted) setLoaded({ key: requestKey, role, level, result });
    });
    return () => controller.abort();
    // `requestKey` gộp role, level, skills và lần thử lại.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [requestKey]);

  useEffect(() => {
    if (role) window.history.replaceState(window.history.state, "", skillProfileHref(role, level));
  }, [role, level]);

  const owned = useMemo(() => new Set(skills), [skills]);
  const names = useMemo(() => {
    const byCode = new Map(vocab?.kind === "ok" ? vocab.skills.map((s) => [s.code, skillDisplayName(s)]) : []);
    return (code: string) => byCode.get(code) ?? code;
  }, [vocab]);

  const save = (next: Partial<Profile>) => {
    saveProfile({ v: PROFILE_VERSION, role, level, skills, ...next });
  };

  const toggle = (skill: string) => {
    save({ skills: owned.has(skill) ? skills.filter((code) => code !== skill) : [...skills, skill] });
  };

  const chooseRole = (next: string) => {
    if (!ROLE_CODES.has(next)) return;
    setChosenRole(next);
    setTitle((current) => (current.kind === "matched" && current.role === next ? current : { kind: "idle" }));
    save({ role: next });
  };

  const chooseLevel = (next: string) => {
    if (!LEVEL_CODES.has(next)) return;
    setLevel(next);
    save({ level: next });
  };

  const onTitle = (outcome: TitleOutcome) => {
    setTitle(outcome);
    if (outcome.kind === "matched") {
      setChosenRole(outcome.role);
      save({ role: outcome.role });
    } else if (outcome.kind === "generic" || outcome.kind === "not_it") {
      setChosenRole(null);
    }
  };

  // Số của lần tải đúng vai trò và cấp đang chọn. Sau khi tick, giữ số cũ tới khi số mới về để danh sách không nhảy.
  const current = role && loaded?.role === role && loaded.level === level ? loaded : null;
  const fresh = current?.key === requestKey;
  const result = current && (fresh || current.result.kind === "ok") ? current.result : null;
  const unmatched = title.kind === "generic" || title.kind === "not_it";

  let content: React.ReactNode = null;
  if (role && result?.kind === "error") {
    content = (
      <LoadError
        message={result.message}
        snapshotDate={result.snapshotDate}
        onRetry={result.retryable ? () => setRetry((n) => n + 1) : undefined}
      />
    );
  } else if (role && result?.kind === "unreadable") {
    content = (
      <LoadError
        message={UNREADABLE}
        onRetry={() => {
          setRetry((n) => n + 1);
          statusRef.current?.focus();
        }}
      />
    );
  } else if (role && result?.kind === "ok") {
    const view = buildSkillProfileView(result.envelope, names);
    content = (
      <>
        {view.fallbackText && (
          <div className="rounded-xl border border-amber-deep bg-notice p-panel">
            <p className="m-0 text-body-md text-text">{view.fallbackText}</p>
            <p className="mt-1 mb-0 font-mono text-footer text-text-muted">{view.nText}</p>
          </div>
        )}
        {view.coreCountText && (
          <p data-testid="core-count" className="m-0 text-body-md text-text-secondary">
            <span className="font-mono text-mono text-text">{view.coreCountText}</span> kỹ năng cốt lõi bạn đã có
          </p>
        )}
        <SkillList lines={view.lines} owned={owned} onToggle={toggle} />
        <p className="m-0 max-w-[68ch] text-caption text-text-quiet">{GROUP_NOTE}</p>
        <SnapshotCaption caption={view.caption} />
      </>
    );
  }

  const roleOptions = role ? PROFILE_ROLES : [{ code: "", label: "Chọn vai trò" }, ...PROFILE_ROLES];

  return (
    <div className="flex flex-col gap-6">
      <h1 className="m-0 text-title text-text">{role ? `Hồ sơ kỹ năng: ${roleLabel(role)}` : "Hồ sơ kỹ năng"}</h1>

      <TitleSearch outcome={title} onOutcome={onTitle} />

      {unmatched && (
        <ul aria-label="Danh sách vai trò" className="m-0 flex list-none flex-wrap gap-2 p-0">
          {PROFILE_ROLES.map((option) => (
            <li key={option.code}>
              <button
                type="button"
                onClick={() => chooseRole(option.code)}
                className="min-h-target rounded-md border border-border-chip px-3 text-ui text-text-secondary transition-colors hover:border-selected hover:text-text"
              >
                {option.label}
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        <FilterSelect label="Vai trò" value={role ?? ""} options={roleOptions} onChange={chooseRole} />
        <FilterSelect label="Cấp bậc" value={level} options={LEVEL_OPTIONS} onChange={chooseLevel} note={LEVEL_ENTRY_NOTE} />
      </div>

      <section aria-labelledby="ky-nang-cua-ban" className="flex flex-col gap-3">
        <h2 id="ky-nang-cua-ban" className="m-0 text-section text-text">
          Kỹ năng của bạn
        </h2>
        <SkillSearch vocab={vocab} owned={owned} onToggle={toggle} />
      </section>

      <section aria-labelledby="ky-nang-tin-yeu-cau" className="flex flex-col gap-4">
        <h2 id="ky-nang-tin-yeu-cau" className="m-0 text-section text-text">
          {role ? `Kỹ năng tin tuyển dụng yêu cầu · ${levelLabel(level)}` : "Kỹ năng tin tuyển dụng yêu cầu"}
        </h2>
        {!role && !unmatched && (
          <p className="m-0 max-w-[68ch] text-body-md text-text-quiet">
            {unknownRole ? `Không có vai trò này. ${PICK_ROLE}` : PICK_ROLE}
          </p>
        )}
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
      </section>
    </div>
  );
}
