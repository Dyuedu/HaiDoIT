"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";

import { isSkillCode } from "@/lib/haido-keys";
import { getLocationSearch, getServerLocationSearch, replaceSearchParam, subscribeLocation } from "@/lib/location-search";
import { getProfileSnapshot, getServerProfileSnapshot, subscribeProfile } from "@/lib/profile-store";
import { type SkillRolesResult, fetchSkillRoles } from "@/lib/skill-roles";
import { buildSkillRolesView } from "@/lib/skill-roles-view";
import { type SkillsResult, fetchSkills } from "@/lib/vocab";

import { LoadError } from "../map/load-error";
import { SnapshotCaption } from "../map/snapshot-caption";
import { SkillPicker } from "./skill-picker";
import { DataTable } from "./overview/charts";
import { SkillRolesList } from "./skill-roles-list";

const LOADING = "Đang tải số liệu…";
const UNREADABLE = "Không đọc được số liệu. Thử lại sau.";

interface Loaded {
  key: string;
  result: SkillRolesResult;
}

/**
 * "Kỹ năng của bạn dùng ở vai trò nào" (#113), phía trình duyệt: chọn một kỹ năng (#167), rồi mỗi vai trò một dòng với
 * tỷ lệ tin entry-level nhắc tới kỹ năng đó (#169). Kỹ năng đã chọn nằm ở `?skill=` của URL để chia sẻ được. Số gọi qua
 * proxy `/api/*` sau khi trang mở, như màn người mới.
 */
export function SkillRolesScreen() {
  const search = useSyncExternalStore(subscribeLocation, getLocationSearch, getServerLocationSearch);
  const fromUrl = new URLSearchParams(search).get("skill");
  const skill = fromUrl !== null && isSkillCode(fromUrl) ? fromUrl : null;
  const profile = useSyncExternalStore(subscribeProfile, getProfileSnapshot, getServerProfileSnapshot);
  const [vocab, setVocab] = useState<SkillsResult | null>(null);
  const [retry, setRetry] = useState(0);
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const statusRef = useRef<HTMLParagraphElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetchSkills({ signal: controller.signal }).then((result) => {
      if (!controller.signal.aborted) setVocab(result);
    });
    return () => controller.abort();
  }, []);

  const requestKey = skill ? `${skill}#${retry}` : null;

  useEffect(() => {
    if (!skill || requestKey === null) return;
    const controller = new AbortController();
    fetchSkillRoles({ skill, signal: controller.signal }).then((result) => {
      if (!controller.signal.aborted) setLoaded({ key: requestKey, result });
    });
    return () => controller.abort();
    // `requestKey` gộp kỹ năng và lần thử lại.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [requestKey]);

  const result = skill && loaded?.key === requestKey ? loaded.result : null;

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
  } else if (result?.kind === "ok") {
    const view = buildSkillRolesView(result.envelope);
    content = (
      <>
        <p className="m-0 text-body-md font-semibold text-text">{view.skillText}</p>
        {view.notMentionedText ? (
          <p className="m-0 text-body-md text-amber">{view.notMentionedText}</p>
        ) : (
          <>
            <SkillRolesList lines={view.lines} />
            <DataTable
              caption="Tỷ lệ tin cho người mới nhắc tới kỹ năng, theo vai trò"
              head={["Vai trò", "Tỷ lệ", "Tính trên"]}
              rows={view.lines.map((l) => [l.label, l.shareText, l.nText || "Chưa có tin nào"])}
              numeric={[]}
            />
          </>
        )}
        <SnapshotCaption caption={view.caption} />
      </>
    );
  }

  return (
    <div className="mt-4 flex flex-col gap-4">
      <SkillPicker
        vocab={vocab}
        selected={skill}
        profileSkills={profile.skills}
        onSelect={(code) => replaceSearchParam("skill", code)}
      />
      {skill && (
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
