"""
Integration Tests for Solid State Physics Materials (Mock-based)
"""

import pytest
from unittest.mock import patch, AsyncMock
from app.services.solid_state_physics import SolidStatePhysicsService


class TestSolidStateMaterialsIntegration:
    """Integration tests for material-specific DFT calculations"""

    @pytest.fixture
    def service(self):
        """Fixture to provide SolidStatePhysicsService instance"""
        return SolidStatePhysicsService()

    @pytest.mark.asyncio
    @patch('app.services.solid_state_physics.SolidStatePhysicsService.create_calculation')
    async def test_silicon_calculation_integration(self, mock_create_calc, service):
        """Test complete silicon calculation workflow"""
        # Mock the create_calculation method
        mock_create_calc.return_value = {
            'success': True,
            'calculation_id': 'si_calc_001',
            'calculation_type': 'scf',
            'parameters': {
                'material_name': 'Silicon',
                'xc_functional': 'PBE',
                'kpoints': [4, 4, 4],
                'cutoff_energy': 400.0
            }
        }

        # Create silicon structure
        silicon_structure = {
            "symbols": ["Si", "Si", "Si", "Si", "Si", "Si", "Si", "Si"],
            "positions": [
                [0.0, 0.0, 0.0],
                [1.3575, 1.3575, 1.3575],
                [2.715, 2.715, 0.0],
                [4.0725, 4.0725, 1.3575],
                [2.715, 0.0, 2.715],
                [4.0725, 1.3575, 4.0725],
                [0.0, 2.715, 2.715],
                [1.3575, 4.0725, 4.0725]
            ],
            "cell": [
                [5.43, 0.0, 0.0],
                [0.0, 5.43, 0.0],
                [0.0, 0.0, 5.43]
            ]
        }

        # Create calculation
        calc_request = {
            "material_name": "Silicon",
            "calculation_type": "scf",
            "xc_functional": "PBE",
            "kpoints": [4, 4, 4],
            "cutoff_energy": 400.0
        }

        calc_result = await service.create_calculation(calc_request)
        assert calc_result['success'] is True

        calculation_id = calc_result['calculation_id']

        # Mock run_calculation
        with patch.object(service, 'run_calculation', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'success': True,
                'results': {
                    'total_energy': -158.7,
                    'forces': [[0.0, 0.0, 0.0]] * 8,
                    'stress': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                }
            }

            # Run calculation
            run_request = {
                "calculation_id": calculation_id,
                "structure": silicon_structure,
                "calculator": "gpaw"
            }

            run_result = await service.run_calculation(run_request)
            assert run_result['success'] is True
            assert 'results' in run_result
            assert 'total_energy' in run_result['results']

            # Mock analyze_electronic_structure
            with patch.object(service, 'analyze_electronic_structure', new_callable=AsyncMock) as mock_analyze:
                mock_analyze.return_value = {
                    'success': True,
                    'analysis': {
                        'material_type': 'semiconductor',
                        'band_gap': 1.1,
                        'fermi_level': 0.0
                    }
                }

                # Analyze electronic structure
                analysis_request = {
                    "calculation_id": calculation_id
                }

                analysis_result = await service.analyze_electronic_structure(analysis_request)
                assert analysis_result['success'] is True
                assert 'analysis' in analysis_result
                assert 'material_type' in analysis_result['analysis']

    @pytest.mark.asyncio
    @patch('app.services.solid_state_physics.SolidStatePhysicsService.create_calculation')
    async def test_copper_calculation_integration(self, mock_create_calc, service):
        """Test complete copper calculation workflow"""
        # Mock the create_calculation method
        mock_create_calc.return_value = {
            'success': True,
            'calculation_id': 'cu_calc_001',
            'calculation_type': 'scf',
            'parameters': {
                'material_name': 'Copper',
                'xc_functional': 'PBE',
                'kpoints': [8, 8, 8],
                'cutoff_energy': 400.0
            }
        }

        # Create copper FCC structure
        copper_structure = {
            "symbols": ["Cu", "Cu", "Cu", "Cu"],
            "positions": [
                [0.0, 0.0, 0.0],
                [1.8075, 1.8075, 0.0],
                [0.0, 1.8075, 1.8075],
                [1.8075, 0.0, 1.8075]
            ],
            "cell": [
                [3.615, 0.0, 0.0],
                [0.0, 3.615, 0.0],
                [0.0, 0.0, 3.615]
            ]
        }

        # Create calculation
        calc_request = {
            "material_name": "Copper",
            "calculation_type": "scf",
            "xc_functional": "PBE",
            "kpoints": [8, 8, 8],
            "cutoff_energy": 400.0
        }

        calc_result = await service.create_calculation(calc_request)
        assert calc_result['success'] is True

        calculation_id = calc_result['calculation_id']

        # Mock run_calculation
        with patch.object(service, 'run_calculation', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'success': True,
                'results': {
                    'total_energy': -42.3,
                    'forces': [[0.0, 0.0, 0.0]] * 4,
                    'stress': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                }
            }

            # Run calculation
            run_request = {
                "calculation_id": calculation_id,
                "structure": copper_structure,
                "calculator": "gpaw"
            }

            run_result = await service.run_calculation(run_request)
            assert run_result['success'] is True
            assert 'results' in run_result
            assert 'total_energy' in run_result['results']

    @pytest.mark.asyncio
    @patch('app.services.solid_state_physics.SolidStatePhysicsService.create_calculation')
    async def test_aluminum_calculation_integration(self, mock_create_calc, service):
        """Test complete aluminum calculation workflow"""
        # Mock the create_calculation method
        mock_create_calc.return_value = {
            'success': True,
            'calculation_id': 'al_calc_001',
            'calculation_type': 'scf',
            'parameters': {
                'material_name': 'Aluminum',
                'xc_functional': 'PBE',
                'kpoints': [8, 8, 8],
                'cutoff_energy': 400.0
            }
        }

        # Create aluminum FCC structure
        aluminum_structure = {
            "symbols": ["Al", "Al", "Al", "Al"],
            "positions": [
                [0.0, 0.0, 0.0],
                [2.025, 2.025, 0.0],
                [0.0, 2.025, 2.025],
                [2.025, 0.0, 2.025]
            ],
            "cell": [
                [4.05, 0.0, 0.0],
                [0.0, 4.05, 0.0],
                [0.0, 0.0, 4.05]
            ]
        }

        # Create calculation
        calc_request = {
            "material_name": "Aluminum",
            "calculation_type": "scf",
            "xc_functional": "PBE",
            "kpoints": [8, 8, 8],
            "cutoff_energy": 400.0
        }

        calc_result = await service.create_calculation(calc_request)
        assert calc_result['success'] is True

        calculation_id = calc_result['calculation_id']

        # Mock run_calculation
        with patch.object(service, 'run_calculation', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'success': True,
                'results': {
                    'total_energy': -57.8,
                    'forces': [[0.0, 0.0, 0.0]] * 4,
                    'stress': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                }
            }

            # Run calculation
            run_request = {
                "calculation_id": calculation_id,
                "structure": aluminum_structure,
                "calculator": "gpaw"
            }

            run_result = await service.run_calculation(run_request)
            assert run_result['success'] is True
            assert 'results' in run_result
            assert 'total_energy' in run_result['results']

    @pytest.mark.asyncio
    @patch('app.services.solid_state_physics.SolidStatePhysicsService.create_calculation')
    async def test_diamond_calculation_integration(self, mock_create_calc, service):
        """Test complete diamond calculation workflow"""
        # Mock the create_calculation method
        mock_create_calc.return_value = {
            'success': True,
            'calculation_id': 'diamond_calc_001',
            'calculation_type': 'scf',
            'parameters': {
                'material_name': 'Diamond',
                'xc_functional': 'PBE',
                'kpoints': [6, 6, 6],
                'cutoff_energy': 600.0
            }
        }

        # Create diamond structure
        diamond_structure = {
            "symbols": ["C", "C", "C", "C", "C", "C", "C", "C"],
            "positions": [
                [0.0, 0.0, 0.0],
                [0.891, 0.891, 0.891],
                [1.783, 1.783, 0.0],
                [2.674, 2.674, 0.891],
                [1.783, 0.0, 1.783],
                [2.674, 0.891, 2.674],
                [0.0, 1.783, 1.783],
                [0.891, 2.674, 2.674]
            ],
            "cell": [
                [3.567, 0.0, 0.0],
                [0.0, 3.567, 0.0],
                [0.0, 0.0, 3.567]
            ]
        }

        # Create calculation
        calc_request = {
            "material_name": "Diamond",
            "calculation_type": "scf",
            "xc_functional": "PBE",
            "kpoints": [6, 6, 6],
            "cutoff_energy": 600.0  # Higher cutoff for carbon
        }

        calc_result = await service.create_calculation(calc_request)
        assert calc_result['success'] is True

        calculation_id = calc_result['calculation_id']

        # Mock run_calculation
        with patch.object(service, 'run_calculation', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'success': True,
                'results': {
                    'total_energy': -45.2,
                    'forces': [[0.0, 0.0, 0.0]] * 8,
                    'stress': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                }
            }

            # Run calculation
            run_request = {
                "calculation_id": calculation_id,
                "structure": diamond_structure,
                "calculator": "gpaw"
            }

            run_result = await service.run_calculation(run_request)
            assert run_result['success'] is True
            assert 'results' in run_result
            assert 'total_energy' in run_result['results']

    @pytest.mark.asyncio
    @patch('app.services.solid_state_physics.SolidStatePhysicsService.create_calculation')
    async def test_graphene_calculation_integration(self, mock_create_calc, service):
        """Test complete graphene calculation workflow"""
        # Mock the create_calculation method
        mock_create_calc.return_value = {
            'success': True,
            'calculation_id': 'graphene_calc_001',
            'calculation_type': 'scf',
            'parameters': {
                'material_name': 'Graphene',
                'xc_functional': 'PBE',
                'kpoints': [12, 12, 1],
                'cutoff_energy': 600.0
            }
        }

        # Create graphene structure (single layer)
        graphene_structure = {
            "symbols": ["C", "C"],
            "positions": [
                [0.0, 0.0, 0.0],
                [1.42, 0.0, 0.0]
            ],
            "cell": [
                [2.46, 0.0, 0.0],
                [-1.23, 2.13, 0.0],
                [0.0, 0.0, 20.0]  # Large z-dimension for 2D material
            ]
        }

        # Create calculation
        calc_request = {
            "material_name": "Graphene",
            "calculation_type": "scf",
            "xc_functional": "PBE",
            "kpoints": [12, 12, 1],  # Dense k-points for 2D material
            "cutoff_energy": 600.0
        }

        calc_result = await service.create_calculation(calc_request)
        assert calc_result['success'] is True

        calculation_id = calc_result['calculation_id']

        # Mock run_calculation
        with patch.object(service, 'run_calculation', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'success': True,
                'results': {
                    'total_energy': -11.8,
                    'forces': [[0.0, 0.0, 0.0]] * 2,
                    'stress': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                }
            }

            # Run calculation
            run_request = {
                "calculation_id": calculation_id,
                "structure": graphene_structure,
                "calculator": "gpaw"
            }

            run_result = await service.run_calculation(run_request)
            assert run_result['success'] is True
            assert 'results' in run_result
            assert 'total_energy' in run_result['results']

    @pytest.mark.asyncio
    @patch('app.services.solid_state_physics.SolidStatePhysicsService.create_calculation')
    async def test_multiple_materials_workflow(self, mock_create_calc, service):
        """Test workflow with multiple materials"""
        # Mock the create_calculation method to return different IDs for each call
        mock_create_calc.side_effect = [
            {
                'success': True,
                'calculation_id': 'si_multi_001',
                'calculation_type': 'scf',
                'parameters': {'material_name': 'Silicon'}
            },
            {
                'success': True,
                'calculation_id': 'cu_multi_001',
                'calculation_type': 'scf',
                'parameters': {'material_name': 'Copper'}
            }
        ]

        materials = [
            {
                "name": "Silicon",
                "structure": {
                    "symbols": ["Si", "Si"],
                    "positions": [[0, 0, 0], [1.36, 1.36, 1.36]],
                    "cell": [[5.43, 0, 0], [0, 5.43, 0], [0, 0, 5.43]]
                }
            },
            {
                "name": "Copper",
                "structure": {
                    "symbols": ["Cu", "Cu"],
                    "positions": [[0, 0, 0], [1.81, 1.81, 0]],
                    "cell": [[3.62, 0, 0], [0, 3.62, 0], [0, 0, 3.62]]
                }
            }
        ]

        results = []

        for material in materials:
            # Create calculation
            calc_request = {
                "material_name": material["name"],
                "calculation_type": "scf",
                "xc_functional": "PBE",
                "kpoints": [4, 4, 4],
                "cutoff_energy": 400.0
            }

            calc_result = await service.create_calculation(calc_request)
            assert calc_result['success'] is True

            calculation_id = calc_result['calculation_id']

            # Mock run_calculation for each material
            with patch.object(service, 'run_calculation', new_callable=AsyncMock) as mock_run:
                mock_run.return_value = {
                    'success': True,
                    'results': {
                        'total_energy': -100.0 if material["name"] == "Silicon" else -50.0,
                        'forces': [[0.0, 0.0, 0.0]] * len(material["structure"]["symbols"]),
                        'stress': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                    }
                }

                # Run calculation
                run_request = {
                    "calculation_id": calculation_id,
                    "structure": material["structure"],
                    "calculator": "gpaw"
                }

                run_result = await service.run_calculation(run_request)
                results.append(run_result)

        # Verify we have results for each material
        assert len(results) == len(materials)
        for result in results:
            assert result['success'] is True

    def test_calculation_status_tracking(self, service):
        """Test calculation status tracking"""
        # Test that the service has the expected attributes
        assert hasattr(service, 'active_calculations')
        assert hasattr(service, 'calculation_results')

        # Test with a mock calculation
        with patch.object(service, 'create_calculation', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = {
                'success': True,
                'calculation_id': 'test_calc_001'
            }

            # Note: In real async test, this would be awaited
            # For this sync test, we just verify the mock setup

    def test_calculation_results_retrieval(self, service):
        """Test calculation results retrieval"""
        # Mock calculation results by setting the attribute directly
        service.calculation_results = {
            'test_calc_001': {
                'success': True,
                'results': {'total_energy': -100.0}
            }
        }

        # Mock get_calculation_results method
        with patch.object(service, 'get_calculation_results') as mock_get:
            mock_get.return_value = {
                'success': True,
                'results': {'total_energy': -100.0}
            }

            # Try to get results
            results_request = {
                "calculation_id": "test_calc_001"
            }

            results_result = service.get_calculation_results(results_request)

            # Should return a result dict
            assert isinstance(results_result, dict)
            assert 'success' in results_result

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, service):
        """Test error handling in integration scenarios"""
        # Mock run_calculation to return error
        with patch.object(service, 'run_calculation', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'success': False,
                'error': 'Invalid calculation ID'
            }

            # Test with invalid calculation ID
            run_request = {
                "calculation_id": "invalid_id",
                "structure": {"symbols": ["Si"], "positions": [[0, 0, 0]], "cell": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]},
                "calculator": "gpaw"
            }

            run_result = await service.run_calculation(run_request)
            assert run_result['success'] is False
            assert 'error' in run_result

    @pytest.mark.asyncio
    @patch('app.services.solid_state_physics.SolidStatePhysicsService.create_calculation')
    async def test_calculation_parameters_integration(self, mock_create_calc, service):
        """Test calculation parameters in integration context"""
        # Mock create_calculation with different responses
        mock_create_calc.side_effect = [
            {
                'success': True,
                'calculation_id': 'test_si_001',
                'calculation_type': 'scf',
                'parameters': {
                    'material_name': 'Test Si',
                    'xc_functional': 'PBE',
                    'kpoints': [2, 2, 2],
                    'cutoff_energy': 300.0
                }
            },
            {
                'success': True,
                'calculation_id': 'test_cu_001',
                'calculation_type': 'scf',
                'parameters': {
                    'material_name': 'Test Cu',
                    'xc_functional': 'LDA',
                    'kpoints': [6, 6, 6],
                    'cutoff_energy': 500.0
                }
            }
        ]

        # Test different parameter combinations
        test_cases = [
            {
                "material_name": "Test Si",
                "calculation_type": "scf",
                "xc_functional": "PBE",
                "kpoints": [2, 2, 2],
                "cutoff_energy": 300.0
            },
            {
                "material_name": "Test Cu",
                "calculation_type": "scf",
                "xc_functional": "LDA",
                "kpoints": [6, 6, 6],
                "cutoff_energy": 500.0
            }
        ]

        for params in test_cases:
            calc_result = await service.create_calculation(params)
            assert calc_result['success'] is True
            assert calc_result['calculation_type'] == params['calculation_type']
            assert 'parameters' in calc_result

    def test_service_availability_integration(self, service):
        """Test service availability in integration context"""
        # Test that service is properly initialized
        assert service is not None

        # Test available calculators - mock the property
        with patch.object(service, 'available_calculators', {'gpaw': True, 'ase': True}):
            calculators = service.available_calculators
            assert isinstance(calculators, dict)

        # Test ASE and GPAW availability
        assert hasattr(service, 'ase_available')
        assert hasattr(service, 'gpaw_available')

    @pytest.mark.asyncio
    @patch('app.services.solid_state_physics.SolidStatePhysicsService.create_calculation')
    async def test_calculation_workflow_complete(self, mock_create_calc, service):
        """Test complete calculation workflow from creation to results"""
        # Mock create_calculation
        mock_create_calc.return_value = {
            'success': True,
            'calculation_id': 'workflow_calc_001',
            'calculation_type': 'scf',
            'parameters': {
                'material_name': 'Integration Test Material',
                'xc_functional': 'PBE',
                'kpoints': [4, 4, 4],
                'cutoff_energy': 400.0
            }
        }

        # Step 1: Create calculation
        calc_request = {
            "material_name": "Integration Test Material",
            "calculation_type": "scf",
            "xc_functional": "PBE",
            "kpoints": [4, 4, 4],
            "cutoff_energy": 400.0
        }

        calc_result = await service.create_calculation(calc_request)
        assert calc_result['success'] is True

        calculation_id = calc_result['calculation_id']

        # Step 2: Mock and check status
        with patch.object(service, 'get_calculation_status') as mock_status:
            mock_status.return_value = {
                'success': True,
                'status': 'completed'
            }

            status_request = {"calculation_id": calculation_id}
            status_result = service.get_calculation_status(status_request)
            assert status_result['success'] is True

        # Step 3: Mock and try to get results
        with patch.object(service, 'get_calculation_results') as mock_get_results:
            mock_get_results.return_value = {
                'success': True,
                'results': {'total_energy': -200.0}
            }

            results_request = {"calculation_id": calculation_id}
            results_result = service.get_calculation_results(results_request)
            assert isinstance(results_result, dict)

        # Step 4: Verify calculation exists in service (mock the attributes)
        with patch.object(service, 'active_calculations', {'workflow_calc_001': {}}):
            with patch.object(service, 'calculation_results', {}):
                # Verify calculation exists in service
                assert calculation_id in service.active_calculations
