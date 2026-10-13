# SignalChain-Q Algorithm Specification

## 1. Mathematical Formulation

### 1.1 ECG Segmentation & Windowing
Given single-lead ECG signal $x \in \mathbb{R}^N$ at sampling rate $f_s = 360$ Hz:
1. Reflection padding of length $M$ is appended to both boundaries.
2. Segments of power-of-two length $M=256$ are extracted with hop length $H=128$ (50% overlap).
3. Each segment $x_j \in \mathbb{R}^M$ is windowed using a periodic Hann window $w$:
   $$x_{w,j}[n] = x_j[n] \cdot w[n], \quad n = 0, \dots, M-1$$

### 1.2 Adaptive Frequency Thresholding
For each segment $x_j$, compute the median absolute activity score:
$$A_j = \frac{1}{M} \sum_{n=0}^{M-1} |x_j[n] - \text{median}(x_j)|$$

Across the recording, compute percentiles $q_{10} = \text{P}_{10}(A)$ and $q_{90} = \text{P}_{90}(A)$.
Normalized activity:
$$u_j = \text{clip}\left(\frac{A_j - q_{10}}{q_{90} - q_{10} + \epsilon}, 0, 1\right)$$

Adaptive high cutoff frequency:
$$f_{\text{high},j} = f_{\text{high,min}} + u_j \cdot (f_{\text{high,max}} - f_{\text{high,min}})$$
where $f_{\text{low}} = 0.5$ Hz, $f_{\text{high,min}} = 25$ Hz, and $f_{\text{high,max}} = 45$ Hz.

Marked Fourier frequency bin indices:
$$k_{\text{low}} = \left\lceil \frac{f_{\text{low}} M}{f_s} \right\rceil, \quad k_{\text{high}} = \left\lfloor \frac{f_{\text{high},j} M}{f_s} \right\rfloor$$
Marked set (symmetric):
$$\text{Marked} = \{ k \mid k_{\text{low}} \le k \le k_{\text{high}} \lor M - k_{\text{high}} \le k \le M - k_{\text{low}} \}$$
DC component ($k=0$) is strictly unmarked.

### 1.3 Quantum State Preparation & Amplitude Encoding
For windowed frame $v = x_{w,j}$, compute scale $S = \|v\|_2$.
If $S < 10^{-12}$, output is identically zero.
Otherwise, normalized amplitude statevector:
$$|\psi_0\rangle = \sum_{k=0}^{M-1} \frac{v[k]}{S} |k\rangle$$
using Qiskit's `StatePreparation` gate over $m = \log_2(M) = 8$ qubits.

### 1.4 Quantum Fourier Transform
$$|\Psi_{\text{freq}}\rangle = \text{QFT}_m |\psi_0\rangle$$

### 1.5 Phase Oracle
Phase inversion on marked frequency states:
$$U_f |k\rangle = \begin{cases} -|k\rangle & \text{if } k \in \text{Marked} \\ +|k\rangle & \text{otherwise} \end{cases}$$

### 1.6 Grover Diffusion Operator
$$D = 2 |s\rangle\langle s| - I, \quad |s\rangle = H^{\otimes m} |0\rangle^{\otimes m}$$
Iterations: $r = \min\left(3, \left\lfloor \frac{\pi}{4} \sqrt{\frac{M}{|\text{Marked}|}} \right\rfloor\right)$.

### 1.7 Inverse QFT & Reconstruction
$$|\psi_{\text{out}}\rangle = \text{IQFT}_m \left( (D U_f)^r |\Psi_{\text{freq}}\rangle \right)$$
Waveform amplitudes:
$$\hat{x}_{w,j}[n] = \text{Re}(\langle n | \psi_{\text{out}} \rangle) \cdot S$$

### 1.8 Weighted Overlap-Add (WOLA)
$$\hat{x}[n] = \frac{\sum_j \hat{x}_{w,j}[n - j H] \cdot w[n - j H]}{\sum_j w^2[n - j H] + \epsilon}$$
