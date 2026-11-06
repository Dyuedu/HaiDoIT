"use client";

import { useEffect, useReducer, useRef } from "react";

import type { ShareLine } from "@/lib/city-shares-view";

import styles from "./share-line.module.css";

/**
 * Vì sao phần trăm của dòng mẫu nhỏ đang hiện. Mỗi nguồn một cờ riêng, để mất một nguồn (rời
 * chuột, rời focus) không giấu phần trăm khi nguồn kia vẫn còn.
 */
interface Reveal {
  /** Con trỏ không phải cảm ứng (chuột, bút) đang ở trên dòng. */
  hovered: boolean;
  /** Dòng đang có focus bằng bàn phím. */
  focused: boolean;
  /** Đã ghim bằng bấm, chạm, Enter hoặc Space. */
  pinned: boolean;
  /** Đã giấu bằng Esc hoặc bấm lần nữa; hết hiệu lực khi con trỏ rời đi hoặc focus đổi chỗ. */
  dismissed: boolean;
}

type RevealEvent = "enter" | "leave" | "keyboard-focus" | "pointer-focus" | "blur" | "press" | "escape";

const HIDDEN: Reveal = { hovered: false, focused: false, pinned: false, dismissed: false };

function nextReveal(state: Reveal, event: RevealEvent): Reveal {
  switch (event) {
    case "enter":
      return { ...state, hovered: true };
    case "leave":
      return { ...state, hovered: false, dismissed: false };
    case "keyboard-focus":
      return { ...state, focused: true, dismissed: false };
    case "pointer-focus":
      return { ...state, dismissed: false };
    case "blur":
      return { ...HIDDEN, hovered: state.hovered };
    case "press":
      // Đang ghim thì bấm là giấu; còn lại bấm là ghim (đang hiện thì vẫn hiện).
      return state.pinned
        ? { ...state, pinned: false, dismissed: true }
        : { ...state, pinned: true, dismissed: false };
    case "escape":
      return { ...state, pinned: false, dismissed: true };
  }
}

function isRevealed(state: Reveal): boolean {
  return state.pinned || (!state.dismissed && (state.hovered || state.focused));
}

interface ShareLineButtonProps {
  line: ShareLine;
  /** Có rãnh và thanh (ba thành phố) hay chỉ là dòng chú thích. */
  withTrack?: boolean;
}

/**
 * Một dòng tỷ trọng là một `<button>`: focus được, cao tối thiểu 44px, tên đọc được luôn gồm
 * tên nơi, phần trăm, `n` và câu mẫu nhỏ. Dòng mẫu nhỏ luôn hiện nhãn; phần trăm chỉ hiện khi
 * trỏ chuột, chạm hoặc focus, và nằm trong chính button nên trỏ lên nó không làm nó biến mất.
 */
export function ShareLineButton({ line, withTrack = false }: ShareLineButtonProps) {
  const [reveal, dispatch] = useReducer(nextReveal, HIDDEN);
  const buttonRef = useRef<HTMLButtonElement>(null);
  // Focus đến từ chuột hoặc chạm thì để lần bấm quyết, không coi là focus bàn phím.
  const focusFromPointer = useRef(false);
  const showPercent = !line.lowSample || isRevealed(reveal);

  // `pointerenter`/`pointerleave` gốc của trình duyệt không bắn khi chuột đi vào phần tử con
  // (chính phần trăm). Bản giả lập của React dựa vào `relatedTarget` của `pointerout`, mà
  // `relatedTarget` không phải lúc nào cũng có, nên trỏ lên phần trăm có thể làm nó biến mất.
  useEffect(() => {
    const button = buttonRef.current;
    if (!button) return;
    const onEnter = (event: PointerEvent) => {
      if (event.pointerType !== "touch") dispatch("enter");
    };
    const onLeave = (event: PointerEvent) => {
      if (event.pointerType !== "touch") dispatch("leave");
    };
    button.addEventListener("pointerenter", onEnter);
    button.addEventListener("pointerleave", onLeave);
    return () => {
      button.removeEventListener("pointerenter", onEnter);
      button.removeEventListener("pointerleave", onLeave);
    };
  }, []);

  return (
    <button
      ref={buttonRef}
      type="button"
      aria-label={line.accessibleName}
      data-low-sample={line.lowSample}
      className={`${styles.line} ${withTrack ? styles.bar : styles.legend}`}
      onPointerDown={() => {
        focusFromPointer.current = true;
      }}
      onPointerUp={() => {
        focusFromPointer.current = false;
      }}
      onPointerCancel={() => {
        focusFromPointer.current = false;
      }}
      onFocus={() => {
        dispatch(focusFromPointer.current ? "pointer-focus" : "keyboard-focus");
        focusFromPointer.current = false;
      }}
      onBlur={() => dispatch("blur")}
      onClick={() => dispatch("press")}
      onKeyDown={(event) => {
        if (event.key === "Escape") dispatch("escape");
      }}
    >
      <span className={styles.label}>{line.label}</span>
      {withTrack && (
        <span data-part="track" className={styles.track} aria-hidden="true">
          <span
            data-part="fill"
            data-low-sample={line.lowSample}
            className={styles.fill}
            style={{ width: `${line.value * 100}%` }}
          />
        </span>
      )}
      <span className={styles.value}>
        {line.lowSampleNote && <span className={styles.note}>{line.lowSampleNote}</span>}
        {showPercent && (
          <span className={styles.reading}>
            <span className={styles.percent}>{line.percent}</span>
            <span className={styles.count}> · {line.nText} tin</span>
          </span>
        )}
      </span>
    </button>
  );
}
