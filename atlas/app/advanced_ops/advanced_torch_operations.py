"""
AXIOM Advanced PyTorch Operations Module
Exploiting PyTorch's full capabilities for maximum performance
"""

# Optional torch import for deep learning support
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    import torch.optim as optim
    from torch.utils.data import DataLoader
    from torch.optim.lr_scheduler import CosineAnnealingLR, ReduceLROnPlateau
    import torch.distributed as dist
    from torch.nn.parallel import DistributedDataParallel as DDP
    import torch.jit as jit
    import torch.cuda.amp as amp
    from torch.profiler import profile, ProfilerActivity
    from torch.optim.swa_utils import AveragedModel
    from torch.optim.lr_scheduler import CyclicLR, OneCycleLR
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None  # type: ignore
    nn = None # type: ignore
    F = None # type: ignore
    optim = None # type: ignore
    DataLoader = None # type: ignore
    CosineAnnealingLR = None # type: ignore
    ReduceLROnPlateau = None # type: ignore
    dist = None # type: ignore
    DDP = None # type: ignore
    jit = None # type: ignore
    amp = None # type: ignore
    profile = None # type: ignore
    ProfilerActivity = None # type: ignore
    AveragedModel = None # type: ignore
    CyclicLR = None # type: ignore
    OneCycleLR = None # type: ignore

try:
    from torch.utils.tensorboard import SummaryWriter
except ImportError:
    SummaryWriter = None  # type: ignore

import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from contextlib import contextmanager
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import os

from app.distributed.gpu_manager import gpu_manager
from app.config import settings

logger = logging.getLogger(__name__)

@dataclass
class TorchConfig:
    """Advanced PyTorch configuration"""
    use_amp: bool = True
    use_jit: bool = True
    use_compile: bool = True
    use_distributed: bool = False
    use_swa: bool = False
    use_profiler: bool = False
    compile_mode: str = "default"
    amp_dtype: torch.dtype = torch.float16
    gradient_checkpointing: bool = False
    memory_efficient_attention: bool = True

