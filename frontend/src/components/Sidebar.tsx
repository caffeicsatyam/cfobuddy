'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getThreads } from '../lib/api';
import { createId } from '../lib/id';
import { ThreadSkeleton } from './LoadingStates';
import styles from './Sidebar.module.css';

interface Props {
  currentThreadId: string;
  onSelectThread: (id: string) => void;
  userName?: string;
  userRole?: string;
  isOpen?: boolean;
  onToggle?: () => void;
  onLogout?: () => void;
}

export default function Sidebar({
  currentThreadId,
  onSelectThread,
  userName = 'Authenticated User',
  userRole = 'JWT Session',
  isOpen = true,
  onToggle,
  onLogout,
}: Props) {
  const [threads, setThreads] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadThreads() {
      try {
        const res = await getThreads();
        setThreads(res.threads);
      } catch (err) {
        console.error('Failed to load threads', err);
        // Fallback or error state
        setThreads(['main']);
      } finally {
        setIsLoading(false);
      }
    }
    loadThreads();
  }, []);

  return (
    <aside className={`${styles.sidebar} ${isOpen ? styles.sidebarOpen : styles.sidebarClosed}`}>
      {/* Top bar: toggle + new chat */}
      <div className={styles.topBar}>
        <button className={styles.toggleBtn} onClick={onToggle} aria-label="Close sidebar">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <path d="M9 3v18" />
          </svg>
        </button>
        <button
          className={styles.newChatBtn}
          onClick={() => onSelectThread(createId())}
          title="New chat"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 5v14M5 12h14" />
          </svg>
        </button>
      </div>

      {/* Threads list */}
      <div className={styles.threadsList}>
        {isLoading ? (
          <ThreadSkeleton />
        ) : (
          threads.map((id) => (
            <button
              key={id}
              onClick={() => onSelectThread(id)}
              className={`${styles.threadItem} ${id === currentThreadId ? styles.threadActive : ''}`}
            >
              <svg className={styles.threadIcon} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
              </svg>
              <span className={styles.threadName}>
                {id === 'main' ? 'Main Analysis' : `Thread ${id.slice(0, 8)}`}
              </span>
            </button>
          ))
        )}
      </div>

      {/* Bottom section – user + logout */}
      <div className={styles.bottomSection}>
        <Link href="/" className={styles.navItem}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
          </svg>
          <span>Home</span>
        </Link>

        <div className={styles.userProfile}>
          <div className={styles.avatar}>{userName.slice(0, 2).toUpperCase()}</div>
          <div className={styles.userInfo}>
            <p className={styles.userName}>{userName}</p>
            <p className={styles.userRole}>{userRole}</p>
          </div>
          {onLogout && (
            <button className={styles.logoutBtn} onClick={onLogout} title="Sign out">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </aside>
  );
}
