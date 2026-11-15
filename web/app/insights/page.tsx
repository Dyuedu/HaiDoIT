import { NewcomerScreen } from "../components/insights/newcomer-screen";

/**
 * Trang `/insights`. Mục đầu tiên là "Cửa vào cho người mới" (#110, #147): vai trò nào còn tuyển Intern, Fresher,
 * Junior. Câu trên trang không chứa số (DEC-6, #132); số nằm ở từng dòng, kèm n, ngày snapshot và nguồn.
 */
export default function InsightsPage() {
  const headingId = "nguoi-moi";
  return (
    <section className="py-2">
      <h1 className="m-0 text-title text-text">Insights</h1>
      <section aria-labelledby={headingId} className="mt-6">
        <h2 id={headingId} className="m-0 text-section text-text">
          Cửa vào cho người mới
        </h2>
        <p data-testid="insight-sentence" className="mt-2 mb-0 max-w-[68ch] text-body-md text-text-quiet">
          Vai trò xếp theo số tin tuyển Intern, Fresher hoặc Junior. Chọn một vai trò để xem kỹ năng mà tin của vai trò
          đó yêu cầu ở cấp mới vào nghề.
        </p>
        <NewcomerScreen />
      </section>
    </section>
  );
}