class AdvancedTorchOperations:
    """Advanced PyTorch operations exploiting full capabilities"""

    def __init__(self, config: Optional[TorchConfig] = None):
        self.config = config or TorchConfig()
        self.device = gpu_manager.get_optimal_device()
        self.scaler = amp.GradScaler() if self.config.use_amp else None
        self.profiler = None
        self.writer = None

        # Initialize distributed training if enabled
        if self.config.use_distributed:
            self._init_distributed()

        # Initialize TensorBoard writer
        if self.config.use_profiler:
            self.writer = SummaryWriter(log_dir='./logs/torch')

        logger.info(f"✅ Advanced PyTorch Operations initialized on {self.device}")

    def _init_distributed(self):
        """Initialize distributed training"""
        try:
            if not dist.is_initialized():
                dist.init_process_group(backend='nccl' if torch.cuda.is_available() else 'gloo')
                logger.info("✅ Distributed training initialized")
        except Exception as e:
            logger.warning(f"⚠️ Distributed training not available: {e}")

    @contextmanager
    def autocast_context(self):
        """Context manager for automatic mixed precision"""
        if self.config.use_amp and self.device.type in ['cuda', 'mps']:
            with amp.autocast():
                yield
        else:
            yield

    def compile_model(self, model: nn.Module) -> Any:
        """Compile model for maximum performance"""
        if self.config.use_compile and hasattr(torch, 'compile'):
            try:
                compiled_model = torch.compile(
                    model,
                    mode=self.config.compile_mode,
                    dynamic=True,
                    fullgraph=False
                )
                logger.info("✅ Model compiled successfully")
                return compiled_model
            except Exception as e:
                logger.warning(f"⚠️ Model compilation failed: {e}")
                return model
        return model

    def jit_trace_model(self, model: nn.Module, example_input: torch.Tensor) -> Any:
        """JIT trace model for inference optimization"""
        if self.config.use_jit:
            try:
                traced_model = jit.trace(model, example_input)
                logger.info("✅ Model JIT traced successfully")
                return traced_model
            except Exception as e:
                logger.warning(f"⚠️ Model JIT tracing failed: {e}")
                return model
        return model

    def create_memory_efficient_model(self, model_class: type, *args, **kwargs) -> nn.Module:
        """Create memory-efficient model with gradient checkpointing"""
        model = model_class(*args, **kwargs)

        if self.config.gradient_checkpointing:
            # Apply gradient checkpointing to reduce memory usage
            if hasattr(model, 'gradient_checkpointing_enable'):
                model.gradient_checkpointing_enable()
            else:
                # For custom models, apply to transformer layers if available
                for module in model.modules():
                    if hasattr(module, 'gradient_checkpointing_enable'):
                        module.gradient_checkpointing_enable()

        return model

    def advanced_optimization_loop(self, model: nn.Module, train_loader: DataLoader,
                                 optimizer: optim.Optimizer, scheduler: Optional[Any] = None,
                                 num_epochs: int = 10, use_swa: bool = False) -> Dict[str, Any]:
        """
        Execute advanced training loop with all PyTorch optimizations enabled.

        This method implements a comprehensive training pipeline that leverages:
        - Automatic Mixed Precision (AMP) for faster training
        - Model compilation for optimized execution
        - Distributed training support
        - Stochastic Weight Averaging (SWA) for better generalization
        - Profiling for performance analysis
        - Memory-efficient techniques

        Args:
            model: PyTorch model to train
            train_loader: DataLoader for training data
            optimizer: Optimizer for parameter updates
            scheduler: Optional learning rate scheduler
            num_epochs: Number of training epochs
            use_swa: Whether to use Stochastic Weight Averaging

        Returns:
            Dictionary containing training results and statistics:
            - final_loss: Loss after last epoch
            - best_loss: Best loss achieved
            - training_stats: Detailed training statistics
            - model: Trained model (with SWA if enabled)
        """
        model = self.compile_model(model)
        model = model.to(self.device)

        if self.config.use_distributed and dist.is_initialized():
            model = DDP(model)

        # SWA setup
        swa_model = None
        if use_swa and self.config.use_swa:
            swa_model = AveragedModel(model)

        # Profiler setup
        if self.config.use_profiler:
            self.profiler = profile(
                activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
                schedule=torch.profiler.schedule(wait=1, warmup=1, active=3, repeat=1),
                on_trace_ready=torch.profiler.tensorboard_trace_handler('./logs/profiler'),
                record_shapes=True,
                profile_memory=True,
                with_stack=True
            )
            self.profiler.start()

        best_loss = float('inf')
        training_stats = {
            'epoch_losses': [],
            'learning_rates': [],
            'memory_usage': [],
            'gpu_utilization': []
        }

        epoch_loss = 0.0  # Initialize epoch_loss

        for epoch in range(num_epochs):
            epoch_loss = 0.0
            model.train()

            for batch_idx, (data, target) in enumerate(train_loader):
                data, target = data.to(self.device), target.to(self.device)

                with self.autocast_context():
                    output = model(data)
                    loss = F.cross_entropy(output, target) if len(target.shape) > 1 else F.mse_loss(output, target)

                if self.scaler:
                    self.scaler.scale(loss).backward()
                    self.scaler.step(optimizer)
                    self.scaler.update()
                else:
                    loss.backward()
                    optimizer.step()

                optimizer.zero_grad()
                epoch_loss += loss.item()

                # Log to TensorBoard
                if self.writer and batch_idx % 10 == 0:
                    self.writer.add_scalar('Loss/train', loss.item(), epoch * len(train_loader) + batch_idx)

            epoch_loss /= len(train_loader)
            training_stats['epoch_losses'].append(epoch_loss)
            training_stats['learning_rates'].append(optimizer.param_groups[0]['lr'])

            # Memory and GPU stats
            if torch.cuda.is_available():
                training_stats['memory_usage'].append(torch.cuda.memory_allocated() / 1024**2)  # MB
                training_stats['gpu_utilization'].append(torch.cuda.utilization())

            # Scheduler step
            if scheduler:
                if isinstance(scheduler, ReduceLROnPlateau):
                    scheduler.step(epoch_loss)
                else:
                    scheduler.step()

            # SWA update
            if swa_model and epoch >= num_epochs - 5:
                swa_model.update_parameters(model)

            logger.info(f"Epoch {epoch+1}/{num_epochs}, Loss: {epoch_loss:.6f}")

            if epoch_loss < best_loss:
                best_loss = epoch_loss

        # SWA final update
        if swa_model:
            torch.optim.swa_utils.update_bn(train_loader, swa_model)
            model = swa_model

        # Stop profiler
        if self.profiler:
            self.profiler.stop()

        if self.writer:
            self.writer.close()

        return {
            'final_loss': epoch_loss,
            'best_loss': best_loss,
            'training_stats': training_stats,
            'model': model
        }

    def parallel_inference(self, model: nn.Module, data_loader: DataLoader,
                          num_workers: int = 4) -> List[torch.Tensor]:
        """
        Execute parallel inference using multiple threads for improved throughput.

        This method distributes inference across multiple worker threads to maximize
        GPU utilization and reduce total inference time for large datasets.

        Args:
            model: PyTorch model for inference
            data_loader: DataLoader containing input data batches
            num_workers: Number of worker threads for parallel processing

        Returns:
            List of model outputs for all input batches
        """
        model = model.to(self.device)
        model.eval()

        results = []

        def inference_worker(data_batch):
            with torch.no_grad(), self.autocast_context():
                batch_data = data_batch.to(self.device)
                output = model(batch_data)
                return output.cpu()

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(inference_worker, data) for data, _ in data_loader]
            for future in futures:
                results.extend(future.result())

        return results

    def advanced_data_parallelism(self, model: nn.Module, inputs: torch.Tensor,
                                num_replicas: int = 4) -> torch.Tensor:
        """Advanced data parallelism with custom splitting"""
        if not torch.cuda.is_available() or torch.cuda.device_count() < 2:
            # Fallback to regular forward pass
            return model(inputs)

        # Split inputs across available GPUs
        inputs_split = torch.chunk(inputs, num_replicas, dim=0)

        # Create model replicas
        models = [model.to(f'cuda:{i}') for i in range(min(num_replicas, torch.cuda.device_count()))]

        # Parallel inference
        with ThreadPoolExecutor(max_workers=len(models)) as executor:
            futures = [executor.submit(self._single_gpu_inference, models[i], inputs_split[i])
                      for i in range(len(models))]

        # Collect results
        outputs = []
        for future in futures:
            outputs.append(future.result())

        # Concatenate results
        return torch.cat(outputs, dim=0)

    def _single_gpu_inference(self, model: nn.Module, inputs: torch.Tensor) -> torch.Tensor:
        """Single GPU inference"""
        with torch.no_grad(), self.autocast_context():
            return model(inputs)

    def memory_efficient_attention(self, query: torch.Tensor, key: torch.Tensor,
                                 value: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Memory-efficient attention mechanism"""
        if not self.config.memory_efficient_attention:
            return F.scaled_dot_product_attention(query, key, value, attn_mask=mask)

        # Custom memory-efficient attention implementation
        # This is a simplified version - in practice you'd use more sophisticated algorithms
        hidden_size = query.shape[-1]

        # Compute attention scores
        scores = torch.matmul(query, key.transpose(-2, -1)) / (hidden_size ** 0.5)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        attention_weights = F.softmax(scores, dim=-1)

        # Apply attention to values
        output = torch.matmul(attention_weights, value)

        return output

    def advanced_gradient_computation(self, model: nn.Module, inputs: torch.Tensor,
                                    targets: torch.Tensor, loss_fn: Callable) -> Dict[str, Any]:
        """Advanced gradient computation with analysis"""
        model.train()
        model.zero_grad()

        with self.autocast_context():
            outputs = model(inputs)
            loss = loss_fn(outputs, targets)

        if self.scaler:
            self.scaler.scale(loss).backward()
        else:
            loss.backward()

        # Gradient analysis
        grad_stats = {}
        total_norm = 0

        for name, param in model.named_parameters():
            if param.grad is not None:
                param_norm = param.grad.data.norm(2)
                total_norm += param_norm.item() ** 2
                grad_stats[name] = {
                    'norm': param_norm.item(),
                    'mean': param.grad.data.mean().item(),
                    'std': param.grad.data.std().item(),
                    'max': param.grad.data.max().item(),
                    'min': param.grad.data.min().item()
                }

        total_norm = total_norm ** (1. / 2)

        return {
            'loss': loss.item(),
            'total_grad_norm': total_norm,
            'grad_stats': grad_stats,
            'gradients': {name: param.grad.clone() for name, param in model.named_parameters()
                         if param.grad is not None}
        }

    def create_advanced_optimizer(self, model: nn.Module, optimizer_type: str = 'adamw',
                                lr: float = 1e-3, weight_decay: float = 0.01) -> optim.Optimizer:
        """Create advanced optimizer with custom parameter groups"""
        # Separate parameters into different groups for different learning rates
        decay_params = []
        no_decay_params = []

        for param in model.parameters():
            if param.requires_grad:
                if len(param.shape) >= 2:  # Weight matrices
                    decay_params.append(param)
                else:  # Bias terms and layer norms
                    no_decay_params.append(param)

        param_groups = [
            {'params': decay_params, 'weight_decay': weight_decay},
            {'params': no_decay_params, 'weight_decay': 0.0}
        ]

        if optimizer_type.lower() == 'adamw':
            optimizer = optim.AdamW(param_groups, lr=lr, betas=(0.9, 0.999), eps=1e-8)
        elif optimizer_type.lower() == 'adam':
            optimizer = optim.Adam(param_groups, lr=lr, betas=(0.9, 0.999), eps=1e-8)
        elif optimizer_type.lower() == 'sgd':
            optimizer = optim.SGD(param_groups, lr=lr, momentum=0.9, weight_decay=weight_decay)
        else:
            raise ValueError(f"Unsupported optimizer type: {optimizer_type}")

        return optimizer

    def create_advanced_scheduler(self, optimizer: optim.Optimizer, scheduler_type: str = 'cosine',
                                **kwargs) -> Any:
        """Create advanced learning rate scheduler"""
        if scheduler_type.lower() == 'cosine':
            scheduler = CosineAnnealingLR(optimizer, **kwargs)
        elif scheduler_type.lower() == 'plateau':
            scheduler = ReduceLROnPlateau(optimizer, **kwargs)
        elif scheduler_type.lower() == 'cyclic':
            scheduler = CyclicLR(optimizer, **kwargs)
        elif scheduler_type.lower() == 'onecycle':
            scheduler = OneCycleLR(optimizer, **kwargs)
        else:
            raise ValueError(f"Unsupported scheduler type: {scheduler_type}")

        return scheduler

    def distributed_training_setup(self, world_size: int, rank: int, backend: str = 'nccl'):
        """Setup for distributed training"""
        settings.MASTER_ADDR = 'localhost'
        settings.MASTER_PORT = '12355'

        dist.init_process_group(backend, rank=rank, world_size=world_size)
        torch.cuda.set_device(rank)

        logger.info(f"✅ Distributed training setup complete for rank {rank}")

    def advanced_model_serving(self, model: nn.Module, batch_size: int = 32,
                             max_concurrent_requests: int = 100) -> Callable:
        """
        Create advanced model serving function with batching and concurrency control.
        
        NOTE: Uses daemon thread for background batch processing.
        This is acceptable because:
        - Daemon thread (daemon=True) runs in separate OS thread
        - Does NOT interfere with asyncio event loop
        - time.sleep() in the thread does NOT block the main event loop
        - Appropriate for request batching with low latency (1ms sleep)
        
        TODO (ROADMAP 5): Consider asyncio.Queue + asyncio.create_task
        for async-native batching if needed, but current implementation
        is correct for thread-based concurrency control.
        """
        model = model.to(self.device)
        model.eval()

        semaphore = threading.Semaphore(max_concurrent_requests)
        request_queue = []
        result_dict = {}

        def batch_processor():
            """
            Background batch processor.
            
            NOTE: Runs in daemon thread (separate OS thread).
            time.sleep() here does NOT block asyncio event loop.
            """
            while True:
                if len(request_queue) >= batch_size:
                    # Process batch
                    batch_requests = request_queue[:batch_size]
                    request_queue[:] = request_queue[batch_size:]

                    batch_data = torch.stack([req['data'] for req in batch_requests])

                    with torch.no_grad(), self.autocast_context():
                        batch_outputs = model(batch_data)

                    # Store results
                    for i, request in enumerate(batch_requests):
                        result_dict[request['id']] = batch_outputs[i].cpu()

                    # Release semaphores
                    for request in batch_requests:
                        request['semaphore'].release()

                time.sleep(0.001)  # Small delay to prevent busy waiting (safe in daemon thread)

        # Start background processor
        processor_thread = threading.Thread(target=batch_processor, daemon=True)
        processor_thread.start()

        def serve_request(data: torch.Tensor) -> torch.Tensor:
            """Serve a single request"""
            semaphore.acquire()

            request_id = id(data)
            request_semaphore = threading.Semaphore(0)

            request_queue.append({
                'id': request_id,
                'data': data.to(self.device),
                'semaphore': request_semaphore
            })

            # Wait for result
            request_semaphore.acquire()

            return result_dict.pop(request_id)

        return serve_request

    def torch_computation_pipeline(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Complete PyTorch computation pipeline"""
        results = {
            'original_problem': problem,
            'computation_steps': [],
            'final_results': {},
            'performance_metrics': {}
        }

        start_time = time.time()

        try:
            problem_type = problem.get('type', 'general')

            if problem_type == 'matrix_multiplication':
                matrix_a = torch.tensor(problem['matrix_a'], dtype=torch.float32)
                matrix_b = torch.tensor(problem['matrix_b'], dtype=torch.float32)
                result = self.advanced_matrix_operations(matrix_a, matrix_b, 'multiply')
                results['final_results']['matrix_multiplication'] = result
                results['computation_steps'].append('matrix_multiplication')

            elif problem_type == 'neural_network':
                # Simple neural network training
                input_size = problem.get('input_size', 10)
                hidden_size = problem.get('hidden_size', 5)
                output_size = problem.get('output_size', 1)
                nn_result = self.advanced_neural_network(input_size, hidden_size, output_size)
                results['final_results']['neural_network'] = nn_result
                results['computation_steps'].append('neural_network')

            elif problem_type == 'optimization':
                # Optimization problem
                objective = problem.get('objective', 'quadratic')
                opt_result = self.advanced_optimization(objective)
                results['final_results']['optimization'] = opt_result
                results['computation_steps'].append('optimization')

        except Exception as e:
            results['error'] = str(e)

        # Performance metrics
        end_time = time.time()
        results['performance_metrics'] = {
            'computation_time': end_time - start_time,
            'steps_completed': len(results['computation_steps']),
            'results_count': len(results['final_results'])
        }

        return results

    def advanced_matrix_operations(self, matrix_a: torch.Tensor, matrix_b: torch.Tensor,
                                 operation: str) -> torch.Tensor:
        """Advanced matrix operations with optimizations"""
        if operation == 'multiply':
            return torch.matmul(matrix_a, matrix_b)
        elif operation == 'add':
            return torch.add(matrix_a, matrix_b)
        elif operation == 'subtract':
            return torch.sub(matrix_a, matrix_b)
        else:
            raise ValueError(f"Unsupported operation: {operation}")

    def advanced_neural_network(self, input_size: int, hidden_size: int, output_size: int) -> Dict[str, Any]:
        """Create and train a simple neural network"""
        model = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )

        # Simple training example
        optimizer = optim.Adam(model.parameters(), lr=0.01)
        criterion = nn.MSELoss()

        # Dummy training data
        x = torch.randn(100, input_size)
        y = torch.randn(100, output_size)

        for _ in range(10):
            optimizer.zero_grad()
            output = model(x)
            loss = criterion(output, y)
            loss.backward()
            optimizer.step()

        return {
            'model': model,
            'final_loss': loss.item(),
            'input_size': input_size,
            'hidden_size': hidden_size,
            'output_size': output_size
        }

    def advanced_optimization(self, objective: str) -> Dict[str, Any]:
        """Advanced optimization for different objective functions"""
        if objective == 'quadratic':
            # Minimize x^2 + y^2
            def quadratic_loss(x, y):
                return x**2 + y**2

            # Simple gradient descent
            x, y = 2.0, 3.0
            lr = 0.1
            for _ in range(100):
                grad_x = 2 * x
                grad_y = 2 * y
                x -= lr * grad_x
                y -= lr * grad_y

            return {
                'objective': objective,
                'solution': {'x': x, 'y': y},
                'final_value': quadratic_loss(x, y)
            }
        else:
            raise ValueError(f"Unsupported objective: {objective}")

# Global instance
advanced_torch_ops = AdvancedTorchOperations()

def get_advanced_torch_operations() -> AdvancedTorchOperations:
    """Get the global advanced torch operations instance"""
    return advanced_torch_ops
