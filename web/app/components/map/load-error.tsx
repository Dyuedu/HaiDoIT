import { formatDate } from "@/lib/city-shares-view";

interface LoadErrorProps {
  message: string;
  /** Ngày snapshot của lỗi (`unknown_cell`); `null` thì không ghi. */
  snapshotDate?: string | null;
  /** Có thì hiện nút "Thử lại". */
  onRetry?: () => void;
}

/** Thông báo lỗi theo bảng lỗi của #46. Không có thanh, bảng hay chú thích kèm theo. */
export function LoadError({ message, snapshotDate = null, onRetry }: LoadErrorProps) {
  return (
    <div className="flex flex-col items-start gap-3 rounded-xl border border-amber-deep bg-notice p-panel">
      <div role="alert" className="flex flex-col gap-1">
        <p className="m-0 text-body-md text-text">{message}</p>
        {snapshotDate && (
          <p className="m-0 text-caption text-text-muted">
            Ngày snapshot: <span className="font-mono text-footer">{formatDate(snapshotDate)}</span>
          </p>
        )}
      </div>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="min-h-target rounded-md border border-border-chip px-4 text-ui text-text-secondary transition-colors hover:border-selected hover:text-text"
        >
          Thử lại
        </button>
      )}
    </div>
  );
}
