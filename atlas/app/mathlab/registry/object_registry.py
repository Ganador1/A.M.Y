"""
Mathematical Object Registry for AXIOM Mathematical Laboratory
Central registry for tracking and managing mathematical objects and relationships
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Tuple, Type, Callable, Union
from dataclasses import dataclass, field
from collections import defaultdict
from abc import ABC, abstractmethod
import weakref
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class ObjectRelationship:
    """Relationship between mathematical objects"""
    from_object_id: str
    to_object_id: str
    relationship_type: str  # "derived_from", "equivalent_to", "subset_of", etc.
    strength: float = 1.0  # Relationship strength 0.0-1.0
    bidirectional: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass 
class ObjectMetrics:
    """Metrics and statistics for mathematical objects"""
    computational_complexity: str = "unknown"  # "polynomial", "exponential", etc.
    memory_usage: Optional[int] = None  # Bytes
    computation_time: Optional[float] = None  # Seconds for last major operation
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    importance_score: float = 0.5  # 0.0-1.0 based on usage and relationships
    novelty_score: float = 0.5  # How novel/interesting the object is


class MathematicalObjectInterface(ABC):
    """Abstract interface for mathematical objects"""
    
    @abstractmethod
    def get_canonical_form(self) -> str:
        """Get canonical string representation"""
        pass
    
    @abstractmethod
    def compute_hash(self) -> str:
        """Compute unique hash for the object"""
        pass
    
    @abstractmethod
    def get_properties(self) -> Dict[str, Any]:
        """Get object properties as dictionary"""
        pass
    
    @abstractmethod
    def get_object_type(self) -> str:
        """Get object type string"""
        pass
    
    def get_name(self) -> str:
        """Get human-readable name"""
        return f"{self.get_object_type()}_{self.compute_hash()[:8]}"


@dataclass
class RegisteredObject:
    """Container for registered mathematical objects"""
    object_id: str
    object_type: str
    canonical_form: str
    hash_value: str
    properties: Dict[str, Any]
    
    # Object reference (weak reference to avoid memory leaks)
    object_ref: Optional[weakref.ReferenceType] = None
    
    # Metadata
    metrics: ObjectMetrics = field(default_factory=ObjectMetrics)
    tags: Set[str] = field(default_factory=set)
    aliases: Set[str] = field(default_factory=set)
    
    # Relationships
    related_objects: Set[str] = field(default_factory=set)  # Object IDs
    
    # Tracking
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "mathematical_laboratory"
    
    def get_object(self) -> Optional[MathematicalObjectInterface]:
        """Get the actual mathematical object if still in memory"""
        if self.object_ref:
            return self.object_ref()
        return None
    
    def is_alive(self) -> bool:
        """Check if the object is still in memory"""
        return self.object_ref is not None and self.object_ref() is not None


class ObjectTypeRegistry:
    """Registry for mathematical object types and their handlers"""
    
    def __init__(self):
        self.type_constructors: Dict[str, Callable] = {}
        self.type_validators: Dict[str, Callable] = {}
        self.type_serializers: Dict[str, Callable] = {}
        self.type_deserializers: Dict[str, Callable] = {}
        self.type_analyzers: Dict[str, Callable] = {}  # For deep analysis
    
    def register_type(self, 
                     object_type: str,
                     constructor: Optional[Callable] = None,
                     validator: Optional[Callable] = None,
                     serializer: Optional[Callable] = None,
                     deserializer: Optional[Callable] = None,
                     analyzer: Optional[Callable] = None):
        """Register handlers for a mathematical object type"""
        if constructor:
            self.type_constructors[object_type] = constructor
        if validator:
            self.type_validators[object_type] = validator
        if serializer:
            self.type_serializers[object_type] = serializer
        if deserializer:
            self.type_deserializers[object_type] = deserializer
        if analyzer:
            self.type_analyzers[object_type] = analyzer
    
    def can_handle(self, object_type: str) -> bool:
        """Check if type can be handled"""
        return object_type in self.type_constructors
    
    def validate_object(self, obj: MathematicalObjectInterface) -> bool:
        """Validate a mathematical object"""
        object_type = obj.get_object_type()
        if object_type in self.type_validators:
            return self.type_validators[object_type](obj)
        return True  # Default to valid if no validator
    
    def serialize_object(self, obj: MathematicalObjectInterface) -> Dict[str, Any]:
        """Serialize an object to dictionary"""
        object_type = obj.get_object_type()
        if object_type in self.type_serializers:
            return self.type_serializers[object_type](obj)
        
        # Default serialization
        return {
            "object_type": object_type,
            "canonical_form": obj.get_canonical_form(),
            "properties": obj.get_properties()
        }
    
    def deserialize_object(self, data: Dict[str, Any]) -> Optional[MathematicalObjectInterface]:
        """Deserialize dictionary to object"""
        object_type = data.get("object_type")
        if not object_type or object_type not in self.type_deserializers:
            return None
        
        return self.type_deserializers[object_type](data)
    
    def analyze_object(self, obj: MathematicalObjectInterface) -> Dict[str, Any]:
        """Perform deep analysis of an object"""
        object_type = obj.get_object_type()
        if object_type in self.type_analyzers:
            return self.type_analyzers[object_type](obj)
        return {}


class MathematicalObjectRegistry:
    """Central registry for mathematical objects and their relationships"""
    
    def __init__(self):
        self.objects: Dict[str, RegisteredObject] = {}
        self.hash_to_id: Dict[str, str] = {}  # Hash -> Object ID mapping
        self.type_to_ids: Dict[str, Set[str]] = defaultdict(set)
        self.relationships: Dict[str, Set[ObjectRelationship]] = defaultdict(set)
        self.type_registry = ObjectTypeRegistry()
        
        # Search indexes
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)  # Tag -> Object IDs
        self.property_index: Dict[str, Dict[Any, Set[str]]] = defaultdict(lambda: defaultdict(set))
        
        # Statistics
        self.stats = {
            "objects_registered": 0,
            "objects_accessed": 0,
            "relationships_created": 0,
            "last_cleanup": datetime.now()
        }
        
        # Callbacks for events
        self.event_callbacks: Dict[str, List[Callable]] = defaultdict(list)
    
    def register_event_callback(self, event: str, callback: Callable):
        """Register callback for registry events"""
        self.event_callbacks[event].append(callback)
    
    def _fire_event(self, event: str, **kwargs):
        """Fire an event to all registered callbacks"""
        for callback in self.event_callbacks[event]:
            try:
                callback(**kwargs)
            except Exception as e:
                logger.warning(f"Event callback failed for {event}: {e}")
    
    def register_object(self, 
                       obj: MathematicalObjectInterface,
                       tags: Optional[Set[str]] = None,
                       aliases: Optional[Set[str]] = None,
                       force_new: bool = False) -> str:
        """Register a mathematical object in the registry"""
        
        # Validate object
        if not self.type_registry.validate_object(obj):
            raise ValueError(f"Object validation failed for {obj.get_object_type()}")
        
        # Compute hash
        hash_value = obj.compute_hash()
        
        # Check if object already exists
        if hash_value in self.hash_to_id and not force_new:
            existing_id = self.hash_to_id[hash_value]
            existing_obj = self.objects[existing_id]
            
            # Update weak reference if object was garbage collected
            if not existing_obj.is_alive():
                existing_obj.object_ref = weakref.ref(obj)
            
            # Update access metrics
            existing_obj.metrics.access_count += 1
            existing_obj.metrics.last_accessed = datetime.now()
            existing_obj.updated_at = datetime.now()
            
            # Update tags and aliases
            if tags:
                existing_obj.tags.update(tags)
                self._update_tag_index(existing_id, tags)
            if aliases:
                existing_obj.aliases.update(aliases)
            
            self.stats["objects_accessed"] += 1
            self._fire_event("object_accessed", object_id=existing_id)
            
            return existing_id
        
        # Create new registration
        object_id = self._generate_object_id(obj.get_object_type())
        
        registered_obj = RegisteredObject(
            object_id=object_id,
            object_type=obj.get_object_type(),
            canonical_form=obj.get_canonical_form(),
            hash_value=hash_value,
            properties=obj.get_properties(),
            object_ref=weakref.ref(obj),
            tags=tags or set(),
            aliases=aliases or set()
        )
        
        # Store in main registry
        self.objects[object_id] = registered_obj
        self.hash_to_id[hash_value] = object_id
        self.type_to_ids[obj.get_object_type()].add(object_id)
        
        # Update search indexes
        self._update_tag_index(object_id, registered_obj.tags)
        self._update_property_index(object_id, registered_obj.properties)
        
        # Update statistics
        self.stats["objects_registered"] += 1
        
        # Fire event
        self._fire_event("object_registered", object_id=object_id, object_type=obj.get_object_type())
        
        logger.info(f"Registered mathematical object: {object_id} ({obj.get_object_type()})")
        
        return object_id
    
    def get_object(self, object_id: str) -> Optional[RegisteredObject]:
        """Get registered object by ID"""
        if object_id not in self.objects:
            return None
        
        obj = self.objects[object_id]
        
        # Update access metrics
        obj.metrics.access_count += 1
        obj.metrics.last_accessed = datetime.now()
        self.stats["objects_accessed"] += 1
        
        return obj
    
    def get_object_by_hash(self, hash_value: str) -> Optional[RegisteredObject]:
        """Get object by hash value"""
        if hash_value in self.hash_to_id:
            return self.get_object(self.hash_to_id[hash_value])
        return None
    
    def find_objects_by_type(self, object_type: str) -> List[RegisteredObject]:
        """Find all objects of a given type"""
        object_ids = self.type_to_ids.get(object_type, set())
        return [self.objects[oid] for oid in object_ids if oid in self.objects]
    
    def find_objects_by_tag(self, tag: str) -> List[RegisteredObject]:
        """Find objects by tag"""
        object_ids = self.tag_index.get(tag, set())
        return [self.objects[oid] for oid in object_ids if oid in self.objects]
    
    def find_objects_by_property(self, property_name: str, property_value: Any) -> List[RegisteredObject]:
        """Find objects by property value"""
        object_ids = self.property_index[property_name].get(property_value, set())
        return [self.objects[oid] for oid in object_ids if oid in self.objects]
    
    def search_objects(self, 
                      object_type: Optional[str] = None,
                      tags: Optional[Set[str]] = None,
                      properties: Optional[Dict[str, Any]] = None,
                      limit: int = 100) -> List[RegisteredObject]:
        """Advanced object search"""
        candidate_ids = set(self.objects.keys())
        
        # Filter by type
        if object_type:
            type_ids = self.type_to_ids.get(object_type, set())
            candidate_ids &= type_ids
        
        # Filter by tags
        if tags:
            for tag in tags:
                tag_ids = self.tag_index.get(tag, set())
                candidate_ids &= tag_ids
        
        # Filter by properties
        if properties:
            for prop_name, prop_value in properties.items():
                prop_ids = self.property_index[prop_name].get(prop_value, set())
                candidate_ids &= prop_ids
        
        # Get objects and sort by importance/access
        results = []
        for oid in candidate_ids:
            if oid in self.objects:
                results.append(self.objects[oid])
        
        # Sort by importance and access metrics
        results.sort(key=lambda obj: (
            obj.metrics.importance_score,
            obj.metrics.access_count,
            -obj.created_at.timestamp()  # More recent first
        ), reverse=True)
        
        return results[:limit]
    
    def create_relationship(self, 
                           from_object_id: str,
                           to_object_id: str,
                           relationship_type: str,
                           strength: float = 1.0,
                           bidirectional: bool = False,
                           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Create relationship between objects"""
        
        if from_object_id not in self.objects or to_object_id not in self.objects:
            return False
        
        relationship = ObjectRelationship(
            from_object_id=from_object_id,
            to_object_id=to_object_id,
            relationship_type=relationship_type,
            strength=strength,
            bidirectional=bidirectional,
            metadata=metadata or {}
        )
        
        # Add to relationship index
        self.relationships[from_object_id].add(relationship)
        if bidirectional:
            reverse_rel = ObjectRelationship(
                from_object_id=to_object_id,
                to_object_id=from_object_id,
                relationship_type=relationship_type,
                strength=strength,
                bidirectional=True,
                metadata=metadata or {}
            )
            self.relationships[to_object_id].add(reverse_rel)
        
        # Update object relationships
        self.objects[from_object_id].related_objects.add(to_object_id)
        self.objects[to_object_id].related_objects.add(from_object_id)
        
        self.stats["relationships_created"] += 1
        
        # Fire event
        self._fire_event("relationship_created", 
                        from_id=from_object_id, 
                        to_id=to_object_id,
                        rel_type=relationship_type)
        
        return True
    
    def get_relationships(self, object_id: str, 
                         relationship_type: Optional[str] = None) -> List[ObjectRelationship]:
        """Get relationships for an object"""
        relationships = list(self.relationships.get(object_id, set()))
        
        if relationship_type:
            relationships = [r for r in relationships if r.relationship_type == relationship_type]
        
        return relationships
    
    def get_related_objects(self, object_id: str, 
                           relationship_type: Optional[str] = None,
                           max_depth: int = 1) -> Set[str]:
        """Get IDs of related objects (with optional traversal depth)"""
        if object_id not in self.objects:
            return set()
        
        visited = set()
        to_visit = [(object_id, 0)]
        related = set()
        
        while to_visit:
            current_id, depth = to_visit.pop(0)
            
            if current_id in visited or depth > max_depth:
                continue
            
            visited.add(current_id)
            
            if depth > 0:  # Don't include the starting object
                related.add(current_id)
            
            # Get direct relationships
            relationships = self.get_relationships(current_id, relationship_type)
            for rel in relationships:
                if rel.to_object_id not in visited and depth < max_depth:
                    to_visit.append((rel.to_object_id, depth + 1))
        
        return related
    
    def update_object_metrics(self, object_id: str, 
                            metrics_update: Dict[str, Any]) -> bool:
        """Update metrics for an object"""
        if object_id not in self.objects:
            return False
        
        obj = self.objects[object_id]
        
        for key, value in metrics_update.items():
            if hasattr(obj.metrics, key):
                setattr(obj.metrics, key, value)
        
        obj.updated_at = datetime.now()
        return True
    
    def cleanup_dead_references(self) -> int:
        """Clean up objects with dead weak references"""
        dead_objects = []
        
        for object_id, obj in self.objects.items():
            if obj.object_ref and not obj.is_alive():
                dead_objects.append(object_id)
        
        cleaned_count = len(dead_objects)
        
        for object_id in dead_objects:
            self._remove_object_from_indexes(object_id)
        
        self.stats["last_cleanup"] = datetime.now()
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} dead object references")
        
        return cleaned_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            **self.stats,
            "total_objects": len(self.objects),
            "objects_by_type": {
                obj_type: len(ids) for obj_type, ids in self.type_to_ids.items()
            },
            "total_relationships": sum(len(rels) for rels in self.relationships.values()),
            "alive_objects": sum(1 for obj in self.objects.values() if obj.is_alive()),
            "memory_objects": len([obj for obj in self.objects.values() if obj.is_alive()])
        }
    
    def export_registry_data(self) -> Dict[str, Any]:
        """Export registry data for persistence"""
        export_data = {
            "objects": {},
            "relationships": {},
            "type_registry": {},  # Could be extended
            "exported_at": datetime.now().isoformat()
        }
        
        # Export objects (without weak references)
        for obj_id, obj in self.objects.items():
            export_data["objects"][obj_id] = {
                "object_id": obj.object_id,
                "object_type": obj.object_type,
                "canonical_form": obj.canonical_form,
                "hash_value": obj.hash_value,
                "properties": obj.properties,
                "tags": list(obj.tags),
                "aliases": list(obj.aliases),
                "metrics": {
                    "computational_complexity": obj.metrics.computational_complexity,
                    "access_count": obj.metrics.access_count,
                    "importance_score": obj.metrics.importance_score,
                    "novelty_score": obj.metrics.novelty_score
                },
                "created_at": obj.created_at.isoformat(),
                "created_by": obj.created_by
            }
        
        # Export relationships
        for obj_id, relationships in self.relationships.items():
            export_data["relationships"][obj_id] = [
                {
                    "from_object_id": rel.from_object_id,
                    "to_object_id": rel.to_object_id,
                    "relationship_type": rel.relationship_type,
                    "strength": rel.strength,
                    "bidirectional": rel.bidirectional,
                    "metadata": rel.metadata,
                    "created_at": rel.created_at.isoformat()
                }
                for rel in relationships
            ]
        
        return export_data
    
    def _generate_object_id(self, object_type: str) -> str:
        """Generate unique object ID"""
        base_id = f"{object_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        counter = 1
        object_id = f"{base_id}_{counter:03d}"
        
        while object_id in self.objects:
            counter += 1
            object_id = f"{base_id}_{counter:03d}"
        
        return object_id
    
    def _update_tag_index(self, object_id: str, tags: Set[str]):
        """Update tag search index"""
        for tag in tags:
            self.tag_index[tag].add(object_id)
    
    def _update_property_index(self, object_id: str, properties: Dict[str, Any]):
        """Update property search index"""
        for prop_name, prop_value in properties.items():
            # Only index hashable values
            try:
                hash(prop_value)
                self.property_index[prop_name][prop_value].add(object_id)
            except TypeError:
                # Skip non-hashable values
                pass
    
    def _remove_object_from_indexes(self, object_id: str):
        """Remove object from all search indexes"""
        obj = self.objects.get(object_id)
        if not obj:
            return
        
        # Remove from hash mapping
        if obj.hash_value in self.hash_to_id:
            del self.hash_to_id[obj.hash_value]
        
        # Remove from type mapping
        self.type_to_ids[obj.object_type].discard(object_id)
        
        # Remove from tag index
        for tag in obj.tags:
            self.tag_index[tag].discard(object_id)
        
        # Remove from property index
        for prop_name, prop_value in obj.properties.items():
            try:
                hash(prop_value)
                self.property_index[prop_name][prop_value].discard(object_id)
            except TypeError:
                pass
        
        # Remove relationships
        if object_id in self.relationships:
            del self.relationships[object_id]
        
        # Remove from main registry
        del self.objects[object_id]


