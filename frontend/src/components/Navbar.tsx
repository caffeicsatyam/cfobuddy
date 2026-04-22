'use client';

import Link from 'next/link';
import { useState } from 'react';
import styles from './Navbar.module.css';

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className={styles.nav}>
      <div className={styles.inner}>
        {/* Logo */}
        <Link href="/" className={styles.logo}>
          <span className={styles.logoIcon}>✦</span>
          <span>CFOBuddy</span>
        </Link>

        {/* Desktop links */}
        <ul className={styles.links}>
          {['Dashboard', 'Features', 'Pricing'].map((item) => (
            <li key={item}>
              <Link
                href={item === 'Dashboard' ? '/dashboard' : `#${item.toLowerCase()}`}
                className={styles.link}
              >
                {item}
              </Link>
            </li>
          ))}
        </ul>

        {/* CTA */}
        <div className={styles.actions}>
          <Link href="/dashboard" className="btn btn-primary btn-sm">
            Try CFOBuddy →
          </Link>
          <button
            className={styles.burger}
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle menu"
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className={styles.mobile}>
          {['Dashboard', 'Features', 'Pricing'].map((item) => (
            <Link
              key={item}
              href={item === 'Dashboard' ? '/dashboard' : `#${item.toLowerCase()}`}
              className={styles.mobileLink}
              onClick={() => setMenuOpen(false)}
            >
              {item}
            </Link>
          ))}
          <Link href="/dashboard" className="btn btn-primary btn-sm" onClick={() => setMenuOpen(false)}>
            Try CFOBuddy →
          </Link>
        </div>
      )}
    </nav>
  );
}
