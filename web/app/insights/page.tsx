import { NewcomerScreen } from "../components/insights/newcomer-screen";
import { MarketOverviewScreen } from "../components/insights/overview/market-overview-screen";
import { SkillRolesScreen } from "../components/insights/skill-roles-screen";

/**
 * Trang `/insights`. Mở đầu là toàn cảnh thị trường (#326, #329): chỉ số, câu tóm tắt, biểu đồ theo cấp, vai trò, số năm,
 * nơi làm việc. Tiếp theo là "Cửa vào cho người mới" (#110, #147): vai trò nào còn tuyển Intern, Fresher,
 * Junior. Mục thứ hai là "Kỹ năng của bạn dùng ở vai trò nào" (#113, #167, #169): chọn một kỹ năng, xem tỷ lệ tin
 * entry-level của từng vai trò nhắc tới nó; `?skill=` giữ kỹ năng đã chọn. Câu trên trang không chứa số (DEC-6, #132);
 * số nằm ở từng dòng, kèm n, ngày snapshot và nguồn.
 */
export default function InsightsPage() {
  const headingId = "nguoi-moi";
  return (
    <section className="py-2">
      <h1 className="m-0 text-title text-text">Insights</h1>
      <section aria-labelledby="toan-canh" className="mt-6">
        <h2 id="toan-canh" className="m-0 text-section text-text">
          Thị trường việc làm IT hôm nay
        </h2>
        <p className="mt-2 mb-0 max-w-[68ch] text-body-md text-text-quiet">
          Tin tuyển dụng IT đang mở trên các trang việc làm, cập nhật mỗi đêm: thị trường cần vai trò nào, ở cấp nào, ở
          đâu, đòi bao nhiêu năm kinh nghiệm.
        </p>
        <MarketOverviewScreen />
      </section>
      <section aria-labelledby={headingId} className="mt-10">
        <h2 id={headingId} className="m-0 text-section text-text">
          Cửa vào cho người mới
        </h2>
        <p data-testid="insight-sentence" className="mt-2 mb-0 max-w-[68ch] text-body-md text-text-quiet">
          Vai trò xếp theo số tin tuyển Intern, Fresher hoặc Junior. Chọn một vai trò để xem kỹ năng mà tin của vai trò
          đó yêu cầu ở cấp mới vào nghề.
        </p>
        <NewcomerScreen />
      </section>
      <section aria-labelledby="ky-nang-cua-ban" className="mt-10">
        <h2 id="ky-nang-cua-ban" className="m-0 text-section text-text">
          Kỹ năng của bạn dùng ở vai trò nào
        </h2>
        <p className="mt-2 mb-0 max-w-[68ch] text-body-md text-text-quiet">
          Chọn một kỹ năng bạn đã có để xem tin tuyển Intern, Fresher hoặc Junior của từng vai trò nhắc tới nó nhiều hay
          ít. Chọn một vai trò để mở hồ sơ kỹ năng của vai trò đó.
        </p>
        <SkillRolesScreen />
      </section>
    </section>
  );
}
