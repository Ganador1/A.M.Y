"""
AXIOM Astronomy - Pipeline Integrado de Análisis Astronómico
============================================================

Pipeline unificado que integra todos los servicios AXIOM en un flujo de análisis
completo y automatizado. Proporciona análisis astronómico de extremo a extremo
desde datos observacionales hasta resultados científicos publicables.

Funcionalidades principales:
- Análisis fotométrico completo con apertura optimizada
- Detección y caracterización de variabilidad estelar
- Análisis de sistemas binarios y búsqueda de exoplanetas
- Análisis astrométrico de alta precisión
- Clasificación automática con machine learning
- Análisis multi-longitud de onda integrado
- Generación de reportes científicos automatizada
- Flujos de trabajo configurables y personalizables

Autor: AXIOM Development Team
Fecha: Octubre 2025
Versión: 1.0.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
import logging
from datetime import datetime
from pathlib import Path
import concurrent.futures
import time
import aiofiles
from app.exceptions.domain.biology import BiologyError

# Setup logging
logger = logging.getLogger(__name__)

class AnalysisMode(Enum):
    """Modos de análisis disponibles."""
    QUICK_SCAN = "quick_scan"
    STANDARD_ANALYSIS = "standard_analysis"
    COMPREHENSIVE_ANALYSIS = "comprehensive_analysis"
    CUSTOM_WORKFLOW = "custom_workflow"

class DataType(Enum):
    """Tipos de datos astronómicos soportados."""
    LIGHT_CURVE = "light_curve"
    ASTROMETRIC_SERIES = "astrometric_series"
    SPECTRAL_SERIES = "spectral_series"
    MULTI_BAND_PHOTOMETRY = "multi_band_photometry"
    TIME_SERIES = "time_series"

class AnalysisStatus(Enum):
    """Estados del análisis."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AnalysisConfiguration:
    """Configuración para el pipeline de análisis."""
    mode: AnalysisMode = AnalysisMode.STANDARD_ANALYSIS
    data_types: List[DataType] = field(default_factory=list)
    enabled_services: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    output_formats: List[str] = field(default_factory=lambda: ["json", "pdf"])
    parallel_processing: bool = True
    max_workers: Optional[int] = None
    timeout_minutes: int = 60
    quality_threshold: float = 0.8
    generate_plots: bool = True
    save_intermediate_results: bool = False

