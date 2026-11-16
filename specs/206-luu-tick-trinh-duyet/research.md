# Research: Lưu tick trong trình duyệt

## Quyết định

- Đọc hồ sơ bằng `useSyncExternalStore` với snapshot server là hồ sơ rỗng: trang render ở server không có `localStorage`, đọc thẳng lúc render làm lệch HTML (hydration mismatch). Bản đầu đọc trong `useEffect` rồi `setState`; lint của repo chặn cách đó.
- Ghi đồng bộ ngay sau mỗi thay đổi, qua `writeProfile` của #205.

## Cách các repo công khai làm

- [astoilkov/use-local-storage-state @ 799291a, `src/useLocalStorageState.ts`](https://github.com/astoilkov/use-local-storage-state/blob/799291ab6152fbdca80823bf6b12e87257d98638/src/useLocalStorageState.ts): hook trả giá trị mặc định lúc render ở server và chỉ đọc `localStorage` ở trình duyệt, để tránh lệch HTML; mọi truy cập bọc try/catch. #205 đã lấy phần try/catch; #206 lấy phần "server dùng giá trị mặc định, trình duyệt mới đọc bộ nhớ", qua `useSyncExternalStore`.
- [pmndrs/zustand @ 9fed2eb, `src/middleware/persist.ts`](https://github.com/pmndrs/zustand/blob/9fed2eb2f3af672da9f7bf694b996df3831fc207/src/middleware/persist.ts): ghi lại toàn bộ state vào một khóa mỗi khi state đổi. Hải Đồ ghi cả hồ sơ vào một khóa `haido:profile` theo cùng cách, không ghi từng trường.

## Không lấy

- Không thêm hook dùng chung hay thư viện: một màn dùng hồ sơ, và cổng AD-23 chỉ cho `haido-keys.ts` gọi `localStorage`.
- Không đồng bộ giữa các tab (sự kiện `storage`): ngoài AC.
