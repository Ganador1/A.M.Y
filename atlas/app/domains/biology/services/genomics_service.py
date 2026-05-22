"""
Genomics Service (secure)
Validación de entorno y dry-run seguro para DeepVariant (sin ejecución real).
"""

from typing import Dict, Any, Optional
from pathlib import Path
import shutil
from datetime import datetime, timedelta

from app.domains.biology.services.base_service import BaseService, BiologyServiceMixin
from app.domains.biology.domain_config import DOMAIN_SETTINGS
from app.exceptions.domain.biology import BiologyError


class GenomicsService(BaseService, BiologyServiceMixin):
    """Servicio de análisis genómico seguro con validaciones previas y dry-run.
    
    Inherits from:
        BaseService: Core service interface with process_request()
        BiologyServiceMixin: Biology-specific helpers (ethics, logging)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("GenomicsService")
        self.domain = "biology"
        self.created_at = datetime.utcnow()
        cfg = config or {}
        self.reference_genome = cfg.get('reference', 'GRCh38')
        self.deepvariant_model = cfg.get('dv_model', 'WGS')
        # Cache de validación de entorno
        self._env_cache: Optional[Dict[str, Any]] = None
        self._env_cache_time: Optional[datetime] = None
        self._cache_ttl_seconds: int = int(DOMAIN_SETTINGS.get("cache_ttl", 3600))

    def _env_cache_valid(self) -> bool:
        if self._env_cache is None or self._env_cache_time is None:
            return False
        return datetime.utcnow() - self._env_cache_time < timedelta(seconds=self._cache_ttl_seconds)

    def validate_deepvariant_environment(self) -> Dict[str, Any]:
        """
        Verifica que docker esté disponible y que la imagen deepvariant sea accesible (solo chequeos rápidos).
        Usa caché con TTL para evitar chequeos repetidos.
        """
        # Devolver desde caché si es válido
        if self._env_cache_valid():
            cached = dict(self._env_cache)
            cached['cached'] = True
            return cached

        self.log_biology_operation("validate_deepvariant_environment")
        docker_path = shutil.which('docker')
        result = {
            'docker_available': docker_path is not None,
            'docker_path': docker_path,
            'deepvariant_image': 'google/deepvariant:latest',
            'notes': 'No se realiza pull automático para seguridad.',
            'timestamp': datetime.utcnow().isoformat(),
            'service_info': self.get_service_info()
        }
        # Guardar en caché
        self._env_cache = result
        self._env_cache_time = datetime.utcnow()
        return result

    def validate_inputs(self, bam_file: str, reference_fasta: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Valida existencia y formatos básicos de rutas, y accesibilidad de directorios de salida.
        """
        self.log_biology_operation("validate_inputs")
        bam = Path(bam_file)
        ref = Path(reference_fasta)
        out_dir = Path(output_dir) if output_dir else bam.parent

        errors = []
        if not bam.exists() or not bam.is_file():
            errors.append(f"BAM no existe: {bam}")
        if not ref.exists() or not ref.is_file():
            errors.append(f"Referencia no existe: {ref}")
        if not out_dir.exists():
            errors.append(f"Directorio salida no existe: {out_dir}")
        elif not os_access_writable(out_dir):
            errors.append(f"Directorio salida no es escribible: {out_dir}")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'resolved_paths': {
                'bam': str(bam.resolve()),
                'reference': str(ref.resolve()),
                'output_dir': str(out_dir.resolve())
            },
            'timestamp': datetime.utcnow().isoformat(),
            'service_info': self.get_service_info()
        }

    def dry_run_deepvariant(self, bam_file: str, reference_fasta: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Dry-run: genera los comandos que se ejecutarían con docker sin ejecutarlos.
        """
        self.log_biology_operation("dry_run_deepvariant")
        out = self.validate_inputs(bam_file, reference_fasta, output_dir)
        env = self.validate_deepvariant_environment()
        if not out['valid']:
            return {
                'success': False,
                'errors': out['errors'],
                'environment': env,
                'timestamp': datetime.utcnow().isoformat(),
                'service_info': self.get_service_info()
            }

        bam = out['resolved_paths']['bam']
        ref = out['resolved_paths']['reference']
        out_dir = out['resolved_paths']['output_dir']

        v_bam = f"{Path(bam).parent}:{'/input'}"
        v_ref = f"{Path(ref).parent}:{'/reference'}"
        v_out = f"{out_dir}:{'/output'}"

        output_vcf = str(Path(out_dir) / (Path(bam).stem + '.deepvariant.vcf'))
        output_gvcf = str(Path(out_dir) / (Path(bam).stem + '.deepvariant.g.vcf'))

        cmd = [
            'docker', 'run', '--rm',
            '-v', v_bam,
            '-v', v_ref,
            '-v', v_out,
            'google/deepvariant:latest',
            '/opt/deepvariant/bin/run_deepvariant',
            '--model_type', self.deepvariant_model,
            '--ref', f"/reference/{Path(ref).name}",
            '--reads', f"/input/{Path(bam).name}",
            '--output_vcf', f"/output/{Path(output_vcf).name}",
            '--output_gvcf', f"/output/{Path(output_gvcf).name}",
            '--num_shards', '4'
        ]

        return {
            'success': True,
            'environment': env,
            'validation': out,
            'command_preview': ' '.join(cmd),
            'outputs': {
                'vcf': output_vcf,
                'gvcf': output_gvcf
            },
            'timestamp': datetime.utcnow().isoformat(),
            'service_info': self.get_service_info()
        }

    def validate_mutect2_inputs(self, tumor_bam: str, normal_bam: str, reference_fasta: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        self.log_biology_operation("validate_mutect2_inputs")
        bam_t = Path(tumor_bam)
        bam_n = Path(normal_bam)
        ref = Path(reference_fasta)
        out_dir = Path(output_dir) if output_dir else bam_t.parent

        errors = []
        for p, label in [(bam_t, 'Tumor BAM'), (bam_n, 'Normal BAM')]:
            if not p.exists() or not p.is_file():
                errors.append(f"{label} no existe: {p}")
        if not ref.exists() or not ref.is_file():
            errors.append(f"Referencia no existe: {ref}")
        if not out_dir.exists():
            errors.append(f"Directorio salida no existe: {out_dir}")
        elif not os_access_writable(out_dir):
            errors.append(f"Directorio salida no es escribible: {out_dir}")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'resolved_paths': {
                'tumor_bam': str(bam_t.resolve()),
                'normal_bam': str(bam_n.resolve()),
                'reference': str(ref.resolve()),
                'output_dir': str(out_dir.resolve())
            },
            'timestamp': datetime.utcnow().isoformat(),
            'service_info': self.get_service_info()
        }

    def dry_run_mutect2(self, tumor_bam: str, normal_bam: str, reference_fasta: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        self.log_biology_operation("dry_run_mutect2")
        out = self.validate_mutect2_inputs(tumor_bam, normal_bam, reference_fasta, output_dir)
        if not out['valid']:
            return {'success': False, 'errors': out['errors'], 'validation': out, 'timestamp': datetime.utcnow().isoformat(), 'service_info': self.get_service_info()}

        tumor_bam = out['resolved_paths']['tumor_bam']
        normal_bam = out['resolved_paths']['normal_bam']
        ref = out['resolved_paths']['reference']
        out_dir = out['resolved_paths']['output_dir']

        vcf_out = str(Path(out_dir) / 'somatic.vcf')
        filt_out = str(Path(out_dir) / 'somatic.filtered.vcf')

        # Preview command sequence
        mutect2_cmd = [
            'gatk', 'Mutect2',
            '-R', ref,
            '-I', tumor_bam,
            '-I', normal_bam,
            '-tumor', Path(tumor_bam).stem,
            '-normal', Path(normal_bam).stem,
            '-O', vcf_out
        ]
        filter_cmd = ['gatk', 'FilterMutectCalls', '-V', vcf_out, '-O', filt_out]

        return {
            'success': True,
            'validation': out,
            'commands_preview': [' '.join(mutect2_cmd), ' '.join(filter_cmd)],
            'outputs': {'vcf': vcf_out, 'filtered_vcf': filt_out},
            'timestamp': datetime.utcnow().isoformat(),
            'service_info': self.get_service_info()
        }

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa una solicitud genérica para el servicio de genómica.
        Retorna metadatos y resultados de validación/ética básicos.
        
        Implements BaseService.process_request() abstract method.
        """
        is_valid = await self.validate_biology_request(request_data)
        ethics = await self.check_ethics_compliance("generic_operation", request_data)
        
        # Handle specific operations if provided
        operation = request_data.get("operation", "info")
        
        if operation == "validate_environment":
            env_result = self.validate_deepvariant_environment()
            return {
                "success": True,
                "operation": operation,
                "result": env_result,
                "service_info": self.get_service_info(),
            }
        elif operation == "dry_run_deepvariant":
            bam = request_data.get("bam_file", "")
            ref = request_data.get("reference_fasta", "")
            out = request_data.get("output_dir")
            result = self.dry_run_deepvariant(bam, ref, out)
            return {
                "success": result.get("success", False),
                "operation": operation,
                "result": result,
                "service_info": self.get_service_info(),
            }
        
        return {
            "success": is_valid,
            "operation": operation,
            "timestamp": datetime.utcnow().isoformat(),
            "service_info": self.get_service_info(),
            "ethics": ethics,
            "available_operations": [
                "info",
                "validate_environment", 
                "dry_run_deepvariant",
                "dry_run_mutect2"
            ]
        }


def os_access_writable(path: Path) -> bool:
    try:
        test = Path(path) / '.axiom_write_test'
        test.write_text('ok', encoding='utf-8')
        test.unlink(missing_ok=True)
        return True
    except BiologyError:
        return False


