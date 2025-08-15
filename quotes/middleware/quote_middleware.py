import logging
from django.db import transaction
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import time

logger = logging.getLogger(__name__)


class QuoteDebugMiddleware(MiddlewareMixin):
    """Debug middleware that logs quote access without interfering with normal flow"""

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Only debug quote GET requests with pk
        if (
            request.path.startswith("/api/v1/quotes/")
            and "pk" in view_kwargs
            and request.method == "GET"
        ):

            quote_id = view_kwargs.get("pk")
            logger.info(f"🔍 MIDDLEWARE - Quote access debug: {quote_id}")
            logger.info(
                f"🔍 MIDDLEWARE - User: {request.user.id} ({request.user.email})"
            )
            logger.info(
                f"🔍 MIDDLEWARE - Is authenticated: {request.user.is_authenticated}"
            )
            logger.info(f"🔍 MIDDLEWARE - Is staff: {request.user.is_staff}")
            logger.info(f"🔍 MIDDLEWARE - Path: {request.path}")

            # Check if quote exists and ownership
            if quote_id:
                from quotes.models import Quote

                try:
                    quote = Quote.objects.get(pk=quote_id)
                    logger.info(f"🔍 MIDDLEWARE - Quote exists: {quote.id}")
                    logger.info(
                        f"🔍 MIDDLEWARE - Quote client: {quote.client.id} ({quote.client.email})"
                    )
                    logger.info(f"🔍 MIDDLEWARE - Quote status: {quote.status}")
                    logger.info(f"🔍 MIDDLEWARE - Quote created: {quote.created_at}")
                    logger.info(
                        f"🔍 MIDDLEWARE - Client match: {quote.client.id == request.user.id}"
                    )

                    # Log what should happen
                    if request.user.is_staff:
                        logger.info(f"🔍 MIDDLEWARE - Staff user - should have access")
                    elif quote.client.id == request.user.id:
                        logger.info(
                            f"🔍 MIDDLEWARE - User owns quote - should have access"
                        )
                    else:
                        logger.error(
                            f"🔍 MIDDLEWARE - User {request.user.id} does NOT own quote owned by {quote.client.id}"
                        )

                except Quote.DoesNotExist:
                    logger.error(
                        f"🔍 MIDDLEWARE - Quote {quote_id} does NOT exist in database!"
                    )
                except Exception as e:
                    logger.error(f"🔍 MIDDLEWARE - Error checking quote: {str(e)}")

        # Always return None to let normal processing continue
        return None

    def process_response(self, request, response):
        # Log the final response for quote requests
        if (
            request.path.startswith("/api/v1/quotes/")
            and "pk" in getattr(request.resolver_match, "kwargs", {})
            and request.method == "GET"
        ):

            quote_id = request.resolver_match.kwargs.get("pk")
            logger.info(
                f"🔍 MIDDLEWARE - Final response for {quote_id}: {response.status_code}"
            )

            if response.status_code == 404:
                logger.error(
                    f"🔍 MIDDLEWARE - 404 RESPONSE - Quote {quote_id} not found by viewset"
                )
            elif response.status_code == 200:
                logger.info(
                    f"🔍 MIDDLEWARE - 200 RESPONSE - Quote {quote_id} successfully retrieved"
                )

        return response


class DatabaseConsistencyMiddleware(MiddlewareMixin):
    """Ensures database consistency for quote operations"""

    def process_response(self, request, response):
        if request.path.startswith("/api/v1/quotes/") and request.method == "POST":
            try:
                transaction.commit()
                logger.info("✅ Database transaction committed after quote creation")
            except Exception as e:
                logger.error(f"❌ Transaction commit failed: {str(e)}")

            # Small delay to ensure database consistency
            if not settings.DEBUG:
                time.sleep(0.1)

        return response
