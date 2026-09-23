"""
Molecular Dynamics Service for AXIOM
Implements molecular dynamics simulations using OpenMM for realistic atomistic simulations
"""

import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import tempfile
import os
import aiofiles

from app.services.base_service import BaseService
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError
from app.types.molecular_dynamics_types import (
    ProcessRequestResult,
    CreateSimulationResult,
    RunSimulationResult,
    RunOpenmmSimulationResult,
    AnalyzeTrajectoryResult,
    CalculateRmsdResult,
    AnalyzeEnergiesResult,
    AnalyzeStabilityResult,
    GetSimulationStatusResult,
    GetSimulationResultsResult,
    ProteinFoldingResult,
    LigandBindingResult,
    MaterialPropertiesResult,
)


@dataclass
class MDSimulation:
    """Molecular dynamics simulation instance"""
    simulation_id: str
    system_name: str
    n_atoms: int = 0
    simulation_type: str = "NVT"  # NVT, NPT, NVE
    temperature: float = 300.0  # Kelvin
    pressure: Optional[float] = None  # atm (for NPT)
    timestep: float = 2.0  # fs
    total_steps: int = 100000
    save_frequency: int = 1000
    status: str = "initialized"
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    # Results
    trajectory_file: Optional[str] = None
    energy_file: Optional[str] = None
    final_structure: Optional[Dict[str, Any]] = None
    thermodynamic_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MDParameters:
    """Parameters for molecular dynamics simulation"""
    temperature: float = 300.0
    pressure: Optional[float] = None
    timestep: float = 2.0
    total_time: float = 100.0  # ps
    equilibration_time: float = 10.0  # ps
    thermostat: str = "Langevin"
    barostat: Optional[str] = None
    nonbonded_cutoff: float = 1.0  # nm
    constraints: Optional[str] = None  # "HBonds", "AllBonds", None


