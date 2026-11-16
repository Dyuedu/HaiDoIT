import Link from "next/link";

import { isSkillCode } from "@/lib/haido-keys";
import { DEFAULT_LEVEL, LEVEL_OPTIONS, ROLE_OPTIONS, levelLabel, roleLabel } from "@/lib/labels";
import { skillProfileHref } from "@/lib/newcomer-roles-view";

import { PathPlaceholder } from "../components/advisor/path-placeholder";

type SearchParams = Promise<{ [key: string]: string | string[] | undefined }>;

function first(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

/**
 * Trang `/co-van`. Tới khi có màn lộ trình (#121, #213–#219) đây là trang giữ chỗ (#153): mở từ một kỹ năng chưa có trên
 * hồ sơ kỹ năng với `?role=&level=&skill=`, gọi tên vai trò, cấp và kỹ năng, và nói lộ trình có ở sprint sau. Không có
 * tham số thì giữ câu giới thiệu chung. Câu trên trang không chứa số (DEC-6).
 */
export default async function AdvisoryPage({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const roleCode = first(params.role);
  const levelCode = first(params.level);
  const skillCode = first(params.skill);

  if (roleCode === undefined && skillCode === undefined) {
    return (
      <section className="py-2">
        <h1 className="m-0 text-title text-text">Cố vấn</h1>
        <p className="mt-4 mb-0 max-w-[68ch] text-body-md text-text-quiet">
          Lộ trình học tập và phân tích khoảng trống kỹ năng dựa trên thị trường.
        </p>
      </section>
    );
  }

  const knownRole = ROLE_OPTIONS.some((option) => option.code === roleCode && option.code !== "all");
  const level = LEVEL_OPTIONS.some((option) => option.code === levelCode) ? (levelCode as string) : DEFAULT_LEVEL;
  const skill = skillCode !== undefined && isSkillCode(skillCode) ? skillCode : null;

  return (
    <section className="py-2">
      <h1 className="m-0 text-title text-text">
        {knownRole ? `Lộ trình học: ${roleLabel(roleCode as string)}` : "Lộ trình học"}
      </h1>
      {knownRole ? (
        <>
          <p className="mt-2 mb-0 text-body-md text-text-secondary">{levelLabel(level)}</p>
          <PathPlaceholder skill={skill} />
          <Link
            href={skillProfileHref(roleCode as string, level)}
            className="mt-6 inline-flex min-h-target items-center rounded-md border border-border-chip px-4 text-ui text-text-secondary transition-colors hover:border-selected hover:text-text"
          >
            Quay lại hồ sơ kỹ năng
          </Link>
        </>
      ) : (
        <>
          <p className="mt-4 mb-0 max-w-[68ch] text-body-md text-text-quiet">
            Không có vai trò này. Chọn một vai trò trên hồ sơ kỹ năng.
          </p>
          <Link
            href="/ho-so-ky-nang"
            className="mt-6 inline-flex min-h-target items-center rounded-md border border-border-chip px-4 text-ui text-text-secondary transition-colors hover:border-selected hover:text-text"
          >
            Quay lại hồ sơ kỹ năng
          </Link>
        </>
      )}
    </section>
  );
}
