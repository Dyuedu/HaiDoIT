# Research: Cache response cho FastAPI

## Repo tham khảo

### 1. long2ice/fastapi-cache — decorator `@cache`

- **Link**: https://github.com/long2ice/fastapi-cache/blob/b2143ef85e2868dace363e432a0683675577bf81/fastapi_cache/decorator.py
- **Cách làm**: Decorator bọc từng endpoint. Khóa do `key_builder` dựng từ hàm và mọi tham số. Lưu giá trị trả về đã encode, hết hạn theo `expire` (TTL). Lúc trúng thì decode lại về kiểu trả về của hàm, thêm `Cache-Control: max-age` và `ETag`, trả 304 khi `If-None-Match` khớp. Bỏ qua khi không phải GET hoặc có `Cache-Control: no-store`.
- **Lấy gì**: Chỉ cache GET. Header báo trạng thái cache. Ý tưởng ETag/304 để dành cho bước CDN.
- **Không lấy**:
  - Xóa theo TTL: snapshot đổi thì số cũ vẫn phục vụ tới hết hạn, trái AC "snapshot đọc được mới nhất".
  - Decode lại về model rồi để FastAPI serialize lần nữa: request trúng vẫn tốn Pydantic, đúng phần CPU mà #342 cho thấy là nút thắt.
  - Khóa gồm mọi tham số, tức sẽ lưu cả `title` và `have`.
  - Thêm một dependency.

### 2. Krukov/cashews — thư viện cache nhiều backend

- **Link**: https://github.com/Krukov/cashews/tree/31604207ee5cfac036395ec5de9d5c60bb0307fb (`cashews/contrib/fastapi.py`)
- **Cách làm**: Decorator và middleware cho FastAPI. Có xóa theo tag, khóa chống stampede (`locked`, `early`), backend RAM và Redis.
- **Lấy gì (để sau)**: Single-flight/lock khi nhiều request cùng MISS một khóa. Bước này chưa cần vì version chỉ đổi mỗi đêm một lần.
- **Không lấy**: Cả thư viện cho một middleware vài chục dòng. Xóa theo version của snapshot đơn giản hơn xóa theo tag.

### 3. florimondmanca/asgi-caches — middleware ASGI (đã archive)

- **Link**: https://github.com/florimondmanca/asgi-caches/blob/dd4257956338363d420ba6d746b39fc10a101fb1/src/asgi_caches/middleware.py
- **Cách làm**: `CacheMiddleware` là middleware ASGI thuần. Bọc `send` để bắt `http.response.start` và `http.response.body`, gom body rồi lưu cả response. Lần sau trả thẳng từ cache.
- **Lấy gì**: Kiểu middleware ASGI thuần bọc `send`, lưu (status, headers, body) và gửi lại nguyên bytes. Request trúng không chạm route, không chạm Pydantic. Không dùng `BaseHTTPMiddleware` vì nó thêm chi phí mỗi request.
- **Không lấy**: Repo đã archive từ 2019. Cách xóa theo `Cache-Control` max-age kiểu Django.

## Kết luận

Viết `haido_api/response_cache.py`: middleware ASGI thuần theo mẫu asgi-caches, xóa theo `version()` của nguồn thay vì TTL, bỏ qua `title`/`have`. Chống stampede (cashews) và ETag/304 (fastapi-cache) để cho các bước sau.
