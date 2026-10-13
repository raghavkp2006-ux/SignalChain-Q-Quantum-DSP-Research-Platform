'use client';

import React, { useState, useEffect, useRef } from 'react';

interface MetricData {
  output_snr_db?: number;
  snr_improvement_db?: number;
  rmse?: number;
  prd?: number;
  pearson_r?: number;
  r_peak_f1?: number;
}

interface QuantumResourceData {
  total_qubits?: number;
  total_gate_count?: number;
  cx_count?: number;
  transpiled_depth?: number;
  stateprep_depth?: number;
  stateprep_time_ms?: number;
  simulation_time_ms?: number;
  total_pipeline_time_ms?: number;
}

export default function ECGStudioPage() {
  const [examples, setExamples] = useState<any[]>([]);
  const [selectedExample, setSelectedExample] = useState<string>('clean_nsr');
  const [method, setMethod] = useState<string>('fft_adaptive_bandpass');
  const [samplingRate, setSamplingRate] = useState<number>(360);
  const [segmentLength, setSegmentLength] = useState<number>(256);
  const [loading, setLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [inputSignal, setInputSignal] = useState<number[]>([]);
  const [processedSignal, setProcessedSignal] = useState<number[]>([]);
  const [metrics, setMetrics] = useState<MetricData | null>(null);
  const [timings, setTimings] = useState<Record<string, number>>({});
  const [quantumResources, setQuantumResources] = useState<QuantumResourceData | null>(null);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Fetch built-in demo examples on mount
  useEffect(() => {
    fetch('/api/datasets/ecg/examples')
      .then((res) => res.json())
      .then((data) => {
        if (data.examples && data.examples.length > 0) {
          setExamples(data.examples);
          const first = data.examples[0];
          setInputSignal(first.signal);
          setSamplingRate(first.sampling_rate_hz);
        }
      })
      .catch((err) => console.log('Could not load examples:', err));
  }, []);

  const handleSelectExample = (exId: string) => {
    setSelectedExample(exId);
    const found = examples.find((e) => e.example_id === exId);
    if (found) {
      setInputSignal(found.signal);
      setSamplingRate(found.sampling_rate_hz);
      setProcessedSignal([]);
      setMetrics(null);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      const lines = text.trim().split('\n');
      const parsed: number[] = [];
      for (const line of lines) {
        const parts = line.split(',');
        const val = parseFloat(parts[parts.length - 1]);
        if (!isNaN(val)) parsed.push(val);
      }
      if (parsed.length > 0) {
        setInputSignal(parsed);
        setProcessedSignal([]);
        setMetrics(null);
        setErrorMsg(null);
      } else {
        setErrorMsg('Failed to parse numeric amplitudes from uploaded file.');
      }
    };
    reader.readAsText(file);
  };

  const handleRunProcessing = async () => {
    if (inputSignal.length === 0) {
      setErrorMsg('No ECG signal loaded.');
      return;
    }

    setLoading(true);
    setErrorMsg(null);

    try {
      const payload = {
        signal: inputSignal,
        sampling_rate_hz: samplingRate,
        method: method,
        parameters: {
          segment_length: segmentLength,
          hop_length: segmentLength / 2,
        },
      };

      const res = await fetch('/api/ecg/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Processing failed');
      }

      const data = await res.json();
      setProcessedSignal(data.processed_signal);
      setMetrics(data.metrics);
      setTimings(data.stage_timings_ms || {});
      setQuantumResources(data.quantum_resources || null);
    } catch (err: any) {
      setErrorMsg(err.message || 'Signal processing request failed.');
    } finally {
      setLoading(false);
    }
  };

  // Render waveforms on HTML5 Canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || inputSignal.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Clear background
    ctx.fillStyle = '#060a12';
    ctx.fillRect(0, 0, width, height);

    // Draw grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for (let x = 0; x < width; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += 40) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Determine scale bounds
    const displaySamples = Math.min(inputSignal.length, 1200);
    const subInput = inputSignal.slice(0, displaySamples);
    const subProcessed = processedSignal.slice(0, displaySamples);

    const allVals = subProcessed.length > 0 ? [...subInput, ...subProcessed] : subInput;
    const minVal = Math.min(...allVals);
    const maxVal = Math.max(...allVals);
    const range = Math.max(maxVal - minVal, 0.1);

    const getY = (val: number) => height - 30 - ((val - minVal) / range) * (height - 60);

    // Draw Input Signal (Orange/Amber)
    ctx.strokeStyle = '#f59e0b';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    for (let i = 0; i < subInput.length; i++) {
      const x = (i / (displaySamples - 1)) * width;
      const y = getY(subInput[i]);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Draw Processed Signal (Cyan) if available
    if (subProcessed.length > 0) {
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2.0;
      ctx.beginPath();
      for (let i = 0; i < subProcessed.length; i++) {
        const x = (i / (displaySamples - 1)) * width;
        const y = getY(subProcessed[i]);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
    }
  }, [inputSignal, processedSignal]);

  return (
    <div className="container">
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800, marginBottom: '0.5rem' }}>ECG Processing Studio</h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Run single-lead ECG records through classical baseline DSP or adaptive QFT Grover quantum denoising with real-time waveform inspection.
        </p>
      </div>

      {errorMsg && (
        <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid var(--accent-red)', padding: '1rem', borderRadius: '8px', color: '#fca5a5', marginBottom: '1.5rem' }}>
          {errorMsg}
        </div>
      )}

      {/* Control Panel Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem', marginBottom: '1.75rem' }}>
        {/* Source selection */}
        <div className="glass-card">
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
            ECG DATA SOURCE
          </label>
          <select
            value={selectedExample}
            onChange={(e) => handleSelectExample(e.target.value)}
            id="select-ecg-example"
            style={{ width: '100%', background: '#0f172a', border: '1px solid var(--border-subtle)', color: 'white', padding: '0.6rem', borderRadius: '6px', marginBottom: '0.75rem' }}
          >
            {examples.map((ex) => (
              <option key={ex.example_id} value={ex.example_id}>
                {ex.name}
              </option>
            ))}
          </select>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>or upload custom .CSV:</div>
          <input
            type="file"
            accept=".csv"
            id="file-upload-ecg"
            onChange={handleFileUpload}
            style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}
          />
        </div>

        {/* Method selection */}
        <div className="glass-card">
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
            DENOISING ALGORITHM
          </label>
          <select
            value={method}
            onChange={(e) => setMethod(e.target.value)}
            id="select-denoising-method"
            style={{ width: '100%', background: '#0f172a', border: '1px solid var(--border-subtle)', color: 'white', padding: '0.6rem', borderRadius: '6px', marginBottom: '0.75rem' }}
          >
            <option value="fft_adaptive_bandpass">Adaptive FFT Bandpass (C3 - Classical Fair)</option>
            <option value="qft_grover_ecg_adaptive">QFT + Adaptive Oracle + Grover (QSP - Quantum)</option>
            <option value="butterworth_bandpass">Butterworth 4th-order SOS (C1)</option>
            <option value="wavelet_db6">Wavelet db6 Universal Threshold (C2)</option>
            <option value="raw">Raw Passthrough (C0)</option>
          </select>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Segment Size (M):</span>
            <select
              value={segmentLength}
              onChange={(e) => setSegmentLength(parseInt(e.target.value))}
              id="select-segment-size"
              style={{ background: '#0f172a', border: '1px solid var(--border-subtle)', color: 'white', padding: '0.3rem 0.6rem', borderRadius: '4px', fontSize: '0.85rem' }}
            >
              <option value={64}>64 (6 qubits)</option>
              <option value={128}>128 (7 qubits)</option>
              <option value={256}>256 (8 qubits)</option>
            </select>
          </div>
        </div>

        {/* Action Panel */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <button
            onClick={handleRunProcessing}
            disabled={loading}
            className="btn-primary"
            id="btn-run-process"
            style={{ width: '100%', justifyContent: 'center', padding: '0.85rem', fontSize: '1rem' }}
          >
            {loading ? 'Processing via QSP...' : '▶ Execute Denoising Pipeline'}
          </button>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textAlign: 'center', marginTop: '0.5rem' }}>
            Sampling: {samplingRate} Hz • Length: {inputSignal.length} samples
          </div>
        </div>
      </div>

      {/* Waveform Canvas View */}
      <div className="glass-card" style={{ marginBottom: '1.75rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Oscilloscope Trace Visualizer</h2>
          <div style={{ display: 'flex', gap: '1.25rem', fontSize: '0.85rem' }}>
            <span style={{ color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ display: 'inline-block', width: '12px', height: '3px', background: '#f59e0b' }}></span>
              Noisy / Raw Input
            </span>
            <span style={{ color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ display: 'inline-block', width: '12px', height: '3px', background: '#38bdf8' }}></span>
              Processed Output ({method})
            </span>
          </div>
        </div>

        <canvas
          ref={canvasRef}
          width={1200}
          height={260}
          className="waveform-canvas"
          id="canvas-ecg-trace"
        />
      </div>

      {/* Metrics Row */}
      {metrics && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.75rem' }}>
          <div className="metric-tile">
            <div className="metric-tile-title">SNR Improvement</div>
            <div className="metric-tile-value" style={{ color: (metrics.snr_improvement_db || 0) >= 0 ? 'var(--accent-green)' : 'var(--accent-red)' }}>
              {metrics.snr_improvement_db !== undefined ? `${metrics.snr_improvement_db.toFixed(2)} dB` : 'N/A'}
            </div>
          </div>
          <div className="metric-tile">
            <div className="metric-tile-title">Output SNR</div>
            <div className="metric-tile-value">{metrics.output_snr_db !== undefined ? `${metrics.output_snr_db.toFixed(2)} dB` : 'N/A'}</div>
          </div>
          <div className="metric-tile">
            <div className="metric-tile-title">PRD (Distortion)</div>
            <div className="metric-tile-value">{metrics.prd !== undefined ? `${metrics.prd.toFixed(2)}%` : 'N/A'}</div>
          </div>
          <div className="metric-tile">
            <div className="metric-tile-title">RMSE</div>
            <div className="metric-tile-value">{metrics.rmse !== undefined ? metrics.rmse.toFixed(4) : 'N/A'}</div>
          </div>
          <div className="metric-tile">
            <div className="metric-tile-title">Pearson Corr (r)</div>
            <div className="metric-tile-value">{metrics.pearson_r !== undefined ? metrics.pearson_r.toFixed(4) : 'N/A'}</div>
          </div>
          <div className="metric-tile">
            <div className="metric-tile-title">R-Peak F1 Score</div>
            <div className="metric-tile-value" style={{ color: 'var(--accent-cyan)' }}>
              {metrics.r_peak_f1 !== undefined ? metrics.r_peak_f1.toFixed(3) : 'N/A'}
            </div>
          </div>
        </div>
      )}

      {/* Quantum Resource Panel (when quantum method is executed) */}
      {quantumResources && (
        <div className="glass-card" style={{ border: '1px solid rgba(56, 189, 248, 0.35)', background: 'rgba(15, 23, 42, 0.9)' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-cyan)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>⚛️</span> Quantum Circuit Resource Accounting (Section 18)
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Signal Qubits</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'white' }}>{quantumResources.total_qubits} Qubits</div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Transpiled Depth</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'white' }}>{quantumResources.transpiled_depth}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Total Gate Count</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'white' }}>{quantumResources.total_gate_count}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>CX (CNOT) Gates</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--accent-amber)' }}>{quantumResources.cx_count}</div>
            </div>
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.75rem' }}>
            <strong>Explicit Runtime Accounting:</strong> State Preparation: {quantumResources.stateprep_time_ms?.toFixed(2)} ms | Statevector Sim: {quantumResources.simulation_time_ms?.toFixed(2)} ms | Total: {quantumResources.total_pipeline_time_ms?.toFixed(2)} ms
          </div>
        </div>
      )}
    </div>
  );
}
