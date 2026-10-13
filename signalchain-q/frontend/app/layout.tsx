import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';

export const metadata: Metadata = {
  title: 'SignalChain-Q | ECG-First Classical + Quantum DSP Platform',
  description: 'Rigorous benchmark platform comparing classical ECG DSP with QFT + adaptive oracle + Grover quantum denoising.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="disclaimer-banner" id="research-disclaimer">
          ⚠️ <strong>RESEARCH USE ONLY:</strong> SignalChain-Q is an algorithmic benchmarking instrument, not a medical diagnosis device. Quantum advantage claims are subject to physical resource accounting.
        </div>
        <header className="header">
          <div className="container nav-inner">
            <Link href="/" className="logo-group">
              <span>SignalChain<span style={{ color: 'var(--accent-cyan)' }}>-Q</span></span>
              <span className="logo-badge">ECG v1.0</span>
            </Link>
            <nav className="nav-links">
              <Link href="/" className="nav-link" id="nav-home">Overview</Link>
              <Link href="/ecg" className="nav-link" id="nav-ecg">ECG Studio</Link>
              <Link href="/benchmark" className="nav-link" id="nav-benchmark">Benchmark</Link>
              <Link href="/research" className="nav-link" id="nav-research">Research & Theory</Link>
            </nav>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span className="status-pill status-online">
                <span className="status-dot"></span>
                API Connected
              </span>
            </div>
          </div>
        </header>

        <main style={{ minHeight: 'calc(100vh - 12rem)', padding: '2rem 0' }}>
          {children}
        </main>

        <footer style={{ borderTop: '1px solid var(--border-subtle)', padding: '2.5rem 0', background: 'rgba(5, 8, 17, 0.95)' }}>
          <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>SignalChain-Q Research Consortium</div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Deterministic Classical vs. Quantum Digital Signal Processing for ECG. Random Seed: 1448.</div>
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Built with Next.js, FastAPI & Qiskit • Physics-grounded resource tracking
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
