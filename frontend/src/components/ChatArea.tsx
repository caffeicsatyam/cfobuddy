'use client';

import Image from 'next/image';
import { useEffect, useMemo, useRef, useState } from 'react';

import { getApiBaseUrl } from '../lib/api';
import type { Message } from '../lib/types';
import { TypingIndicator } from './LoadingStates';
import styles from './ChatArea.module.css';

interface Props {
  messages: Message[];
  isTyping: boolean;
}

interface ChartPreview {
  src: string;
  title: string;
}

function extractChartPath(message: Message): string | null {
  const chartCandidateKeys = ['url', 'file_url', 'chart_url', 'path'];

  if (message.chart && typeof message.chart === 'object') {
    for (const key of chartCandidateKeys) {
      const value = (message.chart as Record<string, unknown>)[key];
      if (typeof value === 'string' && value.length > 0) {
        return value;
      }
    }
  }

  const match = message.content.match(/\/charts\/[^\s`)"']+\.png/);
  return match ? match[0] : null;
}

function resolveChartPreview(message: Message): ChartPreview | null {
  const chartPath = extractChartPath(message);
  if (!chartPath) {
    return null;
  }

  const title =
    (message.chart &&
      typeof message.chart === 'object' &&
      typeof (message.chart as Record<string, unknown>).title === 'string' &&
      ((message.chart as Record<string, string>).title || '').trim()) ||
    'Generated chart';

  const normalizedPath = chartPath.startsWith('http')
    ? chartPath
    : `${getApiBaseUrl()}${chartPath.startsWith('/') ? '' : '/'}${chartPath}`;

  return {
    src: normalizedPath,
    title,
  };
}

export default function ChatArea({ messages, isTyping }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [activeChart, setActiveChart] = useState<ChartPreview | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const previews = useMemo(
    () =>
      new Map(
        messages.map((message) => [message.id, resolveChartPreview(message)])
      ),
    [messages]
  );

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
          {messages.map((msg) => {
            const chartPreview = previews.get(msg.id) ?? null;

            return (
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
                  <div className={styles.content}>
                    {msg.content.split('\n').map((line, i) => (
                      <span key={i}>
                        {line}
                        <br />
                      </span>
                    ))}
                    {msg.isLoading && msg.role === 'assistant' && (
                      <span className="streaming-cursor"></span>
                    )}
                  </div>

                  {chartPreview && (
                    <button
                      type="button"
                      className={styles.chartCard}
                      onClick={() => setActiveChart(chartPreview)}
                    >
                      <div className={styles.chartCardHeader}>
                        <div className={styles.chartIcon}>📊</div>
                        <span className={styles.chartLabel}>{chartPreview.title}</span>
                      </div>
                      <Image
                        src={chartPreview.src}
                        alt={chartPreview.title}
                        className={styles.chartImage}
                        width={960}
                        height={540}
                        unoptimized
                      />
                      <span className={styles.chartHint}>Tap to expand</span>
                    </button>
                  )}
                </div>

                {msg.role === 'user' && (
                  <div className={styles.avatarUser}>AS</div>
                )}
              </div>
            );
          })}

          {isTyping && (
            <div className={`${styles.messageWrap} ${styles.wrapAi}`}>
              <TypingIndicator />
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      )}

      {activeChart && (
        <button
          type="button"
          className={styles.chartModal}
          onClick={() => setActiveChart(null)}
        >
          <div
            className={styles.chartModalContent}
            onClick={(event) => event.stopPropagation()}
          >
            <div className={styles.chartModalHeader}>
              <h3>{activeChart.title}</h3>
              <button
                type="button"
                className={styles.chartClose}
                onClick={() => setActiveChart(null)}
              >
                ×
              </button>
            </div>
            <Image
              src={activeChart.src}
              alt={activeChart.title}
              className={styles.chartModalImage}
              width={1400}
              height={900}
              unoptimized
            />
          </div>
        </button>
      )}
    </div>
  );
}
