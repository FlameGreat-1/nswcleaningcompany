from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_user or request.user.is_staff:
            return True

        if hasattr(obj, "client"):
            return obj.client == request.user

        return False


class IsClientOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_client

    def has_object_permission(self, request, view, obj):
        return obj.client == request.user


class IsAdminOrStaff(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_admin_user or request.user.is_staff)
        )


class InvoiceViewPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if view.action in ["list", "retrieve"]:
            return True

        if view.action in ["download_pdf", "resend_email"]:
            return True

        return request.user.is_admin_user or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_user or request.user.is_staff:
            return True

        if request.user.is_client and obj.client == request.user:
            return True

        return False


class NDISInvoicePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not obj.is_ndis_invoice:
            return False

        if request.user.is_admin_user or request.user.is_staff:
            return True

        return obj.client == request.user and request.user.is_ndis_client
