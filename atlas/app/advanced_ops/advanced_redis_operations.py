"""
AXIOM Advanced Redis Operations Module
Exploiting Redis's full data structure and advanced capabilities
"""

import redis
import json
import time
import logging
import pickle
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor
import zlib
import base64
import os

logger = logging.getLogger(__name__)

@dataclass
class RedisConfig:
    """Configuration for advanced Redis operations"""
    host: str = 'localhost'
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    socket_timeout: Optional[float] = 5.0
    socket_connect_timeout: Optional[float] = 5.0
    socket_keepalive: bool = True
    socket_keepalive_options: Optional[Dict] = None
    health_check_interval: int = 30
    max_connections: int = 20
    decode_responses: bool = True
    compression: bool = True
    serialization: str = 'json'  # json, pickle, msgpack
    cache_ttl: int = 3600  # 1 hour default
    pubsub_channels: List[str] = None

    def __post_init__(self):
        if self.pubsub_channels is None:
            self.pubsub_channels = []

class AdvancedRedisOperations:
    """Advanced Redis operations exploiting full capabilities"""

    def __init__(self, config: Optional[RedisConfig] = None):
        self.config = config or RedisConfig()

        # Connection pool for better performance
        self.connection_pool = redis.ConnectionPool(
            host=self.config.host,
            port=self.config.port,
            db=self.config.db,
            password=self.config.password,
            socket_timeout=self.config.socket_timeout,
            socket_connect_timeout=self.config.socket_connect_timeout,
            socket_keepalive=self.config.socket_keepalive,
            socket_keepalive_options=self.config.socket_keepalive_options,
            max_connections=self.config.max_connections,
            decode_responses=self.config.decode_responses
        )

        # Main Redis client
        self.redis_client = redis.Redis(connection_pool=self.connection_pool)

        # PubSub client
        self.pubsub_client = self.redis_client.pubsub()

        # Thread pool for async operations
        self.thread_pool = ThreadPoolExecutor(max_workers=4)

        # Compression and serialization setup
        self._setup_serialization()

        # Health monitoring
        self.health_status = {'status': 'unknown', 'last_check': 0}
        self._start_health_monitor()

        logger.info("✅ Advanced Redis Operations initialized")

    def _setup_serialization(self):
        """Setup serialization methods"""
        if self.config.serialization == 'json':
            self.serialize = json.dumps
            self.deserialize = json.loads
        elif self.config.serialization == 'pickle':
            # 🔒 SECURITY: Pickle deserialization is CRITICAL VULNERABILITY if not trusted.
            # Only enable if ALLOW_REDIS_PICKLE is explicitly set to true.
            allow_pickle = str(os.getenv('ALLOW_REDIS_PICKLE', 'false')).lower() in ('1', 'true', 'yes')
            if not allow_pickle:
                logger.warning("⚠️ SECURITY: Pickle deserialization disabled by default because it's unsafe. Falling back to json.")
                self.config.serialization = 'json'
                self.serialize = json.dumps
                self.deserialize = json.loads
            else:
                logger.warning("⚠️ SECURITY: Pickle deserialization ENABLED. This is unsafe if Redis content is not fully trusted.")
                self.serialize = lambda x: base64.b64encode(pickle.dumps(x)).decode('utf-8')
                self.deserialize = lambda x: pickle.loads(base64.b64decode(x))
        elif self.config.serialization == 'msgpack':
            try:
                import msgpack
                self.serialize = msgpack.packb
                self.deserialize = msgpack.unpackb
            except ImportError:
                logger.warning("msgpack not available, falling back to json")
                self.serialize = json.dumps
                self.deserialize = json.loads

    def _start_health_monitor(self):
        """
        Start background health monitoring.
        
        NOTE: Uses threading.Thread with time.sleep() in daemon thread.
        This is acceptable because:
        - Runs in separate OS thread (not blocking main event loop)
        - Daemon thread (dies with main process)
        - Configurable health check intervals
        
        TODO (ROADMAP 5): Consider migrating to asyncio.create_task with
        asyncio.sleep() for better integration with async Redis operations.
        """
        def health_check():
            while True:
                try:
                    self.redis_client.ping()
                    self.health_status = {
                        'status': 'healthy',
                        'last_check': time.time()
                    }
                except Exception as e:
                    self.health_status = {
                        'status': 'unhealthy',
                        'error': str(e),
                        'last_check': time.time()
                    }
                # NOTE: time.sleep() in daemon thread - does not block event loop
                time.sleep(self.config.health_check_interval)

        thread = threading.Thread(target=health_check, daemon=True)
        thread.start()

    def advanced_caching(self, key: str, data: Any,
                        ttl: Optional[int] = None,
                        compress: bool = True) -> Dict[str, Any]:
        """Advanced caching with compression and TTL management"""
        results = {}

        try:
            # Serialize data
            serialized_data = self.serialize(data)

            # Compress if enabled
            if compress and self.config.compression:
                compressed_data = zlib.compress(serialized_data.encode('utf-8'))
                final_data = compressed_data
                results['compressed'] = True
                results['original_size'] = len(serialized_data)
                results['compressed_size'] = len(compressed_data)
            else:
                final_data = serialized_data
                results['compressed'] = False

            # Store in Redis
            ttl_value = ttl or self.config.cache_ttl
            self.redis_client.setex(key, ttl_value, final_data)

            # Cache metadata
            metadata_key = f"{key}:metadata"
            metadata = {
                'created_at': time.time(),
                'ttl': ttl_value,
                'compressed': results.get('compressed', False),
                'size': len(final_data),
                'type': type(data).__name__
            }
            self.redis_client.setex(metadata_key, ttl_value, self.serialize(metadata))

            results['success'] = True
            results['key'] = key
            results['ttl'] = ttl_value

        except Exception as e:
            results['error'] = str(e)
            results['success'] = False

        return results

    def advanced_retrieval(self, key: str, decompress: bool = True) -> Dict[str, Any]:
        """Advanced data retrieval with automatic decompression"""
        results = {}

        try:
            # Get data
            data = self.redis_client.get(key)
            if data is None:
                results['found'] = False
                return results

            # Get metadata
            metadata_key = f"{key}:metadata"
            metadata_raw = self.redis_client.get(metadata_key)

            if metadata_raw:
                try:
                    metadata = self.deserialize(metadata_raw)
                    results['metadata'] = metadata
                except Exception as e:
                    logger.warning(f"Failed to deserialize metadata: {e}")
                    results['metadata'] = None

            # Decompress if needed
            if decompress and isinstance(data, bytes) and len(data) > 0:
                try:
                    # Try to decompress
                    decompressed = zlib.decompress(data)
                    final_data = decompressed.decode('utf-8')
                    results['decompressed'] = True
                except zlib.error:
                    # Not compressed, use as is
                    final_data = data.decode('utf-8') if isinstance(data, bytes) else data
                    results['decompressed'] = False
            else:
                final_data = data.decode('utf-8') if isinstance(data, bytes) else data

            # Deserialize
            try:
                deserialized_data = self.deserialize(final_data)
                results['data'] = deserialized_data
            except Exception as e:
                logger.warning(f"Failed to deserialize data: {e}")
                results['data'] = final_data

            results['found'] = True
            results['key'] = key

        except Exception as e:
            results['error'] = str(e)
            results['found'] = False

        return results

    def advanced_data_structures(self, operation: str,
                               key: str, data: Any = None) -> Dict[str, Any]:
        """Advanced Redis data structure operations"""
        results = {}

        try:
            if operation == 'hash_operations':
                # Hash operations
                if isinstance(data, dict):
                    self.redis_client.hset(key, mapping=data)
                    results['hash_set'] = True
                    results['fields_count'] = len(data)

                # Get all hash fields
                hash_data = self.redis_client.hgetall(key)
                results['hash_data'] = hash_data

            elif operation == 'list_operations':
                # List operations
                if isinstance(data, list):
                    self.redis_client.rpush(key, *data)
                    results['list_pushed'] = len(data)

                # Get list with range
                list_data = self.redis_client.lrange(key, 0, -1)
                results['list_data'] = list_data
                results['list_length'] = self.redis_client.llen(key)

            elif operation == 'set_operations':
                # Set operations
                if isinstance(data, (list, set)):
                    self.redis_client.sadd(key, *data)
                    results['set_added'] = len(data)

                # Set operations
                set_data = self.redis_client.smembers(key)
                results['set_data'] = list(set_data)
                results['set_size'] = self.redis_client.scard(key)

            elif operation == 'sorted_set':
                # Sorted set operations
                if isinstance(data, dict):
                    # data should be {member: score}
                    self.redis_client.zadd(key, data)
                    results['sorted_set_added'] = len(data)

                # Get sorted set with scores
                sorted_data = self.redis_client.zrange(key, 0, -1, withscores=True)
                results['sorted_data'] = sorted_data
                results['sorted_set_size'] = self.redis_client.zcard(key)

            elif operation == 'bitmap':
                # Bitmap operations
                if isinstance(data, (list, bytes)):
                    # Set bits
                    for i, bit in enumerate(data):
                        if bit:
                            self.redis_client.setbit(key, i, 1)

                # Get bitmap info
                bit_count = self.redis_client.bitcount(key)
                results['bitmap_bits_set'] = bit_count

            elif operation == 'hyperloglog':
                # HyperLogLog for cardinality estimation
                if isinstance(data, list):
                    self.redis_client.pfadd(key, *data)
                    results['hyperloglog_added'] = len(data)

                # Get estimated cardinality
                cardinality = self.redis_client.pfcount(key)
                results['estimated_cardinality'] = cardinality

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_pubsub(self, channels: List[str],
                       message_handler: Optional[Callable] = None) -> Dict[str, Any]:
        """Advanced PubSub operations"""
        results = {}

        try:
            # Subscribe to channels
            self.pubsub_client.subscribe(*channels)
            results['subscribed_channels'] = channels

            # Listen for messages
            messages = []
            timeout = 1.0  # 1 second timeout

            def listen_for_messages():
                for message in self.pubsub_client.listen():
                    if message['type'] == 'message':
                        messages.append({
                            'channel': message['channel'],
                            'data': message['data'],
                            'timestamp': time.time()
                        })

                        # Call custom handler if provided
                        if message_handler:
                            try:
                                message_handler(message)
                            except Exception as e:
                                logger.error(f"Message handler error: {e}")

                        # Stop after collecting some messages
                        if len(messages) >= 10:
                            break

            # Start listening in a thread
            listen_thread = threading.Thread(target=listen_for_messages)
            listen_thread.start()
            listen_thread.join(timeout=timeout)

            results['messages_received'] = messages
            results['messages_count'] = len(messages)

        except Exception as e:
            results['error'] = str(e)

        return results

    def publish_message(self, channel: str, message: Any) -> Dict[str, Any]:
        """Publish message to a channel"""
        results = {}

        try:
            # Serialize message
            if not isinstance(message, str):
                message = self.serialize(message)

            # Publish
            subscribers = self.redis_client.publish(channel, message)
            results['published'] = True
            results['channel'] = channel
            results['subscribers'] = subscribers

        except Exception as e:
            results['error'] = str(e)
            results['published'] = False

        return results

    def advanced_lua_scripting(self, script: str,
                             keys: List[str] = None,
                             args: List[Any] = None) -> Dict[str, Any]:
        """Advanced Lua scripting operations"""
        results = {}

        try:
            keys = keys or []
            args = args or []

            # Execute Lua script
            lua_script = self.redis_client.register_script(script)
            result = lua_script(keys=keys, args=args)

            results['script_executed'] = True
            results['result'] = result

        except Exception as e:
            results['error'] = str(e)
            results['script_executed'] = False

        return results

    def advanced_pipeline(self, operations: List[Dict]) -> Dict[str, Any]:
        """Advanced pipeline operations for atomic multi-key commands"""
        results = {}

        try:
            with self.redis_client.pipeline() as pipe:
                # Queue operations
                for op in operations:
                    op_type = op.get('type', 'get')
                    key = op.get('key')
                    value = op.get('value')

                    if op_type == 'set':
                        pipe.set(key, value)
                    elif op_type == 'get':
                        pipe.get(key)
                    elif op_type == 'delete':
                        pipe.delete(key)
                    elif op_type == 'hset':
                        pipe.hset(key, mapping=value)
                    elif op_type == 'hget':
                        pipe.hget(key, value)
                    elif op_type == 'lpush':
                        pipe.lpush(key, *value)
                    elif op_type == 'lrange':
                        pipe.lrange(key, 0, -1)

                # Execute all operations atomically
                pipeline_results = pipe.execute()

            results['pipeline_executed'] = True
            results['operations_count'] = len(operations)
            results['results'] = pipeline_results

        except Exception as e:
            results['error'] = str(e)
            results['pipeline_executed'] = False

        return results

    def advanced_clustering(self) -> Dict[str, Any]:
        """Advanced Redis clustering operations"""
        results = {}

        try:
            # Check if Redis Cluster is available
            cluster_info = self.redis_client.cluster('info') if hasattr(self.redis_client, 'cluster') else None

            if cluster_info:
                results['cluster_enabled'] = True
                results['cluster_info'] = cluster_info

                # Get cluster nodes
                nodes = self.redis_client.cluster('nodes')
                results['cluster_nodes'] = nodes

                # Get cluster slots
                slots = self.redis_client.cluster('slots')
                results['cluster_slots'] = len(slots)
            else:
                results['cluster_enabled'] = False

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_monitoring(self) -> Dict[str, Any]:
        """Advanced Redis monitoring and analytics"""
        results = {}

        try:
            # Get Redis info
            info = self.redis_client.info()
            results['redis_info'] = info

            # Memory usage
            memory_info = info.get('memory', {})
            results['memory_usage'] = {
                'used_memory': memory_info.get('used_memory'),
                'used_memory_human': memory_info.get('used_memory_human'),
                'used_memory_peak': memory_info.get('used_memory_peak_human'),
                'total_system_memory': memory_info.get('total_system_memory_human')
            }

            # Keyspace info
            keyspace = info.get('keyspace', {})
            results['keyspace_info'] = keyspace

            # Command statistics
            commandstats = info.get('commandstats', {})
            results['command_stats'] = commandstats

            # Connected clients
            clients = info.get('clients', {})
            results['connected_clients'] = clients.get('connected_clients', 0)

            # Health status
            results['health_status'] = self.health_status

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_search(self, pattern: str = "*",
                       data_type: str = 'all') -> Dict[str, Any]:
        """Advanced key search and filtering"""
        results = {}

        try:
            # Scan for keys matching pattern
            keys = []
            for key in self.redis_client.scan_iter(pattern):
                keys.append(key)

            results['keys_found'] = len(keys)
            results['keys'] = keys[:100]  # Limit for performance

            # Get key types
            key_types = {}
            for key in keys[:50]:  # Sample for performance
                key_type = self.redis_client.type(key)
                key_types[key] = key_type

            results['key_types'] = key_types

            # Filter by data type
            if data_type != 'all':
                filtered_keys = [k for k, t in key_types.items() if t == data_type]
                results['filtered_keys'] = filtered_keys
                results['filtered_count'] = len(filtered_keys)

        except Exception as e:
            results['error'] = str(e)

        return results

    def advanced_backup_restore(self, operation: str,
                              filename: str = None) -> Dict[str, Any]:
        """Advanced backup and restore operations"""
        results = {}

        try:
            if operation == 'backup':
                # Create backup by dumping all data
                all_keys = []
                for key in self.redis_client.scan_iter("*"):
                    all_keys.append(key)

                backup_data = {}
                for key in all_keys[:1000]:  # Limit for safety
                    key_type = self.redis_client.type(key)

                    if key_type == 'string':
                        backup_data[key] = self.redis_client.get(key)
                    elif key_type == 'hash':
                        backup_data[key] = self.redis_client.hgetall(key)
                    elif key_type == 'list':
                        backup_data[key] = self.redis_client.lrange(key, 0, -1)
                    elif key_type == 'set':
                        backup_data[key] = list(self.redis_client.smembers(key))
                    elif key_type == 'zset':
                        backup_data[key] = self.redis_client.zrange(key, 0, -1, withscores=True)

                # Save to file if specified
                if filename:
                    with open(filename, 'w') as f:
                        json.dump(backup_data, f)
                    results['backup_saved'] = True
                    results['backup_file'] = filename

                results['backup_data'] = backup_data
                results['keys_backed_up'] = len(backup_data)

            elif operation == 'restore':
                if filename and os.path.exists(filename):
                    with open(filename, 'r') as f:
                        backup_data = json.load(f)

                    restored_count = 0
                    for key, value in backup_data.items():
                        try:
                            if isinstance(value, str):
                                self.redis_client.set(key, value)
                            elif isinstance(value, dict):
                                self.redis_client.hset(key, mapping=value)
                            elif isinstance(value, list):
                                if value and isinstance(value[0], (list, tuple)):
                                    # Sorted set
                                    self.redis_client.zadd(key, dict(value))
                                else:
                                    # List
                                    self.redis_client.rpush(key, *value)
                            restored_count += 1
                        except Exception as e:
                            logger.error(f"Failed to restore key {key}: {e}")

                    results['restored_keys'] = restored_count
                    results['restore_completed'] = True

        except Exception as e:
            results['error'] = str(e)

        return results

    def redis_computation_pipeline(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Complete Redis computation pipeline"""
        results = {
            'original_problem': problem,
            'computation_steps': [],
            'final_results': {},
            'performance_metrics': {}
        }

        start_time = time.time()

        try:
            problem_type = problem.get('type', 'general')

            if problem_type == 'cache':
                key = problem['key']
                data = problem['data']
                cache_results = self.advanced_caching(key, data)
                results['final_results']['cache'] = cache_results
                results['computation_steps'].append('cache')

            elif problem_type == 'data_structure':
                operation = problem['operation']
                key = problem['key']
                data = problem.get('data')
                ds_results = self.advanced_data_structures(operation, key, data)
                results['final_results']['data_structure'] = ds_results
                results['computation_steps'].append('data_structure')

            elif problem_type == 'pubsub':
                channels = problem['channels']
                pubsub_results = self.advanced_pubsub(channels)
                results['final_results']['pubsub'] = pubsub_results
                results['computation_steps'].append('pubsub')

            elif problem_type == 'pipeline':
                operations = problem['operations']
                pipeline_results = self.advanced_pipeline(operations)
                results['final_results']['pipeline'] = pipeline_results
                results['computation_steps'].append('pipeline')

            elif problem_type == 'monitoring':
                monitoring_results = self.advanced_monitoring()
                results['final_results']['monitoring'] = monitoring_results
                results['computation_steps'].append('monitoring')

            elif problem_type == 'search':
                pattern = problem.get('pattern', '*')
                data_type = problem.get('data_type', 'all')
                search_results = self.advanced_search(pattern, data_type)
                results['final_results']['search'] = search_results
                results['computation_steps'].append('search')

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

# Global instance
advanced_redis_ops = AdvancedRedisOperations()

def get_advanced_redis_operations() -> AdvancedRedisOperations:
    """Get the global advanced redis operations instance"""
    return advanced_redis_ops
