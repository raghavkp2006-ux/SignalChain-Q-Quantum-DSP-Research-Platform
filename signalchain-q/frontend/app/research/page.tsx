import React from 'react';

export default function ResearchPage() {
  return (
    <div className="container" style={{ maxWidth: '960px' }}>
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2.4rem', fontWeight: 800, marginBottom: '0.5rem' }}>Research Protocol & Algorithm Theory</h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Detailed mathematical formulation, prior art comparison, dataset citations, and quantum circuit resource equations.
        </p>
      </div>

      {/* Novelty & Literature Gate (Section 31) */}
      <section className="glass-card" style={{ marginBottom: '2rem', borderLeft: '4px solid var(--accent-purple)' }}>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-purple)', marginBottom: '0.75rem' }}>
          Publication Novelty Positioning (Section 31)
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '1rem' }}>
          SignalChain-Q does <strong>NOT</strong> claim to be the "first QFT ECG denoiser". Instead, this platform addresses the critical research gaps left by prior literature through reproducible benchmark protocols:
        </p>
        <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: '1rem', borderRadius: '8px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          <div style={{ marginBottom: '0.5rem' }}>
            <strong>1. Dutta et al. (IEEE SPL, 2024):</strong> Formulated general QFT signal denoising with amplitude amplification, but evaluated synthetic 1D toy signals without physiological bandpass or QRS morphology preservation.
          </div>
          <div style={{ marginBottom: '0.5rem' }}>
            <strong>2. Laskar et al. (Scientific Reports, 2024):</strong> Penta-diagonal quantum smoothing filter for ECG, but operated strictly in the time domain rather than adaptive Fourier spectrum bandpass.
          </div>
          <div>
            <strong>3. SignalChain-Q Contribution:</strong> An ECG-aware quantum bandpass oracle with adaptive QRS activity cutoff (25–45 Hz), combined with end-to-end state preparation accounting and fair classical-equivalent comparison.
          </div>
        </div>
      </section>

      {/* Pipeline Flow (Section 11) */}
      <section className="glass-card" style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-cyan)', marginBottom: '1rem' }}>
          Quantum Processing Pipeline Flow (Section 11)
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.75rem', borderRadius: '6px' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>STAGE 1</div>
            <div style={{ fontWeight: 600 }}>Hann Windowing</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>M = 256, 50% overlap</div>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.75rem', borderRadius: '6px' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>STAGE 2</div>
            <div style={{ fontWeight: 600 }}>State Prep (|&psi;&gt;)</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>scale = ||v||₂, 8 Qubits</div>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.75rem', borderRadius: '6px' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>STAGE 3</div>
            <div style={{ fontWeight: 600 }}>QFT Gate</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Frequency domain</div>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.75rem', borderRadius: '6px' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>STAGE 4</div>
            <div style={{ fontWeight: 600 }}>Adaptive Oracle</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Phase flip on marked</div>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.75rem', borderRadius: '6px' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>STAGE 5</div>
            <div style={{ fontWeight: 600 }}>Grover Diffusion</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>r = clip(r_est, 0, 3)</div>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.75rem', borderRadius: '6px' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>STAGE 6</div>
            <div style={{ fontWeight: 600 }}>IQFT & WOLA</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Statevector reconstruction</div>
          </div>
        </div>
      </section>

      {/* Dataset Citations (Section 44) */}
      <section className="glass-card" style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1rem' }}>PhysioNet Dataset References (Section 44)</h2>
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
          <li style={{ borderLeft: '2px solid var(--accent-cyan)', paddingLeft: '0.75rem' }}>
            <strong>MIT-BIH Noise Stress Test Database (NSTDB v1.0.0):</strong> Moody et al., primary paired clean/noisy benchmark (records 118 & 119 with calibrated bw, ma, em noise).
          </li>
          <li style={{ borderLeft: '2px solid var(--accent-blue)', paddingLeft: '0.75rem' }}>
            <strong>MIT-BIH Arrhythmia Database (mitdb v1.0.0):</strong> Mark & Moody, 48 dual-channel recordings at 360 Hz. Split into 33 dev, 8 val, and 7 test records (seed 1448).
          </li>
          <li style={{ borderLeft: '2px solid var(--accent-purple)', paddingLeft: '0.75rem' }}>
            <strong>QT Database (qtdb v1.0.0):</strong> Laguna et al., external morphology and wave onset/offset preservation validation.
          </li>
        </ul>
      </section>
    </div>
  );
}
