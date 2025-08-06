from rest_framework import permissions
from rest_framework.permissions import BasePermission
from django.contrib.auth.models import AnonymousUser


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user or request.user.is_staff


class IsClientUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_client


class IsNDISClient(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_ndis_client
        )


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_admin_user
        )


class IsStaffOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_admin_user)
        )


class IsVerifiedUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and request.user.is_verified
        )


class IsActiveUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "user"):
            return obj.user == request.user
        return obj == request.user


class IsOwnerOrStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_admin_user:
            return True
        if hasattr(obj, "user"):
            return obj.user == request.user
        return obj == request.user


class CanManageUsers(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_admin_user)
        )


class CanViewUserDetails(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_admin_user)
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_admin_user:
            return True
        if request.user.is_staff:
            return True
        return obj == request.user


class CanAccessClientProfile(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_client

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_admin_user:
            return True
        return obj.user == request.user


class CanModifyAddress(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_admin_user:
            return True
        return obj.user == request.user


class IsUnauthenticated(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated


class CanResetPassword(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return not obj.is_used and obj.is_valid


class CanVerifyEmail(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return not obj.is_used and obj.is_valid


class CanAccessAdminDashboard(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.is_admin_user
                or request.user.is_superuser
            )
        )


class CanManageClientProfiles(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_admin_user)
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_user or request.user.is_superuser:
            return True
        if request.user.is_staff:
            return request.method in permissions.SAFE_METHODS
        return obj.user == request.user


class CanBulkManageUsers(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_admin_user)
        )


class CanViewUserSessions(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_admin_user)
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_user or request.user.is_superuser:
            return True
        return obj.user == request.user


class CanManageVerifications(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_admin_user)
        )


class NDISCompliancePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_ndis_client:
            return (
                hasattr(request.user, "client_profile")
                and request.user.client_profile.ndis_number
            )

        return True


class AccessibilityCompliancePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return True

        if request.user.is_client and hasattr(request.user, "client_profile"):
            profile = request.user.client_profile
            if profile.accessibility_needs != "none":
                return True

        return True


class RateLimitPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_admin_user:
                return True
        return True


class SecureEndpointPermission(BasePermission):
    def has_permission(self, request, view):
        if (
            not request.is_secure()
            and not request.META.get("HTTP_X_FORWARDED_PROTO") == "https"
        ):
            return False
        return True


class ClientDataAccessPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.user.is_admin_user:
            return True

        if request.user.is_staff:
            return request.method in permissions.SAFE_METHODS

        if hasattr(obj, "user"):
            return obj.user == request.user

        return obj == request.user


class ProfileCompletionPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_client:
            if not hasattr(request.user, "client_profile"):
                return False

            profile = request.user.client_profile
            if request.user.is_ndis_client and not profile.ndis_number:
                return False

        return True


class MultiFactorAuthPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_admin_user or request.user.is_staff:
            return getattr(request.user, "mfa_enabled", False)

        return True
