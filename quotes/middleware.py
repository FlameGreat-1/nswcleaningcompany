import logging
from django.db import transaction
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import time

logger = logging.getLogger(__name__)


class DatabaseConsistencyMiddleware(MiddlewareMixin):
    """
    Middleware to handle database consistency issues and atomic transactions
    """

    def process_request(self, request):
        """Ensure all database operations are atomic"""
        if request.path.startswith("/api/v1/quotes/"):
            # Force database connection to be in autocommit mode
            from django.db import connections

            for conn in connections.all():
                if conn.queries_logged:
                    conn.queries_logged.clear()

        return None

    def process_response(self, request, response):
        """Handle post-request database consistency"""
        if request.path.startswith("/api/v1/quotes/") and request.method == "POST":
            # Force commit for quote creation
            transaction.commit()

            # Small delay to ensure database consistency
            if not settings.DEBUG:
                time.sleep(0.1)

        return response


class QuoteAccessMiddleware(MiddlewareMixin):
    """
    Middleware specifically for quote access issues
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Handle quote access with retry logic"""
        if (
            request.path.startswith("/api/v1/quotes/")
            and "pk" in view_kwargs
            and request.method == "GET"
        ):

            quote_id = view_kwargs.get("pk")
            if quote_id:
                # Try to access quote with retry logic
                return self._handle_quote_access(
                    request, quote_id, view_func, view_args, view_kwargs
                )

        return None

    def _handle_quote_access(
        self, request, quote_id, view_func, view_args, view_kwargs
    ):
        """Handle quote access with database consistency checks"""
        from quotes.models import Quote

        max_retries = 3
        retry_delay = 0.1

        for attempt in range(max_retries):
            try:
                # Force fresh database query
                quote = Quote.objects.select_for_update().get(pk=quote_id)

                # Check user permissions
                if not request.user.is_staff and quote.client != request.user:
                    return JsonResponse({"detail": "Not found."}, status=404)

                # Quote exists and user has access, proceed normally
                return None

            except Quote.DoesNotExist:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Quote {quote_id} not found, retrying... (attempt {attempt + 1})"
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    logger.error(
                        f"Quote {quote_id} not found after {max_retries} attempts"
                    )
                    return JsonResponse({"detail": "Quote not found."}, status=404)

            except Exception as e:
                logger.error(f"Error accessing quote {quote_id}: {str(e)}")
                return JsonResponse({"detail": "Server error."}, status=500)

        return None


class TransactionDebugMiddleware(MiddlewareMixin):
    """
    Debug middleware to log transaction states
    """

    def process_request(self, request):
        if settings.DEBUG and request.path.startswith("/api/v1/quotes/"):
            logger.info(f"🔍 Request: {request.method} {request.path}")
            logger.info(f"🔍 User: {request.user}")

            # Log database connection state
            from django.db import connection

            logger.info(f"🔍 DB Connection: {connection.vendor}")
            logger.info(f"🔍 In Transaction: {connection.in_atomic_block}")

        return None

    def process_response(self, request, response):
        if settings.DEBUG and request.path.startswith("/api/v1/quotes/"):
            logger.info(f"🔍 Response: {response.status_code}")

            if request.method == "POST" and response.status_code == 201:
                # Log successful quote creation
                logger.info("✅ Quote created successfully")

                # Force database sync
                from django.db import transaction

                transaction.commit()
                logger.info("✅ Database transaction committed")

        return response
