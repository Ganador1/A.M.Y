"""
Unit tests for RBAC (Role-Based Access Control)
Tests roles, permissions, and authorization decorators.
"""

import pytest
from fastapi import HTTPException

from app.core.rbac import (
    Role,
    Permission,
    ROLE_PERMISSIONS,
    has_permission,
    has_role,
    require_permission,
    require_role
)


class TestRoleEnum:
    """Test suite for Role enum"""

    def test_all_roles_defined(self):
        """Test that all expected roles are defined"""
        expected_roles = {"ADMIN", "RESEARCHER", "VIEWER", "API_CONSUMER"}
        actual_roles = {role.value for role in Role}
        assert actual_roles == expected_roles

    def test_role_values(self):
        """Test role enum values"""
        assert Role.ADMIN.value == "ADMIN"
        assert Role.RESEARCHER.value == "RESEARCHER"
        assert Role.VIEWER.value == "VIEWER"
        assert Role.API_CONSUMER.value == "API_CONSUMER"


class TestPermissionEnum:
    """Test suite for Permission enum"""

    def test_all_permissions_defined(self):
        """Test that all expected permissions are defined"""
        expected_permissions = {
            "read_hypothesis",
            "create_hypothesis",
            "execute_experiment",
            "read_experiment",
            "manage_models",
            "read_models",
            "access_api",
            "manage_users",
            "read_users",
            "manage_data",
            "read_data",
            "manage_system",
            "read_system"
        }
        actual_permissions = {perm.value for perm in Permission}
        assert actual_permissions == expected_permissions

    def test_permission_values(self):
        """Test specific permission values"""
        assert Permission.READ_HYPOTHESIS.value == "read_hypothesis"
        assert Permission.CREATE_HYPOTHESIS.value == "create_hypothesis"
        assert Permission.MANAGE_SYSTEM.value == "manage_system"


class TestRolePermissions:
    """Test suite for role-permission mappings"""

    def test_admin_has_all_permissions(self):
        """Test that ADMIN role has all permissions"""
        admin_perms = ROLE_PERMISSIONS[Role.ADMIN]
        all_permissions = set(Permission)
        assert admin_perms == all_permissions

    def test_researcher_permissions(self):
        """Test RESEARCHER role permissions"""
        researcher_perms = ROLE_PERMISSIONS[Role.RESEARCHER]
        
        # Should have these permissions
        assert Permission.READ_HYPOTHESIS in researcher_perms
        assert Permission.CREATE_HYPOTHESIS in researcher_perms
        assert Permission.EXECUTE_EXPERIMENT in researcher_perms
        assert Permission.READ_EXPERIMENT in researcher_perms
        assert Permission.MANAGE_MODELS in researcher_perms
        assert Permission.READ_DATA in researcher_perms
        
        # Should NOT have these permissions
        assert Permission.MANAGE_USERS not in researcher_perms
        assert Permission.MANAGE_SYSTEM not in researcher_perms

    def test_viewer_permissions(self):
        """Test VIEWER role permissions"""
        viewer_perms = ROLE_PERMISSIONS[Role.VIEWER]
        
        # Should have read-only permissions
        assert Permission.READ_HYPOTHESIS in viewer_perms
        assert Permission.READ_EXPERIMENT in viewer_perms
        assert Permission.READ_MODELS in viewer_perms
        assert Permission.READ_DATA in viewer_perms
        assert Permission.READ_SYSTEM in viewer_perms
        
        # Should NOT have write permissions
        assert Permission.CREATE_HYPOTHESIS not in viewer_perms
        assert Permission.EXECUTE_EXPERIMENT not in viewer_perms
        assert Permission.MANAGE_MODELS not in viewer_perms
        assert Permission.MANAGE_USERS not in viewer_perms

    def test_api_consumer_permissions(self):
        """Test API_CONSUMER role permissions"""
        api_perms = ROLE_PERMISSIONS[Role.API_CONSUMER]
        
        # Should have API access
        assert Permission.ACCESS_API in api_perms
        assert Permission.READ_HYPOTHESIS in api_perms
        assert Permission.READ_EXPERIMENT in api_perms
        
        # Should NOT have management permissions
        assert Permission.MANAGE_USERS not in api_perms
        assert Permission.MANAGE_SYSTEM not in api_perms


