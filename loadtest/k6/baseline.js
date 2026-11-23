// Đo sức chịu tải baseline của API (#342). Cách chạy: loadtest/README.md.
//
//   SCENARIO=smoke       gọi mỗi URL của kịch bản đúng một lần, kiểm tra mọi URL trả 200.
//   SCENARIO=breakpoint  tăng RPS từ START_RPS lên MAX_RPS trong DURATION; dừng khi p95 >= 200 ms hoặc lỗi >= 0,1%.
//
// Mỗi iteration là đúng một request, nên tốc độ iteration (`iterations/s`) là RPS.
import http from "k6/http";
import { check } from "k6";
import exec from "k6/execution";
import { SharedArray } from "k6/data";

const BASE_URL = __ENV.BASE_URL || "http://127.0.0.1:8001";
const SCENARIO = __ENV.SCENARIO || "smoke";
const START_RPS = Number(__ENV.START_RPS || 10);
const MAX_RPS = Number(__ENV.MAX_RPS || 2000);
const DURATION = __ENV.DURATION || "10m";
const MAX_VUS = Number(__ENV.MAX_VUS || 2000);

const P = new SharedArray("params", () => [JSON.parse(open("./params.json"))])[0];

const pick = (xs) => xs[Math.floor(Math.random() * xs.length)];

// Trọng số phỏng theo một lượt mở trang Insights: toàn cảnh và người mới trước, rồi lọc theo vai trò và kỹ năng.
const STEPS = [
  { name: "market-overview", weight: 25, url: () => "/api/v1/market-overview" },
  { name: "newcomer-roles", weight: 20, url: () => "/api/v1/newcomer-roles" },
  { name: "city-shares", weight: 20, url: () => `/api/v1/city-shares?role=${pick(P.roles)}&level=${pick(P.levels)}` },
  { name: "skill-rates", weight: 15, url: () => `/api/v1/skill-rates?role=${pick(P.roles)}&level=entry` },
  { name: "skill-roles", weight: 15, url: () => `/api/v1/skill-roles?skill=${pick(P.skills)}` },
  { name: "skills", weight: 5, url: () => "/api/v1/skills" },
];
const TOTAL_WEIGHT = STEPS.reduce((s, x) => s + x.weight, 0);

// Mọi URL kịch bản có thể gọi, cho smoke.
const ALL = [
  ["market-overview", "/api/v1/market-overview"],
  ["newcomer-roles", "/api/v1/newcomer-roles"],
  ["skills", "/api/v1/skills"],
  ...P.roles.flatMap((r) => [
    ["skill-rates", `/api/v1/skill-rates?role=${r}&level=entry`],
    ...P.levels.map((l) => ["city-shares", `/api/v1/city-shares?role=${r}&level=${l}`]),
  ]),
  ...P.skills.map((s) => ["skill-roles", `/api/v1/skill-roles?skill=${s}`]),
];

const SCENARIOS = {
  smoke: {
    executor: "shared-iterations",
    vus: 1,
    iterations: ALL.length,
    exec: "smokeStep",
  },
  breakpoint: {
    executor: "ramping-arrival-rate",
    startRate: START_RPS,
    timeUnit: "1s",
    preAllocatedVUs: 100,
    maxVUs: MAX_VUS,
    stages: [{ duration: DURATION, target: MAX_RPS }],
    exec: "randomStep",
  },
};

if (!SCENARIOS[SCENARIO]) {
  throw new Error(`SCENARIO phải là ${Object.keys(SCENARIOS).join(" hoặc ")}`);
}

export const options = {
  scenarios: { [SCENARIO]: SCENARIOS[SCENARIO] },
  // Chỉ cần mã trạng thái: bỏ thân response để k6 không tốn CPU ở RPS cao.
  discardResponseBodies: true,
  thresholds: {
    http_req_duration: [{ threshold: "p(95)<200", abortOnFail: true, delayAbortEval: "30s" }],
    http_req_failed: [{ threshold: "rate<0.001", abortOnFail: true, delayAbortEval: "30s" }],
    checks: ["rate>0.999"],
  },
};

export function setup() {
  const res = http.get(`${BASE_URL}/api/v1/market-overview`);
  if (res.status !== 200) {
    throw new Error(`market-overview trả ${res.status}: DB đo đã seed chưa? (tools/loadtest_seed.py)`);
  }
}

function hit(name, path) {
  const res = http.get(`${BASE_URL}${path}`, { tags: { name } });
  check(res, { "status 200": (r) => r.status === 200 }, { name });
}

export function smokeStep() {
  const [name, path] = ALL[exec.scenario.iterationInTest];
  hit(name, path);
}

export function randomStep() {
  let roll = Math.random() * TOTAL_WEIGHT;
  for (const step of STEPS) {
    roll -= step.weight;
    if (roll < 0) {
      hit(step.name, step.url());
      return;
    }
  }
}
