import { DEFAULT_LEVEL, LEVEL_OPTIONS, ROLE_OPTIONS } from "@/lib/labels";

import { SkillProfileScreen } from "../components/skill-profile/skill-profile-screen";

type SearchParams = Promise<{ [key: string]: string | string[] | undefined }>;

function first(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

/**
 * Trang `/ho-so-ky-nang?role=&level=` (#111, #152): kỹ năng mà tin tuyển dụng của một vai trò yêu cầu, ở cấp của người
 * dùng. Server chỉ đọc tham số; số, hồ sơ trình duyệt và danh sách kỹ năng nằm ở `SkillProfileScreen`. Không có `level`
 * thì dùng cấp mặc định `entry` (#134). Mã vai trò lạ không được in như một tên.
 */
export default async function SkillProfilePage({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const roleCode = first(params.role);
  const levelCode = first(params.level);
  const knownRole = ROLE_OPTIONS.some((option) => option.code === roleCode && option.code !== "all");
  const knownLevel = LEVEL_OPTIONS.some((option) => option.code === levelCode);

  return (
    <section className="py-2">
      <SkillProfileScreen
        initialRole={knownRole ? (roleCode as string) : null}
        initialLevel={knownLevel ? (levelCode as string) : DEFAULT_LEVEL}
        unknownRole={roleCode !== undefined && !knownRole}
      />
    </section>
  );
}
