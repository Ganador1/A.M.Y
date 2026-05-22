# API Guide for Neuroscience Domain

## Authentication
- Include `Authorization: Bearer YOUR_API_KEY` for protected endpoints.

## Analysis (Neuroscience Light)
- Base: `GET/POST /api/neuro-light/*`
- `POST /api/neuro-light/bandpowers` — EEG band powers analysis.
- `POST /api/neuro-light/connectivity` — Connectivity by frequency bands.
- `GET /api/neuro-light/health` — Service health check.
- `GET /api/neuro-light/metrics` — Capability metrics.

Example
```bash
curl -X POST "http://localhost:8000/api/neuro-light/bandpowers" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"signals": [[0.1,0.2,...]], "sampling_rate": 256}'
```

## Neuroimaging (Advanced)
- Base: `GET/POST /neuroimaging/*`
- `POST /neuroimaging/sessions` — Create analysis session.
- `POST /neuroimaging/preprocess` — Preprocess neuroimaging data.
- `POST /neuroimaging/connectivity` — Functional connectivity analysis.
- `POST /neuroimaging/segmentation` — Brain region segmentation.
- `POST /neuroimaging/patterns` — Pattern detection.
- `POST /neuroimaging/real-time` — Real-time processing.
- `GET /neuroimaging/sessions/{session_id}` — Get session state.
- `DELETE /neuroimaging/sessions/{session_id}` — Close session.
- `GET /neuroimaging/sessions` — List sessions.
- `GET /neuroimaging/modalities` — Supported modalities.

Example
```bash
curl -X POST "http://localhost:8000/neuroimaging/preprocess" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"modality": "eeg", "steps": ["bandpass","artifact_removal"], "data": {...}}'
```

## Simulation (Brian2 / NEURON)
- Base: `GET/POST /api/neuro-sim/*`
- `GET /api/neuro-sim/health` — Engines availability status.
- `POST /api/neuro-sim/brian2` — Run Brian2 network simulation.
- `POST /api/neuro-sim/neuron` — Run NEURON single-cell model.

Example
```bash
curl -X POST "http://localhost:8000/api/neuro-sim/brian2" \
  -H "Content-Type: application/json" \
  -d '{"num_neurons": 1000, "sim_time_ms": 1000, "connectivity": 0.1}'
```

## Multi-Scale Modeling
- Base: `GET/POST /multi-scale/*`
- `POST /multi-scale/networks` — Create neural network.
- `POST /multi-scale/simulate` — Simulate an existing network.
- `GET /multi-scale/analyze/{network_id}` — Analyze dynamics.
- `GET /multi-scale/status/{network_id}` — Network status.
- `GET /multi-scale/networks` — List networks.
- `POST /multi-scale/compare-scales` — Compare modeling scales.

Example
```bash
curl -X POST "http://localhost:8000/multi-scale/networks" \
  -H "Content-Type: application/json" \
  -d '{"name":"demo","neurons":100,"scale":"meso"}'
```

## Neuromorphic Computing
- Base: `GET/POST /neuromorphic/*`
- `POST /neuromorphic/snn/create` — Create spiking network.
- `POST /neuromorphic/snn/simulate` — Simulate SNN.
- `POST /neuromorphic/stdp/create-rule` — Create STDP rule.
- `POST /neuromorphic/stdp/simulate-protocol` — Simulate plasticity.
- `POST /neuromorphic/optimization/energy` — Energy optimization.
- `GET /neuromorphic/status` — Service status.
- `GET /neuromorphic/analysis/network-metrics/{network_id}` — Network metrics.
- `POST /neuromorphic/demo/complete-neuromorphic` — Full demo.

## Brain-Computer Interface (BCI)
- Base: `GET/POST /bci/*`
- `POST /bci/decoder/initialize` — Initialize decoder.
- `POST /bci/decoder/train` — Train decoder.
- `POST /bci/decode/realtime` — Real-time decoding.
- `POST /bci/decoder/adapt` — Online adaptation.
- `POST /bci/user/calibrate` — User calibration.
- `GET /bci/system/status` — System status.
- `POST /bci/session/simulate` — Simulate BCI session.
- `GET /bci/modalities` — Supported modalities.