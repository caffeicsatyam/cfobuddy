'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
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
}

export default function Sidebar({
  currentThreadId,
  onSelectThread,
  userName = 'Authenticated User',
  userRole = 'JWT Session',
}: Props) {
  const pathname = usePathname();
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

  const navItems = [
    { name: 'Overview', icon: '◱', path: '/dashboard' },
    { name: 'AI Advisor', icon: '✧', path: '/dashboard' },
    { name: 'Cash Flow', icon: '⇄', path: '/dashboard' },
    { name: 'Investments', icon: '↗', path: '/dashboard' },
  ];

  return (
    <aside className={`${styles.sidebar} surface-low`}>
      {/* Brand */}
      <div className={styles.brand}>
        <Link href="/" className={styles.logo}>
          <span className={styles.logoIcon}>◈</span>
          <span className={styles.brandName}>CFOBuddy</span>
        </Link>
        <span className="label-upper">Precision Finance</span>
      </div>

      {/* Main Nav */}
      <div className={styles.section}>
        <h3 className="label-upper">Main Menu</h3>
        <nav className={styles.nav}>
          {navItems.map((item) => (
            <Link
              key={item.name}
              href={item.path}
              className={`${styles.navItem} ${pathname === item.path ? styles.active : ''}`}
            >
              <span className={styles.icon}>{item.icon}</span>
              {item.name}
            </Link>
          ))}
        </nav>
      </div>

      {/* Threads */}
      <div className={`${styles.section} ${styles.threadsSection}`}>
        <div className={styles.sectionHeader}>
          <h3 className="label-upper">Chat History</h3>
          <button 
            className={styles.newBtn} 
            onClick={() => onSelectThread(createId())}
            title="New Analysis"
          >
            +
          </button>
        </div>
        
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
                <span className={styles.threadIcon}>◷</span>
                <span className={styles.threadName}>{id === 'main' ? 'Main Analysis' : `Thread ${id.slice(0, 6)}`}</span>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Bottom Nav */}
      <div className={styles.bottomSection}>
        <nav className={styles.nav}>
          <button className={styles.navItem}>
             <span className={styles.icon}>?</span> Help
          </button>
          <button className={styles.navItem}>
             <span className={styles.icon}>⚙</span> Settings
          </button>
        </nav>
        
        <div className={styles.userProfile}>
          <div className={styles.avatar}>{userName.slice(0, 2).toUpperCase()}</div>
          <div className={styles.userInfo}>
            <p className={styles.userName}>{userName}</p>
            <p className={styles.userRole}>{userRole}</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
