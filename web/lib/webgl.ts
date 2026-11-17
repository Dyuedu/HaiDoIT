/**
 * Dò WebGL cho `useSyncExternalStore` (#314, FR-36). Server render và lần hydrate đầu thấy "không có", nên HTML tĩnh là
 * lối 2D; trình duyệt có WebGL chuyển sang 3D sau khi hydrate. Dò một lần rồi giữ kết quả: mỗi lần dò tạo một context
 * WebGL, và trình duyệt chỉ cho giữ vài chục context.
 */

let cached: boolean | null = null;

function detect(): boolean {
  // Trình duyệt không có WebGL (và jsdom) không có hàm dựng này: khỏi tạo canvas.
  if (typeof window === "undefined" || typeof window.WebGLRenderingContext === "undefined") return false;
  try {
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("webgl2") ?? canvas.getContext("webgl");
    if (!context) return false;
    // Trả context ngay để không chiếm chỗ của canvas thật.
    (context as WebGLRenderingContext).getExtension("WEBGL_lose_context")?.loseContext();
    return true;
  } catch {
    return false;
  }
}

export function subscribeWebGL(): () => void {
  return () => {};
}

export function getWebGLSnapshot(): boolean {
  cached ??= detect();
  return cached;
}

export function getServerWebGLSnapshot(): boolean {
  return false;
}
