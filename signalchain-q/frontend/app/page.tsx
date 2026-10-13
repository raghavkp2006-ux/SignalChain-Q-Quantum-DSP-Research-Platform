import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="container">
      {/* Hero Section */}
      <section style={{ textAlign: 'center', padding: '3.5rem 0 2.5rem' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(56, 189, 248, 0.1)', border: '1px solid rgba(56, 189, 248, 0.25)', padding: '0.35rem 1rem', borderRadius: '9999px', color: 'var(--accent-cyan)', fontSize: '0.85rem', fontWeight: 600, marginBottom: '1.5rem' }}>
          <span>⚛️</span> Quantum Fourier Transform + Adaptive ECG Bandpass Oracle
        </div>
        <h1 style={{ fontSize: '3rem', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.15, marginBottom: '1.25rem' }}>
          Classical & Quantum DSP <br />
          <span style={{ background: 'linear-gradient(135deg, #38bdf8, #a855f7)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            ECG Research Platform
          </span>
        </h1>
        <p style={{ maxWidth: '780px', margin: '0 auto 2rem', color: 'var(--text-secondary)', fontSize: '1.15rem' }}>
          A reproducible, physics-grounded platform comparing classical digital signal processing against quantum frequency-domain filtering under identical noise conditions, with explicit state-preparation and gate accounting.
        </p>

        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link href="/ecg" className="btn-primary" id="btn-hero-launch">
            Launch ECG Studio &rarr;
          </Link>
          <Link href="/benchmark" className="btn-secondary" id="btn-hero-benchmark">
            Explore 5-Method Benchmark
          </Link>
          <Link href="/research" className="btn-secondary" id="btn-hero-research">
            Research Protocol & Theory
          </Link>
        </div>
      </section>

      {/* Primary Research Question Card */}
      <section style={{ margin: '2rem 0' }}>
        <div className="glass-card" style={{ borderLeft: '4px solid var(--accent-cyan)' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-cyan)', marginBottom: '0.75rem' }}>
            Primary Scientific Hypothesis
          </h2>
          <blockquote style={{ fontSize: '1.05rem', fontStyle: 'italic', color: 'var(--text-primary)', lineHeight: 1.6 }}>
            "Can an ECG-aware quantum frequency-domain denoiser based on QFT + an adaptive band-pass oracle + amplitude amplification + IQFT preserve ECG morphology while suppressing both baseline wander and high-frequency noise, and how does it compare with classical DSP once state preparation, circuit depth, gate count, and reconstruction costs are included?"
          </blockquote>
        </div>
      </section>

      {/* Grid: 3 Pillars */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', margin: '3rem 0' }}>
        <div className="glass-card">
          <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>📊</div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.5rem' }}>Classical DSP Baselines</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '1rem' }}>
            Zero-phase Butterworth SOS filtering (0.5–40 Hz), Daubechies-6 wavelet shrinkage with MAD noise estimation, and a faithful adaptive FFT counterpart.
          </p>
          <ul style={{ color: 'var(--text-muted)', fontSize: '0.85rem', listStyle: 'none' }}>
            <li>✓ Butterworth SOS (C1)</li>
            <li>✓ Wavelet db6 (C2)</li>
            <li>✓ Adaptive FFT Masking (C3)</li>
          </ul>
        </div>

        <div className="glass-card">
          <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>⚛️</div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.5rem' }}>Quantum DSP Pipeline</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '1rem' }}>
            Amplitude state preparation, 8-qubit QFT (M=256), activity-guided adaptive bandpass phase oracle, Grover amplitude amplification, and inverse QFT.
          </p>
          <ul style={{ color: 'var(--text-muted)', fontSize: '0.85rem', listStyle: 'none' }}>
            <li>✓ Aer Ideal Statevector Simulation</li>
            <li>✓ Symmetric Bandpass Phase Oracles</li>
            <li>✓ Grover Diffusion (r &le; 3)</li>
          </ul>
        </div>

        <div className="glass-card">
          <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>⚖️</div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.5rem' }}>Fair Resource Accounting</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '1rem' }}>
            No hidden costs. State preparation depth and time are recorded separately from QFT runtime, gate counts, CNOT/CX overhead, and transpiled circuit metrics.
          </p>
          <ul style={{ color: 'var(--text-muted)', fontSize: '0.85rem', listStyle: 'none' }}>
            <li>✓ Total & Algorithmic Circuit Depth</li>
            <li>✓ CX Gate Overhead Count</li>
            <li>✓ SNR, PRD, RMSE, & R-Peak F1</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
