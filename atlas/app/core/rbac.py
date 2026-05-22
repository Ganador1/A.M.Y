"""
Role-Based Access Control (RBAC) for AXIOM ATLAS
Defines user roles, permissions, and access control decorators.
"""

from enum import Enum
from typing import List, Set, Callable
from functools import wraps
import logging

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """User roles in AXIOM ATLAS"""
    ADMIN = "admin"
    RESEARCHER = "researcher"
    VIEWER = "viewer"
    API_CONSUMER = "api_consumer"


class Permission(str, Enum):
    """System permissions"""
    # Data operations
    READ_DATA = "read:data"
    WRITE_DATA = "write:data"
    DELETE_DATA = "delete:data"

    # Experiment operations
    CREATE_EXPERIMENT = "create:experiment"
    RUN_EXPERIMENT = "run:experiment"
    DELETE_EXPERIMENT = "delete:experiment"

    # Hypothesis operations
    GENERATE_HYPOTHESIS = "generate:hypothesis"
    VALIDATE_HYPOTHESIS = "validate:hypothesis"

    # System operations
    MANAGE_USERS = "manage:users"
    VIEW_AUDIT_LOGS = "view:audit_logs"
    CONFIGURE_SYSTEM = "configure:system"

    # API operations
    API_READ = "api:read"
    API_WRITE = "api:write"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        # Admin has all permissions
        Permission.READ_DATA,
        Permission.WRITE_DATA,
        Permission.DELETE_DATA,
        Permission.CREATE_EXPERIMENT,
        Permission.RUN_EXPERIMENT,
        Permission.DELETE_EXPERIMENT,
        Permission.GENERATE_HYPOTHESIS,
        Permission.VALIDATE_HYPOTHESIS,
        Permission.MANAGE_USERS,
        Permission.VIEW_AUDIT_LOGS,
        Permission.CONFIGURE_SYSTEM,
        Permission.API_READ,
        Permission.API_WRITE,
    },
    Role.RESEARCHER: {
        # Researchers can do scientific work
        Permission.READ_DATA,
        Permission.WRITE_DATA,
        Permission.CREATE_EXPERIMENT,
        Permission.RUN_EXPERIMENT,
        Permission.GENERATE_HYPOTHESIS,
        Permission.VALIDATE_HYPOTHESIS,
        Permission.API_READ,
        Permission.API_WRITE,
    },
    Role.VIEWER: {
        # Viewers have read-only access
        Permission.READ_DATA,
        Permission.API_READ,
    },
    Role.API_CONSUMER: {
        # API consumers have programmatic access
        Permission.API_READ,
        Permission.API_WRITE,
        Permission.READ_DATA,
        Permission.WRITE_DATA,
    },
}


def has_permission(user_role: str, required_permission: Permission) -> bool:
    """
    Check if a user role has a specific permission.

    Args:
        user_role: User's role as string
        required_permission: Permission to check

    Returns:
        True if role has permission, False otherwise
    """
    try:
        role = Role(user_role)
        permissions = ROLE_PERMISSIONS.get(role, set())
        return required_permission in permissions
    except ValueError:
        logger.warning("Invalid role: %s", user_role)
        return False


def has_role(user_role: str, required_roles: List[Role]) -> bool:
    """
    Check if user has one of the required roles.

    Args:
        user_role: User's role as string
        required_roles: List of acceptable roles

    Returns:
        True if user has one of the required roles
    """
    try:
        role = Role(user_role)
        return role in required_roles
    except ValueError:
        logger.warning("Invalid role: %s", user_role)
        return False


def require_permission(permission: Permission) -> Callable:
    """
    Decorator to require specific permission for endpoint access.

    Usage:
        @router.get("/sensitive-data")
        @require_permission(Permission.READ_DATA)
        async def get_sensitive_data(current_user: User = Depends(get_current_user)):
            ...

    Args:
        permission: Required permission

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get('current_user')

            if not current_user:
                logger.error("No current_user found in request")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            user_role = current_user.get('role')

            if not has_permission(user_role, permission):
                logger.warning(
                    "Permission denied - User: %s, Role: %s, Required: %s",
                    current_user.get('sub'),
                    user_role,
                    permission.value
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required: {permission.value}"
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_role(*roles: Role) -> Callable:
    """
    Decorator to require specific role(s) for endpoint access.

    Usage:
        @router.delete("/experiments/{id}")
        @require_role(Role.ADMIN, Role.RESEARCHER)
        async def delete_experiment(id: str, current_user: User = Depends(get_current_user)):
            ...

    Args:
        *roles: Required roles (user must have at least one)

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get('current_user')

            if not current_user:
                logger.error("No current_user found in request")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            user_role = current_user.get('role')

            if not has_role(user_role, list(roles)):
                logger.warning(
                    "Role check failed - User: %s, Role: %s, Required: %s",
                    current_user.get('sub'),
                    user_role,
                    [r.value for r in roles]
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {[r.value for r in roles]}"
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


# Convenience decorators for common role combinations
def admin_only(func: Callable) -> Callable:
    """Require admin role - shortcut decorator"""
    return require_role(Role.ADMIN)(func)


def researcher_or_admin(func: Callable) -> Callable:
    """Require researcher or admin role - shortcut decorator"""
    return require_role(Role.ADMIN, Role.RESEARCHER)(func)
