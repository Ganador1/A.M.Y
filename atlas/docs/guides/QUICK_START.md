# 🚀 AXIOM ATLAS - Quick Start Guide

> **Get up and running in less than 10 minutes!**

## ⚡ Express Installation

### Option 1: Docker (Recommended)
```bash
# Clone and run with Docker
git clone https://github.com/your-repo/axiom-atlas.git
cd axiom-atlas
docker-compose up -d

# Ready! Visit http://localhost:8000/docs
```

### Option 2: Local Installation
```bash
# Requirements: Python 3.8+
git clone https://github.com/your-repo/axiom-atlas.git
cd axiom-atlas

# Install and run
pip install -r requirements.txt
uvicorn app.main:app --reload

# Server at: http://localhost:8000
```

## 🧪 First Steps - 3 Practical Examples

### 1️⃣ Evaluate a Scientific Hypothesis (30 seconds)

```bash
curl -X POST "http://localhost:8000/api/plausibility/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "hypothesis": "Regular exercise improves cognitive function",
    "domain": "neuroscience"
  }'
```

**What does it do?** Analyzes scientific plausibility using AI and medical literature.

### 2️⃣ Quantum Search with Grover (1 minute)

```bash
curl -X POST "http://localhost:8000/api/quantum-computing/grover-search" \
  -H "Content-Type: application/json" \
  -d '{
    "database_size": 16,
    "target_items": [7],
    "optimization_level": 1
  }'
```

**What does it do?** Demonstrates quantum advantage in data search.

### 3️⃣ Scientific Literature Analysis (2 minutes)

```bash
curl -X POST "http://localhost:8000/api/literature-search/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning drug discovery",
    "databases": ["pubmed"],
    "max_results": 10
  }'
```

**What does it do?** Searches and analyzes relevant scientific papers.

## 🎯 Popular Use Cases

| 🔬 **Biomedical Research** | ⚛️ **Quantum Computing** | 📊 **Data Analysis** |
|---|---|---|
| Validate medical hypotheses | Quantum optimization | Statistical analysis |
| Literature search | Quantum algorithms | Data visualization |
| Protein analysis | Molecular simulation | Machine learning |

## 🛠️ Included Tools

### ✅ **Ready to use (no config)**
- ✅ Plausibility evaluation
- ✅ Basic quantum computing
- ✅ Statistical analysis
- ✅ Scientific workflows

### 🔧 **Requires configuration**
- 🔑 PubMed Search (API key)
- 🔑 Advanced AI Models (OpenAI key)
- 🔑 Chemical Databases (ChEMBL key)

## ⚙️ Optional Configuration

### `.env` File (for advanced functions)
```bash
# Create .env file in project root
OPENAI_API_KEY=your_openai_key
PUBMED_API_KEY=your_pubmed_key
CHEMBL_API_KEY=your_chembl_key
```

### Important variables:
- `OPENAI_API_KEY`: For advanced AI analysis
- `PUBMED_API_KEY`: For full medical search
- `CHEMBL_API_KEY`: For chemical and pharmacological data

## 🌐 Web Exploration

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Most Popular Endpoints
```bash
# System status
GET /health

# Hypothesis evaluation
POST /api/plausibility/evaluate

# Quantum search
POST /api/quantum-computing/grover-search

# Schedule experiment
POST /api/scheduler/jobs

# Execute workflow
POST /api/workflows/execute
```

## 🧠 Key Concepts (in 1 minute)

### **Scientific Plausibility**
AI system that evaluates how likely a hypothesis is to be correct based on existing scientific literature.

### **Quantum Computing**
Algorithms that leverage quantum properties to solve problems faster than classical computers.

### **Scientific Workflows**
Automated sequences of experiments and analyses that you can schedule and execute.

### **Reproducibility**
System ensuring that experiments can be repeated and verified by other researchers.

## ❓ Frequently Asked Questions

<details>
<summary><strong>Do I need programming knowledge?</strong></summary>
Not for basic use. The web interface allows using most functions without code. API examples are optional.
</details>

<details>
<summary><strong>Which scientific domains are supported?</strong></summary>
Biomedicine, chemistry, physics, mathematics, astronomy, materials science, and more. See full documentation for detailed list.
</details>

<details>
<summary><strong>Is it free?</strong></summary>
Yes, the software is open-source. Some functions require external APIs that may have costs (OpenAI, etc.).
</details>

<details>
<summary><strong>Does it work offline?</strong></summary>
Basic functions yes. Literature search and some AI models require connection.
</details>

## 🆘 Common Problems

### Error: "Port 8000 in use"
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

### Error: "ModuleNotFoundError"
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Error: "API key invalid"
```bash
# Check .env file
cat .env
```

## 📚 Next Step

Once you have AXIOM running:

1. **Explore**: Visit http://localhost:8000/docs
2. **Experiment**: Try the 3 examples above
3. **Read more**: Consult [README.md](README.md) for full documentation
4. **Join**: Participate in [GitHub Discussions](https://github.com/your-repo/axiom-atlas/discussions)

---

<div align="center">

**[📚 Complete Documentation](README.md)** | **[🐛 Report Issue](https://github.com/your-repo/axiom-atlas/issues)** | **[💬 Community](https://github.com/your-repo/axiom-atlas/discussions)**

</div>

---

*Ready to accelerate your scientific research? Start now! 🚀*
