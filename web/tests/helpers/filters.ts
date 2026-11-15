import { screen } from "@testing-library/react";
import type userEvent from "@testing-library/user-event";

type User = ReturnType<typeof userEvent.setup>;

export function roleSelect(): HTMLSelectElement {
  return screen.getByRole("combobox", { name: "Vai trò" }) as HTMLSelectElement;
}

export function levelSelect(): HTMLSelectElement {
  return screen.getByRole("combobox", { name: "Cấp bậc" }) as HTMLSelectElement;
}

export function yearsSelect(): HTMLSelectElement {
  return screen.getByRole("combobox", { name: "Số năm kinh nghiệm" }) as HTMLSelectElement;
}

/** Nhãn của option đang chọn. */
export function selectedLabel(select: HTMLSelectElement): string {
  return select.selectedOptions[0]?.textContent ?? "";
}

/** Chọn một option theo nhãn bằng `userEvent.selectOptions`, như người dùng chọn trong dropdown. */
export async function pick(user: User, select: HTMLSelectElement, label: string): Promise<void> {
  await user.selectOptions(select, label);
}

/** Nhãn của mọi option, theo thứ tự trong DOM. */
export function optionLabels(select: HTMLSelectElement): string[] {
  return Array.from(select.options).map((option) => option.textContent ?? "");
}
