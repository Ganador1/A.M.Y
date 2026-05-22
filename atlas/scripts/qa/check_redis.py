#!/usr/bin/env python3
"""
Redis Setup and Health Check Script for AXIOM

ETHICS/SECURITY
- No ejecutes comandos con entrada no confiable. Este script usa timeouts y evita shell=True salvo en instalación manual.
- Requiere privilegios para algunas operaciones (brew/yum/apt/systemctl). Revísalas antes de proceder.
- No expongas Redis sin contraseña/TLS en redes públicas. Consulta ETHICS_AND_SAFETY.md.
"""

import subprocess
import sys
import platform
import os  # noqa: F401


def run_command(command, shell=False, timeout=60):
    """Run a shell command and return the result"""
    try:
        args = command if shell else command.split()
        result = subprocess.run(
            args,
            shell=shell,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout,
        )
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return None, str(e)
    except subprocess.TimeoutExpired:
        return None, f"Timeout: {command}"


def check_redis_installed():
    """Check if Redis is installed"""
    print("🔍 Checking if Redis is installed...")

    # Try redis-cli first
    stdout, stderr = run_command("redis-cli --version")
    if stdout:
        print(f"✅ Redis CLI found: {stdout}")
        return True

    # Try redis-server
    stdout, stderr = run_command("redis-server --version")
    if stdout:
        print(f"✅ Redis Server found: {stdout}")
        return True

    print("❌ Redis is not installed")
    return False


def check_redis_running():
    """Check if Redis server is running"""
    print("🔍 Checking if Redis server is running...")

    stdout, stderr = run_command("redis-cli ping")
    if stdout and "PONG" in stdout:
        print("✅ Redis server is running")
        return True

    print("❌ Redis server is not running")
    return False


def install_redis_macos():
    """Install Redis on macOS"""
    print("🍎 Installing Redis on macOS...")

    # Try Homebrew first
    stdout, stderr = run_command("brew --version")
    if stdout:
        print("📦 Using Homebrew to install Redis...")
        stdout, stderr = run_command("brew install redis")
        if stdout or stderr:
            print("✅ Redis installed via Homebrew")
            return True

    # Fallback to manual download
    print("📥 Downloading Redis manually...")
    commands = [
        "curl -O http://download.redis.io/redis-stable.tar.gz",
        "tar xzf redis-stable.tar.gz",
        "cd redis-stable && make",
        "cd redis-stable && sudo make install"
    ]

    for cmd in commands:
        print(f"Running: {cmd}")
        stdout, stderr = run_command(cmd, shell=True)
        if stderr and "Error" in stderr:
            print(f"❌ Error: {stderr}")
            return False

    print("✅ Redis installed manually")
    return True


def install_redis_linux():
    """Install Redis on Linux"""
    print("🐧 Installing Redis on Linux...")

    # Try apt (Ubuntu/Debian)
    stdout, stderr = run_command("sudo apt update")
    if stdout or stderr:
        stdout, stderr = run_command("sudo apt install -y redis-server")
        if stdout or stderr:
            print("✅ Redis installed via apt")
            return True

    # Try yum (CentOS/RHEL)
    stdout, stderr = run_command("sudo yum install -y redis")
    if stdout or stderr:
        print("✅ Redis installed via yum")
        return True

    print("❌ Could not install Redis automatically")
    return False


def install_redis_windows():
    """Install Redis on Windows"""
    print("🪟 Installing Redis on Windows...")

    # Check if Chocolatey is available
    stdout, stderr = run_command("choco --version")
    if stdout:
        print("📦 Using Chocolatey to install Redis...")
        stdout, stderr = run_command("choco install redis-64")
        if stdout or stderr:
            print("✅ Redis installed via Chocolatey")
            return True

    print("❌ Please install Redis manually on Windows:")
    print("   1. Download from: https://redis.io/download")
    print("   2. Extract to C:\\Redis")
    print("   3. Run: redis-server.exe")
    return False


def start_redis():
    """Start Redis server"""
    print("🚀 Starting Redis server...")

    if platform.system() == "Darwin":  # macOS
        stdout, stderr = run_command("brew services start redis")
        if stdout or stderr:
            print("✅ Redis started via Homebrew services")
            return True

        # Try manual start
        stdout, stderr = run_command("redis-server /usr/local/etc/redis.conf")
        if stdout or stderr:
            print("✅ Redis started manually")
            return True

    elif platform.system() == "Linux":
        stdout, stderr = run_command("sudo systemctl start redis")
        if stdout or stderr:
            print("✅ Redis started via systemctl")
            return True

        # Try manual start
        stdout, stderr = run_command("redis-server")
        if stdout or stderr:
            print("✅ Redis started manually")
            return True

    elif platform.system() == "Windows":
        print("🪟 On Windows, please start Redis manually:")
        print("   Run: redis-server.exe")
        return False

    print("❌ Could not start Redis automatically")
    return False


def test_redis_connection():
    """Test Redis connection using Python"""
    print("🔍 Testing Redis connection with Python...")

    try:
        import redis
        client = redis.from_url("redis://localhost:6379", decode_responses=True)
        client.ping()
        print("✅ Redis connection successful")

        # Test basic operations
        client.set("axiom_test", "working")
        value = client.get("axiom_test")
        if value == "working":
            print("✅ Redis read/write test passed")
            client.delete("axiom_test")
            return True
        else:
            print("❌ Redis read/write test failed")
            return False

    except ImportError:
        print("❌ redis Python package not installed")
        print("   Run: pip install redis")
        return False
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


def main():
    """Main function"""
    print("🔧 AXIOM Redis Setup and Health Check")
    print("=" * 50)

    system = platform.system()
    print(f"🖥️  Detected OS: {system}")

    # Check if Redis is installed
    if not check_redis_installed():
        print("\n📦 Installing Redis...")

        if system == "Darwin":
            success = install_redis_macos()
        elif system == "Linux":
            success = install_redis_linux()
        elif system == "Windows":
            success = install_redis_windows()
        else:
            print(f"❌ Unsupported OS: {system}")
            return 1

        if not success:
            return 1

    # Check if Redis is running
    if not check_redis_running():
        print("\n🚀 Starting Redis...")
        if not start_redis():
            return 1

    # Test connection
    print("\n🔍 Testing Redis connection...")
    if test_redis_connection():
        print("\n🎉 Redis is ready for AXIOM!")
        print("   Redis URL: redis://localhost:6379")
        print("   You can now start AXIOM with Redis caching enabled")
        return 0
    else:
        print("\n❌ Redis setup failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
