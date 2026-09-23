"""
WebSocket Router for real-time security event streaming.
Provides WebSocket endpoints for audit events, metrics, and alerts.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from typing import Optional
import uuid
import logging
import json

from app.core.websocket_manager import get_connection_manager, ConnectionManager
from app.core.auth_middleware import get_current_active_user
from app.models.auth_models import User


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ws",
    tags=["websocket"]
)


@router.websocket("/audit/stream")
async def audit_stream(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="JWT token for authentication"),
    manager: ConnectionManager = Depends(get_connection_manager)
):
    """
    WebSocket endpoint for real-time audit event streaming.

    **Authentication:**
    - Optional JWT token via query parameter: `/ws/audit/stream?token=your_jwt_token`
    - Anonymous connections allowed but may have limited access

    **Message Format (Client → Server):**

    Subscribe to topics:
    ```json
    {
        "action": "subscribe",
        "topics": ["events", "metrics", "alerts"]
    }
    ```

    Unsubscribe from topics:
    ```json
    {
        "action": "unsubscribe",
        "topics": ["events"]
    }
    ```

    Ping (keep-alive):
    ```json
    {
        "action": "ping"
    }
    ```

    **Message Format (Server → Client):**

    Connection acknowledged:
    ```json
    {
        "type": "connection",
        "status": "connected",
        "connection_id": "uuid",
        "user": "username",
        "timestamp": "ISO8601"
    }
    ```

    Subscription confirmed:
    ```json
    {
        "type": "subscription",
        "status": "subscribed",
        "topics": ["events", "metrics"],
        "timestamp": "ISO8601"
    }
    ```

    Audit event:
    ```json
    {
        "type": "event",
        "topic": "events",
        "data": { ... },
        "timestamp": "ISO8601"
    }
    ```

    Security metric:
    ```json
    {
        "type": "metric",
        "topic": "metrics",
        "data": { ... },
        "timestamp": "ISO8601"
    }
    ```

    Security alert:
    ```json
    {
        "type": "alert",
        "topic": "alerts",
        "data": { ... },
        "timestamp": "ISO8601"
    }
    ```

    Pong response:
    ```json
    {
        "type": "pong",
        "timestamp": "ISO8601"
    }
    ```

    **Topics:**
    - `events`: Audit events (logins, permissions, etc.)
    - `metrics`: Real-time security metrics
    - `alerts`: Security alerts
    - `all`: All event types

    **Example Usage:**

    JavaScript:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/audit/stream?token=your_jwt');

    ws.onopen = () => {
        // Subscribe to events and alerts
        ws.send(JSON.stringify({
            action: 'subscribe',
            topics: ['events', 'alerts']
        }));
    };

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        console.log('Received:', message);
    };
    ```

    Python:
    ```python
    import websockets
    import json

    async with websockets.connect('ws://localhost:8000/ws/audit/stream') as ws:
        # Subscribe
        await ws.send(json.dumps({
            'action': 'subscribe',
            'topics': ['events']
        }))

        # Receive messages
        async for message in ws:
            data = json.loads(message)
            print(data)
    ```
    """
    connection_id = str(uuid.uuid4())

    # Connect
    connected = await manager.connect(websocket, connection_id, token)
    if not connected:
        return

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                action = message.get("action")

                if action == "subscribe":
                    # Subscribe to topics
                    topics = message.get("topics", [])
                    await manager.subscribe(connection_id, topics)

                elif action == "unsubscribe":
                    # Unsubscribe from topics
                    topics = message.get("topics", [])
                    await manager.unsubscribe(connection_id, topics)

                elif action == "ping":
                    # Respond to ping
                    await manager.send_personal_message(
                        connection_id,
                        {
                            "type": "pong",
                            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
                        }
                    )

                elif action == "stats":
                    # Send connection stats (admin only)
                    stats = manager.get_connection_stats()
                    await manager.send_personal_message(
                        connection_id,
                        {
                            "type": "stats",
                            "data": stats,
                            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
                        }
                    )

                else:
                    # Unknown action
                    await manager.send_personal_message(
                        connection_id,
                        {
                            "type": "error",
                            "message": f"Unknown action: {action}",
                            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
                        }
                    )

            except json.JSONDecodeError:
                await manager.send_personal_message(
                    connection_id,
                    {
                        "type": "error",
                        "message": "Invalid JSON",
                        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
                    }
                )
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await manager.send_personal_message(
                    connection_id,
                    {
                        "type": "error",
                        "message": "Internal server error",
                        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
                    }
                )

    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        logger.info(f"Client disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(connection_id)


@router.get("/audit/connections")
async def get_connection_stats(
    current_user: User = Depends(get_current_active_user),
    manager: ConnectionManager = Depends(get_connection_manager)
):
    """
    Get WebSocket connection statistics.
    Requires authentication.

    Returns:
    - total_connections: Total active WebSocket connections
    - authenticated_connections: Connections with valid JWT
    - anonymous_connections: Connections without authentication
    - unique_users: Number of unique authenticated users
    - topic_subscribers: Subscriber count per topic
    """
    return manager.get_connection_stats()
