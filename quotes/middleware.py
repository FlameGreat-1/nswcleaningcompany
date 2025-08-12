import logging
from django.db import transaction
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import time

logger = logging.getLogger(__name__)


class DatabaseConsistencyMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.path.startswith("/api/v1/quotes/"):
            from django.db import connections

            for conn in connections.all():
                if hasattr(conn, "queries") and conn.queries:
                    conn.queries.clear()

        return None

    def process_response(self, request, response):
        if request.path.startswith("/api/v1/quotes/") and request.method == "POST":
            try:
                transaction.commit()
            except:
                pass

            if not settings.DEBUG:
                time.sleep(0.1)

        return response


class QuoteAccessMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        if (
            request.path.startswith("/api/v1/quotes/")
            and "pk" in view_kwargs
            and request.method == "GET"
        ):

            quote_id = view_kwargs.get("pk")
            logger.info(f"🔍 MIDDLEWARE - Processing quote access: {quote_id}")
            logger.info(f"🔍 MIDDLEWARE - User: {request.user.id}")
            logger.info(f"🔍 MIDDLEWARE - Path: {request.path}")
            logger.info(f"🔍 MIDDLEWARE - View: {view_func}")

            if quote_id and len(str(quote_id)) > 10:
                from quotes.models import Quote

                try:
                    quote = Quote.objects.get(pk=quote_id)
                    logger.info(
                        f"🔍 MIDDLEWARE - Quote exists, client: {quote.client.id}"
                    )
                    logger.info(
                        f"🔍 MIDDLEWARE - Access check: {quote.client == request.user}"
                    )
                except Quote.DoesNotExist:
                    logger.error(f"🔍 MIDDLEWARE - Quote {quote_id} does not exist!")

                return self._handle_quote_access(
                    request, quote_id, view_func, view_args, view_kwargs
                )

        return None

    def _handle_quote_access(
        self, request, quote_id, view_func, view_args, view_kwargs
    ):
        from quotes.models import Quote

        max_retries = 3
        retry_delay = 0.1

        for attempt in range(max_retries):
            try:
                quote = Quote.objects.get(pk=quote_id)

                if not request.user.is_staff and quote.client != request.user:
                    return JsonResponse({"detail": "Not found."}, status=404)

                return None

            except Quote.DoesNotExist:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Quote {quote_id} not found, retrying... (attempt {attempt + 1})"
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    logger.error(
                        f"Quote {quote_id} not found after {max_retries} attempts"
                    )
                    return JsonResponse({"detail": "Quote not found."}, status=404)

            except Exception as e:
                logger.error(f"Error accessing quote {quote_id}: {str(e)}")
                break

        return None


class TransactionDebugMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if settings.DEBUG and request.path.startswith("/api/v1/quotes/"):
            logger.info(f"🔍 Request: {request.method} {request.path}")
            logger.info(f"🔍 User: {request.user}")

        return None

    def process_response(self, request, response):
        if settings.DEBUG and request.path.startswith("/api/v1/quotes/"):
            logger.info(f"🔍 Response: {response.status_code}")

            if request.method == "POST" and response.status_code == 201:
                logger.info("✅ Quote created successfully")

                try:
                    transaction.commit()
                    logger.info("✅ Database transaction committed")
                except:
                    pass

        return response
