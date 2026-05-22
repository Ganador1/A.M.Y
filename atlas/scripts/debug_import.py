try:
    from app.domains.physics.quantum.quantum_computing_service import QuantumComputingService
    print("Successfully imported QuantumComputingService")
except Exception as e:
    print(f"Failed to import QuantumComputingService: {e}")