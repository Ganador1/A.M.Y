"""
Distributed Manager module for compatibility
This is a compatibility stub that redirects to the correct module
"""

# Import specific items from the correct location
from app.distributed.distributed_manager import DistributedManager, distributed_manager, get_distributed_manager, is_distributed_available

__all__ = ["DistributedManager", "distributed_manager", "get_distributed_manager", "is_distributed_available"]