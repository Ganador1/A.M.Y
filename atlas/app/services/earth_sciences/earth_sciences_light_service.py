"""
Earth Sciences Light Service
Análisis ligero de series climáticas (tas trend, extremos) desde CSV/NetCDF locales sin dependencias pesadas.
"""

from typing import Dict, Any, Optional
import math
from app.exceptions.base import AtlasException


class EarthSciencesLightService:
    """Cálculos ligeros: tendencia lineal y conteo de extremos para serie temporal."""

    def __init__(self):
        pass

    @staticmethod
    def _linear_trend(x: list[float], y: list[float]) -> float:
        n = len(x)
        if n < 2:
            return 0.0
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        den = sum((xi - mean_x) ** 2 for xi in x) + 1e-12
        return float(num / den)

    async def analyze_temperature_timeseries(self, times: list[str], temps_c: list[float], threshold_extreme: Optional[float] = None) -> Dict[str, Any]:
        if len(times) != len(temps_c):
            return {"error": "times y temps_c deben tener la misma longitud"}
        n = len(times)
        if n == 0:
            return {"error": "serie vacía"}

        # Mapear tiempos a índices uniformes (asume mensual/diario uniforme)
        x = list(range(n))
        slope = self._linear_trend(x, temps_c)
        mean = sum(temps_c) / n
        var = sum((t - mean) ** 2 for t in temps_c) / max(1, n - 1)
        std = math.sqrt(max(0.0, var))

        thr = threshold_extreme if threshold_extreme is not None else (mean + 2 * std)
        extremes = sum(1 for t in temps_c if t >= thr)

        return {
            "n_points": n,
            "trend_per_step_c": slope,
            "mean_c": mean,
            "std_c": std,
            "extreme_threshold_c": thr,
            "extreme_events": extremes,
            "first": {"time": times[0], "temp_c": temps_c[0]},
            "last": {"time": times[-1], "temp_c": temps_c[-1]},
        }

    async def analyze_temperature_netcdf(self, filepath: str, var_name: str = 'tas') -> Dict[str, Any]:
        try:
            import xarray as xr
        except AtlasException as e:
            return {"error": f"xarray no disponible: {e}"}
        try:
            ds = xr.open_dataset(filepath)
            if var_name not in ds:
                return {"error": f"Variable {var_name} no encontrada en dataset"}
            da = ds[var_name]
            # Reduce a serie global si tiene dims extra
            if 'time' not in da.dims:
                return {"error": "Variable no contiene dimensión 'time'"}
            series = da
            for d in list(series.dims):
                if d != 'time':
                    series = series.mean(dim=d)
            vals = series.values.astype(float).tolist()
            times = [str(t) for t in series['time'].values]
            return await self.analyze_temperature_timeseries(times, vals)
        except AtlasException as e:
            return {"error": str(e)}

    async def analyze_seismic_signal(self, samples: list[float], sampling_rate_hz: float = 100.0) -> Dict[str, Any]:
        n = len(samples)
        if n == 0:
            return {"error": "señal vacía"}
        mean = sum(samples) / n
        centered = [s - mean for s in samples]
        # RMS and peak
        rms = math.sqrt(sum(c*c for c in centered) / n)
        peak = max(abs(c) for c in centered)
        # Zero crossing rate
        zc = 0
        for i in range(1, n):
            if centered[i-1] == 0:
                continue
            if (centered[i-1] > 0 and centered[i] < 0) or (centered[i-1] < 0 and centered[i] > 0):
                zc += 1
        zcr_hz = (zc * sampling_rate_hz) / n
        # Simple STA/LTA indicator (window sizes relative)
        sta_w = max(1, n // 100)
        lta_w = max(sta_w + 1, n // 10)
        def moving_avg(arr: list[float], w: int) -> list[float]:
            out = []
            acc = 0.0
            for i, v in enumerate(arr):
                acc += abs(v)
                if i >= w:
                    acc -= abs(arr[i-w])
                if i >= w-1:
                    out.append(acc / w)
            return out
        sta = moving_avg(centered, sta_w)
        lta = moving_avg(centered, lta_w)
        # Align lengths
        m = min(len(sta), len(lta))
        sta = sta[-m:]
        lta = lta[-m:] or [1e-9]
        ratios = [s/max(l,1e-9) for s, l in zip(sta, lta)] if m > 0 else []
        max_ratio = max(ratios) if ratios else 0.0
        event_likely = max_ratio > 3.0
        return {
            "n_samples": n,
            "sampling_rate_hz": sampling_rate_hz,
            "rms": rms,
            "peak": peak,
            "zero_crossing_rate_hz": zcr_hz,
            "sta_lta_max_ratio": max_ratio,
            "event_likely": event_likely
        }

    async def seismic_psd(self, samples: list[float], sampling_rate_hz: float = 100.0, nperseg: int = 512) -> Dict[str, Any]:
        try:
            from scipy.signal import welch
        except AtlasException as e:
            return {"error": f"scipy no disponible: {e}"}
        if len(samples) < 2:
            return {"error": "señal demasiado corta"}
        f, pxx = welch(samples, fs=sampling_rate_hz, nperseg=min(nperseg, len(samples)))
        return {"freqs_hz": f.tolist(), "psd": pxx.tolist()}

    async def ocean_current_stats(self, u: list[float], v: list[float]) -> Dict[str, Any]:
        if len(u) != len(v):
            return {"error": "u y v deben tener igual longitud"}
        n = len(u)
        if n == 0:
            return {"error": "series vacías"}
        speeds = [math.sqrt(ux*ux + vx*vx) for ux, vx in zip(u, v)]
        mean_speed = sum(speeds) / n
        max_speed = max(speeds)
        # Simple front index via adjacent gradient (1D proxy)
        grads = [abs(speeds[i] - speeds[i-1]) for i in range(1, n)]
        front_index = sum(1 for g in grads if g > (0.5 * (sum(grads)/max(1,len(grads)))))
        return {
            "n_points": n,
            "mean_speed": mean_speed,
            "max_speed": max_speed,
            "front_index": front_index
        }

    async def detect_eddies_2d(self, grid: list[list[float]], threshold: float = 0.05) -> Dict[str, Any]:
        """
        Detección ligera de remolinos (eddies) en un campo 2D de anomalía SSH u otra métrica.
        Usa contornos por umbral absoluto simple para marcar regiones ciclónicas/anticiclónicas.
        """
        try:
            import numpy as np
        except AtlasException as e:
            return {"error": f"numpy no disponible: {e}"}
        arr = np.array(grid, dtype=float)
        if arr.ndim != 2 or arr.size == 0:
            return {"error": "grid inválido (se espera matriz 2D no vacía)"}
        # Marcadores binarios por umbral
        cyclonic = arr <= -abs(threshold)
        anticyclonic = arr >= abs(threshold)

        def label_regions(mask: np.ndarray) -> int:
            # Conteo básico de componentes conexas 4-vecindad
            visited = np.zeros_like(mask, dtype=bool)
            count = 0
            H, W = mask.shape
            for i in range(H):
                for j in range(W):
                    if mask[i, j] and not visited[i, j]:
                        count += 1
                        stack = [(i, j)]
                        visited[i, j] = True
                        while stack:
                            x, y = stack.pop()
                            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                                nx, ny = x+dx, y+dy
                                if 0 <= nx < H and 0 <= ny < W and mask[nx, ny] and not visited[nx, ny]:
                                    visited[nx, ny] = True
                                    stack.append((nx, ny))
            return count

        num_cyclonic = label_regions(cyclonic)
        num_anticyclonic = label_regions(anticyclonic)
        return {
            "threshold": float(abs(threshold)),
            "cyclonic_count": int(num_cyclonic),
            "anticyclonic_count": int(num_anticyclonic)
        }


