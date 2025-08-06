from rest_framework import permissions
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

User = get_user_model()


class IsServiceManager(permissions.BasePermission):
    message = "You must be a service manager to perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.user_type == "admin")
        )


class CanViewServices(permissions.BasePermission):
    message = "You do not have permission to view services."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_active


class CanManageServices(permissions.BasePermission):
    message = "You do not have permission to manage services."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.user_type in ["admin", "staff"])
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff or request.user.user_type in ["admin", "staff"]


class CanAccessNDISServices(permissions.BasePermission):
    message = "You do not have permission to access NDIS services."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff or request.user.user_type in ["admin", "staff"]:
            return True

        return request.user.user_type == "client" and request.user.client_type == "ndis"

    def has_object_permission(self, request, view, obj):
        if not obj.is_ndis_eligible:
            return True

        return self.has_permission(request, view)


class CanViewServicePricing(permissions.BasePermission):
    message = "You do not have permission to view service pricing."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.user_type in ["admin", "staff"]:
            return True

        if obj.service.is_ndis_eligible:
            return (
                request.user.user_type == "client"
                and request.user.client_type == "ndis"
            )

        return request.user.user_type == "client"


class CanManageServicePricing(permissions.BasePermission):
    message = "You do not have permission to manage service pricing."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.user_type == "admin")
        )


class CanViewServiceAreas(permissions.BasePermission):
    message = "You do not have permission to view service areas."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_active


class CanManageServiceAreas(permissions.BasePermission):
    message = "You do not have permission to manage service areas."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.user_type in ["admin", "staff"])
        )


class CanAccessServiceAvailability(permissions.BasePermission):
    message = "You do not have permission to access service availability."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.user_type in ["admin", "staff"]:
            return True

        if obj.service.is_ndis_eligible:
            return (
                request.user.user_type == "client"
                and request.user.client_type == "ndis"
            )

        return request.user.user_type == "client"


class CanManageServiceAvailability(permissions.BasePermission):
    message = "You do not have permission to manage service availability."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.user_type in ["admin", "staff"])
        )


class CanViewNDISServiceCodes(permissions.BasePermission):
    message = "You do not have permission to view NDIS service codes."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff or request.user.user_type in ["admin", "staff"]:
            return True

        return request.user.user_type == "client" and request.user.client_type == "ndis"


class CanManageNDISServiceCodes(permissions.BasePermission):
    message = "You do not have permission to manage NDIS service codes."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.user_type == "admin")
        )


class CanViewServiceCategories(permissions.BasePermission):
    message = "You do not have permission to view service categories."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_active


class CanManageServiceCategories(permissions.BasePermission):
    message = "You do not have permission to manage service categories."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.user_type in ["admin", "staff"])
        )


class CanAccessServiceAddOns(permissions.BasePermission):
    message = "You do not have permission to access service add-ons."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.user_type in ["admin", "staff"]:
            return True

        for service in obj.services.all():
            if service.is_ndis_eligible and not (
                request.user.user_type == "client"
                and request.user.client_type == "ndis"
            ):
                return False

        return request.user.user_type == "client"


class CanManageServiceAddOns(permissions.BasePermission):
    message = "You do not have permission to manage service add-ons."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.user_type in ["admin", "staff"])
        )


class IsServiceOwnerOrStaff(permissions.BasePermission):
    message = "You can only access your own service data or be staff."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.user_type in ["admin", "staff"]:
            return True

        if hasattr(obj, "user"):
            return obj.user == request.user

        return False


class CanBulkManageServices(permissions.BasePermission):
    message = "You do not have permission to perform bulk service operations."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.user_type == "admin")
        )


class CanAccessServiceReports(permissions.BasePermission):
    message = "You do not have permission to access service reports."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.user_type in ["admin", "staff"])
        )


class CanExportServiceData(permissions.BasePermission):
    message = "You do not have permission to export service data."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.user_type == "admin")
        )


class NDISCompliancePermission(permissions.BasePermission):
    message = "NDIS compliance requirements not met."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff or request.user.user_type in ["admin", "staff"]:
            return True

        if request.user.user_type == "client" and request.user.client_type == "ndis":
            if not hasattr(request.user, "client_profile"):
                return False

            profile = request.user.client_profile
            return bool(
                profile.ndis_number
                and profile.emergency_contact_name
                and profile.emergency_contact_phone
            )

        return request.user.user_type == "client"


class ServiceLocationPermission(permissions.BasePermission):
    message = "Service not available in your location."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.user_type in ["admin", "staff"]:
            return True

        if not hasattr(request.user, "addresses"):
            return False

        user_addresses = request.user.addresses.filter(is_primary=True)
        if not user_addresses.exists():
            user_addresses = request.user.addresses.all()

        for address in user_addresses:
            if obj.is_available_in_area(address.postcode):
                return True

        return False


class ServiceTimePermission(permissions.BasePermission):
    message = "Service not available at requested time."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.user_type in ["admin", "staff"]:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        return True


class ServiceQuotePermission(permissions.BasePermission):
    message = "You do not have permission to request quotes for this service."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type == "client"
            and request.user.is_active
        )

    def has_object_permission(self, request, view, obj):
        if obj.is_ndis_eligible:
            return (
                request.user.user_type == "client"
                and request.user.client_type == "ndis"
            )

        return request.user.user_type == "client"


class ServiceBookingPermission(permissions.BasePermission):
    message = "You do not have permission to book this service."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type == "client"
            and request.user.is_active
            and request.user.is_verified
        )

    def has_object_permission(self, request, view, obj):
        if obj.requires_quote:
            return False

        if obj.is_ndis_eligible:
            return (
                request.user.user_type == "client"
                and request.user.client_type == "ndis"
                and hasattr(request.user, "client_profile")
                and request.user.client_profile.ndis_number
            )

        return request.user.user_type == "client"