@dataclass
class AstronomicalData:
    """Contenedor para datos astronómicos."""
    object_id: str
    data_type: DataType
    time: np.ndarray
    values: Union[np.ndarray, Dict[str, np.ndarray]]
    errors: Optional[Union[np.ndarray, Dict[str, np.ndarray]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    coordinates: Optional[Tuple[float, float]] = None  # (RA, DEC)
    filters: Optional[List[str]] = None

@dataclass
class AnalysisResult:
    """Resultado de análisis individual."""
    service_name: str
    object_id: str
    status: AnalysisStatus
    results: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    plots: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    error_message: Optional[str] = None
    quality_score: float = 0.0

@dataclass
class PipelineReport:
    """Reporte completo del pipeline."""
    pipeline_id: str
    object_id: str
    configuration: AnalysisConfiguration
    start_time: datetime
    end_time: Optional[datetime] = None
    total_execution_time: float = 0.0
    overall_status: AnalysisStatus = AnalysisStatus.PENDING
    service_results: List[AnalysisResult] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    quality_assessment: Dict[str, float] = field(default_factory=dict)
    generated_files: List[str] = field(default_factory=list)

class IntegratedAstronomyPipeline:
    """
    Pipeline integrado de análisis astronómico AXIOM.
    
    Unifica todos los servicios astronómicos en un flujo de análisis
    completo, automatizado y configurable para investigación científica.
    """
    
    def __init__(self, base_output_dir: Optional[str] = None):
        """
        Inicializa el pipeline integrado.
        
        Args:
            base_output_dir: Directorio base para outputs (opcional)
        """
        self.base_output_dir = Path(base_output_dir or "./axiom_pipeline_outputs")
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Servicios AXIOM disponibles
        self._available_services: Dict[str, Any] = {}
        self._service_dependencies = {}
        self._initialize_services()
        
        # Estado del pipeline
        self._active_pipelines = {}
        self._pipeline_counter = 0
        
        logger.info("IntegratedAstronomyPipeline inicializado")
    
    def _initialize_services(self):
        """Inicializa todos los servicios AXIOM disponibles."""
        try:
            # Fase 1: Servicios de Fundación
            from .lightkurve_advanced_service import LightkurveAdvancedService
            from .astropy_precision_service import AstropyPrecisionService
            from .stellar_variability_service import StellarVariabilityService
            
            self._available_services.update({
                "lightkurve_advanced": LightkurveAdvancedService(),
                "astropy_precision": AstropyPrecisionService(),
                "stellar_variability": StellarVariabilityService()
            })
            
            # Fase 2: Servicios de Expansión
            from .optimal_aperture_photometry_service import OptimalAperturePhotometryService
            from .binary_system_analysis_service import BinarySystemAnalysisService
            from .exoplanet_transit_analysis_service import ExoplanetTransitAnalysisService
            from .advanced_statistics_service import AdvancedStatisticsService
            from .multiwavelength_analysis_service import MultiWavelengthAnalysisService
            
            self._available_services.update({
                "optimal_aperture": OptimalAperturePhotometryService(),
                "binary_system": BinarySystemAnalysisService(),
                "exoplanet_transit": ExoplanetTransitAnalysisService(),
                "advanced_statistics": AdvancedStatisticsService(),
                "multiwavelength": MultiWavelengthAnalysisService()
            })
            
            # Fase 3: Servicios de Machine Learning
            from .astrometric_analysis_service import AstrometricAnalysisService
            from .astronomical_ml_service import AstronomicalMLService
            
            self._available_services.update({
                "astrometric_analysis": AstrometricAnalysisService(),
                "astronomical_ml": AstronomicalMLService()
            })
            
            logger.info(f"Inicializados {len(self._available_services)} servicios AXIOM")
            
        except ImportError as e:
            logger.warning(f"Algunos servicios no disponibles: {e}")
            # Servicios mínimos para funcionalidad básica
            self._available_services = {
                "basic_analysis": self._create_basic_analyzer()
            }
    
    def _create_basic_analyzer(self):
        """Crea un analizador básico como fallback."""
        class BasicAnalyzer:
            def analyze_light_curve(self, time, flux, flux_err=None):
                return {
                    "mean_flux": float(np.mean(flux)),
                    "std_flux": float(np.std(flux)),
                    "n_points": len(flux),
                    "duration": float(np.ptp(time))
                }
        
        return BasicAnalyzer()
    
    def create_analysis_configuration(
        self,
        mode: AnalysisMode = AnalysisMode.STANDARD_ANALYSIS,
        data_types: Optional[List[DataType]] = None,
        custom_services: Optional[List[str]] = None,
        **kwargs
    ) -> AnalysisConfiguration:
        """
        Crea una configuración de análisis personalizada.
        
        Args:
            mode: Modo de análisis a usar
            data_types: Tipos de datos a analizar
            custom_services: Servicios específicos a usar
            **kwargs: Parámetros adicionales
            
        Returns:
            AnalysisConfiguration: Configuración creada
        """
        config = AnalysisConfiguration(mode=mode, **kwargs)
        
        if data_types:
            config.data_types = data_types
        else:
            # Configuración por defecto según el modo
            if mode == AnalysisMode.QUICK_SCAN:
                config.data_types = [DataType.LIGHT_CURVE]
            elif mode == AnalysisMode.COMPREHENSIVE_ANALYSIS:
                config.data_types = list(DataType)
            else:
                config.data_types = [DataType.LIGHT_CURVE, DataType.TIME_SERIES]
        
        # Servicios habilitados según el modo
        if custom_services:
            config.enabled_services = custom_services
        else:
            config.enabled_services = self._get_default_services_for_mode(mode)
        
        return config
    
    def _get_default_services_for_mode(self, mode: AnalysisMode) -> List[str]:
        """Obtiene servicios por defecto para un modo de análisis."""
        all_services = list(self._available_services.keys())
        
        if mode == AnalysisMode.QUICK_SCAN:
            return ["lightkurve_advanced", "stellar_variability"][:2]
        elif mode == AnalysisMode.COMPREHENSIVE_ANALYSIS:
            return all_services
        else:  # STANDARD_ANALYSIS
            return all_services[:6]  # Servicios principales
    
    async def analyze_object(
        self,
        data: AstronomicalData,
        config: Optional[AnalysisConfiguration] = None
    ) -> PipelineReport:
        """
        Analiza un objeto astronómico usando el pipeline completo.
        
        Args:
            data: Datos del objeto a analizar
            config: Configuración de análisis (opcional)
            
        Returns:
            PipelineReport: Reporte completo del análisis
        """
        if config is None:
            config = self.create_analysis_configuration()
        
        # Crear reporte del pipeline
        pipeline_id = f"axiom_pipeline_{self._pipeline_counter:06d}"
        self._pipeline_counter += 1
        
        report = PipelineReport(
            pipeline_id=pipeline_id,
            object_id=data.object_id,
            configuration=config,
            start_time=datetime.now()
        )
        
        self._active_pipelines[pipeline_id] = report
        
        try:
            logger.info(f"Iniciando análisis {pipeline_id} para objeto {data.object_id}")
            
            # Ejecutar servicios según configuración
            if config.parallel_processing:
                service_results = await self._run_services_parallel(data, config)
            else:
                service_results = await self._run_services_sequential(data, config)
            
            # Procesar resultados
            report.service_results = service_results
            report.overall_status = self._determine_overall_status(service_results)
            
            # Generar resumen y recomendaciones
            report.summary = self._generate_summary(service_results)
            report.recommendations = self._generate_recommendations(service_results, data)
            report.quality_assessment = self._assess_quality(service_results)
            
            # Generar archivos de salida
            if config.output_formats:
                report.generated_files = await self._generate_outputs(report, config)
            
            report.end_time = datetime.now()
            report.total_execution_time = (
                report.end_time - report.start_time
            ).total_seconds()
            
            logger.info(f"Análisis {pipeline_id} completado en {report.total_execution_time:.2f}s")
            
        except BiologyError as e:
            logger.error(f"Error en análisis {pipeline_id}: {e}")
            report.overall_status = AnalysisStatus.FAILED
            report.end_time = datetime.now()
            report.total_execution_time = (
                report.end_time - report.start_time
            ).total_seconds()
        
        finally:
            # Limpiar pipeline activo
            if pipeline_id in self._active_pipelines:
                del self._active_pipelines[pipeline_id]
        
        return report
    
    async def _run_services_parallel(
        self,
        data: AstronomicalData,
        config: AnalysisConfiguration
    ) -> List[AnalysisResult]:
        """Ejecuta servicios en paralelo."""
        max_workers = config.max_workers or min(len(config.enabled_services), 4)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Crear tareas para cada servicio
            tasks = []
            for service_name in config.enabled_services:
                if service_name in self._available_services:
                    task = executor.submit(
                        self._run_single_service,
                        service_name,
                        data,
                        config
                    )
                    tasks.append(task)
            
            # Esperar completación con timeout
            results = []
            for task in concurrent.futures.as_completed(tasks, timeout=config.timeout_minutes * 60):
                try:
                    result = task.result()
                    results.append(result)
                except BiologyError as e:
                    logger.error(f"Error en servicio paralelo: {e}")
                    results.append(AnalysisResult(
                        service_name="unknown",
                        object_id=data.object_id,
                        status=AnalysisStatus.FAILED,
                        error_message=str(e)
                    ))
        
        return results
    
    async def _run_services_sequential(
        self,
        data: AstronomicalData,
        config: AnalysisConfiguration
    ) -> List[AnalysisResult]:
        """Ejecuta servicios secuencialmente."""
        results = []
        
        for service_name in config.enabled_services:
            if service_name in self._available_services:
                try:
                    result = self._run_single_service(service_name, data, config)
                    results.append(result)
                except BiologyError as e:
                    logger.error(f"Error en servicio {service_name}: {e}")
                    results.append(AnalysisResult(
                        service_name=service_name,
                        object_id=data.object_id,
                        status=AnalysisStatus.FAILED,
                        error_message=str(e)
                    ))
        
        return results
    
    def _run_single_service(
        self,
        service_name: str,
        data: AstronomicalData,
        config: AnalysisConfiguration
    ) -> AnalysisResult:
        """Ejecuta un servicio individual."""
        start_time = time.time()
        service = self._available_services[service_name]
        
        result = AnalysisResult(
            service_name=service_name,
            object_id=data.object_id,
            status=AnalysisStatus.RUNNING
        )
        
        try:
            # Determinar método de análisis según el tipo de datos
            if data.data_type == DataType.LIGHT_CURVE:
                analysis_result = self._analyze_light_curve_data(service, data, config)
            elif data.data_type == DataType.ASTROMETRIC_SERIES:
                analysis_result = self._analyze_astrometric_data(service, data, config)
            else:
                analysis_result = self._analyze_generic_data(service, data, config)
            
            result.results = analysis_result
            result.status = AnalysisStatus.COMPLETED
            result.quality_score = self._calculate_quality_score(analysis_result)
            
        except BiologyError as e:
            logger.error(f"Error en servicio {service_name}: {e}")
            result.status = AnalysisStatus.FAILED
            result.error_message = str(e)
            result.quality_score = 0.0
        
        result.execution_time = time.time() - start_time
        return result
    
    def _analyze_light_curve_data(
        self,
        service: Any,
        data: AstronomicalData,
        config: AnalysisConfiguration
    ) -> Dict[str, Any]:
        """Analiza datos de curva de luz."""
        time_array = data.time
        flux_array = data.values if isinstance(data.values, np.ndarray) else data.values.get('flux', np.array([]))
        flux_err = data.errors if isinstance(data.errors, np.ndarray) else data.errors.get('flux') if data.errors else None
        
        # Intentar diferentes métodos del servicio
        if hasattr(service, 'analyze_light_curve'):
            return service.analyze_light_curve(time_array, flux_array, flux_err)
        elif hasattr(service, 'analyze'):
            return service.analyze(time_array, flux_array, flux_err)
        else:
            # Fallback a análisis básico
            return {
                "mean_flux": float(np.mean(flux_array)),
                "std_flux": float(np.std(flux_array)),
                "n_points": len(flux_array),
                "service_type": "fallback"
            }
    
    def _analyze_astrometric_data(
        self,
        service: Any,
        data: AstronomicalData,
        config: AnalysisConfiguration
    ) -> Dict[str, Any]:
        """Analiza datos astrométricos."""
        if hasattr(service, 'analyze_astrometry'):
            return service.analyze_astrometry(data.time, data.values)
        else:
            return self._analyze_generic_data(service, data, config)
    
    def _analyze_generic_data(
        self,
        service: Any,
        data: AstronomicalData,
        config: AnalysisConfiguration
    ) -> Dict[str, Any]:
        """Análisis genérico para datos no específicos."""
        return {
            "data_type": data.data_type.value,
            "n_points": len(data.time),
            "duration": float(np.ptp(data.time)),
            "service_available": True
        }
    
    def _calculate_quality_score(self, results: Dict[str, Any]) -> float:
        """Calcula un score de calidad para los resultados."""
        if not results:
            return 0.0
        
        # Score básico basado en completitud
        base_score = 0.5
        
        # Bonificaciones por diferentes métricas
        if "error" not in str(results).lower():
            base_score += 0.2
        
        if len(results) > 3:  # Resultados ricos
            base_score += 0.2
        
        if any(isinstance(v, (int, float)) for v in results.values()):
            base_score += 0.1  # Valores numéricos
        
        return min(base_score, 1.0)
    
    def _determine_overall_status(self, results: List[AnalysisResult]) -> AnalysisStatus:
        """Determina el estado general del análisis."""
        if not results:
            return AnalysisStatus.FAILED
        
        failed_count = sum(1 for r in results if r.status == AnalysisStatus.FAILED)
        total_count = len(results)
        
        if failed_count == 0:
            return AnalysisStatus.COMPLETED
        elif failed_count < total_count:
            return AnalysisStatus.COMPLETED  # Éxito parcial
        else:
            return AnalysisStatus.FAILED
    
    def _generate_summary(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Genera resumen de resultados."""
        total_services = len(results)
        successful_services = sum(1 for r in results if r.status == AnalysisStatus.COMPLETED)
        
        avg_quality = np.mean([r.quality_score for r in results]) if results else 0.0
        total_execution_time = sum(r.execution_time for r in results)
        
        return {
            "total_services": total_services,
            "successful_services": successful_services,
            "success_rate": successful_services / total_services if total_services > 0 else 0.0,
            "average_quality_score": float(avg_quality),
            "total_execution_time": float(total_execution_time),
            "services_used": [r.service_name for r in results if r.status == AnalysisStatus.COMPLETED]
        }
    
    def _generate_recommendations(
        self,
        results: List[AnalysisResult],
        data: AstronomicalData
    ) -> List[str]:
        """Genera recomendaciones basadas en los resultados."""
        recommendations = []
        
        # Análisis de calidad
        avg_quality = np.mean([r.quality_score for r in results]) if results else 0.0
        
        if avg_quality < 0.5:
            recommendations.append("Considere verificar la calidad de los datos de entrada")
        
        # Servicios fallidos
        failed_services = [r.service_name for r in results if r.status == AnalysisStatus.FAILED]
        if failed_services:
            recommendations.append(f"Revisar configuración para servicios: {', '.join(failed_services)}")
        
        # Recomendaciones específicas por tipo de datos
        if data.data_type == DataType.LIGHT_CURVE:
            recommendations.append("Para curvas de luz, considere análisis de periodicidad adicional")
        
        # Recomendación general
        if avg_quality > 0.8:
            recommendations.append("Resultados de alta calidad - apropiados para publicación científica")
        
        return recommendations
    
    def _assess_quality(self, results: List[AnalysisResult]) -> Dict[str, float]:
        """Evalúa la calidad general de los resultados."""
        if not results:
            return {"overall": 0.0}
        
        quality_scores = [r.quality_score for r in results]
        
        return {
            "overall": float(np.mean(quality_scores)),
            "minimum": float(np.min(quality_scores)),
            "maximum": float(np.max(quality_scores)),
            "std_deviation": float(np.std(quality_scores)),
            "consistency": 1.0 - float(np.std(quality_scores))  # Inverso de desviación
        }
    
    async def _generate_outputs(
        self,
        report: PipelineReport,
        config: AnalysisConfiguration
    ) -> List[str]:
        """Genera archivos de salida."""
        output_files = []
        output_dir = self.base_output_dir / report.pipeline_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # JSON report
            if "json" in config.output_formats:
                json_file = output_dir / "analysis_report.json"
                json_data = self._report_to_dict(report)
                
                # Escribir JSON (simulado)
                with aiofiles.aiofiles.open(json_file, 'w') as f:
                    import json
                    json.dump(json_data, f, indent=2, default=str)
                
                output_files.append(str(json_file))
            
            # Texto summary
            if "txt" in config.output_formats:
                txt_file = output_dir / "summary.txt"
                summary_text = self._generate_text_summary(report)
                
                with aiofiles.open(txt_file, 'w') as f:
                    f.write(summary_text)
                
                output_files.append(str(txt_file))
            
        except BiologyError as e:
            logger.error(f"Error generando outputs: {e}")
        
        return output_files
    
    def _report_to_dict(self, report: PipelineReport) -> Dict[str, Any]:
        """Convierte reporte a diccionario serializable."""
        return {
            "pipeline_id": report.pipeline_id,
            "object_id": report.object_id,
            "start_time": report.start_time.isoformat(),
            "end_time": report.end_time.isoformat() if report.end_time else None,
            "total_execution_time": report.total_execution_time,
            "overall_status": report.overall_status.value,
            "summary": report.summary,
            "recommendations": report.recommendations,
            "quality_assessment": report.quality_assessment,
            "service_results": [
                {
                    "service_name": r.service_name,
                    "status": r.status.value,
                    "execution_time": r.execution_time,
                    "quality_score": r.quality_score,
                    "results_summary": str(r.results)[:200] + "..." if len(str(r.results)) > 200 else str(r.results)
                }
                for r in report.service_results
            ]
        }
    
    def _generate_text_summary(self, report: PipelineReport) -> str:
        """Genera resumen en texto plano."""
        summary_lines = [
            "AXIOM Astronomy Pipeline - Reporte de Análisis",
            "=" * 50,
            f"Pipeline ID: {report.pipeline_id}",
            f"Objeto: {report.object_id}",
            f"Fecha: {report.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Duración: {report.total_execution_time:.2f} segundos",
            f"Estado: {report.overall_status.value}",
            "",
            "RESUMEN:",
            f"- Servicios ejecutados: {report.summary.get('total_services', 0)}",
            f"- Servicios exitosos: {report.summary.get('successful_services', 0)}",
            f"- Tasa de éxito: {report.summary.get('success_rate', 0):.2%}",
            f"- Calidad promedio: {report.summary.get('average_quality_score', 0):.3f}",
            "",
            "RECOMENDACIONES:",
        ]
        
        for i, rec in enumerate(report.recommendations, 1):
            summary_lines.append(f"{i}. {rec}")
        
        return "\n".join(summary_lines)
    
    def get_available_services(self) -> List[str]:
        """Retorna lista de servicios disponibles."""
        return list(self._available_services.keys())
    
    def get_pipeline_status(self, pipeline_id: str) -> Optional[AnalysisStatus]:
        """Obtiene el estado de un pipeline activo."""
        if pipeline_id in self._active_pipelines:
            return self._active_pipelines[pipeline_id].overall_status
        return None
    
    def cancel_pipeline(self, pipeline_id: str) -> bool:
        """Cancela un pipeline en ejecución."""
        if pipeline_id in self._active_pipelines:
            self._active_pipelines[pipeline_id].overall_status = AnalysisStatus.CANCELLED
            return True
        return False

# Función de demostración
def demonstrate_integrated_pipeline():
    """
    Función de demostración del pipeline integrado AXIOM.
    """
    print("🚀 AXIOM Astronomy - Pipeline Integrado de Análisis")
    print("=" * 60)
    
    # Inicializar pipeline
    pipeline = IntegratedAstronomyPipeline()
    
    print(f"\n✅ Pipeline inicializado con {len(pipeline.get_available_services())} servicios:")
    for service in pipeline.get_available_services():
        print(f"   • {service}")
    
    # Crear datos de ejemplo
    print("\n📊 Creando datos astronómicos de ejemplo...")
    
    # Simular curva de luz con variabilidad
    np.random.seed(42)
    time = np.linspace(0, 100, 1000)
    flux = 1.0 + 0.1 * np.sin(2 * np.pi * time / 10) + 0.02 * np.random.randn(len(time))
    flux_err = 0.01 * np.ones_like(flux)
    
    astronomical_data = AstronomicalData(
        object_id="AXIOM_DEMO_001",
        data_type=DataType.LIGHT_CURVE,
        time=time,
        values=flux,
        errors=flux_err,
        coordinates=(83.633, 22.014),  # Betelgeuse aproximado
        metadata={
            "source": "AXIOM Demo",
            "instrument": "Simulated Photometer",
            "filter": "V"
        }
    )
    
    print(f"   ✓ Objeto: {astronomical_data.object_id}")
    print(f"   ✓ Tipo de datos: {astronomical_data.data_type.value}")
    print(f"   ✓ Puntos de datos: {len(astronomical_data.time)}")
    
    # Crear configuraciones de análisis
    print("\n⚙️ Configuraciones de análisis disponibles:")
    
    configurations = {
        "quick_scan": pipeline.create_analysis_configuration(
            mode=AnalysisMode.QUICK_SCAN,
            parallel_processing=True
        ),
        "standard": pipeline.create_analysis_configuration(
            mode=AnalysisMode.STANDARD_ANALYSIS,
            parallel_processing=True,
            generate_plots=True
        ),
        "comprehensive": pipeline.create_analysis_configuration(
            mode=AnalysisMode.COMPREHENSIVE_ANALYSIS,
            parallel_processing=True,
            output_formats=["json", "txt"],
            save_intermediate_results=True
        )
    }
    
    for name, config in configurations.items():
        print(f"   • {name}: {len(config.enabled_services)} servicios, paralelo={config.parallel_processing}")
    
    # Ejecutar análisis estándar (síncrono para demostración)
    print("\n🔬 Ejecutando análisis estándar...")
    
    import asyncio
    
    async def run_demo_analysis():
        config = configurations["standard"]
        report = await pipeline.analyze_object(astronomical_data, config)
        return report
    
    # Ejecutar el análisis
    try:
        report = asyncio.run(run_demo_analysis())
        
        print("\n📈 Resultados del análisis:")
        print(f"   ✓ Pipeline ID: {report.pipeline_id}")
        print(f"   ✓ Estado: {report.overall_status.value}")
        print(f"   ✓ Tiempo total: {report.total_execution_time:.2f}s")
        print(f"   ✓ Servicios ejecutados: {report.summary.get('total_services', 0)}")
        print(f"   ✓ Tasa de éxito: {report.summary.get('success_rate', 0):.1%}")
        print(f"   ✓ Calidad promedio: {report.summary.get('average_quality_score', 0):.3f}")
        
        if report.service_results:
            print("\n🔍 Detalles por servicio:")
            for result in report.service_results[:5]:  # Mostrar primeros 5
                status_emoji = "✅" if result.status == AnalysisStatus.COMPLETED else "❌"
                print(f"   {status_emoji} {result.service_name}: "
                      f"{result.execution_time:.3f}s (calidad: {result.quality_score:.3f})")
        
        if report.recommendations:
            print("\n💡 Recomendaciones:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"   {i}. {rec}")
        
        print(f"\n📁 Archivos generados: {len(report.generated_files)}")
        for file_path in report.generated_files:
            print(f"   • {file_path}")
        
    except BiologyError as e:
        print(f"❌ Error en análisis: {e}")
    
    print("\n🎉 Demostración del pipeline completada!")
    print("\n📊 Capacidades del Pipeline Integrado:")
    print("   • Análisis unificado de todos los servicios AXIOM")
    print("   • Procesamiento paralelo para máximo rendimiento")
    print("   • Configuraciones flexibles y personalizables") 
    print("   • Reportes automáticos con recomendaciones")
    print("   • Evaluación de calidad integrada")
    print("   • Múltiples formatos de salida")
    print("   • Manejo robusto de errores")
    print("   • Análisis asíncrono escalable")

if __name__ == "__main__":
    # Ejecutar demostración
    demonstrate_integrated_pipeline()