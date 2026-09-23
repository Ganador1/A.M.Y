"""
Servicio de Matemáticas Bioinformáticas
Proporciona herramientas matemáticas especializadas para análisis biológicos y bioinformáticos.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import logging
from scipy import stats, optimize, linalg
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
import networkx as nx
from app.exceptions.domain.mathematics import MathematicsError
try:
    from Bio import SeqIO, Phylo, AlignIO
    from Bio.Seq import Seq
    from Bio.SeqRecord import SeqRecord
    from Bio.SeqUtils import molecular_weight
    from Bio.SeqUtils.ProtParam import ProteinAnalysis
    from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
    from Bio.Align import MultipleSeqAlignment, PairwiseAligner
    # Importar GC de forma compatible
    try:
        from Bio.SeqUtils import GC
    except ImportError:
        # Fallback para versiones más nuevas de Biopython
        def GC(seq):
            """Calcular contenido GC manualmente"""
            seq_str = str(seq).upper()
            gc_count = seq_str.count('G') + seq_str.count('C')
            return (gc_count / len(seq_str)) * 100 if len(seq_str) > 0 else 0
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False
    # Definir funciones fallback
    def GC(seq):
        seq_str = str(seq).upper()
        gc_count = seq_str.count('G') + seq_str.count('C')
        return (gc_count / len(seq_str)) * 100 if len(seq_str) > 0 else 0
import matplotlib.pyplot as plt
try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except Exception:
    SEABORN_AVAILABLE = False
    sns = None

logger = logging.getLogger(__name__)

class SequenceType(Enum):
    DNA = "dna"
    RNA = "rna"
    PROTEIN = "protein"

class AnalysisType(Enum):
    PHYLOGENETIC = "phylogenetic"
    POPULATION_GENETICS = "population_genetics"
    PROTEIN_STRUCTURE = "protein_structure"
    GENE_EXPRESSION = "gene_expression"
    GENOMIC_VARIATION = "genomic_variation"

@dataclass
class SequenceData:
    """Datos de secuencia biológica"""
    sequence: str
    sequence_type: SequenceType
    identifier: str
    description: Optional[str] = None
    quality_scores: Optional[List[int]] = None

@dataclass
class PhylogeneticResult:
    """Resultado de análisis filogenético"""
    tree: Any  # Bio.Phylo tree object
    distance_matrix: np.ndarray
    bootstrap_values: Optional[List[float]] = None
    tree_statistics: Dict[str, float] = None

@dataclass
class PopulationGeneticsResult:
    """Resultado de análisis de genética de poblaciones"""
    allele_frequencies: Dict[str, float]
    hardy_weinberg_p: float
    fst_values: Optional[Dict[str, float]] = None
    diversity_indices: Dict[str, float] = None

@dataclass
class ProteinAnalysisResult:
    """Resultado de análisis de proteínas"""
    molecular_weight: float
    isoelectric_point: float
    hydrophobicity_profile: List[float]
    secondary_structure_prediction: List[str]
    disorder_regions: List[Tuple[int, int]]

class BioinformaticsService:
    """
    Servicio de Matemáticas Bioinformáticas
    
    Proporciona análisis matemáticos especializados para:
    - Análisis filogenético y evolutivo
    - Genética de poblaciones
    - Análisis de secuencias
    - Estructura de proteínas
    - Expresión génica
    - Variación genómica
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if BIOPYTHON_AVAILABLE:
            self.pairwise_aligner = PairwiseAligner()
            self._setup_aligner()
        else:
            self.pairwise_aligner = None
    
    def _setup_aligner(self):
        """Configurar el alineador de secuencias"""
        self.pairwise_aligner.match_score = 2
        self.pairwise_aligner.mismatch_score = -1
        self.pairwise_aligner.open_gap_score = -2
        self.pairwise_aligner.extend_gap_score = -0.5
    
    # === ANÁLISIS FILOGENÉTICO ===
    
    def phylogenetic_analysis(self, sequences: List[SequenceData], 
                            method: str = "nj") -> PhylogeneticResult:
        """
        Realizar análisis filogenético
        
        Args:
            sequences: Lista de secuencias para analizar
            method: Método de construcción del árbol ('nj', 'upgma')
        
        Returns:
            PhylogeneticResult con árbol filogenético y estadísticas
        """
        try:
            # Crear alineamiento múltiple
            alignment = self._create_multiple_alignment(sequences)
            
            # Calcular matriz de distancias
            calculator = DistanceCalculator('identity')
            distance_matrix = calculator.get_distance(alignment)
            
            # Construir árbol filogenético
            constructor = DistanceTreeConstructor()
            if method == "nj":
                tree = constructor.nj(distance_matrix)
            elif method == "upgma":
                tree = constructor.upgma(distance_matrix)
            else:
                raise ValueError(f"Método no soportado: {method}")
            
            # Calcular estadísticas del árbol
            tree_stats = self._calculate_tree_statistics(tree)
            
            # Convertir matriz de distancias a numpy array
            dist_array = np.array([[distance_matrix[i, j] for j in range(len(distance_matrix.names))] 
                                 for i in range(len(distance_matrix.names))])
            
            return PhylogeneticResult(
                tree=tree,
                distance_matrix=dist_array,
                tree_statistics=tree_stats
            )
            
        except MathematicsError as e:
            self.logger.error(f"Error en análisis filogenético: {e}")
            raise
    
    def _create_multiple_alignment(self, sequences: List[SequenceData]):
        """Crear alineamiento múltiple de secuencias"""
        # Implementación simplificada - en producción usar MUSCLE, ClustalW, etc.
        from Bio.Align import MultipleSeqAlignment
        from Bio.SeqRecord import SeqRecord
        
        seq_records = []
        for seq_data in sequences:
            record = SeqRecord(Seq(seq_data.sequence), 
                             id=seq_data.identifier,
                             description=seq_data.description or "")
            seq_records.append(record)
        
        return MultipleSeqAlignment(seq_records)
    
    def _calculate_tree_statistics(self, tree) -> Dict[str, float]:
        """Calcular estadísticas del árbol filogenético"""
        stats = {}
        
        # Número de nodos
        stats['total_nodes'] = len(list(tree.find_clades()))
        stats['terminal_nodes'] = len(tree.get_terminals())
        stats['internal_nodes'] = stats['total_nodes'] - stats['terminal_nodes']
        
        # Longitud total del árbol
        stats['total_branch_length'] = tree.total_branch_length()
        
        # Profundidad máxima
        stats['max_depth'] = max(tree.distance(terminal) for terminal in tree.get_terminals())
        
        return stats
    
    # === GENÉTICA DE POBLACIONES ===
    
    def population_genetics_analysis(self, genotype_data: pd.DataFrame) -> PopulationGeneticsResult:
        """
        Análisis de genética de poblaciones
        
        Args:
            genotype_data: DataFrame con datos de genotipos
        
        Returns:
            PopulationGeneticsResult con análisis poblacional
        """
        try:
            # Calcular frecuencias alélicas
            allele_freq = self._calculate_allele_frequencies(genotype_data)
            
            # Test de Hardy-Weinberg
            hw_p = self._hardy_weinberg_test(genotype_data)
            
            # Índices de diversidad
            diversity = self._calculate_diversity_indices(genotype_data)
            
            return PopulationGeneticsResult(
                allele_frequencies=allele_freq,
                hardy_weinberg_p=hw_p,
                diversity_indices=diversity
            )
            
        except MathematicsError as e:
            self.logger.error(f"Error en análisis de genética de poblaciones: {e}")
            raise
    
    def _calculate_allele_frequencies(self, genotype_data: pd.DataFrame) -> Dict[str, float]:
        """Calcular frecuencias alélicas"""
        allele_counts = {}
        total_alleles = 0
        
        for column in genotype_data.columns:
            for genotype in genotype_data[column].dropna():
                # Asumir genotipos como "AA", "AB", "BB", etc.
                alleles = list(genotype)
                for allele in alleles:
                    allele_counts[allele] = allele_counts.get(allele, 0) + 1
                    total_alleles += 1
        
        return {allele: count/total_alleles for allele, count in allele_counts.items()}
    
    def _hardy_weinberg_test(self, genotype_data: pd.DataFrame) -> float:
        """Test de equilibrio de Hardy-Weinberg"""
        # Implementación simplificada del test chi-cuadrado
        observed_counts = {}
        expected_counts = {}
        
        # Contar genotipos observados
        for column in genotype_data.columns:
            for genotype in genotype_data[column].dropna():
                observed_counts[genotype] = observed_counts.get(genotype, 0) + 1
        
        # Calcular frecuencias esperadas (implementación básica)
        total_individuals = sum(observed_counts.values())
        
        # Chi-cuadrado test (simplificado)
        chi_square = 0
        df = len(observed_counts) - 1
        
        if df > 0:
            expected_per_genotype = total_individuals / len(observed_counts)
            for genotype, observed in observed_counts.items():
                chi_square += (observed - expected_per_genotype)**2 / expected_per_genotype
            
            p_value = 1 - stats.chi2.cdf(chi_square, df)
            return p_value
        
        return 1.0
    
    def _calculate_diversity_indices(self, genotype_data: pd.DataFrame) -> Dict[str, float]:
        """Calcular índices de diversidad genética"""
        diversity = {}
        
        # Diversidad de Shannon
        allele_freq = self._calculate_allele_frequencies(genotype_data)
        shannon_diversity = -sum(freq * np.log(freq) for freq in allele_freq.values() if freq > 0)
        diversity['shannon_diversity'] = shannon_diversity
        
        # Heterocigosidad esperada
        expected_heterozygosity = 1 - sum(freq**2 for freq in allele_freq.values())
        diversity['expected_heterozygosity'] = expected_heterozygosity
        
        return diversity
    
    # === ANÁLISIS DE PROTEÍNAS ===
    
    def protein_analysis(self, protein_sequence: str) -> ProteinAnalysisResult:
        """
        Análisis completo de proteínas
        
        Args:
            protein_sequence: Secuencia de aminoácidos
        
        Returns:
            ProteinAnalysisResult con análisis de la proteína
        """
        try:
            seq = Seq(protein_sequence)
            
            # Peso molecular
            mol_weight = molecular_weight(seq, seq_type='protein')
            
            # Punto isoeléctrico (aproximación)
            isoelectric_pt = self._calculate_isoelectric_point(protein_sequence)
            
            # Perfil de hidrofobicidad
            hydrophobicity = self._calculate_hydrophobicity_profile(protein_sequence)
            
            # Predicción de estructura secundaria (simplificada)
            secondary_structure = self._predict_secondary_structure(protein_sequence)
            
            # Regiones de desorden
            disorder_regions = self._predict_disorder_regions(protein_sequence)
            
            return ProteinAnalysisResult(
                molecular_weight=mol_weight,
                isoelectric_point=isoelectric_pt,
                hydrophobicity_profile=hydrophobicity,
                secondary_structure_prediction=secondary_structure,
                disorder_regions=disorder_regions
            )
            
        except MathematicsError as e:
            self.logger.error(f"Error en análisis de proteínas: {e}")
            raise
    
    def _calculate_isoelectric_point(self, sequence: str) -> float:
        """Calcular punto isoeléctrico aproximado"""
        # Valores de pKa simplificados para aminoácidos
        pka_values = {
            'D': 3.9, 'E': 4.3, 'H': 6.0, 'C': 8.3,
            'Y': 10.1, 'K': 10.5, 'R': 12.5
        }
        
        # Cálculo simplificado
        acidic_residues = sum(1 for aa in sequence if aa in ['D', 'E'])
        basic_residues = sum(1 for aa in sequence if aa in ['K', 'R', 'H'])
        
        if acidic_residues == basic_residues:
            return 7.0
        elif acidic_residues > basic_residues:
            return 6.0 - (acidic_residues - basic_residues) * 0.5
        else:
            return 8.0 + (basic_residues - acidic_residues) * 0.5
    
    def _calculate_hydrophobicity_profile(self, sequence: str) -> List[float]:
        """Calcular perfil de hidrofobicidad"""
        # Escala de hidrofobicidad de Kyte-Doolittle
        hydrophobicity_scale = {
            'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
            'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
            'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
            'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2
        }
        
        window_size = 9
        profile = []
        
        for i in range(len(sequence) - window_size + 1):
            window = sequence[i:i + window_size]
            avg_hydrophobicity = np.mean([hydrophobicity_scale.get(aa, 0) for aa in window])
            profile.append(avg_hydrophobicity)
        
        return profile
    
    def _predict_secondary_structure(self, sequence: str) -> List[str]:
        """Predicción simplificada de estructura secundaria"""
        # Implementación muy básica - en producción usar PSIPRED, JPred, etc.
        structure = []
        
        for i, aa in enumerate(sequence):
            # Reglas muy simplificadas
            if aa in ['P']:  # Prolina rompe estructuras
                structure.append('C')  # Coil
            elif aa in ['A', 'E', 'L']:  # Aminoácidos que favorecen hélices
                structure.append('H')  # Helix
            elif aa in ['V', 'I', 'Y', 'F']:  # Aminoácidos que favorecen láminas
                structure.append('E')  # Extended (beta sheet)
            else:
                structure.append('C')  # Coil
        
        return structure
    
    def _predict_disorder_regions(self, sequence: str) -> List[Tuple[int, int]]:
        """Predicción de regiones desordenadas"""
        # Implementación simplificada basada en composición de aminoácidos
        disorder_prone = set(['P', 'E', 'S', 'Q', 'K', 'A', 'R'])
        
        regions = []
        start = None
        
        for i, aa in enumerate(sequence):
            if aa in disorder_prone:
                if start is None:
                    start = i
            else:
                if start is not None and i - start >= 10:  # Mínimo 10 residuos
                    regions.append((start, i - 1))
                start = None
        
        # Verificar región final
        if start is not None and len(sequence) - start >= 10:
            regions.append((start, len(sequence) - 1))
        
        return regions
    
    # === ANÁLISIS DE EXPRESIÓN GÉNICA ===
    
    def gene_expression_analysis(self, expression_data: pd.DataFrame, 
                               conditions: List[str]) -> Dict[str, Any]:
        """
        Análisis de expresión génica diferencial
        
        Args:
            expression_data: DataFrame con datos de expresión
            conditions: Lista de condiciones experimentales
        
        Returns:
            Diccionario con resultados del análisis
        """
        try:
            results = {}
            
            # Análisis de componentes principales
            pca_result = self._perform_pca_analysis(expression_data)
            results['pca'] = pca_result
            
            # Clustering de genes
            clustering_result = self._cluster_genes(expression_data)
            results['clustering'] = clustering_result
            
            # Análisis de expresión diferencial
            if len(conditions) >= 2:
                diff_expr = self._differential_expression_analysis(expression_data, conditions)
                results['differential_expression'] = diff_expr
            
            # Análisis de co-expresión
            coexpression = self._coexpression_analysis(expression_data)
            results['coexpression'] = coexpression
            
            return results
            
        except MathematicsError as e:
            self.logger.error(f"Error en análisis de expresión génica: {e}")
            raise
    
    def _perform_pca_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Análisis de componentes principales"""
        pca = PCA(n_components=min(10, data.shape[1]))
        pca_result = pca.fit_transform(data.T)  # Transponer para genes como features
        
        return {
            'components': pca_result,
            'explained_variance_ratio': pca.explained_variance_ratio_,
            'cumulative_variance': np.cumsum(pca.explained_variance_ratio_)
        }
    
    def _cluster_genes(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Clustering de genes basado en patrones de expresión"""
        # Normalizar datos
        normalized_data = (data - data.mean()) / data.std()
        
        # K-means clustering
        n_clusters = min(8, data.shape[0] // 10)  # Heurística para número de clusters
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(normalized_data)
        
        # Calcular silhouette score
        silhouette_avg = silhouette_score(normalized_data, cluster_labels)
        
        return {
            'cluster_labels': cluster_labels,
            'n_clusters': n_clusters,
            'silhouette_score': silhouette_avg,
            'cluster_centers': kmeans.cluster_centers_
        }
    
    def _differential_expression_analysis(self, data: pd.DataFrame, 
                                        conditions: List[str]) -> Dict[str, Any]:
        """Análisis de expresión diferencial entre condiciones"""
        # Implementación simplificada usando t-test
        results = {}
        
        # Asumir que las columnas están etiquetadas por condición
        condition1_cols = [col for col in data.columns if conditions[0] in col]
        condition2_cols = [col for col in data.columns if conditions[1] in col]
        
        if len(condition1_cols) > 0 and len(condition2_cols) > 0:
            p_values = []
            fold_changes = []
            
            for gene in data.index:
                group1 = data.loc[gene, condition1_cols]
                group2 = data.loc[gene, condition2_cols]
                
                # T-test
                t_stat, p_val = stats.ttest_ind(group1, group2)
                p_values.append(p_val)
                
                # Fold change (log2)
                mean1 = np.mean(group1)
                mean2 = np.mean(group2)
                fold_change = np.log2((mean2 + 1) / (mean1 + 1))
                fold_changes.append(fold_change)
            
            # Corrección múltiple (Benjamini-Hochberg)
            from scipy.stats import false_discovery_control
            adjusted_p = false_discovery_control(p_values)
            
            results = {
                'p_values': p_values,
                'adjusted_p_values': adjusted_p,
                'fold_changes': fold_changes,
                'significant_genes': [gene for i, gene in enumerate(data.index) 
                                    if adjusted_p[i] < 0.05]
            }
        
        return results
    
    def _coexpression_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Análisis de co-expresión génica"""
        # Calcular matriz de correlación
        correlation_matrix = data.T.corr()
        
        # Crear red de co-expresión
        threshold = 0.7  # Umbral de correlación
        G = nx.Graph()
        
        genes = list(data.index)
        G.add_nodes_from(genes)
        
        for i, gene1 in enumerate(genes):
            for j, gene2 in enumerate(genes[i+1:], i+1):
                corr = correlation_matrix.loc[gene1, gene2]
                if abs(corr) > threshold:
                    G.add_edge(gene1, gene2, weight=abs(corr))
        
        # Análisis de red
        network_stats = {
            'nodes': G.number_of_nodes(),
            'edges': G.number_of_edges(),
            'density': nx.density(G),
            'clustering_coefficient': nx.average_clustering(G),
            'connected_components': nx.number_connected_components(G)
        }
        
        return {
            'correlation_matrix': correlation_matrix,
            'network': G,
            'network_statistics': network_stats
        }
    
    # === UTILIDADES ===
    
    def sequence_alignment(self, seq1: str, seq2: str) -> Dict[str, Any]:
        """Alineamiento de secuencias por pares"""
        try:
            alignments = self.pairwise_aligner.align(seq1, seq2)
            best_alignment = alignments[0]
            
            return {
                'score': best_alignment.score,
                'alignment': str(best_alignment),
                'identity': self._calculate_identity(best_alignment),
                'similarity': self._calculate_similarity(best_alignment)
            }
            
        except MathematicsError as e:
            self.logger.error(f"Error en alineamiento de secuencias: {e}")
            raise
    
    def _calculate_identity(self, alignment) -> float:
        """Calcular identidad del alineamiento"""
        aligned_seq1, aligned_seq2 = str(alignment).split('\n')[0::2]
        matches = sum(1 for a, b in zip(aligned_seq1, aligned_seq2) if a == b and a != '-')
        total_length = len(aligned_seq1)
        return matches / total_length if total_length > 0 else 0.0
    
    def _calculate_similarity(self, alignment) -> float:
        """Calcular similitud del alineamiento"""
        # Implementación simplificada - en producción usar matrices de sustitución
        return self._calculate_identity(alignment)  # Placeholder
    
    def calculate_gc_content(self, sequence: str) -> float:
        """Calcular contenido GC de una secuencia"""
        return GC(sequence)
    
    def translate_dna(self, dna_sequence: str) -> str:
        """Traducir secuencia de DNA a proteína"""
        seq = Seq(dna_sequence)
        return str(seq.translate())
    
    def reverse_complement(self, dna_sequence: str) -> str:
        """Obtener complemento reverso de DNA"""
        seq = Seq(dna_sequence)
        return str(seq.reverse_complement())