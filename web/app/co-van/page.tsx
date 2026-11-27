import { isSkillCode } from "@/lib/haido-keys";
import { DEFAULT_LEVEL, LEVEL_OPTIONS, ROLE_OPTIONS } from "@/lib/labels";

import { LearningPathScreen } from "../components/advisor/learning-path-screen";

type SearchParams = Promise<{ [key: string]: string | string[] | undefined }>;

function first(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

/**
 * Trang `/co-van?role=&level=&skill=` (#121, #217): lộ trình học theo chặng của một vai trò, mở ở một kỹ năng khi có
 * `skill` (#153). Server chỉ đọc tham số; số và hồ sơ trình duyệt nằm ở `LearningPathScreen`. Mã vai trò hay kỹ năng lạ
 * không được in như một tên.
 */
export default async function AdvisoryPage({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const roleCode = first(params.role);
  const levelCode = first(params.level);
  const skillCode = first(params.skill);
  const knownRole = ROLE_OPTIONS.some((option) => option.code === roleCode && option.code !== "all");
  const knownLevel = LEVEL_OPTIONS.some((option) => option.code === levelCode);

  return (
    <section className="py-2">
      <LearningPathScreen
        initialRole={knownRole ? (roleCode as string) : null}
        initialLevel={knownLevel ? (levelCode as string) : null}
        profileLevel={knownLevel ? (levelCode as string) : DEFAULT_LEVEL}
        initialSkill={skillCode !== undefined && isSkillCode(skillCode) ? skillCode : null}
        unknownRole={roleCode !== undefined && !knownRole}
      />
    </section>
  );
}
