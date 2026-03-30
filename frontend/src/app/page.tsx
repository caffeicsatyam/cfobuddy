import Navbar from '@/components/Navbar';
import Link from 'next/link';
import styles from './page.module.css';

export default function Home() {
  return (
    <>
      <Navbar />
      
      <main className={styles.main}>
        {/* Hero Section */}
        <section className={styles.hero}>
          <div className={styles.heroContent}>
            <div className={styles.badgeWrap}>
              <span className={styles.badge}>v1.0 is Live</span>
            </div>
            <h1 className={styles.headline}>
              Your Precision AI <span className="gradient-text">Financial Analyst.</span>
            </h1>
            <p className={styles.subhead}>
              A cutting-edge vector database for real-time insights and automated reporting. 
              Transform raw data into executive strategy instantly.
            </p>
            <div className={styles.heroActions}>
              <Link href="/dashboard" className="btn btn-primary">
                Explore Dashboard
              </Link>
              <Link href="#features" className="btn btn-ghost">
                View Features
              </Link>
            </div>
          </div>

          {/* Stat Cards Layered Pattern */}
          <div className={styles.heroStats}>
            <div className={`${styles.statCard} ${styles.stat1} glass`}>
              <span className="label-upper">Net Liquidity</span>
              <div className={styles.statValue}>$1.42M</div>
              <div className={styles.statTrend}>+12.4% MoM</div>
            </div>
            <div className={`${styles.statCard} ${styles.stat2} glass`}>
              <span className="label-upper">AI Forecast Accuracy</span>
              <div className={styles.statValue}>99.8%</div>
              <div className={styles.statTrend}>Q3 Validated</div>
            </div>
            <div className={`${styles.statCard} ${styles.stat3} glass`}>
              <span className="label-upper">Risk Index</span>
              <div className={styles.statValue} style={{ color: 'var(--secondary)' }}>Low</div>
              <div className={styles.statTrend}>Audited today</div>
            </div>
          </div>
        </section>

        {/* Features / Value Prop */}
        <section id="features" className={styles.section}>
          <div className={styles.sectionHead}>
            <h2 className={styles.sectionTitle}>Architected for Professional Growth.</h2>
            <p className={styles.sectionDesc}>
              Leave manual spreadsheets behind. Our AI infrastructure bridges the gap 
              between historical data and future predictions.
            </p>
          </div>

          <div className={styles.grid}>
            {[
              { title: 'AI-driven analysis', icon: '◈', desc: 'Our proprietary Large Language Model interprets complex P&L statements with contextual nuance, identifying hidden inefficiencies in seconds.' },
              { title: 'Automated chart generation', icon: '📊', desc: 'Instant visual storytelling. Convert raw CSV data into boardroom-ready pitch decks and reporting modules.' },
              { title: 'Multi-file support', icon: '📁', desc: 'PDF, XLSX, CSV, or direct SQL integrations. CFOBuddy handles cross-platform data mapping effortlessly.' },
              { title: 'Real-time Insights', icon: '⚡', desc: 'Connect your bank feeds for a live pulse on your runway, burn rate, and capital efficiency.' }
            ].map((feat, i) => (
              <div key={i} className={styles.featureCard}>
                <div className={styles.featureIcon}>{feat.icon}</div>
                <h3 className={styles.featureTitle}>{feat.title}</h3>
                <p className={styles.featureDesc}>{feat.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Pricing */}
        <section className={`${styles.section} surface-low`}>
          <div className={styles.sectionHead}>
            <h2 className={styles.sectionTitle}>Simple and transparent pricing.</h2>
            <p className={styles.sectionDesc}>No hidden tiers. Just elite financial intelligence for every scale.</p>
          </div>

          <div className={styles.pricingGrid}>
            
            <div className={styles.priceCard}>
              <h3 className={styles.priceName}>Professional</h3>
              <ul className={styles.priceFeatures}>
                <li>✔ 5 AI Analysis/mo</li>
                <li>✔ Basic Chart Generation</li>
                <li className={styles.disabledFeature}>✖ Multi-file Support</li>
              </ul>
            </div>

            <div className={`${styles.priceCard} ${styles.priceCardActive} gradient-bg-subtle`}>
              <div className={styles.popularBadge}>Most Popular</div>
              <h3 className={styles.priceName} style={{ color: 'var(--primary)' }}>Enterprise AI</h3>
              <ul className={styles.priceFeatures}>
                <li>✔ Unlimited AI Reasoning</li>
                <li>✔ Vector DB File Sync</li>
                <li>✔ Custom Strategy Export</li>
                <li>✔ 24/7 Financial Support</li>
              </ul>
              <button className="btn btn-primary" style={{ width: '100%', marginTop: '1.5rem' }}>
                Start Free Trial
              </button>
            </div>

            <div className={styles.priceCard}>
              <h3 className={styles.priceName}>Custom</h3>
              <p className={styles.featureDesc} style={{ margin: '1rem 0' }}>
                Tailored infrastructure for hedge funds, VCs, and multi-national corporations with high-throughput needs.
              </p>
              <button className="btn btn-ghost" style={{ width: '100%' }}>Contact Sales</button>
            </div>

          </div>
        </section>

        {/* CTA */}
        <section className={styles.ctaSection}>
          <div className={`${styles.ctaInner} glass`}>
            <h2>Ready to upgrade your financial stack?</h2>
            <p>Join over 500+ high-growth companies using CFOBuddy to automate their entire financial operations.</p>
            <Link href="/dashboard" className="btn btn-primary">
              Launch Dashboard →
            </Link>
          </div>
        </section>
      </main>

      <footer className={styles.footer}>
        <div className={styles.footerInner}>
          <div className={styles.footerBrand}>
            <span className={styles.logoIcon} style={{ marginRight: 8 }}>◈</span>
            <span style={{ fontWeight: 800 }}>CFOBuddy AI.</span>
            <span> Algorithmic Precision.</span>
          </div>
          <p className={styles.copyright}>© 2024 CFOBuddy. All rights reserved.</p>
          <div className={styles.footerLinks}>
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">Security</a>
            <a href="#">Contact</a>
          </div>
        </div>
      </footer>
    </>
  );
}