async def demo_object_registry():
    """Demo of mathematical object registry"""
    print("🗃️  Mathematical Object Registry Demo")
    print("=" * 50)
    
    # Create registry
    registry = MathematicalObjectRegistry()
    
    # Create some mock objects (would normally be real mathematical objects)
    class MockMathObject(MathematicalObjectInterface):
        def __init__(self, obj_type: str, form: str, props: Dict[str, Any]):
            self.obj_type = obj_type
            self.form = form
            self.props = props
        
        def get_canonical_form(self) -> str:
            return self.form
        
        def compute_hash(self) -> str:
            return hashlib.sha256(self.form.encode()).hexdigest()[:16]
        
        def get_properties(self) -> Dict[str, Any]:
            return self.props
        
        def get_object_type(self) -> str:
            return self.obj_type
    
    # Register some objects
    print("\n📝 Registering mathematical objects...")
    
    obj1 = MockMathObject("elliptic_curve", "y^2 = x^3 + x + 1", {"a": 1, "b": 1})
    obj2 = MockMathObject("sequence", "fibonacci", {"recursive": True})
    obj3 = MockMathObject("elliptic_curve", "y^2 = x^3 - x", {"a": -1, "b": 0})
    
    id1 = registry.register_object(obj1, tags={"curves", "number_theory"})
    id2 = registry.register_object(obj2, tags={"sequences", "recursive"})
    id3 = registry.register_object(obj3, tags={"curves", "torsion"})
    
    print(f"  Registered: {id1}")
    print(f"  Registered: {id2}")
    print(f"  Registered: {id3}")
    
    # Create relationships
    print("\n🔗 Creating relationships...")
    registry.create_relationship(id1, id3, "similar_type", strength=0.8)
    registry.create_relationship(id1, id2, "derived_from", strength=0.3)
    
    # Search objects
    print("\n🔍 Searching objects...")
    curves = registry.find_objects_by_type("elliptic_curve")
    print(f"  Found {len(curves)} elliptic curves")
    
    tagged_objects = registry.find_objects_by_tag("curves")
    print(f"  Found {len(tagged_objects)} objects tagged with 'curves'")
    
    # Get related objects
    print(f"\n🌐 Objects related to {id1[:8]}...")
    related = registry.get_related_objects(id1)
    print(f"  Related objects: {list(related)}")
    
    # Statistics
    print("\n📊 Registry statistics:")
    stats = registry.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Registry demo completed!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_object_registry())
