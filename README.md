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
            logger.info(f"🔍 MIDDLEWARE - User: {request.user}")
            logger.info(f"🔍 MIDDLEWARE - User ID: {getattr(request.user, 'id', None)}")
            logger.info(
                f"🔍 MIDDLEWARE - Is authenticated: {request.user.is_authenticated}"
            )
            logger.info(f"🔍 MIDDLEWARE - Path: {request.path}")
            logger.info(f"🔍 MIDDLEWARE - View: {view_func}")

            if quote_id and len(str(quote_id)) > 10:
                from quotes.models import Quote

                try:
                    quote = Quote.objects.get(pk=quote_id)
                    logger.info(
                        f"🔍 MIDDLEWARE - Quote exists, client: {quote.client.id}"
                    )

                    if request.user.is_authenticated:
                        user_matches = quote.client.id == request.user.id
                        logger.info(
                            f"🔍 MIDDLEWARE - User matches client: {user_matches}"
                        )
                        logger.info(
                            f"🔍 MIDDLEWARE - quote.client.id: {quote.client.id}, request.user.id: {request.user.id}"
                        )
                    else:
                        logger.info(f"🔍 MIDDLEWARE - User is not authenticated")

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

        try:
            quote = Quote.objects.get(pk=quote_id)

            if not request.user.is_authenticated:
                logger.error(
                    f"🔍 MIDDLEWARE - User not authenticated for quote {quote_id}"
                )
                return JsonResponse({"detail": "Authentication required."}, status=401)

            if not request.user.is_staff and quote.client.id != request.user.id:
                logger.error(
                    f"🔍 MIDDLEWARE - Access denied: quote belongs to client {quote.client.id}, user is {request.user.id}"
                )
                return JsonResponse({"detail": "Not found."}, status=404)

            logger.info(f"🔍 MIDDLEWARE - Access granted for quote {quote_id}")
            return None

        except Quote.DoesNotExist:
            logger.error(f"🔍 MIDDLEWARE - Quote {quote_id} not found")
            return JsonResponse({"detail": "Quote not found."}, status=404)

        except Exception as e:
            logger.error(f"🔍 MIDDLEWARE - Error accessing quote {quote_id}: {str(e)}")
            return JsonResponse({"detail": "Server error."}, status=500)


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
