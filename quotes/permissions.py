from rest_framework import permissions
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from .models import Quote, QuoteItem, QuoteAttachment, QuoteRevision, QuoteTemplate


class IsQuoteOwnerOrStaff(permissions.BasePermission):

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


class IsQuoteOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "client"):
            return obj.client == request.user

        if hasattr(obj, "quote"):
            return obj.quote.client == request.user

        return False


class IsStaffUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff


class CanViewQuote(permissions.BasePermission):

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


class CanEditQuote(permissions.BasePermission):

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

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and request.user.has_perm("quotes.approve_quote")
        )

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


class CanRejectQuote(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and request.user.has_perm("quotes.reject_quote")
        )

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


class CanDeleteQuote(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.user.is_staff and request.user.has_perm("quotes.delete_quote"):
            return True

        if hasattr(obj, "client"):
            quote = obj
        elif hasattr(obj, "quote"):
            quote = obj.quote
        else:
            return False

        if quote.client == request.user:
            return quote.status == "draft"

        return False


class CanUploadAttachment(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        if hasattr(obj, "quote"):
            quote = obj.quote
        else:
            quote = obj

        if quote.client != request.user:
            return False

        return quote.status in ["draft", "submitted", "under_review"]


class CanViewAttachment(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        if obj.quote.client == request.user:
            return True

        if obj.uploaded_by == request.user:
            return True

        return False


class CanDeleteAttachment(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        if obj.uploaded_by == request.user:
            return obj.quote.status in ["draft", "submitted"]

        return False


class CanCreateQuoteRevision(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and request.user.has_perm("quotes.add_quoterevision")
        )

    def has_object_permission(self, request, view, obj):
        if not request.user.is_staff:
            return False

        if hasattr(obj, "quote"):
            quote = obj.quote
        else:
            quote = obj

        return quote.status in ["submitted", "under_review", "approved"]


class CanViewQuoteRevision(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        return obj.quote.client == request.user


class CanManageQuoteTemplate(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and request.user.has_perm("quotes.change_quotetemplate")
        )


class CanViewQuoteAnalytics(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and request.user.has_perm("quotes.view_quote_analytics")
        )


class CanExportQuotes(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and request.user.has_perm("quotes.export_quotes")
        )


class CanBulkUpdateQuotes(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and request.user.has_perm("quotes.bulk_update_quotes")
        )


class CanAssignQuote(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and request.user.has_perm("quotes.assign_quote")
        )

    def has_object_permission(self, request, view, obj):
        if not request.user.is_staff:
            return False

        if hasattr(obj, "client"):
            quote = obj
        elif hasattr(obj, "quote"):
            quote = obj.quote
        else:
            return False

        return quote.status in ["submitted", "under_review", "approved"]


class QuoteStatusPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "client"):
            quote = obj
        elif hasattr(obj, "quote"):
            quote = obj.quote
        else:
            return False

        action = getattr(view, "action", None)

        if action == "submit":
            return quote.client == request.user and quote.status == "draft"

        if action in ["approve", "reject"]:
            return request.user.is_staff and quote.status in [
                "submitted",
                "under_review",
            ]

        if action == "cancel":
            return (
                quote.client == request.user and quote.status in ["draft", "submitted"]
            ) or (
                request.user.is_staff and quote.status not in ["converted", "cancelled"]
            )

        if action == "convert":
            return (
                request.user.is_staff
                and quote.status == "approved"
                and not quote.is_expired
            )

        return False


class NDISQuotePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "client"):
            quote = obj
        elif hasattr(obj, "quote"):
            quote = obj.quote
        else:
            return False

        if not quote.is_ndis_client:
            return True

        if request.user.is_staff:
            return request.user.has_perm("quotes.handle_ndis_quotes")

        if quote.client == request.user:
            return (
                hasattr(request.user, "client_profile")
                and request.user.client_profile.client_type == "ndis"
            )

        return False


class QuoteItemPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        if obj.quote.client == request.user:
            return obj.quote.status in ["draft", "submitted"]

        return False


class QuoteCalculatorPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True


class QuoteReportPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and request.user.has_perm("quotes.view_quote_reports")
        )


class QuoteArchivePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and request.user.has_perm("quotes.archive_quotes")
        )

    def has_object_permission(self, request, view, obj):
        if not request.user.is_staff:
            return False

        if hasattr(obj, "client"):
            quote = obj
        elif hasattr(obj, "quote"):
            quote = obj.quote
        else:
            return False

        return quote.status in ["expired", "rejected", "cancelled"]


class QuoteDuplicatePermission(permissions.BasePermission):

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

        return quote.client == request.user


def check_quote_permission(user, quote, action):
    if not user.is_authenticated:
        return False

    permission_map = {
        "view": _can_view_quote,
        "edit": _can_edit_quote,
        "delete": _can_delete_quote,
        "submit": _can_submit_quote,
        "approve": _can_approve_quote,
        "reject": _can_reject_quote,
        "cancel": _can_cancel_quote,
        "convert": _can_convert_quote,
        "assign": _can_assign_quote,
        "duplicate": _can_duplicate_quote,
        "archive": _can_archive_quote,
    }

    permission_func = permission_map.get(action)
    if permission_func:
        return permission_func(user, quote)

    return False


def _can_view_quote(user, quote):
    if user.is_staff:
        return True
    return quote.client == user


def _can_edit_quote(user, quote):
    if user.is_staff:
        return True

    if quote.client == user:
        return quote.status in ["draft", "submitted"]

    return False


def _can_delete_quote(user, quote):
    if user.is_superuser:
        return True

    if user.is_staff and user.has_perm("quotes.delete_quote"):
        return True

    if quote.client == user:
        return quote.status == "draft"

    return False


def _can_submit_quote(user, quote):
    return quote.client == user and quote.status == "draft"


def _can_approve_quote(user, quote):
    return (
        user.is_staff
        and user.has_perm("quotes.approve_quote")
        and quote.status in ["submitted", "under_review"]
    )


def _can_reject_quote(user, quote):
    return (
        user.is_staff
        and user.has_perm("quotes.reject_quote")
        and quote.status in ["submitted", "under_review"]
    )


def _can_cancel_quote(user, quote):
    if quote.client == user:
        return quote.status in ["draft", "submitted"]

    if user.is_staff:
        return quote.status not in ["converted", "cancelled"]

    return False


def _can_convert_quote(user, quote):
    return (
        user.is_staff
        and user.has_perm("quotes.convert_quote")
        and quote.status == "approved"
        and not quote.is_expired
    )


def _can_assign_quote(user, quote):
    return (
        user.is_staff
        and user.has_perm("quotes.assign_quote")
        and quote.status in ["submitted", "under_review", "approved"]
    )


def _can_duplicate_quote(user, quote):
    if user.is_staff:
        return True
    return quote.client == user


def _can_archive_quote(user, quote):
    return (
        user.is_staff
        and user.has_perm("quotes.archive_quotes")
        and quote.status in ["expired", "rejected", "cancelled"]
    )


def check_attachment_permission(user, attachment, action):
    if not user.is_authenticated:
        return False

    permission_map = {
        "view": _can_view_attachment,
        "upload": _can_upload_attachment,
        "delete": _can_delete_attachment,
        "download": _can_download_attachment,
    }

    permission_func = permission_map.get(action)
    if permission_func:
        return permission_func(user, attachment)

    return False


def _can_view_attachment(user, attachment):
    if user.is_staff:
        return True

    if attachment.quote.client == user:
        return True

    if attachment.uploaded_by == user:
        return True

    return False


def _can_upload_attachment(user, quote):
    if user.is_staff:
        return True

    if quote.client == user:
        return quote.status in ["draft", "submitted", "under_review"]

    return False


def _can_delete_attachment(user, attachment):
    if user.is_staff:
        return True

    if attachment.uploaded_by == user:
        return attachment.quote.status in ["draft", "submitted"]

    return False


def _can_download_attachment(user, attachment):
    return _can_view_attachment(user, attachment)


def get_user_quote_permissions(user):
    if not user.is_authenticated:
        return []

    permissions = ["view_own_quotes"]

    if user.is_staff:
        staff_permissions = [
            "view_all_quotes",
            "edit_all_quotes",
            "approve_quotes",
            "reject_quotes",
            "assign_quotes",
            "view_quote_analytics",
            "export_quotes",
            "bulk_update_quotes",
            "manage_quote_templates",
            "handle_ndis_quotes",
            "archive_quotes",
            "view_quote_reports",
        ]
        permissions.extend(staff_permissions)

    if user.is_superuser:
        permissions.append("delete_any_quote")

    return permissions


def has_quote_feature_access(user, feature):
    feature_permissions = {
        "calculator": True,
        "submit_quote": lambda u: u.is_authenticated,
        "view_quotes": lambda u: u.is_authenticated,
        "edit_quotes": lambda u: u.is_authenticated,
        "upload_attachments": lambda u: u.is_authenticated,
        "quote_analytics": lambda u: u.is_staff,
        "quote_reports": lambda u: u.is_staff
        and u.has_perm("quotes.view_quote_reports"),
        "bulk_operations": lambda u: u.is_staff
        and u.has_perm("quotes.bulk_update_quotes"),
        "quote_templates": lambda u: u.is_staff
        and u.has_perm("quotes.change_quotetemplate"),
        "ndis_quotes": lambda u: u.is_authenticated,
        "quote_approval": lambda u: u.is_staff and u.has_perm("quotes.approve_quote"),
        "quote_assignment": lambda u: u.is_staff and u.has_perm("quotes.assign_quote"),
        "quote_export": lambda u: u.is_staff and u.has_perm("quotes.export_quotes"),
    }

    permission_check = feature_permissions.get(feature)

    if permission_check is True:
        return True
    elif callable(permission_check):
        return permission_check(user)

    return False


class QuotePermissionMixin:

    def get_quote_permissions(self, user, quote=None):
        permissions = {
            "can_view": False,
            "can_edit": False,
            "can_delete": False,
            "can_submit": False,
            "can_approve": False,
            "can_reject": False,
            "can_cancel": False,
            "can_convert": False,
            "can_assign": False,
            "can_duplicate": False,
            "can_archive": False,
            "can_upload_attachments": False,
        }

        if not user.is_authenticated or not quote:
            return permissions

        permissions.update(
            {
                "can_view": check_quote_permission(user, quote, "view"),
                "can_edit": check_quote_permission(user, quote, "edit"),
                "can_delete": check_quote_permission(user, quote, "delete"),
                "can_submit": check_quote_permission(user, quote, "submit"),
                "can_approve": check_quote_permission(user, quote, "approve"),
                "can_reject": check_quote_permission(user, quote, "reject"),
                "can_cancel": check_quote_permission(user, quote, "cancel"),
                "can_convert": check_quote_permission(user, quote, "convert"),
                "can_assign": check_quote_permission(user, quote, "assign"),
                "can_duplicate": check_quote_permission(user, quote, "duplicate"),
                "can_archive": check_quote_permission(user, quote, "archive"),
                "can_upload_attachments": _can_upload_attachment(user, quote),
            }
        )

        return permissions


def require_quote_permission(permission_name):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            quote_id = kwargs.get("quote_id") or kwargs.get("pk")
            if quote_id:
                try:
                    quote = Quote.objects.get(pk=quote_id)
                    if not check_quote_permission(request.user, quote, permission_name):
                        raise PermissionDenied(
                            f"You don't have permission to {permission_name} this quote."
                        )
                except Quote.DoesNotExist:
                    raise PermissionDenied("Quote not found.")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