class TestHasPermission:
    """Test suite for has_permission function"""

    def test_admin_has_all_permissions(self):
        """Test admin has all permissions"""
        for permission in Permission:
            assert has_permission(Role.ADMIN, permission) is True

    def test_researcher_has_create_hypothesis(self):
        """Test researcher has create_hypothesis permission"""
        assert has_permission(Role.RESEARCHER, Permission.CREATE_HYPOTHESIS) is True

    def test_viewer_lacks_create_hypothesis(self):
        """Test viewer lacks create_hypothesis permission"""
        assert has_permission(Role.VIEWER, Permission.CREATE_HYPOTHESIS) is False

    def test_viewer_has_read_permissions(self):
        """Test viewer has read permissions"""
        assert has_permission(Role.VIEWER, Permission.READ_HYPOTHESIS) is True
        assert has_permission(Role.VIEWER, Permission.READ_EXPERIMENT) is True
        assert has_permission(Role.VIEWER, Permission.READ_DATA) is True

    def test_api_consumer_has_api_access(self):
        """Test API consumer has API access"""
        assert has_permission(Role.API_CONSUMER, Permission.ACCESS_API) is True

    def test_non_admin_lacks_manage_system(self):
        """Test non-admin roles lack system management"""
        assert has_permission(Role.RESEARCHER, Permission.MANAGE_SYSTEM) is False
        assert has_permission(Role.VIEWER, Permission.MANAGE_SYSTEM) is False
        assert has_permission(Role.API_CONSUMER, Permission.MANAGE_SYSTEM) is False


class TestHasRole:
    """Test suite for has_role function"""

    def test_exact_role_match(self):
        """Test exact role matching"""
        assert has_role(Role.ADMIN, Role.ADMIN) is True
        assert has_role(Role.RESEARCHER, Role.RESEARCHER) is True
        assert has_role(Role.VIEWER, Role.VIEWER) is True

    def test_role_mismatch(self):
        """Test role mismatch"""
        assert has_role(Role.VIEWER, Role.ADMIN) is False
        assert has_role(Role.RESEARCHER, Role.VIEWER) is False
        assert has_role(Role.API_CONSUMER, Role.ADMIN) is False


class TestRequirePermissionDecorator:
    """Test suite for require_permission decorator"""

    def test_decorator_allows_with_permission(self):
        """Test decorator allows access with correct permission"""
        @require_permission(Permission.READ_HYPOTHESIS)
        def protected_function(user_role: Role):
            return "success"
        
        # Admin has all permissions
        result = protected_function(Role.ADMIN)
        assert result == "success"
        
        # Researcher has read_hypothesis
        result = protected_function(Role.RESEARCHER)
        assert result == "success"

    def test_decorator_denies_without_permission(self):
        """Test decorator denies access without permission"""
        @require_permission(Permission.MANAGE_USERS)
        def admin_only_function(user_role: Role):
            return "success"
        
        # Viewer doesn't have manage_users permission
        with pytest.raises(HTTPException) as exc_info:
            admin_only_function(Role.VIEWER)
        
        assert exc_info.value.status_code == 403
        assert "insufficient permissions" in exc_info.value.detail.lower()

    def test_decorator_allows_admin(self):
        """Test decorator always allows admin"""
        @require_permission(Permission.MANAGE_SYSTEM)
        def system_function(user_role: Role):
            return "success"
        
        result = system_function(Role.ADMIN)
        assert result == "success"


class TestRequireRoleDecorator:
    """Test suite for require_role decorator"""

    def test_decorator_allows_exact_role(self):
        """Test decorator allows exact role match"""
        @require_role(Role.RESEARCHER)
        def researcher_function(user_role: Role):
            return "success"
        
        result = researcher_function(Role.RESEARCHER)
        assert result == "success"

    def test_decorator_denies_wrong_role(self):
        """Test decorator denies wrong role"""
        @require_role(Role.ADMIN)
        def admin_function(user_role: Role):
            return "success"
        
        with pytest.raises(HTTPException) as exc_info:
            admin_function(Role.VIEWER)
        
        assert exc_info.value.status_code == 403
        assert "requires role" in exc_info.value.detail.lower()

    def test_decorator_allows_admin_role(self):
        """Test decorator allows admin role"""
        @require_role(Role.ADMIN)
        def admin_only_function(user_role: Role):
            return "admin success"
        
        result = admin_only_function(Role.ADMIN)
        assert result == "admin success"


