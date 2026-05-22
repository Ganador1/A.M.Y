"""
IP Whitelisting Module - AXIOM ATLAS
====================================

Módulo para control de acceso basado en IP.
Implementa whitelisting de IPs permitidas.

Author: AXIOM Team
Date: 2025-01-01
Version: 1.0.0
"""

import ipaddress
from typing import List, Optional
from fastapi import Request, HTTPException
import logging

logger = logging.getLogger(__name__)


class IPWhitelist:
    """Control de acceso basado en IP"""
    
    def __init__(self, allowed_networks: List[str] = None):
        self.allowed_networks = allowed_networks or [
            "127.0.0.1/32",      # localhost
            "10.0.0.0/8",         # redes privadas clase A
            "172.16.0.0/12",     # redes privadas clase B
            "192.168.0.0/16"     # redes privadas clase C
        ]
        self._compile_networks()
    
    def _compile_networks(self):
        """Compilar redes permitidas para verificación rápida"""
        self.networks = []
        for network_str in self.allowed_networks:
            try:
                network = ipaddress.ip_network(network_str, strict=False)
                self.networks.append(network)
            except ValueError as e:
                logger.error(f"Invalid network {network_str}: {e}")
    
    def is_allowed(self, ip: str) -> bool:
        """Verificar si una IP está permitida"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return any(ip_obj in network for network in self.networks)
        except ValueError:
            logger.error(f"Invalid IP address: {ip}")
            return False
    
    def add_network(self, network_str: str):
        """Agregar red permitida"""
        try:
            network = ipaddress.ip_network(network_str, strict=False)
            self.networks.append(network)
            self.allowed_networks.append(network_str)
            logger.info(f"Added allowed network: {network_str}")
        except ValueError as e:
            logger.error(f"Invalid network {network_str}: {e}")
    
    def remove_network(self, network_str: str):
        """Remover red permitida"""
        try:
            network = ipaddress.ip_network(network_str, strict=False)
            self.networks = [n for n in self.networks if n != network]
            if network_str in self.allowed_networks:
                self.allowed_networks.remove(network_str)
            logger.info(f"Removed allowed network: {network_str}")
        except ValueError as e:
            logger.error(f"Invalid network {network_str}: {e}")


# Instancia global
ip_whitelist = IPWhitelist()


def check_ip_access(request: Request) -> bool:
    """Verificar acceso basado en IP"""
    client_ip = request.client.host
    
    # Verificar IP real si hay proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    
    is_allowed = ip_whitelist.is_allowed(client_ip)
    
    if not is_allowed:
        logger.warning(f"Blocked access from IP: {client_ip}")
        raise HTTPException(
            status_code=403,
            detail={"error": "IP not allowed", "ip": client_ip}
        )
    
    return True


def setup_ip_whitelisting_middleware(app):
    """Configurar middleware de IP whitelisting"""
    from fastapi import Request
    from starlette.middleware.base import BaseHTTPMiddleware
    
    class IPWhitelistMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            # Verificar IP antes de procesar request
            check_ip_access(request)
            response = await call_next(request)
            return response
    
    app.add_middleware(IPWhitelistMiddleware)
    logger.info("✅ IP whitelisting middleware configured")
