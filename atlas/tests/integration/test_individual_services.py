"""Test directo de un servicio individual para diagnosticar errores"""
import asyncio
from app.domains.medicine.imaging.medical_imaging_service import MedicalImagingService
from app.advanced_ops.advanced_torch_operations import AdvancedTorchOperations

async def test_individual_services():
    print("🔬 Test directo de servicios individuales")
    print("=" * 50)
    
    # Test 1: MedicalImagingService
    print("🏥 1. Testing MedicalImagingService...")
    try:
        medical_service = MedicalImagingService()
        result = medical_service.list_methods()
        print(f"   ✅ list_methods: {type(result)} - {str(result)[:100]}...")
    except Exception as e:
        print(f"   ❌ list_methods error: {e}")
    
    # Test 2: AdvancedTorchOperations 
    print("\n🔥 2. Testing AdvancedTorchOperations...")
    try:
        torch_service = AdvancedTorchOperations()
        # Verificar métodos disponibles
        methods = [m for m in dir(torch_service) if not m.startswith('_') and callable(getattr(torch_service, m))]
        print(f"   📋 Métodos disponibles: {methods[:5]}...")
        
        # Test neural_network_training
        if hasattr(torch_service, 'neural_network_training'):
            result = torch_service.neural_network_training(architecture="mlp", task="classification")
            print(f"   ✅ neural_network_training: {type(result)} - {str(result)[:100]}...")
        else:
            print(f"   ❌ neural_network_training: método no existe")
            
    except Exception as e:
        print(f"   ❌ torch_service error: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(test_individual_services())