class TestPermissionHierarchy:
    """Test suite for permission hierarchy and edge cases"""

    def test_all_roles_have_permissions(self):
        """Test that all roles have at least one permission"""
        for role in Role:
            perms = ROLE_PERMISSIONS[role]
            assert len(perms) > 0, f"Role {role} has no permissions"

    def test_viewer_is_most_restrictive(self):
        """Test that VIEWER has the least permissions (excluding API_CONSUMER)"""
        viewer_perms = ROLE_PERMISSIONS[Role.VIEWER]
        researcher_perms = ROLE_PERMISSIONS[Role.RESEARCHER]
        admin_perms = ROLE_PERMISSIONS[Role.ADMIN]
        
        assert len(viewer_perms) < len(researcher_perms)
        assert len(viewer_perms) < len(admin_perms)

    def test_admin_has_most_permissions(self):
        """Test that ADMIN has the most permissions"""
        admin_count = len(ROLE_PERMISSIONS[Role.ADMIN])
        
        for role in Role:
            if role != Role.ADMIN:
                role_count = len(ROLE_PERMISSIONS[role])
                assert admin_count >= role_count

    def test_no_duplicate_permissions_in_role(self):
        """Test that roles don't have duplicate permissions"""
        for role in Role:
            perms = ROLE_PERMISSIONS[role]
            assert len(perms) == len(set(perms))


class TestSecurityScenarios:
    """Test suite for security-specific scenarios"""

    def test_permission_check_with_none_role(self):
        """Test permission check handles None role gracefully"""
        # This would normally be caught by type checking, but test anyway
        with pytest.raises((TypeError, AttributeError)):
            has_permission(None, Permission.READ_HYPOTHESIS)  # type: ignore

    def test_multiple_permission_checks(self):
        """Test checking multiple permissions"""
        required_permissions = [
            Permission.READ_HYPOTHESIS,
            Permission.CREATE_HYPOTHESIS,
            Permission.EXECUTE_EXPERIMENT
        ]
        
        # Researcher should have all three
        for perm in required_permissions:
            assert has_permission(Role.RESEARCHER, perm) is True
        
        # Viewer should not have any write permissions
        write_perms = [Permission.CREATE_HYPOTHESIS, Permission.EXECUTE_EXPERIMENT]
        for perm in write_perms:
            assert has_permission(Role.VIEWER, perm) is False

    def test_read_vs_write_permissions(self):
        """Test separation of read and write permissions"""
        # Define read and write permission pairs
        read_write_pairs = [
            (Permission.READ_HYPOTHESIS, Permission.CREATE_HYPOTHESIS),
            (Permission.READ_EXPERIMENT, Permission.EXECUTE_EXPERIMENT),
            (Permission.READ_MODELS, Permission.MANAGE_MODELS),
            (Permission.READ_DATA, Permission.MANAGE_DATA),
        ]
        
        # Viewer should have all read permissions but no write permissions
        for read_perm, write_perm in read_write_pairs:
            assert has_permission(Role.VIEWER, read_perm) is True
            assert has_permission(Role.VIEWER, write_perm) is False


@pytest.mark.parametrize("role,expected_permission_count", [
    (Role.ADMIN, 13),  # All permissions
    (Role.RESEARCHER, 9),
    (Role.VIEWER, 5),
    (Role.API_CONSUMER, 4),
])
def test_role_permission_counts(role, expected_permission_count):
    """Test that roles have expected number of permissions"""
    actual_count = len(ROLE_PERMISSIONS[role])
    assert actual_count == expected_permission_count, \
        f"Role {role} expected {expected_permission_count} permissions, got {actual_count}"
