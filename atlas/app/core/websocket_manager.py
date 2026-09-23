"""
WebSocket Manager for real-time security event streaming.
Manages WebSocket connections, authentication, and event broadcasting.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, List, Optional
from datetime import datetime
import logging

from app.core.jwt_handler import JWTHandler


logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time event streaming.

    Features:
    - Connection tracking by user and connection ID
    - JWT-based authentication
    - Topic-based subscriptions (events, metrics, alerts)
    - Broadcasting to all or filtered connections
    - Automatic cleanup on disconnect
    """

    def __init__(self):
        """Initialize the connection manager"""
        # Active connections: {connection_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}

        # User to connections mapping: {user_id: Set[connection_id]}
        self.user_connections: Dict[str, Set[str]] = {}

        # Connection metadata: {connection_id: {user_id, username, topics, connected_at}}
        self.connection_metadata: Dict[str, Dict] = {}

        # Topic subscriptions: {topic: Set[connection_id]}
        self.topic_subscriptions: Dict[str, Set[str]] = {
            "events": set(),
            "metrics": set(),
            "alerts": set(),
            "all": set()
        }

        self.jwt_handler = JWTHandler()

    async def connect(
        self,
        websocket: WebSocket,
        connection_id: str,
        token: Optional[str] = None
    ) -> bool:
        """
        Accept and authenticate a WebSocket connection.

        Args:
            websocket: WebSocket instance
            connection_id: Unique connection identifier
            token: Optional JWT token for authentication

        Returns:
            True if connection accepted, False otherwise
        """
        try:
            await websocket.accept()

            # Verify JWT token if provided
            user_id = None
            username = "anonymous"

            if token:
                try:
                    payload = self.jwt_handler.verify_token(token)
                    user_id = payload.get("sub")
                    username = payload.get("username", "unknown")
                except Exception as e:
                    logger.warning(f"Invalid token for WebSocket connection: {e}")
                    await websocket.close(code=4001, reason="Invalid token")
                    return False

            # Store connection
            self.active_connections[connection_id] = websocket

            # Store metadata
            self.connection_metadata[connection_id] = {
                "user_id": user_id,
                "username": username,
                "topics": set(),
                "connected_at": datetime.utcnow().isoformat(),
                "authenticated": user_id is not None
            }

            # Map user to connection
            if user_id:
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = set()
                self.user_connections[user_id].add(connection_id)

            logger.info(f"WebSocket connected: {connection_id} (user: {username})")

            # Send welcome message
            await self.send_personal_message(
                connection_id,
                {
                    "type": "connection",
                    "status": "connected",
                    "connection_id": connection_id,
                    "user": username,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

            return True

        except Exception as e:
            logger.error(f"Failed to connect WebSocket: {e}")
            return False

    def disconnect(self, connection_id: str):
        """
        Disconnect and cleanup a WebSocket connection.

        Args:
            connection_id: Connection identifier to disconnect
        """
        try:
            # Get metadata
            metadata = self.connection_metadata.get(connection_id)

            # Remove from active connections
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]

            # Remove from user connections
            if metadata and metadata["user_id"]:
                user_id = metadata["user_id"]
                if user_id in self.user_connections:
                    self.user_connections[user_id].discard(connection_id)
                    if not self.user_connections[user_id]:
                        del self.user_connections[user_id]

            # Remove from topic subscriptions
            for topic_subs in self.topic_subscriptions.values():
                topic_subs.discard(connection_id)

            # Remove metadata
            if connection_id in self.connection_metadata:
                del self.connection_metadata[connection_id]

            logger.info(f"WebSocket disconnected: {connection_id}")

        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {e}")

    async def subscribe(self, connection_id: str, topics: List[str]):
        """
        Subscribe a connection to specific topics.

        Args:
            connection_id: Connection identifier
            topics: List of topics to subscribe to ('events', 'metrics', 'alerts', 'all')
        """
        try:
            metadata = self.connection_metadata.get(connection_id)
            if not metadata:
                return

            for topic in topics:
                if topic in self.topic_subscriptions:
                    self.topic_subscriptions[topic].add(connection_id)
                    metadata["topics"].add(topic)

            logger.info(f"Connection {connection_id} subscribed to: {topics}")

            # Acknowledge subscription
            await self.send_personal_message(
                connection_id,
                {
                    "type": "subscription",
                    "status": "subscribed",
                    "topics": list(metadata["topics"]),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Error subscribing to topics: {e}")

    async def unsubscribe(self, connection_id: str, topics: List[str]):
        """
        Unsubscribe a connection from specific topics.

        Args:
            connection_id: Connection identifier
            topics: List of topics to unsubscribe from
        """
        try:
            metadata = self.connection_metadata.get(connection_id)
            if not metadata:
                return

            for topic in topics:
                if topic in self.topic_subscriptions:
                    self.topic_subscriptions[topic].discard(connection_id)
                    metadata["topics"].discard(topic)

            logger.info(f"Connection {connection_id} unsubscribed from: {topics}")

        except Exception as e:
            logger.error(f"Error unsubscribing from topics: {e}")

    async def send_personal_message(self, connection_id: str, message: dict):
        """
        Send a message to a specific connection.

        Args:
            connection_id: Target connection identifier
            message: Message dictionary to send
        """
        try:
            websocket = self.active_connections.get(connection_id)
            if websocket:
                await websocket.send_json(message)
        except WebSocketDisconnect:
            self.disconnect(connection_id)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_to_topic(self, topic: str, message: dict):
        """
        Broadcast a message to all connections subscribed to a topic.

        Args:
            topic: Topic name
            message: Message dictionary to broadcast
        """
        # Get connections subscribed to this topic or 'all'
        subscribers = self.topic_subscriptions.get(topic, set()).union(
            self.topic_subscriptions.get("all", set())
        )

        # Add topic to message
        message["topic"] = topic

        # Send to all subscribers
        disconnected = []
        for connection_id in subscribers:
            try:
                websocket = self.active_connections.get(connection_id)
                if websocket:
                    await websocket.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_id}: {e}")

        # Cleanup disconnected
        for connection_id in disconnected:
            self.disconnect(connection_id)

    async def broadcast_event(self, event_data: dict):
        """
        Broadcast an audit event to all subscribers.

        Args:
            event_data: Event data dictionary
        """
        message = {
            "type": "event",
            "data": event_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_topic("events", message)

    async def broadcast_metric(self, metric_data: dict):
        """
        Broadcast security metrics to all subscribers.

        Args:
            metric_data: Metric data dictionary
        """
        message = {
            "type": "metric",
            "data": metric_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_topic("metrics", message)

    async def broadcast_alert(self, alert_data: dict):
        """
        Broadcast a security alert to all subscribers.

        Args:
            alert_data: Alert data dictionary
        """
        message = {
            "type": "alert",
            "data": alert_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast_to_topic("alerts", message)

    async def send_to_user(self, user_id: str, message: dict):
        """
        Send a message to all connections of a specific user.

        Args:
            user_id: Target user ID
            message: Message dictionary to send
        """
        connection_ids = self.user_connections.get(user_id, set())
        for connection_id in connection_ids:
            await self.send_personal_message(connection_id, message)

    def get_connection_stats(self) -> dict:
        """
        Get statistics about current connections.

        Returns:
            Dictionary with connection statistics
        """
        return {
            "total_connections": len(self.active_connections),
            "authenticated_connections": sum(
                1 for m in self.connection_metadata.values() if m["authenticated"]
            ),
            "anonymous_connections": sum(
                1 for m in self.connection_metadata.values() if not m["authenticated"]
            ),
            "unique_users": len(self.user_connections),
            "topic_subscribers": {
                topic: len(subs) for topic, subs in self.topic_subscriptions.items()
            }
        }

    def get_user_connections(self, user_id: str) -> List[str]:
        """
        Get all connection IDs for a specific user.

        Args:
            user_id: User identifier

        Returns:
            List of connection IDs
        """
        return list(self.user_connections.get(user_id, set()))


# Singleton instance
_connection_manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    """Get the singleton connection manager instance"""
    return _connection_manager
