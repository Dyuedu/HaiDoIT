import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  EMPTY_PROFILE,
  HAIDO_KEYS,
  HAIDO_PREFIX,
  MAX_PROFILE_SKILLS,
  clearHaidoData,
  isSkillCode,
  readProfile,
  writeProfile,
} from "@/lib/haido-keys";

beforeEach(() => {
  localStorage.clear();
});

afterEach(() => {
  localStorage.clear();
});

describe("AD-23 danh sách khóa đóng", () => {
  it("mọi khóa có tiền tố haido: và đúng ba khóa", () => {
    expect(HAIDO_PREFIX).toBe("haido:");
    expect(Object.values(HAIDO_KEYS).sort()).toEqual(
      ["haido:eval", "haido:profile", "haido:session"],
    );
  });
});

describe("FR-13 định dạng mã kỹ năng", () => {
  it("nhận snake_case ASCII tối đa 40 ký tự", () => {
    for (const ok of ["python", "cpp", "ci_cd", "machine_learning", "s3"]) {
      expect(isSkillCode(ok)).toBe(true);
    }
    for (const bad of ["", "Python", "c++", "ci/cd", "_sql", "sql_", "a__b", "a,b", "x".repeat(41)]) {
      expect(isSkillCode(bad)).toBe(false);
    }
  });
});

describe("FR-14 hồ sơ trong trình duyệt", () => {
  it("chưa có gì thì trả hồ sơ rỗng", () => {
    expect(readProfile()).toEqual(EMPTY_PROFILE);
  });

  it("ghi rồi đọc lại đúng hồ sơ", () => {
    const profile = { v: 1 as const, role: "backend", level: "fresher", skills: ["python", "sql"] };
    writeProfile(profile);
    expect(JSON.parse(localStorage.getItem("haido:profile") ?? "null")).toEqual(profile);
    expect(readProfile()).toEqual(profile);
  });

  it("bỏ mã sai, mã trùng và cắt ở 200 mã", () => {
    const many = Array.from({ length: 250 }, (_, i) => `skill_${i}`);
    writeProfile({ v: 1, role: "backend", level: null, skills: ["sql", "C++", "sql", ...many] });
    const saved = readProfile();
    expect(saved.skills[0]).toBe("sql");
    expect(saved.skills).not.toContain("C++");
    expect(new Set(saved.skills).size).toBe(saved.skills.length);
    expect(saved.skills).toHaveLength(MAX_PROFILE_SKILLS);
  });

  it("JSON hỏng, sai phiên bản hay sai kiểu thì trả hồ sơ rỗng", () => {
    for (const raw of ["{", '{"v":2,"role":null,"level":null,"skills":[]}', '"x"', "[]", "null"]) {
      localStorage.setItem("haido:profile", raw);
      expect(readProfile()).toEqual(EMPTY_PROFILE);
    }
  });

  it("bỏ trường lạ và mã vai trò hay cấp bậc sai định dạng", () => {
    localStorage.setItem(
      "haido:profile",
      JSON.stringify({ v: 1, role: "Back End", level: "fresher", skills: ["sql"], name: "An" }),
    );
    expect(readProfile()).toEqual({ v: 1, role: null, level: "fresher", skills: ["sql"] });
  });
});

describe("FR-14 xóa hồ sơ", () => {
  it("xóa mọi khóa haido: kể cả khóa ngoài danh sách, giữ khóa của trang khác", () => {
    writeProfile({ v: 1, role: "backend", level: null, skills: ["sql"] });
    localStorage.setItem("haido:session", "abc");
    localStorage.setItem("haido:future", "1");
    localStorage.setItem("other-site", "keep");
    clearHaidoData();
    expect(Object.keys(localStorage)).toEqual(["other-site"]);
  });
});

describe("trình duyệt chặn bộ nhớ", () => {
  it("không ném lỗi ra ngoài module", () => {
    const boom = () => {
      throw new DOMException("blocked", "SecurityError");
    };
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(boom);
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(boom);
    vi.spyOn(Storage.prototype, "removeItem").mockImplementation(boom);
    expect(() => writeProfile({ v: 1, role: null, level: null, skills: ["sql"] })).not.toThrow();
    expect(readProfile()).toEqual(EMPTY_PROFILE);
    expect(() => clearHaidoData()).not.toThrow();
  });
});
