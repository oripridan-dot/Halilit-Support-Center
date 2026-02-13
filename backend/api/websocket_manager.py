"""
WebSocket Manager for Halilit Support Center v8.5

Manages real-time task status updates via WebSocket,
allowing frontend to receive live progress without polling.

Features:
- Connection pooling (multiple clients per task)
- Task state broadcasting
- Automatic retry/reconnection
- Graceful disconnection handling
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Set, Dict, List, Optional, Any
import json
import asyncio
import logging
from datetime import datetime
from celery.result import AsyncResult

from backend.celery_config import celery_app

logger = logging.getLogger(__name__)


class TaskConnectionManager:
    """
    Manages WebSocket connections for task status updates.

    Allows multiple clients to subscribe to the same task and receive
    real-time updates as the task progresses.
    """

    def __init__(self):
        # {task_id -> Set[WebSocket]}
        self.task_subscriptions: Dict[str, Set[WebSocket]] = {}

        # {task_id -> last_reported_state}
        self.task_state_cache: Dict[str, str] = {}

        # Async lock for thread-safe operations
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, task_id: str):
        """
        Register a WebSocket connection for a task.

        Args:
            websocket: FastAPI WebSocket connection
            task_id: Celery task ID to monitor
        """
        await websocket.accept()

        async with self.lock:
            if task_id not in self.task_subscriptions:
                self.task_subscriptions[task_id] = set()

            self.task_subscriptions[task_id].add(websocket)

        logger.info(f"✅ WebSocket connected for task {task_id} "
                    f"(total subscribers: {len(self.task_subscriptions[task_id])})")

        # Send initial status on connect
        await self._send_task_status(websocket, task_id)

    async def disconnect(self, websocket: WebSocket, task_id: str):
        """
        Unregister a WebSocket connection.

        Args:
            websocket: FastAPI WebSocket connection
            task_id: Celery task ID
        """
        async with self.lock:
            if task_id in self.task_subscriptions:
                self.task_subscriptions[task_id].discard(websocket)

                # Clean up empty task subscription
                if not self.task_subscriptions[task_id]:
                    del self.task_subscriptions[task_id]

        logger.info(f"👋 WebSocket disconnected for task {task_id}")

    async def broadcast_status(self, task_id: str, status: Dict[str, Any]):
        """
        Broadcast task status update to all subscribers.

        Args:
            task_id: Celery task ID
            status: Task status dictionary
        """
        async with self.lock:
            if task_id not in self.task_subscriptions:
                return

            connections = list(self.task_subscriptions[task_id])

        # Broadcast to all subscribers (outside lock to avoid deadlock)
        disconnected = []

        for websocket in connections:
            try:
                message = {
                    'type': 'task_status',
                    'task_id': task_id,
                    'data': status,
                    'timestamp': datetime.utcnow().isoformat()
                }

                await websocket.send_json(message)

            except Exception as e:
                logger.warning(f"⚠️ Failed to send message to subscriber: {e}")
                disconnected.append(websocket)

        # Clean up disconnected clients
        async with self.lock:
            for ws in disconnected:
                self.task_subscriptions[task_id].discard(ws)

    async def _send_task_status(self, websocket: WebSocket, task_id: str):
        """
        Send current task status to a single WebSocket.

        Args:
            websocket: WebSocket connection
            task_id: Celery task ID
        """
        try:
            result = AsyncResult(task_id, app=celery_app)

            # Build status response
            status = {
                'task_id': task_id,
                'state': result.state,
                'ready': result.ready(),
                'successful': result.successful() if result.ready() else None,
                'failed': result.failed() if result.ready() else None,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Add progress info
            if result.state == 'PROGRESS':
                if isinstance(result.info, dict):
                    status['progress'] = result.info.get(
                        'status', 'processing')
                    status['meta'] = result.info
                else:
                    status['progress'] = 'processing'

            # Add result on completion
            if result.ready():
                try:
                    if result.successful():
                        status['result'] = result.get(timeout=1)
                    else:
                        status['error'] = str(result.info)
                except Exception as e:
                    logger.warning(f"Failed to get result: {e}")

            message = {
                'type': 'task_status',
                'task_id': task_id,
                'data': status,
                'timestamp': datetime.utcnow().isoformat()
            }

            await websocket.send_json(message)

        except Exception as e:
            logger.error(f"Error sending status: {e}")

    async def poll_and_broadcast(self, task_id: str, interval: int = 2):
        """
        Continuously poll task status and broadcast updates to subscribers.

        Runs as a background task for a specific task_id.

        Args:
            task_id: Celery task ID to monitor
            interval: Polling interval in seconds
        """
        logger.info(f"📡 Started polling task {task_id} (interval={interval}s)")

        last_state = None
        consecutive_errors = 0

        while True:
            # Check if anyone is still subscribed
            async with self.lock:
                if task_id not in self.task_subscriptions or not self.task_subscriptions[task_id]:
                    logger.info(
                        f"🛑 No subscribers for task {task_id}, stopping poll")
                    break

            try:
                result = AsyncResult(task_id, app=celery_app)
                current_state = result.state

                # Only broadcast if state changed
                if current_state != last_state:
                    status = {
                        'task_id': task_id,
                        'state': current_state,
                        'ready': result.ready(),
                        'timestamp': datetime.utcnow().isoformat()
                    }

                    # Add progress/result data
                    if current_state == 'PROGRESS':
                        if isinstance(result.info, dict):
                            status['progress'] = result.info.get(
                                'status', 'processing')
                            status['meta'] = result.info
                    elif current_state == 'SUCCESS':
                        try:
                            status['result'] = result.get(timeout=1)
                        except Exception as e:
                            logger.warning(f"Failed to get result: {e}")
                    elif current_state == 'FAILURE':
                        status['error'] = str(result.info)

                    await self.broadcast_status(task_id, status)
                    last_state = current_state
                    consecutive_errors = 0

                    # Stop polling if task completed
                    if result.ready():
                        logger.info(
                            f"✅ Task {task_id} completed (state={current_state})")
                        break

                await asyncio.sleep(interval)

            except Exception as e:
                consecutive_errors += 1
                logger.warning(
                    f"⚠️ Poll error for task {task_id}: {e} (attempt {consecutive_errors})")

                if consecutive_errors >= 5:
                    logger.error(
                        f"❌ Giving up on task {task_id} after 5 consecutive errors")
                    break

                await asyncio.sleep(interval * 2)  # Backoff on error

    async def handle_websocket(self, websocket: WebSocket, task_id: str):
        """
        Handle a WebSocket connection for a task.

        This is meant to be called from a FastAPI route.

        Args:
            websocket: FastAPI WebSocket connection
            task_id: Celery task ID to monitor

        Example usage in FastAPI route:

        @app.websocket("/ws/tasks/{task_id}")
        async def websocket_endpoint(websocket: WebSocket, task_id: str):
            await connection_manager.handle_websocket(websocket, task_id)
        """
        await self.connect(websocket, task_id)

        try:
            while True:
                # Receive heartbeat or commands from client
                data = await websocket.receive_text()

                try:
                    message = json.loads(data)
                    command = message.get('command', 'ping')

                    if command == 'ping':
                        # Send pong with current status
                        await self._send_task_status(websocket, task_id)

                    elif command == 'cancel':
                        # Cancel the task
                        celery_app.control.revoke(task_id, terminate=True)
                        await websocket.send_json({
                            'type': 'task_cancelled',
                            'task_id': task_id,
                            'timestamp': datetime.utcnow().isoformat()
                        })

                    else:
                        logger.warning(f"Unknown command: {command}")

                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received: {data}")

        except WebSocketDisconnect:
            await self.disconnect(websocket, task_id)
            logger.info(f"WebSocket disconnected for task {task_id}")

        except Exception as e:
            logger.error(f"WebSocket error for task {task_id}: {e}")
            await self.disconnect(websocket, task_id)


# Global connection manager instance
connection_manager = TaskConnectionManager()


# ============================================================================
# FastAPI WebSocket Route (to be included in main app)
# ============================================================================

async def create_websocket_route(app):
    """
    Factory function to add WebSocket route to FastAPI app.

    Usage:

    app = FastAPI()
    await create_websocket_route(app)
    """

    @app.websocket("/ws/tasks/{task_id}")
    async def websocket_endpoint(websocket: WebSocket, task_id: str):
        """
        WebSocket endpoint for real-time task status.

        Connects to a task and receives live updates as it progresses.

        Path Parameters:
        - task_id: Celery task ID

        Message Format (Server → Client):
        {
            "type": "task_status",
            "task_id": "uuid",
            "data": {
                "state": "PROGRESS",
                "progress": "enriching",
                "meta": {...}
            },
            "timestamp": "2026-02-09T12:34:56.789123"
        }

        Client Commands (Client → Server):
        - {"command": "ping"}  # Request current status
        - {"command": "cancel"}  # Cancel the task

        Example (JavaScript):

        const ws = new WebSocket('ws://localhost:8000/ws/tasks/task-uuid-here');

        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            console.log('Task state:', msg.data.state);
            console.log('Progress:', msg.data.progress);
        };

        ws.send(JSON.stringify({command: 'ping'}));
        """
        await connection_manager.handle_websocket(websocket, task_id)


__all__ = [
    'connection_manager',
    'TaskConnectionManager',
    'create_websocket_route',
]
