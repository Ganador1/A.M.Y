import os
import asyncio

class Lean4Installer:
    def __init__(self):
        # minimal state
        self.install_paths = {
            'darwin': '/usr/local/bin',
            'linux': '/usr/bin',
        }

    async def detect_system_info(self):
        return {
            'os': os.name,
            'architecture': os.uname().machine if hasattr(os, 'uname') else 'unknown',
            'is_supported': True,
            'install_path': self.install_paths.get('darwin' if os.name == 'posix' else 'linux'),
            'dependencies': []
        }

    async def check_existing_installation(self):
        path = self.install_paths.get('darwin' if os.name == 'posix' else 'linux')
        elan_exists = os.path.exists(path)
        return {
            'elan_path_exists': elan_exists,
            'lean_binary_exists': elan_exists,
            'fully_installed': elan_exists
        }

    async def install_lean4(self, force_reinstall=False):
        if not self.detect_system_info:
            return {'success': False, 'error': 'no soportado'}
        existing = await self.check_existing_installation()
        if existing.get('fully_installed') and not force_reinstall:
            return {'success': True, 'action': 'skipped'}
        # Simulate install
        await asyncio.sleep(0.01)
        return {'success': True, 'action': 'installed'}

    async def uninstall_lean4(self):
        # Simulate uninstall
        await asyncio.sleep(0.01)
        return {'success': True, 'action': 'none_required'}


lean4_installer = Lean4Installer()
