// Mathematics AI - JavaScript Application Completo

// API Base URL
const API_BASE = '/api';

// Utility functions
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    element.innerHTML = '<div class="loading-spinner"></div> Procesando...';
    element.className = 'result-box show';
}

function showResult(elementId, content, isError = false) {
    const element = document.getElementById(elementId);
    element.innerHTML = content;
    element.className = isError ? 'result-box show result-error' : 'result-box show result-success';
}

function parseNumberArray(str) {
    return str.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n));
}

function formatMathExpression(expr) {
    return `<span class="math-expression">${expr}</span>`;
}

function formatChemicalFormula(formula) {
    return `<span class="math-expression">${formula}</span>`;
}

function formatQuantumState(state) {
    return `<span class="math-expression">${state}</span>`;
}

// API Functions
async function apiRequest(endpoint, data = null, method = 'GET') {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Error en la solicitud');
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ==================== AXIOM MODULE EXPLORER ====================

// Map friendly category names to actual API base paths and quick demo payloads
const MODULE_CATALOG_OVERRIDES = {
    'Arithmetic': {
        base: '/arithmetic',
        demo: async () => apiRequest('/arithmetic/calculate', { operation: 'add', operands: [5, 3, 2] }, 'POST'),
        explain: 'Operaciones básicas y avanzadas (suma, resta, potencias, trigonometría).'
    },
    'Calculus': {
        base: '/calculus',
        demo: async () => apiRequest('/calculus/calculate', { expression: 'x^3 + 2*x', variable: 'x', operation: 'derivative', order: 1 }, 'POST'),
        explain: 'Derivadas, integrales, límites y series con SymPy.'
    },
    'Equations': {
        base: '/equations',
        demo: async () => apiRequest('/equations/solve', { equation: 'x^2 - 5*x + 6 = 0', variable: 'x' }, 'POST'),
        explain: 'Resolución de ecuaciones y sistemas algebraicos.'
    },
    'Statistics': {
        base: '/statistics',
        demo: async () => apiRequest('/statistics/calculate', { data: [1,2,3,4,5,6,7,8,9,10], operations: ['mean','median','std'] }, 'POST'),
        explain: 'Estadística descriptiva, correlación y regresión.'
    },
    'Graphing': {
        base: '/graphing',
        demo: async () => apiRequest('/graphing/generate', { expression: 'x^2 + 2*x + 1', variable: 'x', x_min: -5, x_max: 5, points: 400, title: 'Parábola' }, 'POST'),
        explain: 'Gráficos 2D/3D y visualización matemática.'
    },
    'Computational Chemistry': {
        base: '/chemistry',
        demo: async () => apiRequest('/chemistry/examples') // fallback info if heavy calcs not configured
            .catch(() => ({ message: 'Ejemplos de química listados. Prueba analizar moléculas vía API.' })),
        explain: 'Análisis molecular, conformeros y química cuántica.'
    },
    'Quantum Physics': {
        base: '/quantum-physics',
        demo: async () => apiRequest('/quantum-physics/examples')
            .catch(() => ({ message: 'Ejemplos de física cuántica listados.' })),
        explain: 'Simulaciones de espín, osciladores y óptica cuántica.'
    },
    'Quantum Computing': {
        base: '/quantum-computing',
        demo: async () => apiRequest('/quantum-computing/bell-state', { framework: 'qiskit' }, 'POST'),
        explain: 'Estados de Bell, Grover, QFT y VQE.'
    },
    'Advanced Algebra': {
        base: '/advanced-algebra',
        demo: async () => apiRequest('/advanced-algebra/examples')
            .catch(() => ({ message: 'Ejemplos de álgebra avanzada listados.' })),
        explain: 'Álgebra lineal y operaciones avanzadas.'
    },
    'Number Theory': {
        base: '/number-theory',
        demo: async () => apiRequest('/number-theory/examples')
            .catch(() => ({ message: 'Ejemplos de teoría de números listados.' })),
        explain: 'Primos, factorización y propiedades numéricas.'
    },
    'Optimization': {
        base: '/optimization',
        demo: async () => apiRequest('/optimization/examples')
            .catch(() => ({ message: 'Ejemplos de optimización listados.' })),
        explain: 'Programación lineal y no lineal.'
    },
    'Scientific AI': {
        base: '/scientific-ai',
        demo: async () => apiRequest('/scientific-ai/examples')
            .catch(() => ({ message: 'Ejemplos de IA científica listados.' })),
        explain: 'Razonamiento científico y PDEs asistidas por IA.'
    }
};

async function loadAxiomModulesExplorer() {
    const container = document.getElementById('axiomModulesContainer');
    if (!container) return;

    try {
        const resp = await apiRequest('/friendly');
        const categories = (resp && resp.data && resp.data.categories) ? resp.data.categories : [];

        const cards = categories.map((cat, idx) => {
            const icon = {
                'Arithmetic': 'fa-plus-circle',
                'Calculus': 'fa-integral',
                'Equations': 'fa-equals',
                'Statistics': 'fa-chart-bar',
                'Graphing': 'fa-chart-line',
                'Computational Chemistry': 'fa-flask',
                'Quantum Physics': 'fa-atom',
                'Quantum Computing': 'fa-microchip',
                'Scientific AI': 'fa-brain',
                'Advanced Algebra': 'fa-superscript',
                'Number Theory': 'fa-hashtag',
                'Optimization': 'fa-bullseye'
            }[cat.name] || 'fa-cube';

            const override = MODULE_CATALOG_OVERRIDES[cat.name] || { base: cat.endpoint.replace('/api',''), explain: cat.description };

            return `
                <div class="col-xl-3 col-lg-4 col-md-6">
                    <div class="card h-100 card-hover">
                        <div class="card-header d-flex align-items-center">
                            <i class="fas ${icon} me-2 text-primary"></i>
                            <h6 class="mb-0">${cat.name}</h6>
                        </div>
                        <div class="card-body d-flex flex-column">
                            <p class="text-muted small flex-grow-1">${override.explain || cat.description}</p>
                            <div class="mt-2">
                                <button class="btn btn-sm btn-primary me-2" data-module-name="${cat.name}" data-module-index="${idx}" onclick="openModuleDemo('${cat.name}')">
                                    <i class="fas fa-play me-1"></i> Probar demo
                                </button>
                                <a class="btn btn-sm btn-outline-secondary" href="${cat.endpoint}" target="_blank">
                                    <i class="fas fa-book me-1"></i> API
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = cards || '<div class="col-12 text-center text-muted">No hay módulos para mostrar.</div>';
    } catch (e) {
        container.innerHTML = `<div class="col-12"><div class="alert alert-warning">No se pudo cargar el catálogo de módulos: ${e.message}</div></div>`;
    }
}

window.openModuleDemo = async function(moduleName) {
    const modalEl = document.getElementById('moduleDemoModal');
    const titleEl = document.getElementById('moduleDemoTitle');
    const descEl = document.getElementById('moduleDemoDescription');
    const examplesEl = document.getElementById('moduleDemoExamples');
    const resultEl = document.getElementById('moduleDemoResult');

    titleEl.textContent = `Demo: ${moduleName}`;
    descEl.textContent = MODULE_CATALOG_OVERRIDES[moduleName]?.explain || '';
    examplesEl.innerHTML = '<div class="text-muted">Cargando ejemplos…</div>';
    resultEl.innerHTML = '';

    // Try to fetch examples endpoint if available
    let examplesData = null;
    try {
        const base = MODULE_CATALOG_OVERRIDES[moduleName]?.base || '';
        if (base) {
            const ex = await apiRequest(`${base}/examples`);
            examplesData = ex.data || ex;
        }
    } catch (_) { /* optional */ }

    // Render examples list (simple textual dump)
    if (examplesData) {
        const pretty = Array.isArray(examplesData) ? examplesData : Object.keys(examplesData).map(k => ({[k]: examplesData[k]}));
        examplesEl.innerHTML = `
            <h6>Ejemplos</h6>
            <pre class="small bg-light p-2 rounded" style="max-height: 240px; overflow: auto;">${escapeHtml(JSON.stringify(pretty, null, 2))}</pre>
            <button class="btn btn-success" onclick="runModuleQuickDemo('${moduleName}')"><i class='fas fa-bolt me-1'></i> Ejecutar demo rápida</button>
        `;
    } else {
        examplesEl.innerHTML = `
            <div class="d-flex align-items-center justify-content-between">
                <span class="text-muted">No hay listado de ejemplos. Puedes ejecutar una demo rápida.</span>
                <button class="btn btn-success" onclick="runModuleQuickDemo('${moduleName}')"><i class='fas fa-bolt me-1'></i> Demo rápida</button>
            </div>`;
    }

    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();
};

function escapeHtml(unsafe) {
    return String(unsafe)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

window.runModuleQuickDemo = async function(moduleName) {
    const resultEl = document.getElementById('moduleDemoResult');
    showLoading('moduleDemoResult');
    try {
        const runner = MODULE_CATALOG_OVERRIDES[moduleName]?.demo;
        if (!runner) throw new Error('Demo no disponible para este módulo.');
        const data = await runner();
        const safe = escapeHtml(JSON.stringify(data, null, 2));
        showResult('moduleDemoResult', `<pre class="small bg-light p-2 rounded" style="max-height: 360px; overflow: auto;">${safe}</pre>`);
    } catch (e) {
        showResult('moduleDemoResult', `Error al ejecutar la demo: ${e.message}`, true);
    }
};

// ==================== MATHEMATICS SECTION ====================

// Arithmetic Operations
async function calculateArithmetic() {
    const operation = document.getElementById('arithmeticOperation').value;
    const operandsStr = document.getElementById('arithmeticOperands').value;

    if (!operandsStr.trim()) {
        showResult('arithmeticResult', 'Por favor ingrese los operandos', true);
        return;
    }

    const operands = parseNumberArray(operandsStr);
    if (operands.length === 0) {
        showResult('arithmeticResult', 'Por favor ingrese números válidos', true);
        return;
    }

    showLoading('arithmeticResult');

    try {
        const result = await apiRequest('/arithmetic/calculate', {
            operation: operation,
            operands: operands
        }, 'POST');

        const content = `
            <div class="result-title">Resultado de la operación</div>
            <div class="result-content">
                <p><strong>Operación:</strong> ${result.operation}</p>
                <p><strong>Expresión:</strong> ${formatMathExpression(result.formatted_expression)}</p>
                <p><strong>Resultado:</strong> <span class="text-primary fs-4">${result.result}</span></p>
            </div>
        `;

        showResult('arithmeticResult', content);
    } catch (error) {
        showResult('arithmeticResult', `Error: ${error.message}`, true);
    }
}
window.calculateArithmetic = calculateArithmetic;

// Equation Solving
async function solveEquation() {
    const equation = document.getElementById('equation').value;
    const variable = document.getElementById('variable').value;

    if (!equation.trim()) {
        showResult('equationResult', 'Por favor ingrese una ecuación', true);
        return;
    }

    showLoading('equationResult');

    try {
        const result = await apiRequest('/equations/solve', {
            equation: equation,
            variable: variable
        }, 'POST');

        const solutionsHtml = result.solutions.map(sol => `<li>${sol}</li>`).join('');
        const stepsHtml = result.steps ? result.steps.map(step => `<li>${step}</li>`).join('') : '';

        const content = `
            <div class="result-title">Solución de la ecuación</div>
            <div class="result-content">
                <p><strong>Ecuación:</strong> ${formatMathExpression(result.equation)}</p>
                <p><strong>Variable:</strong> ${result.variable}</p>
                <p><strong>Tipo de solución:</strong> ${result.solution_type}</p>
                <p><strong>Soluciones:</strong></p>
                <ul>${solutionsHtml}</ul>
                ${stepsHtml ? `<p><strong>Pasos:</strong></p><ol class="result-steps">${stepsHtml}</ol>` : ''}
            </div>
        `;

        showResult('equationResult', content);
    } catch (error) {
        showResult('equationResult', `Error: ${error.message}`, true);
    }
}
window.solveEquation = solveEquation;

// Calculus Operations
async function calculateCalculus() {
    const operation = document.getElementById('calculusOperation').value;
    const expression = document.getElementById('calculusExpression').value;
    const variable = document.getElementById('calculusVariable').value;
    const order = parseInt(document.getElementById('calculusOrder').value);

    if (!expression.trim()) {
        showResult('calculusResult', 'Por favor ingrese una expresión', true);
        return;
    }

    showLoading('calculusResult');

    try {
        const result = await apiRequest('/calculus/calculate', {
            operation: operation,
            expression: expression,
            variable: variable,
            order: order
        }, 'POST');

        const stepsHtml = result.steps ? result.steps.map(step => `<li>${step}</li>`).join('') : '';

        const content = `
            <div class="result-title">Resultado del cálculo</div>
            <div class="result-content">
                <p><strong>Operación:</strong> ${result.operation}</p>
                <p><strong>Expresión original:</strong> ${formatMathExpression(result.original_expression)}</p>
                <p><strong>Variable:</strong> ${result.variable}</p>
                <p><strong>Resultado:</strong> ${formatMathExpression(result.result)}</p>
                ${stepsHtml ? `<p><strong>Pasos:</strong></p><ol class="result-steps">${stepsHtml}</ol>` : ''}
            </div>
        `;

        showResult('calculusResult', content);
    } catch (error) {
        showResult('calculusResult', `Error: ${error.message}`, true);
    }
}
window.calculateCalculus = calculateCalculus;

// Statistics
async function calculateStatistics() {
    const dataStr = document.getElementById('statisticsData').value;

    if (!dataStr.trim()) {
        showResult('statisticsResult', 'Por favor ingrese los datos', true);
        return;
    }

    const data = parseNumberArray(dataStr);
    if (data.length === 0) {
        showResult('statisticsResult', 'Por favor ingrese números válidos', true);
        return;
    }

    showLoading('statisticsResult');

    try {
        const result = await apiRequest('/statistics/calculate', {
            data: data,
            operations: ['mean', 'median', 'std', 'variance', 'min', 'max', 'range']
        }, 'POST');

        const resultsHtml = Object.entries(result.results).map(([key, value]) => {
            const displayName = {
                'mean': 'Media',
                'median': 'Mediana',
                'std': 'Desviación estándar',
                'variance': 'Varianza',
                'min': 'Mínimo',
                'max': 'Máximo',
                'range': 'Rango'
            }[key] || key;

            return `
                <tr>
                    <td><strong>${displayName}</strong></td>
                    <td>${typeof value === 'number' ? value.toFixed(4) : value}</td>
                </tr>
            `;
        }).join('');

        const content = `
            <div class="result-title">Análisis estadístico</div>
            <div class="result-content">
                <p><strong>Tamaño de muestra:</strong> ${result.sample_size}</p>
                <p><strong>Datos:</strong> [${result.data.join(', ')}]</p>
                <table class="result-table">
                    <thead>
                        <tr>
                            <th>Estadística</th>
                            <th>Valor</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${resultsHtml}
                    </tbody>
                </table>
            </div>
        `;

        showResult('statisticsResult', content);
    } catch (error) {
        showResult('statisticsResult', `Error: ${error.message}`, true);
    }
}
window.calculateStatistics = calculateStatistics;

// Graphing
async function generateGraph() {
    const expression = document.getElementById('graphExpression').value;
    const xMin = parseFloat(document.getElementById('graphXMin').value);
    const xMax = parseFloat(document.getElementById('graphXMax').value);
    const title = document.getElementById('graphTitle').value;

    if (!expression.trim()) {
        showResult('graphResult', 'Por favor ingrese una expresión', true);
        return;
    }

    if (xMin >= xMax) {
        showResult('graphResult', 'El valor mínimo de X debe ser menor que el máximo', true);
        return;
    }

    showLoading('graphResult');

    try {
        const result = await apiRequest('/graphing/generate', {
            expression: expression,
            variable: 'x',
            x_min: xMin,
            x_max: xMax,
            points: 1000,
            title: title || null
        }, 'POST');

        const content = `
            <div class="result-title">Gráfico generado</div>
            <div class="result-content">
                <p><strong>Expresión:</strong> ${formatMathExpression(result.expression)}</p>
                <div class="graph-container">
                    <img src="/${result.image_path}" alt="Gráfico de ${result.expression}" />
                </div>
                <div class="graph-info">
                    <h6>Información del gráfico:</h6>
                    <p><strong>Rango X:</strong> [${result.x_range[0]}, ${result.x_range[1]}]</p>
                    <p><strong>Rango Y:</strong> [${result.y_range[0].toFixed(2)}, ${result.y_range[1].toFixed(2)}]</p>
                    <p><strong>Puntos graficados:</strong> ${result.points_count}</p>
                </div>
            </div>
        `;

        showResult('graphResult', content);
    } catch (error) {
        showResult('graphResult', `Error: ${error.message}`, true);
    }
}
window.generateGraph = generateGraph;

// ==================== CHEMISTRY SECTION ====================

// Molecular Analysis
async function analyzeMolecule() {
    const smiles = document.getElementById('moleculeSmiles').value;
    const detailed = document.getElementById('detailedAnalysis')?.checked || false;

    if (!smiles?.trim()) {
        showResult('moleculeResult', 'Por favor ingrese un SMILES válido', true);
        return;
    }

    showLoading('moleculeResult');

    try {
        const result = await apiRequest('/chemistry/analyze-molecule', { smiles, detailed }, 'POST');
        const data = result?.data || result;

        let content = `
            <div class="result-title">Análisis molecular</div>
            <div class="result-content">
                <p><strong>SMILES:</strong> ${formatChemicalFormula(smiles)}</p>
        `;

        if (data.descriptors) {
            content += `<h6>Descriptores:</h6><ul>`;
            Object.entries(data.descriptors).forEach(([key, value]) => {
                content += `<li><strong>${key}:</strong> ${value}</li>`;
            });
            content += `</ul>`;
        }

        if (data.explanations) {
            content += `<h6>Explicaciones:</h6><ul>`;
            Object.entries(data.explanations).forEach(([key, value]) => {
                content += `<li><strong>${key}:</strong> ${value}</li>`;
            });
            content += `</ul>`;
        }

        content += `</div>`;
        showResult('moleculeResult', content);
    } catch (error) {
        showResult('moleculeResult', `Error: ${error.message}`, true);
    }
}

// Exponer funciones a ámbito global para handlers inline en HTML
window.analyzeMolecule = analyzeMolecule;

// Conformational Analysis
async function analyzeConformers() {
    const smiles = document.getElementById('conformerSmiles').value;
    const num = parseInt(document.getElementById('numConformers').value);
    const optimize = document.getElementById('optimizeConformers')?.checked ?? true;

    if (!smiles?.trim()) {
        showResult('conformerResult', 'Por favor ingrese un SMILES válido', true);
        return;
    }

    showLoading('conformerResult');

    try {
        const result = await apiRequest('/chemistry/generate-conformers', {
            smiles: smiles,
            num_conformers: isNaN(num) ? 10 : num,
            optimize: !!optimize
        }, 'POST');
        const data = result?.data || result;

        let content = `
            <div class="result-title">Análisis conformacional</div>
            <div class="result-content">
                <p><strong>Molécula:</strong> ${formatChemicalFormula(smiles)}</p>
                <p><strong>Conformeros generados:</strong> ${data.conformers?.length || data.conformers_count || 0}</p>
        `;

        if (data.conformers && data.conformers.length > 0) {
            content += `<h6>Conformeros principales:</h6><ul>`;
            data.conformers.forEach((conformer, index) => {
                const energy = (typeof conformer.energy === 'number') ? conformer.energy.toFixed(4) : conformer.energy;
                content += `<li><strong>Conformero ${index + 1}:</strong> Energía = ${energy} kcal/mol</li>`;
            });
            content += `</ul>`;
        }

        content += `</div>`;
        showResult('conformerResult', content);
    } catch (error) {
        showResult('conformerResult', `Error: ${error.message}`, true);
    }
}

// Alias para compatibilidad con la UI existente
window.generateConformers = analyzeConformers;

// Sequence Analysis
async function analyzeSequence() {
    const sequence = document.getElementById('sequence').value;
    const sequenceType = document.getElementById('sequenceType').value;

    if (!sequence?.trim()) {
        showResult('sequenceResult', 'Por favor ingrese una secuencia', true);
        return;
    }

    showLoading('sequenceResult');

    try {
        const result = await apiRequest('/chemistry/analyze-sequence', {
            sequence: sequence,
            sequence_type: sequenceType
        }, 'POST');

        const data = result?.data || result;

        let content = `
            <div class="result-title">Análisis de secuencia</div>
            <div class="result-content">
                <p><strong>Tipo de secuencia:</strong> ${data.type || data.sequence_type}</p>
                <p><strong>Longitud:</strong> ${data.length}</p>
        `;

        if (data.gc_content !== undefined) {
            content += `<p><strong>Contenido GC:</strong> ${data.gc_content}%</p>`;
        }

        if (data.explanations) {
            content += `<h6>Explicaciones:</h6><ul>`;
            Object.entries(data.explanations).forEach(([key, value]) => {
                content += `<li><strong>${key}:</strong> ${value}</li>`;
            });
            content += `</ul>`;
        }

        content += `</div>`;
        showResult('sequenceResult', content);
    } catch (error) {
        showResult('sequenceResult', `Error: ${error.message}`, true);
    }
}
window.analyzeSequence = analyzeSequence;

// Quantum Chemistry
async function runQuantumChemistry() {
    const atom = document.getElementById('quantumAtom').value;
    const basis = document.getElementById('quantumBasis').value;
    const method = document.getElementById('quantumMethod').value;

    if (!atom?.trim()) {
        showResult('quantumResult', 'Por favor ingrese coordenadas atómicas', true);
        return;
    }

    showLoading('quantumResult');

    try {
        const result = await apiRequest('/chemistry/quantum-chemistry', { atom, basis, method }, 'POST');
        const data = result?.data || result;

        let content = `
            <div class="result-title">Química cuántica</div>
            <div class="result-content">
                <p><strong>Coordenadas:</strong> ${formatChemicalFormula(atom)}</p>
                <p><strong>Método:</strong> ${(data.calculation_info?.method || method).toUpperCase()}</p>
                <p><strong>Base:</strong> ${data.calculation_info?.basis_set || basis}</p>
        `;

        if (data.total_energy || data.energy) {
            const E = data.total_energy ?? data.energy;
            content += `<p><strong>Energía total:</strong> ${Number(E).toFixed ? Number(E).toFixed(6) : E} Hartrees</p>`;
        }

        content += `</div>`;
        showResult('quantumResult', content);
    } catch (error) {
        showResult('quantumResult', `Error: ${error.message}`, true);
    }
}
window.runQuantumChemistry = runQuantumChemistry;

// ==================== PHYSICS SECTION ====================

// Spin Evolution
async function simulateSpinEvolution() {
    const Bx = parseFloat(document.getElementById('spinBx').value);
    const By = parseFloat(document.getElementById('spinBy').value);
    const Bz = parseFloat(document.getElementById('spinBz').value);
    const t_max = parseFloat(document.getElementById('spinTmax').value);
    const n_points = parseInt(document.getElementById('spinPoints').value);

    if ([Bx, By, Bz, t_max, n_points].some(v => isNaN(v))) {
        showResult('spinResult', 'Por favor ingrese parámetros válidos', true);
        return;
    }

    showLoading('spinResult');

    try {
        const result = await apiRequest('/quantum-physics/spin-evolution', { Bx, By, Bz, t_max, n_points }, 'POST');
        const data = result?.data || result;

        const content = `
            <div class="result-title">Evolución del espín</div>
            <div class="result-content">
                <p><strong>Campo magnético:</strong> [${Bx}, ${By}, ${Bz}]</p>
                <p><strong>Tiempo:</strong> ${t_max}</p>
                <p><strong>Puntos:</strong> ${n_points}</p>
            </div>
        `;

        showResult('spinResult', content);
    } catch (error) {
        showResult('spinResult', `Error: ${error.message}`, true);
    }
}
window.simulateSpinEvolution = simulateSpinEvolution;

// Harmonic Oscillator
async function simulateHarmonicOscillator() {
    const omega = parseFloat(document.getElementById('oscillatorOmega').value);
    const n_max = parseInt(document.getElementById('oscillatorNmax').value);
    const alpha = parseFloat(document.getElementById('oscillatorAlpha').value);
    const t_max = parseFloat(document.getElementById('oscillatorTmax').value);

    if ([omega, n_max, alpha, t_max].some(v => isNaN(v))) {
        showResult('oscillatorResult', 'Por favor ingrese parámetros válidos', true);
        return;
    }

    showLoading('oscillatorResult');

    try {
        await apiRequest('/quantum-physics/harmonic-oscillator', { omega, n_max, alpha, t_max }, 'POST');
        const content = `
            <div class="result-title">Oscilador armónico</div>
            <div class="result-content">
                <p>Simulación ejecutada con ω=${omega}, N=${n_max}, α=${alpha}, T=${t_max}</p>
            </div>
        `;
        showResult('oscillatorResult', content);
    } catch (error) {
        showResult('oscillatorResult', `Error: ${error.message}`, true);
    }
}
window.simulateHarmonicOscillator = simulateHarmonicOscillator;

// Quantum Entanglement
async function analyzeEntanglement() {
    const stateType = document.getElementById('entanglementType').value;
    showLoading('entanglementResult');
    try {
        const result = await apiRequest('/quantum-physics/entanglement-analysis', { state_type: stateType }, 'POST');
        const data = result?.data || result;
        const content = `
            <div class="result-title">Entrelazamiento cuántico</div>
            <div class="result-content">
                <p><strong>Tipo de estado:</strong> ${data.state_type || stateType}</p>
                <p><strong>Concurrencia:</strong> ${data.concurrence ?? 'N/A'}</p>
                <p><strong>Fidelidad:</strong> ${data.fidelity ?? 'N/A'}</p>
            </div>
        `;
        showResult('entanglementResult', content);
    } catch (error) {
        showResult('entanglementResult', `Error: ${error.message}`, true);
    }
}
window.analyzeEntanglement = analyzeEntanglement;

async function simulateTwoLevelSystem() {
    const omega = parseFloat(document.getElementById('twoLevelOmega').value);
    const gamma = parseFloat(document.getElementById('twoLevelGamma').value);
    const t_max = parseFloat(document.getElementById('twoLevelTmax').value);
    showLoading('twoLevelResult');
    try {
        await apiRequest('/quantum-physics/two-level-system', { omega, gamma, t_max }, 'POST');
        const content = `
            <div class="result-title">Sistema de dos niveles</div>
            <div class="result-content">
                <p>Simulación ejecutada con ω=${omega}, γ=${gamma}, T=${t_max}</p>
            </div>
        `;
        showResult('twoLevelResult', content);
    } catch (error) {
        showResult('twoLevelResult', `Error: ${error.message}`, true);
    }
}
window.simulateTwoLevelSystem = simulateTwoLevelSystem;

async function simulateQuantumOptics() {
    const n_max = parseInt(document.getElementById('opticsNmax').value);
    const kappa = parseFloat(document.getElementById('opticsKappa').value);
    const g = parseFloat(document.getElementById('opticsG').value);
    const alpha = parseFloat(document.getElementById('opticsAlpha').value);
    const t_max = parseFloat(document.getElementById('opticsTmax').value);
    showLoading('opticsResult');
    try {
        await apiRequest('/quantum-physics/quantum-optics', { n_max, kappa, g, alpha, t_max }, 'POST');
        const content = `
            <div class="result-title">Óptica cuántica</div>
            <div class="result-content">
                <p>Simulación ejecutada (n_max=${n_max}, κ=${kappa}, g=${g}, α=${alpha}, T=${t_max})</p>
            </div>
        `;
        showResult('opticsResult', content);
    } catch (error) {
        showResult('opticsResult', `Error: ${error.message}`, true);
    }
}
window.simulateQuantumOptics = simulateQuantumOptics;

// ==================== COMPUTING SECTION ====================

// Bell States
async function createBellState() {
    const framework = document.getElementById('bellFramework').value;
    showLoading('bellResult');
    try {
        const result = await apiRequest('/quantum-computing/bell-state', { framework }, 'POST');
        const data = result?.data || result;
        const probs = data.measurement_probabilities || {};
        const content = `
            <div class="result-title">Estado de Bell</div>
            <div class="result-content">
                <p><strong>Framework:</strong> ${framework}</p>
                <p><strong>Estado:</strong> ${formatQuantumState(data.bell_state || '|Φ⁺⟩')}</p>
                <p><strong>Probabilidades:</strong></p>
                <ul>
                    ${Object.entries(probs).map(([outcome, prob]) => `<li><strong>${outcome}:</strong> ${(prob * 100).toFixed(2)}%</li>`).join('')}
                </ul>
            </div>
        `;
        showResult('bellResult', content);
    } catch (error) {
        showResult('bellResult', `Error: ${error.message}`, true);
    }
}
window.createBellState = createBellState;

// Grover Search
async function runGroverSearch() {
    const target_state = document.getElementById('groverTarget').value;
    const n_qubits = parseInt(document.getElementById('groverNqubits').value);
    if (!target_state || isNaN(n_qubits)) {
        showResult('groverResult', 'Complete los parámetros', true);
        return;
    }
    showLoading('groverResult');
    try {
        const result = await apiRequest('/quantum-computing/grover-search', { n_qubits, target_state }, 'POST');
        const data = result?.data || result;
        const content = `
            <div class="result-title">Búsqueda de Grover</div>
            <div class="result-content">
                <p><strong>Qubits:</strong> ${n_qubits}</p>
                <p><strong>Objetivo:</strong> ${target_state}</p>
                <p><strong>Mensaje:</strong> ${result.message || 'OK'}</p>
            </div>
        `;
        showResult('groverResult', content);
    } catch (error) {
        showResult('groverResult', `Error: ${error.message}`, true);
    }
}
window.runGroverSearch = runGroverSearch;

// Quantum Fourier Transform
async function runQuantumFourierTransform() {
    const n_qubits = parseInt(document.getElementById('qftNqubits').value);
    if (isNaN(n_qubits) || n_qubits < 1 || n_qubits > 10) {
        showResult('qftResult', 'Por favor ingrese un número válido de qubits (1-10)', true);
        return;
    }
    showLoading('qftResult');
    try {
        const result = await apiRequest('/quantum-computing/quantum-fourier-transform', { n_qubits }, 'POST');
        const data = result?.data || result;
        const content = `
            <div class="result-title">Transformada de Fourier Cuántica</div>
            <div class="result-content">
                <p>QFT ejecutada para ${n_qubits} qubits</p>
            </div>
        `;
        showResult('qftResult', content);
    } catch (error) {
        showResult('qftResult', `Error: ${error.message}`, true);
    }
}
window.runQuantumFourierTransform = runQuantumFourierTransform;

// Variational Quantum Eigensolver
async function runVQE() {
    const n_qubits = parseInt(document.getElementById('vqeNqubits').value);
    if (isNaN(n_qubits) || n_qubits < 1 || n_qubits > 6) {
        showResult('vqeResult', 'Por favor ingrese un número de qubits válido (1-6)', true);
        return;
    }
    showLoading('vqeResult');
    try {
        const result = await apiRequest('/quantum-computing/vqe', { n_qubits }, 'POST');
        const data = result?.data || result;
        const content = `
            <div class="result-title">VQE</div>
            <div class="result-content">
                <p>VQE ejecutado para ${n_qubits} qubits.</p>
            </div>
        `;
        showResult('vqeResult', content);
    } catch (error) {
        showResult('vqeResult', `Error: ${error.message}`, true);
    }
}
window.runVQE = runVQE;

async function runQuantumClassicalComparison() {
    const problem_size = parseInt(document.getElementById('comparisonSize').value);
    if (isNaN(problem_size) || problem_size < 1 || problem_size > 20) {
        showResult('comparisonResult', 'Tamaño del problema inválido (1-20)', true);
        return;
    }
    showLoading('comparisonResult');
    try {
        const result = await apiRequest('/quantum-computing/quantum-classical-comparison', { problem_size }, 'POST');
        const data = result?.data || result;
        const content = `
            <div class="result-title">Comparación Cuántico vs Clásico</div>
            <div class="result-content">
                <p>${result.message || 'Comparación completada.'}</p>
            </div>
        `;
        showResult('comparisonResult', content);
    } catch (error) {
        showResult('comparisonResult', `Error: ${error.message}`, true);
    }
}
window.runQuantumClassicalComparison = runQuantumClassicalComparison;

// ==================== ADVANCED TOOLS SECTION ====================

// Advanced Algebra
async function solveAdvancedAlgebra() {
    const problemType = document.getElementById('advancedAlgebraType').value;
    const expression = document.getElementById('advancedAlgebraExpression').value;

    if (!expression.trim()) {
        showResult('advancedAlgebraResult', 'Por favor ingrese una expresión', true);
        return;
    }

    showLoading('advancedAlgebraResult');

    try {
        const result = await apiRequest('/advanced-algebra/solve', {
            problem_type: problemType,
            expression: expression
        }, 'POST');

        let content = `
            <div class="result-title">Álgebra avanzada</div>
            <div class="result-content">
                <p><strong>Tipo de problema:</strong> ${result.problem_type}</p>
                <p><strong>Expresión:</strong> ${formatMathExpression(result.expression)}</p>
        `;

        if (result.solution) {
            content += `<p><strong>Solución:</strong> ${formatMathExpression(result.solution)}</p>`;
        }

        if (result.steps && result.steps.length > 0) {
            content += `<h6>Pasos de resolución:</h6><ol class="result-steps">`;
            result.steps.forEach(step => {
                content += `<li>${step}</li>`;
            });
            content += `</ol>`;
        }

        content += `</div>`;
        showResult('advancedAlgebraResult', content);
    } catch (error) {
        showResult('advancedAlgebraResult', `Error: ${error.message}`, true);
    }
}
window.solveAdvancedAlgebra = solveAdvancedAlgebra;

// Differential Equations
async function solveDifferentialEquation() {
    const equation = document.getElementById('diffEquation').value;
    const method = document.getElementById('diffMethod').value;
    const initialConditions = document.getElementById('initialConditions').value;

    if (!equation.trim()) {
        showResult('diffEquationResult', 'Por favor ingrese una ecuación diferencial', true);
        return;
    }

    showLoading('diffEquationResult');

    try {
        const result = await apiRequest('/differential-equations/solve', {
            equation: equation,
            method: method,
            initial_conditions: initialConditions || null
        }, 'POST');

        let content = `
            <div class="result-title">Ecuación diferencial</div>
            <div class="result-content">
                <p><strong>Ecuación:</strong> ${formatMathExpression(result.equation)}</p>
                <p><strong>Método:</strong> ${result.method}</p>
        `;

        if (result.solution) {
            content += `<p><strong>Solución general:</strong> ${formatMathExpression(result.solution)}</p>`;
        }

        if (result.particular_solution) {
            content += `<p><strong>Solución particular:</strong> ${formatMathExpression(result.particular_solution)}</p>`;
        }

        if (result.steps && result.steps.length > 0) {
            content += `<h6>Pasos de resolución:</h6><ol class="result-steps">`;
            result.steps.forEach(step => {
                content += `<li>${step}</li>`;
            });
            content += `</ol>`;
        }

        content += `</div>`;
        showResult('diffEquationResult', content);
    } catch (error) {
        showResult('diffEquationResult', `Error: ${error.message}`, true);
    }
}
window.solveDifferentialEquation = solveDifferentialEquation;

// Optimization
async function runOptimization() {
    const objective = document.getElementById('optimizationObjective').value;
    const constraints = document.getElementById('optimizationConstraints').value;
    const method = document.getElementById('optimizationMethod').value;

    if (!objective.trim()) {
        showResult('optimizationResult', 'Por favor ingrese una función objetivo', true);
        return;
    }

    showLoading('optimizationResult');

    try {
        const result = await apiRequest('/optimization/solve', {
            objective: objective,
            constraints: constraints || null,
            method: method
        }, 'POST');

        let content = `
            <div class="result-title">Optimización</div>
            <div class="result-content">
                <p><strong>Función objetivo:</strong> ${formatMathExpression(result.objective)}</p>
                <p><strong>Método:</strong> ${result.method}</p>
        `;

        if (result.optimal_value !== undefined) {
            content += `<p><strong>Valor óptimo:</strong> ${result.optimal_value.toFixed(6)}</p>`;
        }

        if (result.optimal_point) {
            content += `<p><strong>Punto óptimo:</strong> [${result.optimal_point.join(', ')}]</p>`;
        }

        if (result.constraints_satisfied !== undefined) {
            content += `<p><strong>Restricciones satisfechas:</strong> ${result.constraints_satisfied ? 'Sí' : 'No'}</p>`;
        }

        content += `</div>`;
        showResult('optimizationResult', content);
    } catch (error) {
        showResult('optimizationResult', `Error: ${error.message}`, true);
    }
}
window.runOptimization = runOptimization;

// ==================== EVENT LISTENERS ====================

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Enter key handlers for all input fields
    const inputFields = [
        'arithmeticOperands', 'equation', 'calculusExpression', 'statisticsData', 'graphExpression',
        'moleculeFormula', 'conformerMolecule', 'sequenceInput', 'quantumMolecule',
        'spinValue', 'evolutionTime', 'fieldStrength', 'oscillatorMass', 'oscillatorFrequency',
        'oscillatorAmplitude', 'oscillatorTime', 'entanglementParticles',
        'groverSearchSpace', 'groverTargetItem', 'qftQubits', 'vqeMolecule',
        'advancedAlgebraExpression', 'diffEquation', 'initialConditions', 'optimizationObjective', 'optimizationConstraints'
    ];

    inputFields.forEach(fieldId => {
        const element = document.getElementById(fieldId);
        if (element) {
            element.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    // Find the corresponding button and click it
                    const buttonId = fieldId.replace(/Input|Expression|Data|Formula|Molecule|Value|Time|Strength|Mass|Frequency|Amplitude|Particles|SearchSpace|TargetItem|Qubits|Objective|Constraints|Equation/g, '') + 'Btn';
                    const button = document.getElementById(buttonId);
                    if (button) {
                        button.click();
                    }
                }
            });
        }
    });

    // Load examples on page load (legacy helper)
    loadExamples();
    // Load dynamic explorer for Axiom modules
    loadAxiomModulesExplorer();
});

// Load examples for each section
async function loadExamples() {
    try {
        // Load examples for different modules
        const modules = [
            'arithmetic', 'equations', 'calculus', 'statistics', 'graphing',
            'chemistry', 'quantum-physics', 'quantum-computing', 'advanced-algebra',
            'differential-equations', 'optimization'
        ];

        for (const module of modules) {
            try {
                const examples = await apiRequest(`/${module}/examples`);
                console.log(`${module} examples loaded:`, examples);
            } catch (error) {
                console.log(`No examples available for ${module}:`, error.message);
            }
        }
    } catch (error) {
        console.error('Error loading examples:', error);
    }
}
window.loadExamples = loadExamples;

// Error handling
// window.addEventListener('error', function(e) {
//     console.error('JavaScript Error:', e.error);
// });

// ==================== UI HELPERS & SYSTEM TOOLS ====================

function scrollToSection(sectionId) {
    const target = document.getElementById(sectionId);
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
window.scrollToSection = scrollToSection;

function showAbout() {
    const el = document.getElementById('aboutModal');
    if (!el) return;
    const modal = bootstrap.Modal.getOrCreateInstance(el);
    modal.show();
}
window.showAbout = showAbout;

function showHelp() {
    alert('Explora las secciones, llena los parámetros y presiona los botones para ejecutar demos. También puedes usar la sección "Módulos de Axiom" para probar demos rápidas.');
}
window.showHelp = showHelp;

function showDemo() {
    // Abre el modal de módulos como demo general
    const section = document.getElementById('axiom-modules');
    if (section) section.scrollIntoView({ behavior: 'smooth' });
    // Abrimos la primera demo tras un pequeño retraso
    setTimeout(() => {
        const firstBtn = document.querySelector('#axiomModulesContainer button.btn-primary');
        if (firstBtn) firstBtn.click();
    }, 600);
}
window.showDemo = showDemo;

async function getSystemInfo() {
    showLoading('systemInfoResult');
    try {
        const result = await apiRequest('/stats');
        const safe = escapeHtml(JSON.stringify(result, null, 2));
        showResult('systemInfoResult', `<pre class="small bg-light p-2 rounded" style="max-height: 360px; overflow: auto;">${safe}</pre>`);
    } catch (e) {
        showResult('systemInfoResult', `Error al obtener info del sistema: ${e.message}`, true);
    }
}
window.getSystemInfo = getSystemInfo;

async function checkAPIHealth() {
    showLoading('apiHealthResult');
    try {
        const result = await apiRequest('/health');
        const safe = escapeHtml(JSON.stringify(result, null, 2));
        showResult('apiHealthResult', `<pre class="small bg-light p-2 rounded" style="max-height: 360px; overflow: auto;">${safe}</pre>`);
    } catch (e) {
        showResult('apiHealthResult', `Error al verificar salud: ${e.message}`, true);
    }
}
window.checkAPIHealth = checkAPIHealth;

// ==================== FUNCIONES DE ESCALABILIDAD ====================

async function testLoadBalancer() {
    showLoading('loadBalancerResult');
    try {
        const strategy = document.getElementById('lbStrategy').value;
        const clientIP = document.getElementById('clientIP').value;

        // Cambiar estrategia primero
        await apiRequest('/scalability/load-balancer/strategy', { strategy }, 'POST');

        // Probar load balancer
        const result = await apiRequest('/scalability/load-balancer/test', { client_ip: clientIP }, 'POST');

        let html = `<div class="alert alert-success"><strong>Load Balancer Test</strong></div>`;
        html += `<p><strong>Estrategia:</strong> ${strategy}</p>`;
        html += `<p><strong>Cliente IP:</strong> ${clientIP}</p>`;

        if (result.selected_instance) {
            html += `<p><strong>Instancia Seleccionada:</strong> ${result.selected_instance.id}</p>`;
            html += `<p><strong>URL:</strong> ${result.selected_instance.url}</p>`;
            html += `<p><strong>Estado:</strong> ${result.selected_instance.status}</p>`;
            html += `<p><strong>Conexiones:</strong> ${result.selected_instance.connections}</p>`;
        } else {
            html += `<p class="text-warning">${result.message || 'No hay instancias disponibles'}</p>`;
        }

        showResult('loadBalancerResult', html);
    } catch (e) {
        showResult('loadBalancerResult', `Error en load balancer: ${e.message}`, true);
    }
}
window.testLoadBalancer = testLoadBalancer;

async function registerInstance() {
    showLoading('serviceDiscoveryResult');
    try {
        const instanceId = document.getElementById('instanceId').value;
        const host = document.getElementById('instanceHost').value;
        const port = parseInt(document.getElementById('instancePort').value);

        const result = await apiRequest('/scalability/instances/register', {
            instance_id: instanceId,
            host: host,
            port: port,
            weight: 1
        }, 'POST');

        showResult('serviceDiscoveryResult',
            `<div class="alert alert-success">✅ Instancia ${instanceId} registrada exitosamente</div>
             <p><strong>URL:</strong> http://${host}:${port}</p>`);
    } catch (e) {
        showResult('serviceDiscoveryResult', `Error al registrar instancia: ${e.message}`, true);
    }
}
window.registerInstance = registerInstance;

async function getScalabilityStatus() {
    showLoading('healthCheckResult');
    try {
        const result = await apiRequest('/scalability/status');
        const safe = escapeHtml(JSON.stringify(result, null, 2));
        showResult('healthCheckResult', `<pre class="small bg-light p-2 rounded" style="max-height: 360px; overflow: auto;">${safe}</pre>`);
    } catch (e) {
        showResult('healthCheckResult', `Error al obtener estado: ${e.message}`, true);
    }
}
window.getScalabilityStatus = getScalabilityStatus;

async function getLoadBalancerStats() {
    showLoading('healthCheckResult');
    try {
        const result = await apiRequest('/scalability/load-balancer/stats');
        const safe = escapeHtml(JSON.stringify(result, null, 2));
        showResult('healthCheckResult', `<pre class="small bg-light p-2 rounded" style="max-height: 360px; overflow: auto;">${safe}</pre>`);
    } catch (e) {
        showResult('healthCheckResult', `Error al obtener estadísticas: ${e.message}`, true);
    }
}
window.getLoadBalancerStats = getLoadBalancerStats;

async function listInstances() {
    showLoading('healthCheckResult');
    try {
        const result = await apiRequest('/scalability/instances');
        let html = `<div class="alert alert-info"><strong>Instancias Registradas: ${result.total_instances}</strong></div>`;

        if (result.instances && result.instances.length > 0) {
            html += '<div class="table-responsive"><table class="table table-sm">';
            html += '<thead><tr><th>ID</th><th>URL</th><th>Estado</th><th>Peso</th><th>Conexiones</th></tr></thead><tbody>';

            result.instances.forEach(instance => {
                const statusClass = instance.status === 'healthy' ? 'success' : 'danger';
                html += `<tr>
                    <td>${instance.id}</td>
                    <td>${instance.url}</td>
                    <td><span class="badge bg-${statusClass}">${instance.status}</span></td>
                    <td>${instance.weight}</td>
                    <td>${instance.connections}</td>
                </tr>`;
            });

            html += '</tbody></table></div>';
        } else {
            html += '<p class="text-muted">No hay instancias registradas</p>';
        }

        showResult('healthCheckResult', html);
    } catch (e) {
        showResult('healthCheckResult', `Error al listar instancias: ${e.message}`, true);
    }
}
window.listInstances = listInstances;

async function startWorkers() {
    showLoading('workerResult');
    try {
        const count = parseInt(document.getElementById('workerCount').value);
        await apiRequest('/scalability/workers/start', { count }, 'POST');

        showResult('workerResult',
            `<div class="alert alert-success">✅ ${count} workers iniciados exitosamente</div>`);
    } catch (e) {
        showResult('workerResult', `Error al iniciar workers: ${e.message}`, true);
    }
}
window.startWorkers = startWorkers;

async function getWorkerStats() {
    showLoading('workerResult');
    try {
        const result = await apiRequest('/scalability/workers/stats');
        const safe = escapeHtml(JSON.stringify(result, null, 2));
        showResult('workerResult', `<pre class="small bg-light p-2 rounded" style="max-height: 360px; overflow: auto;">${safe}</pre>`);
    } catch (e) {
        showResult('workerResult', `Error al obtener estadísticas: ${e.message}`, true);
    }
}
window.getWorkerStats = getWorkerStats;

// ==================== FUNCIONES DE DASHBOARDS ====================

async function getSystemHealth() {
    showLoading('systemDashboardResult');
    try {
        const result = await apiRequest('/health');
        let html = `<div class="alert alert-success"><strong>✅ Sistema Saludable</strong></div>`;

        if (result.components) {
            html += '<div class="row g-3 mt-2">';
            Object.entries(result.components).forEach(([component, status]) => {
                const statusClass = status === 'active' || status === 'healthy' ? 'success' : 'warning';
                html += `<div class="col-md-6">
                    <div class="card border-${statusClass}">
                        <div class="card-body p-2">
                            <small class="text-muted">${component.toUpperCase()}</small><br>
                            <span class="badge bg-${statusClass}">${status}</span>
                        </div>
                    </div>
                </div>`;
            });
            html += '</div>';
        }

        showResult('systemDashboardResult', html);
    } catch (e) {
        showResult('systemDashboardResult', `Error al obtener salud del sistema: ${e.message}`, true);
    }
}
window.getSystemHealth = getSystemHealth;

async function getSystemMetrics() {
    showLoading('systemDashboardResult');
    try {
        const result = await apiRequest('/metrics');
        const safe = escapeHtml(JSON.stringify(result, null, 2));
        showResult('systemDashboardResult', `<pre class="small bg-light p-2 rounded" style="max-height: 360px; overflow: auto;">${safe}</pre>`);
    } catch (e) {
        showResult('systemDashboardResult', `Error al obtener métricas: ${e.message}`, true);
    }
}
window.getSystemMetrics = getSystemMetrics;

async function getOptimizationStats() {
    showLoading('systemDashboardResult');
    try {
        const result = await apiRequest('/optimization/stats');
        const safe = escapeHtml(JSON.stringify(result, null, 2));
        showResult('systemDashboardResult', `<pre class="small bg-light p-2 rounded" style="max-height: 360px; overflow: auto;">${safe}</pre>`);
    } catch (e) {
        showResult('systemDashboardResult', `Error al obtener estadísticas de optimización: ${e.message}`, true);
    }
}
window.getOptimizationStats = getOptimizationStats;

async function getPerformanceStats() {
    showLoading('performanceDashboardResult');
    try {
        const result = await apiRequest('/profiling/stats');
        const safe = escapeHtml(JSON.stringify(result, null, 2));
        showResult('performanceDashboardResult', `<pre class="small bg-light p-2 rounded" style="max-height: 360px; overflow: auto;">${safe}</pre>`);
    } catch (e) {
        showResult('performanceDashboardResult', `Error al obtener estadísticas de rendimiento: ${e.message}`, true);
    }
}
window.getPerformanceStats = getPerformanceStats;

async function getGPUStats() {
    showLoading('performanceDashboardResult');
    try {
        const result = await apiRequest('/gpu/status');
        const safe = escapeHtml(JSON.stringify(result, null, 2));
        showResult('performanceDashboardResult', `<pre class="small bg-light p-2 rounded" style="max-height: 360px; overflow: auto;">${safe}</pre>`);
    } catch (e) {
        showResult('performanceDashboardResult', `Error al obtener estadísticas GPU: ${e.message}`, true);
    }
}
window.getGPUStats = getGPUStats;

async function getCacheStats() {
    showLoading('performanceDashboardResult');
    try {
        const result = await apiRequest('/cache/stats');
        const safe = escapeHtml(JSON.stringify(result, null, 2));
        showResult('performanceDashboardResult', `<pre class="small bg-light p-2 rounded" style="max-height: 360px; overflow: auto;">${safe}</pre>`);
    } catch (e) {
        showResult('performanceDashboardResult', `Error al obtener estadísticas de caché: ${e.message}`, true);
    }
}
window.getCacheStats = getCacheStats;

async function getScalabilityDashboard() {
    showLoading('scalabilityDashboardResult');
    try {
        const result = await apiRequest('/scalability/status');
        let html = `<div class="alert alert-info"><strong>Dashboard de Escalabilidad</strong></div>`;

        if (result.load_balancer) {
            html += `<div class="row g-3">
                <div class="col-md-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3 class="text-primary">${result.load_balancer.total_instances || 0}</h3>
                            <small class="text-muted">Instancias Totales</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3 class="text-success">${result.load_balancer.healthy_instances || 0}</h3>
                            <small class="text-muted">Instancias Saludables</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h3 class="text-info">${result.load_balancer.strategy || 'N/A'}</h3>
                            <small class="text-muted">Estrategia</small>
                        </div>
                    </div>
                </div>
            </div>`;
        }

        showResult('scalabilityDashboardResult', html);
    } catch (e) {
        showResult('scalabilityDashboardResult', `Error al obtener dashboard de escalabilidad: ${e.message}`, true);
    }
}
window.getScalabilityDashboard = getScalabilityDashboard;

async function getLoadBalancerDashboard() {
    showLoading('scalabilityDashboardResult');
    try {
        const result = await apiRequest('/scalability/load-balancer/stats');
        const safe = escapeHtml(JSON.stringify(result, null, 2));
        showResult('scalabilityDashboardResult', `<pre class="small bg-light p-2 rounded" style="max-height: 360px; overflow: auto;">${safe}</pre>`);
    } catch (e) {
        showResult('scalabilityDashboardResult', `Error al obtener dashboard load balancer: ${e.message}`, true);
    }
}
window.getLoadBalancerDashboard = getLoadBalancerDashboard;

async function getWorkerDashboard() {
    showLoading('scalabilityDashboardResult');
    try {
        const result = await apiRequest('/scalability/workers/stats');
        const safe = escapeHtml(JSON.stringify(result, null, 2));
        showResult('scalabilityDashboardResult', `<pre class="small bg-light p-2 rounded" style="max-height: 360px; overflow: auto;">${safe}</pre>`);
    } catch (e) {
        showResult('scalabilityDashboardResult', `Error al obtener dashboard workers: ${e.message}`, true);
    }
}
window.getWorkerDashboard = getWorkerDashboard;

async function getScientificServicesStatus() {
    showLoading('scientificDashboardResult');
    try {
        // Intentar obtener estado de servicios científicos
        const services = ['dnabert2', 'gnome-materials', 'alphafold3', 'protgpt2'];
        let html = `<div class="alert alert-info"><strong>Estado de Servicios Científicos</strong></div>`;

        for (const service of services) {
            try {
                const result = await apiRequest(`/${service}/status`);
                html += `<div class="mb-2">
                    <strong>${service.toUpperCase()}:</strong>
                    <span class="badge bg-success">Activo</span>
                </div>`;
            } catch (e) {
                html += `<div class="mb-2">
                    <strong>${service.toUpperCase()}:</strong>
                    <span class="badge bg-warning">No disponible</span>
                </div>`;
            }
        }

        showResult('scientificDashboardResult', html);
    } catch (e) {
        showResult('scientificDashboardResult', `Error al obtener estado de servicios: ${e.message}`, true);
    }
}
window.getScientificServicesStatus = getScientificServicesStatus;

async function getDNABERT2Status() {
    showLoading('scientificDashboardResult');
    try {
        const result = await apiRequest('/dnabert2/status');
        const safe = escapeHtml(JSON.stringify(result, null, 2));
        showResult('scientificDashboardResult', `<pre class="small bg-light p-2 rounded" style="max-height: 360px; overflow: auto;">${safe}</pre>`);
    } catch (e) {
        showResult('scientificDashboardResult', `Error al obtener estado DNABERT2: ${e.message}`, true);
    }
}
window.getDNABERT2Status = getDNABERT2Status;

async function getGNOMEMaterialsStatus() {
    showLoading('scientificDashboardResult');
    try {
        const result = await apiRequest('/gnome-materials/status');
        const safe = escapeHtml(JSON.stringify(result, null, 2));
        showResult('scientificDashboardResult', `<pre class="small bg-light p-2 rounded" style="max-height: 360px; overflow: auto;">${safe}</pre>`);
    } catch (e) {
        showResult('scientificDashboardResult', `Error al obtener estado GNOME Materials: ${e.message}`, true);
    }
}
window.getGNOMEMaterialsStatus = getGNOMEMaterialsStatus;

// ==================== FUNCIONES DEL ORQUESTADOR ====================

async function executeWorkflow() {
    showLoading('workflowResult');
    try {
        const workflowType = document.getElementById('workflowType').value;
        const result = await apiRequest('/api/workflow-orchestration/execute', {
            workflow_type: workflowType,
            parameters: {}
        }, 'POST');

        let html = `<div class="alert alert-success"><strong>Workflow Ejecutado</strong></div>`;
        html += `<p><strong>Tipo:</strong> ${workflowType}</p>`;
        html += `<p><strong>Estado:</strong> ${result.status || 'Completado'}</p>`;

        if (result.results) {
            html += `<div class="mt-3"><strong>Resultados:</strong></div>`;
            html += `<pre class="small bg-light p-2 rounded">${escapeHtml(JSON.stringify(result.results, null, 2))}</pre>`;
        }

        showResult('workflowResult', html);
    } catch (e) {
        showResult('workflowResult', `Error al ejecutar workflow: ${e.message}`, true);
    }
}
window.executeWorkflow = executeWorkflow;

async function startExperiment() {
    showLoading('experimentResult');
    try {
        const experimentName = document.getElementById('experimentName').value;
        const result = await apiRequest('/api/experiment-tracking/start', {
            name: experimentName,
            parameters: {}
        }, 'POST');

        showResult('experimentResult',
            `<div class="alert alert-success">✅ Experimento "${experimentName}" iniciado</div>
             <p><strong>ID:</strong> ${result.experiment_id || 'N/A'}</p>`);
    } catch (e) {
        showResult('experimentResult', `Error al iniciar experimento: ${e.message}`, true);
    }
}
window.startExperiment = startExperiment;

async function listExperiments() {
    showLoading('experimentResult');
    try {
        const result = await apiRequest('/api/experiment-tracking/list');
        let html = `<div class="alert alert-info"><strong>Experimentos Registrados</strong></div>`;

        if (result.experiments && result.experiments.length > 0) {
            html += '<div class="table-responsive"><table class="table table-sm">';
            html += '<thead><tr><th>Nombre</th><th>ID</th><th>Estado</th><th>Fecha</th></tr></thead><tbody>';

            result.experiments.forEach(exp => {
                html += `<tr>
                    <td>${exp.name}</td>
                    <td>${exp.id}</td>
                    <td><span class="badge bg-primary">${exp.status || 'Activo'}</span></td>
                    <td>${exp.created_at || 'N/A'}</td>
                </tr>`;
            });

            html += '</tbody></table></div>';
        } else {
            html += '<p class="text-muted">No hay experimentos registrados</p>';
        }

        showResult('experimentResult', html);
    } catch (e) {
        showResult('experimentResult', `Error al listar experimentos: ${e.message}`, true);
    }
}
window.listExperiments = listExperiments;

async function versionData() {
    showLoading('versioningResult');
    try {
        const datasetName = document.getElementById('datasetName').value;
        const version = document.getElementById('datasetVersion').value;

        const result = await apiRequest('/api/data-versioning/version', {
            dataset_name: datasetName,
            version: version,
            metadata: {}
        }, 'POST');

        showResult('versioningResult',
            `<div class="alert alert-success">✅ Dataset "${datasetName}" versionado</div>
             <p><strong>Versión:</strong> ${version}</p>
             <p><strong>Hash:</strong> ${result.version_hash || 'N/A'}</p>`);
    } catch (e) {
        showResult('versioningResult', `Error al versionar datos: ${e.message}`, true);
    }
}
window.versionData = versionData;

async function executeResearchCycle() {
    showLoading('researchResult');
    try {
        const researchType = document.getElementById('researchType').value;
        const result = await apiRequest('/api/research-cycle/execute', {
            research_type: researchType,
            parameters: {}
        }, 'POST');

        let html = `<div class="alert alert-success"><strong>Ciclo de Investigación Ejecutado</strong></div>`;
        html += `<p><strong>Tipo:</strong> ${researchType}</p>`;
        html += `<p><strong>Estado:</strong> ${result.status || 'Completado'}</p>`;

        if (result.outputs) {
            html += `<div class="mt-3"><strong>Resultados:</strong></div>`;
            html += `<pre class="small bg-light p-2 rounded">${escapeHtml(JSON.stringify(result.outputs, null, 2))}</pre>`;
        }

        showResult('researchResult', html);
    } catch (e) {
        showResult('researchResult', `Error al ejecutar ciclo de investigación: ${e.message}`, true);
    }
}
window.executeResearchCycle = executeResearchCycle;

// ==================== FUNCIONES DE MONITOREO AVANZADO ====================

async function getMonitoringStatus() {
    showLoading('systemStatusResult');
    try {
        const result = await apiRequest('/monitoring/status');
        let html = `<div class="alert alert-info"><strong>Estado del Sistema de Monitoreo</strong></div>`;

        html += `<div class="row g-3 mb-3">
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h4 class="text-${result.status === 'running' ? 'success' : 'warning'}">
                            ${result.status === 'running' ? '🟢' : '🟡'}
                        </h4>
                        <small class="text-muted">Estado</small>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h4 class="text-primary">${result.alerts.active_count}</h4>
                        <small class="text-muted">Alertas Activas</small>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h4 class="text-info">${result.metrics_history.total_metrics}</h4>
                        <small class="text-muted">Métricas Totales</small>
                    </div>
                </div>
            </div>
        </div>`;

        if (result.alerts.active_alerts && result.alerts.active_alerts.length > 0) {
            html += '<div class="mt-3"><h6>Alertas Activas:</h6><div class="table-responsive"><table class="table table-sm">';
            html += '<thead><tr><th>Regla</th><th>Descripción</th><th>Severidad</th><th>Valor</th></tr></thead><tbody>';

            result.alerts.active_alerts.forEach(alert => {
                const severityClass = {
                    'low': 'secondary',
                    'medium': 'warning',
                    'high': 'danger',
                    'critical': 'danger'
                }[alert.severity] || 'secondary';

                html += `<tr>
                    <td>${alert.rule_name}</td>
                    <td>${alert.description}</td>
                    <td><span class="badge bg-${severityClass}">${alert.severity.toUpperCase()}</span></td>
                    <td>${alert.value}</td>
                </tr>`;
            });

            html += '</tbody></table></div></div>';
        }

        showResult('systemStatusResult', html);
    } catch (e) {
        showResult('systemStatusResult', `Error al obtener estado del monitoreo: ${e.message}`, true);
    }
}
window.getMonitoringStatus = getMonitoringStatus;

async function getCurrentMetrics() {
    showLoading('systemStatusResult');
    try {
        const result = await apiRequest('/monitoring/metrics/current');
        let html = `<div class="alert alert-success"><strong>Métricas Actuales del Sistema</strong></div>`;

        // Sistema
        if (result.system) {
            html += `<div class="mb-3">
                <h6>📊 Sistema:</h6>
                <div class="row g-2">
                    <div class="col-md-3"><div class="card p-2 text-center"><small class="text-muted">CPU</small><br><strong>${result.system.cpu_percent}%</strong></div></div>
                    <div class="col-md-3"><div class="card p-2 text-center"><small class="text-muted">Memoria</small><br><strong>${result.system.memory_percent}%</strong></div></div>
                    <div class="col-md-3"><div class="card p-2 text-center"><small class="text-muted">Disco</small><br><strong>${result.system.disk_percent}%</strong></div></div>
                    <div class="col-md-3"><div class="card p-2 text-center"><small class="text-muted">Load Avg</small><br><strong>${result.system.load_average[0].toFixed(2)}</strong></div></div>
                </div>
            </div>`;
        }

        // Aplicación
        if (result.application) {
            html += `<div class="mb-3">
                <h6>🚀 Aplicación:</h6>
                <div class="row g-2">
                    <div class="col-md-3"><div class="card p-2 text-center"><small class="text-muted">Conexiones</small><br><strong>${result.application.active_connections}</strong></div></div>
                    <div class="col-md-3"><div class="card p-2 text-center"><small class="text-muted">Requests</small><br><strong>${result.application.total_requests}</strong></div></div>
                    <div class="col-md-3"><div class="card p-2 text-center"><small class="text-muted">Error Rate</small><br><strong>${result.application.error_rate}%</strong></div></div>
                    <div class="col-md-3"><div class="card p-2 text-center"><small class="text-muted">Response Time</small><br><strong>${result.application.avg_response_time}ms</strong></div></div>
                </div>
            </div>`;
        }

        showResult('systemStatusResult', html);
    } catch (e) {
        showResult('systemStatusResult', `Error al obtener métricas actuales: ${e.message}`, true);
    }
}
window.getCurrentMetrics = getCurrentMetrics;

async function getMonitoringDashboard() {
    showLoading('systemStatusResult');
    try {
        const result = await apiRequest('/monitoring/dashboard');
        let html = `<div class="alert alert-primary"><strong>Dashboard Completo de Monitoreo</strong></div>`;

        // Métricas actuales
        if (result.current) {
            html += `<div class="mb-4">
                <h6>📈 Métricas Actuales:</h6>
                <div class="row g-3">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">Sistema</div>
                            <div class="card-body">
                                <p><strong>CPU:</strong> ${result.current.system.cpu_percent}%</p>
                                <p><strong>Memoria:</strong> ${result.current.system.memory_used_gb}GB / ${result.current.system.memory_total_gb}GB</p>
                                <p><strong>Disco:</strong> ${result.current.system.disk_used_gb}GB / ${result.current.system.disk_total_gb}GB</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">Aplicación</div>
                            <div class="card-body">
                                <p><strong>Conexiones Activas:</strong> ${result.current.application.active_connections}</p>
                                <p><strong>Tasa de Error:</strong> ${result.current.application.error_rate}%</p>
                                <p><strong>Tiempo de Respuesta:</strong> ${result.current.application.avg_response_time}ms</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;
        }

        // Alertas
        if (result.alerts && result.alerts.active_alerts && result.alerts.active_alerts.length > 0) {
            html += `<div class="mb-4">
                <h6>🚨 Alertas Activas:</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead><tr><th>Regla</th><th>Descripción</th><th>Severidad</th><th>Valor</th></tr></thead>
                        <tbody>`;

            result.alerts.active_alerts.forEach(alert => {
                const severityClass = {
                    'low': 'secondary',
                    'medium': 'warning',
                    'high': 'danger',
                    'critical': 'danger'
                }[alert.severity] || 'secondary';

                html += `<tr>
                    <td>${alert.rule_name}</td>
                    <td>${alert.description}</td>
                    <td><span class="badge bg-${severityClass}">${alert.severity.toUpperCase()}</span></td>
                    <td>${alert.value}</td>
                </tr>`;
            });

            html += `</tbody></table></div></div>`;
        }

        showResult('systemStatusResult', html);
    } catch (e) {
        showResult('systemStatusResult', `Error al obtener dashboard: ${e.message}`, true);
    }
}
window.getMonitoringDashboard = getMonitoringDashboard;

async function getActiveAlerts() {
    showLoading('alertsResult');
    try {
        const result = await apiRequest('/monitoring/alerts/active');
        let html = `<div class="alert alert-warning"><strong>Alertas Activas (${result.count})</strong></div>`;

        if (result.alerts && result.alerts.length > 0) {
            html += '<div class="table-responsive"><table class="table table-sm">';
            html += '<thead><tr><th>ID</th><th>Regla</th><th>Descripción</th><th>Severidad</th><th>Valor</th><th>Umbral</th><th>Creada</th></tr></thead><tbody>';

            result.alerts.forEach(alert => {
                const severityClass = {
                    'low': 'secondary',
                    'medium': 'warning',
                    'high': 'danger',
                    'critical': 'danger'
                }[alert.severity] || 'secondary';

                const created = new Date(alert.created_at).toLocaleString();
                html += `<tr>
                    <td>${alert.id}</td>
                    <td>${alert.rule_name}</td>
                    <td>${alert.description}</td>
                    <td><span class="badge bg-${severityClass}">${alert.severity.toUpperCase()}</span></td>
                    <td>${alert.value}</td>
                    <td>${alert.threshold}</td>
                    <td><small>${created}</small></td>
                </tr>`;
            });

            html += '</tbody></table></div>';
        } else {
            html += '<p class="text-muted">No hay alertas activas</p>';
        }

        showResult('alertsResult', html);
    } catch (e) {
        showResult('alertsResult', `Error al obtener alertas activas: ${e.message}`, true);
    }
}
window.getActiveAlerts = getActiveAlerts;

async function getAlertsHistory() {
    showLoading('alertsResult');
    try {
        const result = await apiRequest('/monitoring/alerts/history');
        let html = `<div class="alert alert-info"><strong>Historial de Alertas (${result.count})</strong></div>`;

        if (result.alerts && result.alerts.length > 0) {
            html += '<div class="table-responsive"><table class="table table-sm">';
            html += '<thead><tr><th>Regla</th><th>Descripción</th><th>Severidad</th><th>Estado</th><th>Creada</th><th>Resuelta</th></tr></thead><tbody>';

            result.alerts.forEach(alert => {
                const severityClass = {
                    'low': 'secondary',
                    'medium': 'warning',
                    'high': 'danger',
                    'critical': 'danger'
                }[alert.severity] || 'secondary';

                const statusClass = {
                    'active': 'danger',
                    'resolved': 'success',
                    'acknowledged': 'info'
                }[alert.status] || 'secondary';

                const created = new Date(alert.created_at).toLocaleString();
                const resolved = alert.resolved_at ? new Date(alert.resolved_at).toLocaleString() : '-';

                html += `<tr>
                    <td>${alert.rule_name}</td>
                    <td>${alert.description}</td>
                    <td><span class="badge bg-${severityClass}">${alert.severity.toUpperCase()}</span></td>
                    <td><span class="badge bg-${statusClass}">${alert.status.toUpperCase()}</span></td>
                    <td><small>${created}</small></td>
                    <td><small>${resolved}</small></td>
                </tr>`;
            });

            html += '</tbody></table></div>';
        } else {
            html += '<p class="text-muted">No hay alertas en el historial</p>';
        }

        showResult('alertsResult', html);
    } catch (e) {
        showResult('alertsResult', `Error al obtener historial de alertas: ${e.message}`, true);
    }
}
window.getAlertsHistory = getAlertsHistory;

async function getAlertRules() {
    showLoading('alertsResult');
    try {
        const result = await apiRequest('/monitoring/alerts/rules');
        let html = `<div class="alert alert-secondary"><strong>Reglas de Alertas (${result.count})</strong></div>`;

        if (result.rules && result.rules.length > 0) {
            html += '<div class="table-responsive"><table class="table table-sm">';
            html += '<thead><tr><th>Nombre</th><th>Descripción</th><th>Métrica</th><th>Condición</th><th>Umbral</th><th>Severidad</th><th>Estado</th></tr></thead><tbody>';

            result.rules.forEach(rule => {
                const severityClass = {
                    'low': 'secondary',
                    'medium': 'warning',
                    'high': 'danger',
                    'critical': 'danger'
                }[rule.severity] || 'secondary';

                html += `<tr>
                    <td>${rule.name}</td>
                    <td>${rule.description}</td>
                    <td>${rule.metric_name}</td>
                    <td>${rule.condition}</td>
                    <td>${rule.threshold}</td>
                    <td><span class="badge bg-${severityClass}">${rule.severity.toUpperCase()}</span></td>
                    <td><span class="badge bg-${rule.enabled ? 'success' : 'secondary'}">${rule.enabled ? 'Activa' : 'Inactiva'}</span></td>
                </tr>`;
            });

            html += '</tbody></table></div>';
        } else {
            html += '<p class="text-muted">No hay reglas de alertas configuradas</p>';
        }

        showResult('alertsResult', html);
    } catch (e) {
        showResult('alertsResult', `Error al obtener reglas de alertas: ${e.message}`, true);
    }
}
window.getAlertRules = getAlertRules;

async function acknowledgeAlert() {
    const alertId = document.getElementById('alertId').value;
    const user = document.getElementById('ackUser').value;

    if (!alertId.trim()) {
        showResult('alertManagementResult', 'Por favor ingrese el ID de la alerta', true);
        return;
    }

    showLoading('alertManagementResult');
    try {
        const result = await apiRequest('/monitoring/alerts/' + alertId + '/acknowledge', { user }, 'POST');
        showResult('alertManagementResult',
            `<div class="alert alert-success">✅ Alerta ${alertId} reconocida por ${user}</div>`);
    } catch (e) {
        showResult('alertManagementResult', `Error al reconocer alerta: ${e.message}`, true);
    }
}
window.acknowledgeAlert = acknowledgeAlert;

async function getMetricsHistory() {
    const metricName = document.getElementById('metricName').value;
    const hours = parseInt(document.getElementById('metricHours').value);

    if (!metricName) {
        showResult('metricsHistoryResult', 'Por favor seleccione una métrica', true);
        return;
    }

    showLoading('metricsHistoryResult');
    try {
        const result = await apiRequest('/monitoring/metrics/history/' + metricName + '?hours=' + hours);

        let html = `<div class="alert alert-info"><strong>Historial de ${metricName} (${result.data_points} puntos)</strong></div>`;

        if (result.metrics && result.metrics.length > 0) {
            html += '<div class="table-responsive"><table class="table table-sm">';
            html += '<thead><tr><th>Valor</th><th>Timestamp</th></tr></thead><tbody>';

            result.metrics.forEach(metric => {
                const timestamp = new Date(metric.timestamp).toLocaleString();
                html += `<tr>
                    <td>${metric.value}</td>
                    <td><small>${timestamp}</small></td>
                </tr>`;
            });

            html += '</tbody></table></div>';
        } else {
            html += '<p class="text-muted">No hay datos históricos disponibles</p>';
        }

        showResult('metricsHistoryResult', html);
    } catch (e) {
        showResult('metricsHistoryResult', `Error al obtener historial de métricas: ${e.message}`, true);
    }
}
window.getMetricsHistory = getMetricsHistory;

async function startMonitoring() {
    showLoading('monitoringControlResult');
    try {
        const result = await apiRequest('/monitoring/start', {}, 'POST');
        showResult('monitoringControlResult',
            `<div class="alert alert-success">✅ Sistema de monitoreo iniciado exitosamente</div>`);
    } catch (e) {
        showResult('monitoringControlResult', `Error al iniciar monitoreo: ${e.message}`, true);
    }
}
window.startMonitoring = startMonitoring;

async function stopMonitoring() {
    showLoading('monitoringControlResult');
    try {
        const result = await apiRequest('/monitoring/stop', {}, 'POST');
        showResult('monitoringControlResult',
            `<div class="alert alert-warning">⚠️ Sistema de monitoreo detenido</div>`);
    } catch (e) {
        showResult('monitoringControlResult', `Error al detener monitoreo: ${e.message}`, true);
    }
}
window.stopMonitoring = stopMonitoring;

async function getMonitoringHealth() {
    showLoading('monitoringControlResult');
    try {
        const result = await apiRequest('/monitoring/health');
        let html = `<div class="alert alert-${result.status === 'healthy' ? 'success' : 'warning'}">
            <strong>Health Check: ${result.status.toUpperCase()}</strong>
        </div>`;

        html += `<div class="row g-3">
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h4 class="text-${result.monitoring_active ? 'success' : 'warning'}">
                            ${result.monitoring_active ? '🟢' : '🔴'}
                        </h4>
                        <small class="text-muted">Monitoreo Activo</small>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h4 class="text-danger">${result.active_alerts}</h4>
                        <small class="text-muted">Alertas Activas</small>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h4 class="text-info">${result.total_metrics}</h4>
                        <small class="text-muted">Métricas Totales</small>
                    </div>
                </div>
            </div>
        </div>`;

        showResult('monitoringControlResult', html);
    } catch (e) {
        showResult('monitoringControlResult', `Error en health check: ${e.message}`, true);
    }
}
window.getMonitoringHealth = getMonitoringHealth;

async function createAlertRule() {
    const ruleName = document.getElementById('ruleName').value;
    const ruleMetric = document.getElementById('ruleMetric').value;
    const ruleCondition = document.getElementById('ruleCondition').value;
    const ruleThreshold = parseFloat(document.getElementById('ruleThreshold').value);
    const ruleSeverity = document.getElementById('ruleSeverity').value;

    if (!ruleName.trim() || !ruleMetric || isNaN(ruleThreshold)) {
        showResult('newRuleResult', 'Por favor complete todos los campos correctamente', true);
        return;
    }

    showLoading('newRuleResult');
    try {
        const result = await apiRequest('/monitoring/alerts/rules', {
            name: ruleName,
            description: `Alerta automática para ${ruleMetric}`,
            metric_name: ruleMetric,
            condition: ruleCondition,
            threshold: ruleThreshold,
            severity: ruleSeverity,
            enabled: true,
            cooldown_minutes: 5
        }, 'POST');

        showResult('newRuleResult',
            `<div class="alert alert-success">✅ Regla de alerta "${ruleName}" creada exitosamente</div>`);
    } catch (e) {
        showResult('newRuleResult', `Error al crear regla de alerta: ${e.message}`, true);
    }
}
window.createAlertRule = createAlertRule;

// Función auxiliar para escapar HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
