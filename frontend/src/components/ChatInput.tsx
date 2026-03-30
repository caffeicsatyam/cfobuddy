'use client';

import { useRef, useEffect, KeyboardEvent } from 'react';
import { Spinner } from './LoadingStates';
import styles from './ChatInput.module.css';

interface Props {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  disabled?: boolean;
  loading?: boolean;
  placeholder?: string;
}

export default function ChatInput({
  value,
  onChange,
  onSend,
  disabled = false,
  loading = false,
  placeholder = 'Ask CFOBuddy anything about your financials…',
}: Props) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  }, [value]);

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!disabled && !loading && value.trim()) onSend();
    }
  };

  return (
    <div className={styles.wrap}>
      <div className={styles.inputRow}>
        <textarea
          ref={textareaRef}
          id="chat-input"
          className={`input-field ${styles.textarea}`}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKey}
          placeholder={placeholder}
          disabled={disabled || loading}
          rows={1}
          aria-label="Chat message"
        />
        <button
          id="chat-send-btn"
          className={styles.sendBtn}
          onClick={onSend}
          disabled={disabled || loading || !value.trim()}
          aria-label="Send message"
        >
          {loading ? <Spinner size={16} /> : <span className={styles.sendIcon}>↑</span>}
        </button>
      </div>
      <p className={styles.hint}>
        Press <kbd>Enter</kbd> to send, <kbd>Shift+Enter</kbd> for new line
      </p>
    </div>
  );
}
