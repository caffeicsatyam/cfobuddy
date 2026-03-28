'use client';

import { useEffect, useRef } from 'react';
import type { Message } from '../lib/types';
import { TypingIndicator } from './LoadingStates';
import styles from './ChatArea.module.css';

interface Props {
  messages: Message[];
  isTyping: boolean;
}

export default function ChatArea({ messages, isTyping }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change or typing status changes
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  return (
    <div className={styles.chatContainer}>
      {messages.length === 0 ? (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>◈</div>
          <h2>How can CFOBuddy assist your financial strategy today?</h2>
          <p>I&apos;m ready to analyze ledgers, forecast trends, or audit risk.</p>
        </div>
      ) : (
        <div className={styles.messageList}>
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`${styles.messageWrap} ${
                msg.role === 'user' ? styles.wrapUser : styles.wrapAi
              }`}
            >
              {msg.role === 'assistant' && (
                <div className={styles.avatarAi}>◈</div>
              )}
              
              <div 
                className={`${styles.bubble} ${
                  msg.role === 'user' ? styles.bubbleUser : styles.bubbleAi
                }`}
              >
                {/* 
                  Note: In a real app we'd use react-markdown here. 
                  For now we just render text preserving newlines.
                */}
                <div className={styles.content}>
                  {msg.content.split('\n').map((line, i) => (
                    <span key={i}>
                      {line}
                      <br />
                    </span>
                  ))}
                  {/* Streaming cursor if this is the latest AI message and it's loading */}
                  {msg.isLoading && msg.role === 'assistant' && (
                    <span className="streaming-cursor"></span>
                  )}
                </div>

                {/* If there's chart data, we'd render it here using Plotly.js */}
                {msg.chart && (
                  <div className={styles.chartPlaceholder}>
                    <div className={styles.chartIcon}>📊</div>
                    <span>Interactive Chart Generated</span>
                  </div>
                )}
              </div>
              
              {msg.role === 'user' && (
                <div className={styles.avatarUser}>AS</div>
              )}
            </div>
          ))}
          
          {isTyping && (
            <div className={`${styles.messageWrap} ${styles.wrapAi}`}>
              <TypingIndicator />
            </div>
          )}
          
          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
}
