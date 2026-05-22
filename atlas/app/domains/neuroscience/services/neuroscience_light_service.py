"""
Neuroscience Light Service
Análisis EEG ligero (band powers) sin dependencias pesadas.
"""

from typing import Dict, Any, List, Tuple
import numpy as np


from app.services.base_service import BaseService

class NeuroscienceLightService(BaseService):
    """Servicio ligero para análisis EEG (band powers por canal)."""

    def __init__(self, sampling_rate_hz: float = 1000.0):
        super().__init__("NeuroscienceLightService")
        self.fs = float(sampling_rate_hz)

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a service request.
        """
        operation = request_data.get("operation")
        
        if operation == "analyze_eeg":
            data = request_data.get("data", [])
            return await self.analyze_eeg_bandpowers(data)
            
        return {"success": False, "error": f"Unknown operation: {operation}"}

    def _bandpower_fft(self, signal: np.ndarray, band: List[float]) -> float:
        n = len(signal)
        if n == 0:
            return 0.0
        # Hann window to reduce spectral leakage
        window = np.hanning(n)
        sig_w = signal * window
        # One-sided FFT
        fft_vals = np.fft.rfft(sig_w)
        fft_freqs = np.fft.rfftfreq(n, d=1.0 / self.fs)
        psd = (np.abs(fft_vals) ** 2) / (np.sum(window ** 2))

        fmin, fmax = band
        idx = np.logical_and(fft_freqs >= fmin, fft_freqs <= fmax)
        # Trapz integration of PSD over band
        if not np.any(idx):
            return 0.0
        return float(np.trapz(psd[idx], fft_freqs[idx]))

    async def analyze_eeg_bandpowers(self, data: List[List[float]]) -> Dict[str, Any]:
        """
        Calcula potencias de banda por canal para bandas estándar: delta, theta, alpha, beta, gamma.

        Args:
            data: lista de canales, cada canal es lista de floats (shape: n_channels x n_samples)

        Returns:
            dict con band powers por canal y totales normalizados.
        """
        arr = np.array(data, dtype=float)
        if arr.ndim != 2:
            return {"error": "Formato inválido: se espera [n_channels][n_samples]"}

        bands = {
            "delta": (1.0, 4.0),
            "theta": (4.0, 8.0),
            "alpha": (8.0, 13.0),
            "beta": (13.0, 30.0),
            "gamma": (30.0, 45.0),
        }

        channel_results: List[Dict[str, float]] = []
        for ch in arr:
            ch_res: Dict[str, float] = {}
            total_power = 0.0
            # Wideband power for normalization
            total_power = self._bandpower_fft(ch, [1.0, min(0.5 * self.fs, 45.0)])
            total_power = max(total_power, 1e-12)

            for name, (lo, hi) in bands.items():
                p = self._bandpower_fft(ch, [lo, hi])
                ch_res[name] = p
                ch_res[f"{name}_rel"] = p / total_power
            ch_res["total_power"] = total_power
            channel_results.append(ch_res)

        # Aggregate means across channels
        agg: Dict[str, float] = {}
        for key in channel_results[0].keys():
            agg[key] = float(np.mean([cr[key] for cr in channel_results]))

        return {
            "sampling_rate_hz": self.fs,
            "n_channels": int(arr.shape[0]),
            "n_samples": int(arr.shape[1]),
            "bands": list(bands.keys()),
            "channel_bandpowers": channel_results,
            "aggregate": agg,
        }

    async def connectivity_by_band(self, data: List[List[float]]) -> Dict[str, Any]:
        """
        Calcula conectividad simple por pares (coherencia normalizada) por banda usando correlación de señales filtradas por FFT-mask.
        Ligero y sin dependencias externas.
        """
        arr = np.array(data, dtype=float)
        if arr.ndim != 2 or arr.shape[0] < 2:
            return {"error": "Se requieren >=2 canales con formato [n_channels][n_samples]"}

        bands = {
            "delta": (1.0, 4.0),
            "theta": (4.0, 8.0),
            "alpha": (8.0, 13.0),
            "beta": (13.0, 30.0),
            "gamma": (30.0, 45.0),
        }

        def band_filter(sig: np.ndarray, lo: float, hi: float) -> np.ndarray:
            n = len(sig)
            if n == 0:
                return sig
            fft_vals = np.fft.rfft(sig)
            freqs = np.fft.rfftfreq(n, d=1.0 / self.fs)
            mask = (freqs >= lo) & (freqs <= hi)
            fft_vals[~mask] = 0
            rec = np.fft.irfft(fft_vals, n=n)
            return rec

        results: Dict[str, Any] = {"bands": list(bands.keys()), "matrices": {}}
        n_ch = arr.shape[0]
        for name, (lo, hi) in bands.items():
            filt = np.stack([band_filter(arr[i], lo, hi) for i in range(n_ch)], axis=0)
            # Normalized correlation matrix as simple connectivity proxy
            if filt.shape[1] < 2:
                conn = np.eye(n_ch)
            else:
                filt_z = (filt - filt.mean(axis=1, keepdims=True))
                denom = np.sqrt(np.sum(filt_z**2, axis=1, keepdims=True)) + 1e-12
                filt_z /= denom
                conn = np.matmul(filt_z, filt_z.T) / max(1, filt_z.shape[1])
                conn = np.clip(conn, -1.0, 1.0)
            results["matrices"][name] = conn.tolist()

        return {
            "sampling_rate_hz": self.fs,
            "n_channels": int(n_ch),
            "n_samples": int(arr.shape[1]),
            **results,
        }

    # === Advanced analysis helpers ===
    def _detrend_zscore(self, arr: np.ndarray) -> np.ndarray:
        mean = arr.mean(axis=1, keepdims=True)
        std = arr.std(axis=1, keepdims=True) + 1e-12
        return (arr - mean) / std

    def _welch(self, x: np.ndarray, fs: float, nperseg: int = 256, noverlap: int = 128) -> Tuple[np.ndarray, np.ndarray]:
        # Prefer SciPy/MNE if disponibles
        try:
            import mne  # noqa: F401
            from mne.time_frequency import psd_array_welch
            x2 = x if x.ndim == 2 else x[None, :]
            psd, freqs = psd_array_welch(x2, sfreq=fs, n_per_seg=nperseg, n_overlap=noverlap, average='mean')
            return freqs, psd
        except Exception:
            try:
                from scipy.signal import welch
                x2 = x if x.ndim == 2 else x[None, :]
                freqs, psds = [], []
                for row in x2:
                    f, p = welch(row, fs=fs, nperseg=nperseg, noverlap=noverlap, window='hann')
                    freqs = f
                    psds.append(p)
                return np.array(freqs), np.array(psds)
            except Exception:
                pass
        x = np.asarray(x, dtype=float)
        step = nperseg - noverlap
        if x.ndim == 1:
            x = x[None, :]
        n = x.shape[1]
        if n < nperseg:
            pad = np.zeros((x.shape[0], nperseg - n))
            x = np.concatenate([x, pad], axis=1)
            n = x.shape[1]
        window = np.hanning(nperseg)
        scale = (window**2).sum()
        segments = max(1, (n - noverlap) // step - 1)
        freqs = np.fft.rfftfreq(nperseg, d=1.0/fs)
        psd = np.zeros((x.shape[0], freqs.shape[0]))
        for i in range(segments):
            s = i * step
            e = s + nperseg
            seg = x[:, s:e] * window
            fftv = np.fft.rfft(seg, axis=1)
            psd += (np.abs(fftv) ** 2) / scale
        psd /= max(1, segments)
        return freqs, psd

    def _coherence(self, a: np.ndarray, b: np.ndarray, fs: float, nperseg: int = 256, noverlap: int = 128) -> Tuple[np.ndarray, np.ndarray]:
        # Prefer SciPy if disponible
        try:
            from scipy.signal import coherence
            f, cxy = coherence(a, b, fs=fs, nperseg=nperseg, noverlap=noverlap, window='hann')
            return f, cxy
        except Exception:
            pass
        # Welch cross/auto power spectral densities
        step = nperseg - noverlap
        window = np.hanning(nperseg)
        scale = (window**2).sum()
        n = len(a)
        segments = max(1, (n - noverlap) // step - 1)
        freqs = np.fft.rfftfreq(nperseg, d=1.0/fs)
        Sxx = np.zeros_like(freqs, dtype=float)
        Syy = np.zeros_like(freqs, dtype=float)
        Sxy = np.zeros_like(freqs, dtype=complex)
        for i in range(segments):
            s = i * step
            e = s + nperseg
            seg_a = a[s:e] * window
            seg_b = b[s:e] * window
            Fa = np.fft.rfft(seg_a)
            Fb = np.fft.rfft(seg_b)
            Sxx += (np.abs(Fa)**2) / scale
            Syy += (np.abs(Fb)**2) / scale
            Sxy += (Fa * np.conj(Fb)) / scale
        Sxx /= max(1, segments)
        Syy /= max(1, segments)
        Sxy /= max(1, segments)
        coh = np.abs(Sxy)**2 / (Sxx * Syy + 1e-18)
        return freqs, coh

    def _analytic_signal(self, x: np.ndarray) -> np.ndarray:
        # Hilbert transform via FFT (analytic signal)
        n = len(x)
        Xf = np.fft.fft(x)
        h = np.zeros(n)
        if n % 2 == 0:
            h[0] = 1
            h[n//2] = 1
            h[1:n//2] = 2
        else:
            h[0] = 1
            h[1:(n+1)//2] = 2
        return np.fft.ifft(Xf * h)

    async def analyze_eeg_full(self, data: List[List[float]], nperseg: int = 256, noverlap: int = 128) -> Dict[str, Any]:
        arr = np.array(data, dtype=float)
        if arr.ndim != 2:
            return {"error": "Formato inválido: se espera [n_channels][n_samples]"}
        pre = self._detrend_zscore(arr)
        freqs, psd = self._welch(pre, self.fs, nperseg=nperseg, noverlap=noverlap)
        return {
            'sampling_rate_hz': self.fs,
            'n_channels': int(pre.shape[0]),
            'n_samples': int(pre.shape[1]),
            'psd': {'freqs_hz': freqs.tolist(), 'values': psd.tolist()}
        }

    async def connectivity_advanced(self, data: List[List[float]], bands: Dict[str, Tuple[float, float]] | None = None) -> Dict[str, Any]:
        arr = np.array(data, dtype=float)
        if arr.ndim != 2 or arr.shape[0] < 2:
            return {"error": "Se requieren >=2 canales con formato [n_channels][n_samples]"}
        if bands is None:
            bands = {"delta": (1.0, 4.0), "theta": (4.0, 8.0), "alpha": (8.0, 13.0), "beta": (13.0, 30.0), "gamma": (30.0, 45.0)}
        n_ch = arr.shape[0]
        results: Dict[str, Any] = {"bands": list(bands.keys()), "coherence": {}, "plv": {}}

        # Coherence matrices
        for name, (lo, hi) in bands.items():
            coh_mat = np.eye(n_ch, dtype=float)
            for i in range(n_ch):
                for j in range(i+1, n_ch):
                    freqs, coh = self._coherence(arr[i], arr[j], self.fs)
                    # band-average coherence
                    idx = (freqs >= lo) & (freqs <= hi)
                    cval = float(np.mean(coh[idx])) if np.any(idx) else 0.0
                    coh_mat[i, j] = coh_mat[j, i] = cval
            results["coherence"][name] = coh_mat.tolist()

        # PLV matrices (phase locking value)
        for name, (lo, hi) in bands.items():
            # crude bandpass via FFT masking
            def bandpass(sig: np.ndarray) -> np.ndarray:
                n = len(sig)
                X = np.fft.rfft(sig)
                freqs = np.fft.rfftfreq(n, d=1.0/self.fs)
                mask = (freqs >= lo) & (freqs <= hi)
                X[~mask] = 0
                return np.fft.irfft(X, n=n)
            plv_mat = np.ones((n_ch, n_ch), dtype=float)
            filtered = [bandpass(arr[i]) for i in range(n_ch)]
            phases = [np.angle(self._analytic_signal(f)) for f in filtered]
            for i in range(n_ch):
                for j in range(i+1, n_ch):
                    dphi = phases[i] - phases[j]
                    plv = np.abs(np.mean(np.exp(1j * dphi)))
                    plv_mat[i, j] = plv_mat[j, i] = float(plv)
            results["plv"][name] = plv_mat.tolist()

        return {
            'sampling_rate_hz': self.fs,
            'n_channels': int(n_ch),
            'n_samples': int(arr.shape[1]),
            **results
        }

    async def simulate_whole_brain(self, connectivity_matrix: list[list[float]], simulation_time_ms: int = 10000) -> Dict[str, Any]:
        """
        Simulación de cerebro completo usando modelo de oscilador acoplado.
        """
        try:
            import numpy as np
            from scipy.integrate import odeint
        except Exception as e:
            return {"error": f"numpy/scipy no disponible: {e}"}
        
        conn_matrix = np.array(connectivity_matrix, dtype=float)
        if conn_matrix.ndim != 2 or conn_matrix.shape[0] != conn_matrix.shape[1]:
            return {"error": "matriz de conectividad debe ser cuadrada"}
        
        n_regions = conn_matrix.shape[0]
        if n_regions == 0:
            return {"error": "matriz de conectividad vacía"}
        
        # Parámetros del modelo de oscilador
        dt = 0.1  # ms
        t = np.arange(0, simulation_time_ms, dt)
        
        # Modelo de oscilador acoplado (Kuramoto simplificado)
        def kuramoto_model(y, t, K, omega, conn):
            n = len(y)
            dydt = np.zeros(n)
            
            for i in range(n):
                # Término de acoplamiento
                coupling = 0
                for j in range(n):
                    if i != j:
                        coupling += conn[i, j] * np.sin(y[j] - y[i])
                
                dydt[i] = omega[i] + K * coupling
            
            return dydt
        
        # Parámetros
        K = 0.1  # Fuerza de acoplamiento
        omega = np.random.uniform(0.5, 2.0, n_regions)  # Frecuencias naturales
        
        # Condiciones iniciales
        y0 = np.random.uniform(0, 2*np.pi, n_regions)
        
        # Integrar
        sol = odeint(kuramoto_model, y0, t, args=(K, omega, conn_matrix))
        
        # Análisis de sincronización
        order_parameter = np.abs(np.mean(np.exp(1j * sol), axis=1))
        mean_order = np.mean(order_parameter)
        
        # Conectividad funcional (correlación entre regiones)
        functional_conn = np.corrcoef(sol.T)
        
        return {
            "n_regions": n_regions,
            "simulation_time_ms": simulation_time_ms,
            "phases": sol.tolist(),
            "order_parameter": order_parameter.tolist(),
            "mean_synchronization": float(mean_order),
            "functional_connectivity": functional_conn.tolist(),
            "synchronization_level": "high" if mean_order > 0.7 else "medium" if mean_order > 0.3 else "low"
        }

    async def analyze_brain_networks(self, connectivity_matrix: list[list[float]], threshold: float = 0.3) -> Dict[str, Any]:
        """
        Análisis de redes cerebrales usando métricas de teoría de grafos.
        """
        try:
            import numpy as np
            from scipy.sparse import csgraph
        except Exception as e:
            return {"error": f"numpy/scipy no disponible: {e}"}
        
        conn_matrix = np.array(connectivity_matrix, dtype=float)
        if conn_matrix.ndim != 2 or conn_matrix.shape[0] != conn_matrix.shape[1]:
            return {"error": "matriz de conectividad debe ser cuadrada"}
        
        n_nodes = conn_matrix.shape[0]
        if n_nodes == 0:
            return {"error": "matriz de conectividad vacía"}
        
        # Binarizar matriz
        binary_matrix = (conn_matrix > threshold).astype(int)
        
        # Métricas de red
        # Grado de cada nodo
        degrees = np.sum(binary_matrix, axis=1)
        
        # Clustering coefficient
        clustering_coeffs = []
        for i in range(n_nodes):
            neighbors = np.where(binary_matrix[i] == 1)[0]
            if len(neighbors) < 2:
                clustering_coeffs.append(0)
            else:
                # Contar triángulos
                triangles = 0
                for j in range(len(neighbors)):
                    for k in range(j+1, len(neighbors)):
                        if binary_matrix[neighbors[j], neighbors[k]] == 1:
                            triangles += 1
                
                possible_triangles = len(neighbors) * (len(neighbors) - 1) / 2
                clustering_coeffs.append(triangles / possible_triangles if possible_triangles > 0 else 0)
        
        # Path length (distancia promedio)
        try:
            dist_matrix = csgraph.shortest_path(binary_matrix, directed=False)
            # Reemplazar infinitos con NaN
            dist_matrix[dist_matrix == np.inf] = np.nan
            path_lengths = np.nanmean(dist_matrix, axis=1)
            mean_path_length = np.nanmean(path_lengths)
        except:
            mean_path_length = np.nan
        
        # Eficiencia de red
        efficiency_matrix = 1 / (dist_matrix + np.eye(n_nodes))
        efficiency_matrix[np.isnan(efficiency_matrix)] = 0
        network_efficiency = np.mean(efficiency_matrix)
        
        # Centralidad de grado
        degree_centrality = degrees / (n_nodes - 1)
        
        # Métricas globales
        mean_degree = np.mean(degrees)
        mean_clustering = np.mean(clustering_coeffs)
        
        # Small-worldness (aproximación)
        if not np.isnan(mean_path_length) and mean_clustering > 0:
            # Valores de referencia para red aleatoria
            random_path_length = np.log(n_nodes) / np.log(mean_degree) if mean_degree > 1 else np.nan
            random_clustering = mean_degree / n_nodes
            
            if not np.isnan(random_path_length) and random_clustering > 0:
                small_worldness = (mean_clustering / random_clustering) / (mean_path_length / random_path_length)
            else:
                small_worldness = np.nan
        else:
            small_worldness = np.nan
        
        return {
            "n_nodes": n_nodes,
            "threshold": threshold,
            "mean_degree": float(mean_degree),
            "mean_clustering": float(mean_clustering),
            "mean_path_length": float(mean_path_length) if not np.isnan(mean_path_length) else None,
            "network_efficiency": float(network_efficiency),
            "small_worldness": float(small_worldness) if not np.isnan(small_worldness) else None,
            "degree_centrality": degree_centrality.tolist(),
            "clustering_coefficients": clustering_coeffs,
            "network_type": "small_world" if not np.isnan(small_worldness) and small_worldness > 1 else "random"
        }


