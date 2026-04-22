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
  placeholder = 'Message CFOBuddy…',
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
      <div className={styles.inputContainer}>
        <textarea
          ref={textareaRef}
          id="chat-input"
          className={styles.textarea}
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
          {loading ? (
            <Spinner size={16} />
          ) : (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94l18.04-8.01a.75.75 0 000-1.36L3.478 2.405z" />
            </svg>
          )}
        </button>
      </div>
      <p className={styles.hint}>
        CFOBuddy can make mistakes. Verify important financial data.
      </p>
    </div>
  );
}
