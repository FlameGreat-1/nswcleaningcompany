from rest_framework import permissions
from django.core.exceptions import PermissionDenied


class IsQuoteOwnerOrStaff(permissions.BasePermission):
    """Allow access to quote owners or staff members"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        if hasattr(obj, "client"):
            return obj.client == request.user

        if hasattr(obj, "quote"):
            return obj.quote.client == request.user

        return False


class IsStaffUser(permissions.BasePermission):
    """Allow access only to staff members"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class CanEditQuote(permissions.BasePermission):
    """Allow editing quotes for owners (draft/submitted) or staff"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        if hasattr(obj, "client"):
            quote = obj
        elif hasattr(obj, "quote"):
            quote = obj.quote
        else:
            return False

        if quote.client != request.user:
            return False

        return quote.status in ["draft", "submitted"]


class CanApproveQuote(permissions.BasePermission):
    """Allow quote approval for staff with permission"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if not request.user.is_staff:
            return False

        if hasattr(obj, "client"):
            quote = obj
        elif hasattr(obj, "quote"):
            quote = obj.quote
        else:
            return False

        return quote.status in ["submitted", "under_review"]


def check_quote_permission(user, quote, action):
    """Simple permission checker for quotes"""
    if not user.is_authenticated:
        return False

    # Staff can do everything
    if user.is_staff:
        return True

    # Quote owner permissions
    if quote.client == user:
        if action == "view":
            return True
        elif action == "edit":
            return quote.status in ["draft", "submitted"]
        elif action == "delete":
            return quote.status == "draft"
        elif action == "submit":
            return quote.status == "draft"

    return False


def check_attachment_permission(user, attachment, action):
    """Simple permission checker for attachments"""
    if not user.is_authenticated:
        return False

    # Staff can do everything
    if user.is_staff:
        return True

    # Quote owner or uploader permissions
    if attachment.quote.client == user or attachment.uploaded_by == user:
        if action in ["view", "download"]:
            return True
        elif action == "upload":
            return attachment.quote.status in ["draft", "submitted", "under_review"]
        elif action == "delete":
            return attachment.uploaded_by == user and attachment.quote.status in [
                "draft",
                "submitted",
            ]

    return False
