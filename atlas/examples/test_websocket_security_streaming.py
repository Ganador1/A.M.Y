"""
Test script for WebSocket Security Streaming (R3.8)
Demonstrates real-time audit event broadcasting via WebSocket.
"""

import asyncio
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.audit_service import AuditService
from app.core.websocket_manager import get_connection_manager


async def simulate_security_events():
    """
    Simulate various security events to test WebSocket broadcasting.
    """
    print("\n" + "="*80)
    print("🔐 ATLAS Security Dashboard - WebSocket Streaming Test")
    print("="*80)

    db: Session = SessionLocal()
    service = AuditService()
    manager = get_connection_manager()

    try:
        print(f"\n📊 Connection Manager Status:")
        stats = manager.get_connection_stats()
        print(f"  - Total connections: {stats['total_connections']}")
        print(f"  - Authenticated: {stats['authenticated_connections']}")
        print(f"  - Anonymous: {stats['anonymous_connections']}")
        print(f"  - Unique users: {stats['unique_users']}")

        print("\n🎬 Starting event simulation...")
        print("-" * 80)

        # Event 1: Successful login
        print("\n1️⃣  Simulating successful login...")
        event1 = await service.log_event(
            db=db,
            event_type=service.EVENT_AUTH_LOGIN,
            category=service.CAT_AUTH,
            message="User logged in successfully",
            user_id="user_001",
            username="john_doe",
            ip_address="192.168.1.100",
            severity=service.SEV_INFO,
            success=True,
            endpoint="/api/auth/login",
            method="POST"
        )
        print(f"   ✅ Event logged: {event1.id}")
        await asyncio.sleep(1)

        # Event 2: Failed login attempt
        print("\n2️⃣  Simulating failed login attempt...")
        event2 = await service.log_event(
            db=db,
            event_type=service.EVENT_AUTH_FAILED,
            category=service.CAT_AUTH,
            message="Invalid credentials provided",
            username="attacker_user",
            ip_address="203.0.113.42",
            severity=service.SEV_WARNING,
            success=False,
            endpoint="/api/auth/login",
            method="POST"
        )
        print(f"   ⚠️  Event logged: {event2.id}")
        await asyncio.sleep(1)

        # Event 3: Rate limit exceeded
        print("\n3️⃣  Simulating rate limit exceeded...")
        event3 = await service.log_event(
            db=db,
            event_type=service.EVENT_RATE_LIMIT,
            category=service.CAT_SECURITY,
            message="Rate limit exceeded for endpoint",
            ip_address="203.0.113.42",
            severity=service.SEV_ERROR,
            success=False,
            endpoint="/api/data-versioning/versions",
            method="GET"
        )
        print(f"   🚫 Event logged: {event3.id}")
        await asyncio.sleep(1)

        # Event 4: Permission denied
        print("\n4️⃣  Simulating permission denied...")
        event4 = await service.log_event(
            db=db,
            event_type=service.EVENT_PERMISSION_DENIED,
            category=service.CAT_AUTHZ,
            message="User attempted to access admin endpoint without permissions",
            user_id="user_002",
            username="regular_user",
            ip_address="192.168.1.105",
            severity=service.SEV_WARNING,
            success=False,
            endpoint="/api/admin/users",
            method="DELETE"
        )
        print(f"   ⛔ Event logged: {event4.id}")
        await asyncio.sleep(1)

        # Event 5: User created
        print("\n5️⃣  Simulating user creation...")
        event5 = await service.log_event(
            db=db,
            event_type=service.EVENT_USER_CREATED,
            category=service.CAT_ADMIN,
            message="New user account created",
            user_id="admin_001",
            username="admin",
            ip_address="192.168.1.1",
            severity=service.SEV_INFO,
            success=True,
            endpoint="/api/admin/users",
            method="POST",
            details={"new_user": "jane_smith", "role": "researcher"}
        )
        print(f"   ✅ Event logged: {event5.id}")
        await asyncio.sleep(1)

        # Event 6-10: Multiple failed logins (should trigger brute force alert)
        print("\n6️⃣-1️⃣0️⃣  Simulating brute force attack (5 failed logins)...")
        for i in range(5):
            event = await service.log_event(
                db=db,
                event_type=service.EVENT_AUTH_FAILED,
                category=service.CAT_AUTH,
                message=f"Brute force attempt {i+1}/5",
                username="target_user",
                ip_address="198.51.100.99",
                severity=service.SEV_WARNING,
                success=False,
                endpoint="/api/auth/login",
                method="POST"
            )
            print(f"   ⚠️  Failed login {i+1}: {event.id}")
            await asyncio.sleep(0.5)

        print("\n🚨 Checking for triggered alerts...")
        alerts = await service.get_active_alerts(db=db, limit=10)
        if alerts:
            print(f"   Found {len(alerts)} active alert(s):")
            for alert in alerts:
                print(f"   - {alert.alert_type}: {alert.title} (Risk: {alert.risk_score})")
        else:
            print("   No alerts triggered")

        # Get recent metrics
        print("\n📈 Getting real-time metrics...")
        metrics = await service.get_realtime_metrics(
            db=db,
            window_minutes=60
        )
        print(f"   - Total events (1h): {metrics['total_events']}")
        print(f"   - Failed attempts: {metrics['failed_attempts']}")
        print(f"   - Unique users: {metrics['unique_users']}")
        print(f"   - Unique IPs: {metrics['unique_ips']}")

        print("\n" + "-" * 80)
        print("✅ Event simulation completed!")
        print("\n💡 To view these events in real-time:")
        print("   1. Start the FastAPI server: python main.py")
        print("   2. Open: examples/websocket_dashboard.html in a browser")
        print("   3. Connect to: ws://localhost:8000/ws/audit/stream")
        print("   4. Run this script again to see live updates")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Error during simulation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    # Run async event simulation
    asyncio.run(simulate_security_events())
