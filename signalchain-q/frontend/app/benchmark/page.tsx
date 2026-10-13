'use client';

import React, { useState } from 'react';

interface BenchmarkResultRow {
  method: string;
  output_snr_db?: number;
  snr_improvement_db?: number;
  rmse?: number;
  prd?: number;
  pearson_r?: number;
  r_peak_f1?: number;
  runtime_ms?: number;
  quantum_resources?: any;
  error?: string;
}

export default function BenchmarkPage() {
  const [loading, setLoading] = useState<boolean>(false);
  const [results, setResults] = useState<BenchmarkResultRow[]>([]);
  const [sampleCount, setSampleCount] = useState<number>(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleRunMiniBenchmark = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch('/api/benchmark/ecg', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          max_duration_sec: 2.5,
          sampling_rate_hz: 360,
        }),
      });

      if (!res.ok) {
        throw new Error('Benchmark execution failed');
      }

      const data = await res.json();
      setResults(data.results);
      setSampleCount(data.sample_count);
    } catch (err: any) {
      setErrorMsg(err.message || 'Benchmark request failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800, marginBottom: '0.5rem' }}>Classical vs. Quantum Benchmark</h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Side-by-side evaluation of all five required signal processing methods on identical ECG input and noise conditions.
        </p>
      </div>

      {errorMsg && (
        <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid var(--accent-red)', padding: '1rem', borderRadius: '8px', color: '#fca5a5', marginBottom: '1.5rem' }}>
          {errorMsg}
        </div>
      )}

      {/* Control Banner */}
      <div className="glass-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: '1.1rem', marginBottom: '0.25rem' }}>Interactive Web Benchmark</div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Evaluates: Raw Baseline (C0), Butterworth (C1), Wavelet db6 (C2), Adaptive FFT (C3), and QFT Grover (QSP).
          </div>
        </div>
        <button
          onClick={handleRunMiniBenchmark}
          disabled={loading}
          className="btn-primary"
          id="btn-run-benchmark"
        >
          {loading ? 'Evaluating 5 Methods...' : '▶ Run Interactive Comparison'}
        </button>
      </div>

      {/* Results Table */}
      {results.length > 0 && (
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Comparative Performance Table</h2>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Segment Samples: {sampleCount}</span>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Method Identifier</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Domain</th>
                  <th style={{ padding: '0.75rem 1rem' }}>SNR Imp. (dB)</th>
                  <th style={{ padding: '0.75rem 1rem' }}>PRD (%)</th>
                  <th style={{ padding: '0.75rem 1rem' }}>RMSE</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Pearson (r)</th>
                  <th style={{ padding: '0.75rem 1rem' }}>R-Peak F1</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Latency (ms)</th>
                </tr>
              </thead>
              <tbody>
                {results.map((row) => {
                  const isQuantum = row.method.includes('qft');
                  const isAdaptiveFFT = row.method.includes('fft_adaptive');
                  return (
                    <tr
                      key={row.method}
                      style={{
                        borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                        background: isQuantum ? 'rgba(56, 189, 248, 0.05)' : isAdaptiveFFT ? 'rgba(168, 85, 247, 0.05)' : 'transparent',
                      }}
                    >
                      <td style={{ padding: '0.75rem 1rem', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
                        {row.method}
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span
                          style={{
                            padding: '0.2rem 0.5rem',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            background: isQuantum ? 'rgba(56, 189, 248, 0.2)' : 'rgba(148, 163, 184, 0.15)',
                            color: isQuantum ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                          }}
                        >
                          {isQuantum ? 'Quantum QSP' : 'Classical DSP'}
                        </span>
                      </td>
                      <td
                        style={{
                          padding: '0.75rem 1rem',
                          fontFamily: 'var(--font-mono)',
                          fontWeight: 700,
                          color: (row.snr_improvement_db || 0) >= 0 ? 'var(--accent-green)' : 'var(--accent-red)',
                        }}
                      >
                        {row.snr_improvement_db !== undefined ? `${row.snr_improvement_db.toFixed(2)} dB` : '-'}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontFamily: 'var(--font-mono)' }}>
                        {row.prd !== undefined ? `${row.prd.toFixed(2)}%` : '-'}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontFamily: 'var(--font-mono)' }}>
                        {row.rmse !== undefined ? row.rmse.toFixed(4) : '-'}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontFamily: 'var(--font-mono)' }}>
                        {row.pearson_r !== undefined ? row.pearson_r.toFixed(4) : '-'}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>
                        {row.r_peak_f1 !== undefined ? row.r_peak_f1.toFixed(3) : '-'}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                        {row.runtime_ms !== undefined ? `${row.runtime_ms.toFixed(1)} ms` : '-'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div style={{ marginTop: '1.25rem', fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            * <strong>Notice on Fairness:</strong> Adaptive FFT (C3) and QFT Grover (QSP) utilize the identical frequency marking oracle and Hann windowing. Performance differences reflect amplitude amplification dynamics and state preparation overhead.
          </div>
        </div>
      )}
    </div>
  );
}
