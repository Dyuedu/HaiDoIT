import Link from "next/link";

import { LEVEL_OPTIONS, ROLE_OPTIONS, levelLabel, roleLabel } from "@/lib/labels";
import { NEWCOMER_LEVEL } from "@/lib/newcomer-roles-view";

type SearchParams = Promise<{ [key: string]: string | string[] | undefined }>;

function first(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

/**
 * Trang giữ chỗ của hồ sơ kỹ năng (#147, tới khi có #111): gọi tên vai trò và cấp đã chọn, nói hồ sơ kỹ năng có ở
 * sprint sau. Mã vai trò hay cấp lạ thì không in mã ra như một tên. Câu trên trang không chứa số (DEC-6).
 */
export default async function SkillProfilePlaceholder({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const roleCode = first(params.role);
  const levelCode = first(params.level) ?? NEWCOMER_LEVEL;
  const knownRole = ROLE_OPTIONS.some((option) => option.code === roleCode && option.code !== "all");
  const knownLevel = LEVEL_OPTIONS.some((option) => option.code === levelCode);

  return (
    <section className="py-2">
      <h1 className="m-0 text-title text-text">
        {knownRole ? `Hồ sơ kỹ năng: ${roleLabel(roleCode as string)}` : "Hồ sơ kỹ năng"}
      </h1>
      {knownRole ? (
        <>
          {knownLevel && <p className="mt-2 mb-0 text-body-md text-text-secondary">{levelLabel(levelCode)}</p>}
          <p data-testid="insight-sentence" className="mt-4 mb-0 max-w-[68ch] text-body-md text-text-quiet">
            Hồ sơ kỹ năng của vai trò này, gồm các kỹ năng mà tin tuyển dụng yêu cầu và mức thường gặp của từng kỹ
            năng, sẽ có ở sprint sau.
          </p>
        </>
      ) : (
        <p data-testid="insight-sentence" className="mt-4 mb-0 max-w-[68ch] text-body-md text-text-quiet">
          Không có vai trò này. Chọn một vai trò trong danh sách người mới.
        </p>
      )}
      <Link
        href="/insights"
        className="mt-6 inline-flex min-h-target items-center rounded-md border border-border-chip px-4 text-ui text-text-secondary transition-colors hover:border-selected hover:text-text"
      >
        Quay lại danh sách người mới
      </Link>
    </section>
  );
}