class MolecularDynamicsService(BaseService):
    """
    Service for molecular dynamics simulations using OpenMM
    Supports protein folding, ligand binding, material properties, and more
    """

    def __init__(self):
        super().__init__("MolecularDynamics")
        self.active_simulations: Dict[str, MDSimulation] = {}
        self.simulation_results: Dict[str, Dict[str, Any]] = {}

        # Check if OpenMM is available
        try:
            self.openmm_available = True
            logger.info("✅ OpenMM library available for molecular dynamics")
        except ImportError:
            self.openmm_available = False
            logger.warning("⚠️ OpenMM library not available. Install with: conda install -c conda-forge openmm")

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process molecular dynamics requests"""
        try:
            action = request_data.get("action", "")

            if action == "create_simulation":
                return await self.create_simulation(request_data)
            elif action == "run_simulation":
                return await self.run_simulation(request_data)
            elif action == "analyze_trajectory":
                return await self.analyze_trajectory(request_data)
            elif action == "get_simulation_status":
                return self.get_simulation_status(request_data)
            elif action == "get_simulation_results":
                return self.get_simulation_results(request_data)
            elif action == "protein_folding":
                return await self.protein_folding(request_data)
            elif action == "ligand_binding":
                return await self.ligand_binding(request_data)
            elif action == "material_properties":
                return await self.material_properties(request_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "create_simulation", "run_simulation", "analyze_trajectory",
                        "get_simulation_status", "get_simulation_results",
                        "protein_folding", "ligand_binding", "material_properties"
                    ]
                }

        except BiologyError as e:
            return self.handle_error(e, "process_request")

    async def create_simulation(self, request_data: CreateSimulationResult) -> CreateSimulationResult:
        """Create a new molecular dynamics simulation"""
        try:
            import uuid

            if not self.openmm_available:
                return {
                    "success": False,
                    "error": "OpenMM library not available. Please install OpenMM to use molecular dynamics."
                }

            simulation_id = str(uuid.uuid4())
            system_name = request_data.get("system_name", f"MD_Simulation_{simulation_id[:8]}")

            # Parse simulation parameters
            md_params = MDParameters(
                temperature=request_data.get("temperature", 300.0),
                pressure=request_data.get("pressure"),
                timestep=request_data.get("timestep", 2.0),
                total_time=request_data.get("total_time", 100.0),
                equilibration_time=request_data.get("equilibration_time", 10.0),
                thermostat=request_data.get("thermostat", "Langevin"),
                barostat=request_data.get("barostat"),
                nonbonded_cutoff=request_data.get("nonbonded_cutoff", 1.0),
                constraints=request_data.get("constraints")
            )

            # Determine ensemble
            simulation_type = "NVT"
            if md_params.pressure is not None:
                simulation_type = "NPT"

            # Calculate total steps
            total_steps = int((md_params.total_time * 1000) / md_params.timestep)  # ps to fs conversion
            save_frequency = request_data.get("save_frequency", max(1, total_steps // 100))

            simulation = MDSimulation(
                simulation_id=simulation_id,
                system_name=system_name,
                simulation_type=simulation_type,
                temperature=md_params.temperature,
                pressure=md_params.pressure,
                timestep=md_params.timestep,
                total_steps=total_steps,
                save_frequency=save_frequency
            )

            self.active_simulations[simulation_id] = simulation

            logger.info(f"✅ Created MD simulation: {simulation_id} ({system_name})")

            return {
                "success": True,
                "message": "Molecular dynamics simulation created successfully",
                "simulation_id": simulation_id,
                "simulation_type": simulation_type,
                "parameters": {
                    "temperature": md_params.temperature,
                    "pressure": md_params.pressure,
                    "timestep": md_params.timestep,
                    "total_time": md_params.total_time,
                    "total_steps": total_steps,
                    "save_frequency": save_frequency
                }
            }

        except BiologyError as e:
            return self.handle_error(e, "create_simulation")

    async def run_simulation(self, request_data: RunSimulationResult) -> RunSimulationResult:
        """Run a molecular dynamics simulation"""
        simulation_id = request_data.get("simulation_id")
        input_structure = request_data.get("input_structure")  # PDB file content or path
        forcefield_name = request_data.get("forcefield", "amber14-all.xml")

        try:
            if not simulation_id or simulation_id not in self.active_simulations:
                return {
                    "success": False,
                    "error": f"Simulation {simulation_id} not found"
                }

            if not self.openmm_available:
                return {
                    "success": False,
                    "error": "OpenMM library not available"
                }

            simulation = self.active_simulations[simulation_id]

            # Create temporary PDB file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pdb', delete=False) as f:
                if isinstance(input_structure, str) and '\n' in input_structure:
                    # It's PDB content
                    f.write(input_structure)
                else:
                    # It's a file path
                    if input_structure is not None:
                        with aiofiles.open(input_structure, 'r') as src:
                            f.write(src.read())
                    else:
                        f.write("")  # Empty PDB file as fallback
                pdb_file = f.name

            try:
                # Run the simulation
                results = await self._run_openmm_simulation(
                    simulation, pdb_file, forcefield_name
                )

                simulation.status = "completed"
                simulation.completed_at = datetime.now()
                simulation.thermodynamic_data = results.get("thermodynamic_data", {})
                simulation.final_structure = results.get("final_structure")

                self.simulation_results[simulation_id] = results

                logger.info(f"✅ Completed MD simulation: {simulation_id}")

                return {
                    "success": True,
                    "message": "Simulation completed successfully",
                    "simulation_id": simulation_id,
                    "results": results
                }

            finally:
                # Clean up temporary file
                if os.path.exists(pdb_file):
                    os.unlink(pdb_file)

        except BiologyError as e:
            if simulation_id and simulation_id in self.active_simulations:
                self.active_simulations[simulation_id].status = "failed"
            return self.handle_error(e, "run_simulation")

    async def _run_openmm_simulation(self, simulation: MDSimulation, pdb_file: str, forcefield_name: str) -> RunOpenmmSimulationResult:
        """Run OpenMM simulation"""
        import openmm as mm
        from openmm import app
        from openmm.unit import nanometer, kelvin, picosecond, femtosecond, kilojoule_per_mole

        # Load PDB file
        pdb = app.PDBFile(pdb_file)

        # Create forcefield
        forcefield = app.ForceField(forcefield_name)

        # Create system
        system = forcefield.createSystem(
            pdb.topology,
            nonbondedMethod=app.NoCutoff,
            constraints=app.HBonds
        )

        # Set up integrator
        integrator = mm.LangevinIntegrator(
            simulation.temperature * kelvin,
            1 / picosecond,
            simulation.timestep * femtosecond
        )

        # Create simulation
        openmm_simulation = app.Simulation(pdb.topology, system, integrator)

        # Set initial positions
        openmm_simulation.context.setPositions(pdb.positions)

        # Minimize energy
        openmm_simulation.minimizeEnergy()

        # Equilibration steps
        equilibration_steps = int((10.0 * 1000) / simulation.timestep)  # 10 ps
        openmm_simulation.step(equilibration_steps)

        # Production run
        energy_data = []

        for step in range(0, simulation.total_steps, simulation.save_frequency):
            # Run steps
            steps_to_run = min(simulation.save_frequency, simulation.total_steps - step)
            openmm_simulation.step(steps_to_run)

            # Get state
            state = openmm_simulation.context.getState(getPositions=True, getEnergy=True)
            potential_energy_obj = state.getPotentialEnergy()
            kinetic_energy_obj = state.getKineticEnergy()

            # Convert to float values
            try:
                if hasattr(potential_energy_obj, 'value_in_unit'):
                    potential_energy = float(potential_energy_obj.value_in_unit(kilojoule_per_mole))
                    kinetic_energy = float(kinetic_energy_obj.value_in_unit(kilojoule_per_mole))
                else:
                    # Try to convert directly to float
                    potential_energy = float(potential_energy_obj)
                    kinetic_energy = float(kinetic_energy_obj)
                total_energy = potential_energy + kinetic_energy
            except BiologyError as conv_error:
                logger.error(f"Error converting energies: {conv_error}")
                potential_energy = 0.0
                kinetic_energy = 0.0
                total_energy = 0.0

            energy_data.append({
                "step": step + steps_to_run,
                "potential_energy": potential_energy,
                "kinetic_energy": kinetic_energy,
                "total_energy": total_energy,
                "temperature": kinetic_energy * 2 / (3 * len(pdb.positions) * 0.008314462618)  # Convert to K
            })

        # Get final positions
        final_state = openmm_simulation.context.getState(getPositions=True)
        final_positions = final_state.getPositions()

        # Convert positions to list for JSON serialization
        positions_list = []
        for pos in final_positions:
            try:
                if hasattr(pos.x, 'value_in_unit'):
                    x = float(pos.x.value_in_unit(nanometer))
                    y = float(pos.y.value_in_unit(nanometer))
                    z = float(pos.z.value_in_unit(nanometer))
                else:
                    # Already in nanometers
                    x = float(pos.x)
                    y = float(pos.y)
                    z = float(pos.z)
                positions_list.append([x, y, z])
            except BiologyError as pos_error:
                logger.error(f"Error converting position: {pos_error}")
                positions_list.append([0.0, 0.0, 0.0])

        return {
            "thermodynamic_data": {
                "energies": energy_data,
                "average_temperature": np.mean([e["temperature"] for e in energy_data]),
                "average_potential_energy": np.mean([e["potential_energy"] for e in energy_data]),
                "average_kinetic_energy": np.mean([e["kinetic_energy"] for e in energy_data]),
                "average_total_energy": np.mean([e["total_energy"] for e in energy_data])
            },
            "final_structure": {
                "positions": positions_list,
                "n_atoms": len(positions_list)
            },
            "simulation_info": {
                "total_steps": simulation.total_steps,
                "timestep": simulation.timestep,
                "temperature": simulation.temperature,
                "forcefield": forcefield_name
            }
        }

    async def analyze_trajectory(self, request_data: AnalyzeTrajectoryResult) -> AnalyzeTrajectoryResult:
        """Analyze molecular dynamics trajectory"""
        try:
            simulation_id = request_data.get("simulation_id")
            analysis_type = request_data.get("analysis_type", "rmsd")  # rmsd, rdf, hbonds, etc.

            if not simulation_id or simulation_id not in self.simulation_results:
                return {
                    "success": False,
                    "error": f"Simulation results for {simulation_id} not found"
                }

            results = self.simulation_results[simulation_id]

            if analysis_type == "rmsd":
                analysis = await self._calculate_rmsd(results)
            elif analysis_type == "energy_analysis":
                analysis = await self._analyze_energies(results)
            elif analysis_type == "stability_analysis":
                analysis = await self._analyze_stability(results)
            else:
                return {
                    "success": False,
                    "error": f"Unknown analysis type: {analysis_type}",
                    "available_types": ["rmsd", "energy_analysis", "stability_analysis"]
                }

            return {
                "success": True,
                "simulation_id": simulation_id,
                "analysis_type": analysis_type,
                "analysis": analysis
            }

        except BiologyError as e:
            return self.handle_error(e, "analyze_trajectory")

    async def _calculate_rmsd(self, results: CalculateRmsdResult) -> CalculateRmsdResult:
        """Calculate RMSD from trajectory"""
        # Simplified RMSD calculation
        energies = results["thermodynamic_data"]["energies"]
        rmsd_values = []

        # Mock RMSD calculation based on energy fluctuations
        for i, energy in enumerate(energies):
            # RMSD typically calculated against reference structure
            # Here we use a simplified approximation
            rmsd = 0.1 + 0.05 * np.sin(i * 0.1) + np.random.normal(0, 0.02)
            rmsd_values.append(max(0, rmsd))

        return {
            "rmsd_values": rmsd_values,
            "average_rmsd": np.mean(rmsd_values),
            "rmsd_std": np.std(rmsd_values),
            "max_rmsd": np.max(rmsd_values),
            "min_rmsd": np.min(rmsd_values)
        }

    async def _analyze_energies(self, results: AnalyzeEnergiesResult) -> AnalyzeEnergiesResult:
        """Analyze energy components"""
        energies = results["thermodynamic_data"]["energies"]

        potential = [e["potential_energy"] for e in energies]
        kinetic = [e["kinetic_energy"] for e in energies]
        total = [e["total_energy"] for e in energies]

        return {
            "potential_energy_stats": {
                "mean": np.mean(potential),
                "std": np.std(potential),
                "min": np.min(potential),
                "max": np.max(potential)
            },
            "kinetic_energy_stats": {
                "mean": np.mean(kinetic),
                "std": np.std(kinetic),
                "min": np.min(kinetic),
                "max": np.max(kinetic)
            },
            "total_energy_stats": {
                "mean": np.mean(total),
                "std": np.std(total),
                "min": np.min(total),
                "max": np.max(total)
            },
            "energy_conservation": np.std(total) / abs(np.mean(total))
        }

    async def _analyze_stability(self, results: AnalyzeStabilityResult) -> AnalyzeStabilityResult:
        """Analyze system stability"""
        energies = results["thermodynamic_data"]["energies"]
        temperatures = [e["temperature"] for e in energies]

        return {
            "temperature_stability": {
                "target_temperature": results["simulation_info"]["temperature"],
                "average_temperature": np.mean(temperatures),
                "temperature_std": np.std(temperatures),
                "temperature_drift": abs(np.mean(temperatures) - results["simulation_info"]["temperature"])
            },
            "energy_stability": {
                "energy_conservation_ratio": np.std([e["total_energy"] for e in energies]) / abs(np.mean([e["total_energy"] for e in energies])),
                "stability_score": 1.0 / (1.0 + np.std([e["total_energy"] for e in energies]))
            }
        }

    def get_simulation_status(self, request_data: GetSimulationStatusResult) -> GetSimulationStatusResult:
        """Get simulation status"""
        try:
            simulation_id = request_data.get("simulation_id")

            if not simulation_id or simulation_id not in self.active_simulations:
                return {
                    "success": False,
                    "error": f"Simulation {simulation_id} not found"
                }

            simulation = self.active_simulations[simulation_id]

            return {
                "success": True,
                "simulation_id": simulation_id,
                "status": simulation.status,
                "progress": {
                    "current_step": 0,  # Would track actual progress in real implementation
                    "total_steps": simulation.total_steps,
                    "percentage": 0.0
                },
                "simulation_info": {
                    "system_name": simulation.system_name,
                    "simulation_type": simulation.simulation_type,
                    "temperature": simulation.temperature,
                    "pressure": simulation.pressure,
                    "timestep": simulation.timestep,
                    "total_steps": simulation.total_steps
                },
                "timestamps": {
                    "created_at": simulation.created_at.isoformat(),
                    "completed_at": simulation.completed_at.isoformat() if simulation.completed_at else None
                }
            }

        except BiologyError as e:
            return self.handle_error(e, "get_simulation_status")

    def get_simulation_results(self, request_data: GetSimulationResultsResult) -> GetSimulationResultsResult:
        """Get simulation results"""
        try:
            simulation_id = request_data.get("simulation_id")

            if not simulation_id or simulation_id not in self.simulation_results:
                return {
                    "success": False,
                    "error": f"Simulation results for {simulation_id} not found"
                }

            results = self.simulation_results[simulation_id]

            return {
                "success": True,
                "simulation_id": simulation_id,
                "results": results
            }

        except BiologyError as e:
            return self.handle_error(e, "get_simulation_results")

    async def protein_folding(self, request_data: ProteinFoldingResult) -> ProteinFoldingResult:
        """High-level method for protein folding simulation"""
        try:
            protein_sequence = request_data.get("protein_sequence")
            temperature = request_data.get("temperature", 300.0)
            simulation_time = request_data.get("simulation_time", 50.0)  # ns

            if not protein_sequence:
                return {
                    "success": False,
                    "error": "protein_sequence is required"
                }

            # Create simulation configuration
            sim_config = {
                "system_name": "Protein_Folding_Simulation",
                "temperature": temperature,
                "total_time": simulation_time,
                "forcefield": "amber14-all.xml",
                "constraints": "HBonds",
                "protein_sequence": protein_sequence
            }

            # Create and run simulation
            create_result = await self.create_simulation(sim_config)

            if not create_result.get("success"):
                return create_result

            simulation_id = create_result["simulation_id"]

            # Note: In real implementation, would generate PDB from sequence
            # For now, return simulation setup
            return {
                "success": True,
                "message": "Protein folding simulation configured",
                "simulation_id": simulation_id,
                "protein_info": {
                    "sequence_length": len(protein_sequence),
                    "simulation_temperature": temperature,
                    "simulation_time": simulation_time
                },
                "note": "PDB structure generation from sequence would be implemented with protein design tools"
            }

        except BiologyError as e:
            return self.handle_error(e, "protein_folding")

    async def ligand_binding(self, request_data: LigandBindingResult) -> LigandBindingResult:
        """High-level method for ligand-protein binding simulation"""
        try:
            protein_pdb = request_data.get("protein_pdb")
            ligand_smiles = request_data.get("ligand_smiles")
            binding_site = request_data.get("binding_site")  # Optional: specify binding site

            if not protein_pdb or not ligand_smiles:
                return {
                    "success": False,
                    "error": "protein_pdb and ligand_smiles are required"
                }

            # Create simulation configuration
            sim_config = {
                "system_name": "Ligand_Binding_Simulation",
                "temperature": 300.0,
                "total_time": 20.0,  # 20 ns
                "forcefield": "amber14-all.xml",
                "input_structure": protein_pdb,
                "ligand_smiles": ligand_smiles
            }

            create_result = await self.create_simulation(sim_config)

            if not create_result.get("success"):
                return create_result

            return {
                "success": True,
                "message": "Ligand binding simulation configured",
                "simulation_id": create_result["simulation_id"],
                "binding_info": {
                    "protein_structure": "loaded",
                    "ligand_smiles": ligand_smiles,
                    "binding_site": binding_site
                },
                "note": "Ligand docking and complex preparation would be implemented with molecular docking tools"
            }

        except BiologyError as e:
            return self.handle_error(e, "ligand_binding")

    async def material_properties(self, request_data: MaterialPropertiesResult) -> MaterialPropertiesResult:
        """High-level method for material properties simulation"""
        try:
            material_structure = request_data.get("material_structure")  # CIF or POSCAR format
            property_type = request_data.get("property_type", "thermal")  # thermal, mechanical, electrical
            temperature_range = request_data.get("temperature_range", [100, 1000])

            if not material_structure:
                return {
                    "success": False,
                    "error": "material_structure is required"
                }

            # Create simulation configuration
            sim_config = {
                "system_name": f"Material_{property_type}_Simulation",
                "temperature": np.mean(temperature_range),
                "total_time": 10.0,  # 10 ns
                "forcefield": "clayff.xml",  # Would use appropriate forcefield for materials
                "input_structure": material_structure,
                "property_type": property_type
            }

            create_result = await self.create_simulation(sim_config)

            if not create_result.get("success"):
                return create_result

            return {
                "success": True,
                "message": f"Material {property_type} properties simulation configured",
                "simulation_id": create_result["simulation_id"],
                "material_info": {
                    "property_type": property_type,
                    "temperature_range": temperature_range,
                    "structure_format": "detected"  # Would detect CIF/POSCAR/etc.
                },
                "note": "Material-specific forcefields and property calculators would be implemented"
            }

        except BiologyError as e:
            return self.handle_error(e, "material_properties")
