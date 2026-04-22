'use client';

import styles from './LoadingStates.module.css';

/* ─── Typing indicator (AI is responding) ─────────────────────────────────── */
export function TypingIndicator() {
  return (
    <div className={styles.typingRow}>
      <div className={styles.avatar}>✦</div>
      <div className={styles.typingContent}>
        <div className={styles.typingDots}>
          <span className="typing-dot" />
          <span className="typing-dot" />
          <span className="typing-dot" />
        </div>
      </div>
    </div>
  );
}

/* ─── Skeleton message placeholder ───────────────────────────────────────────*/
export function MessageSkeleton() {
  return (
    <div className={styles.skeletonWrap}>
      <div className={`skeleton ${styles.skeletonLine}`} style={{ width: '60%' }} />
      <div className={`skeleton ${styles.skeletonLine}`} style={{ width: '80%' }} />
      <div className={`skeleton ${styles.skeletonLine}`} style={{ width: '45%' }} />
    </div>
  );
}

/* ─── Sidebar thread skeleton ────────────────────────────────────────────────*/
export function ThreadSkeleton() {
  return (
    <div className={styles.threadSkeleton}>
      {[0.7, 0.85, 0.6].map((w, i) => (
        <div key={i} className={`skeleton ${styles.skeletonThread}`} style={{ width: `${w * 100}%` }} />
      ))}
    </div>
  );
}

/* ─── File list skeleton ─────────────────────────────────────────────────────*/
export function FileSkeleton() {
  return (
    <div className={styles.fileSkeleton}>
      {[1, 2, 3].map((i) => (
        <div key={i} className={styles.fileSkeletonRow}>
          <div className={`skeleton ${styles.skeletonIcon}`} />
          <div style={{ flex: 1 }}>
            <div className={`skeleton ${styles.skeletonLine}`} style={{ width: '70%', height: 12 }} />
            <div className={`skeleton ${styles.skeletonLine}`} style={{ width: '40%', height: 10, marginTop: 4 }} />
          </div>
        </div>
      ))}
    </div>
  );
}

/* ─── Inline spinner ─────────────────────────────────────────────────────────*/
export function Spinner({ size = 18 }: { size?: number }) {
  return (
    <span
      className={styles.spinner}
      style={{ width: size, height: size }}
      role="status"
      aria-label="Loading"
    />
  );
}

/* ─── Error banner ───────────────────────────────────────────────────────────*/
export function ErrorBanner({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className={styles.errorBanner} role="alert">
      <span className={styles.errorIcon}>⚠</span>
      <span>{message}</span>
      {onRetry && (
        <button className={styles.retryBtn} onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  );
}
