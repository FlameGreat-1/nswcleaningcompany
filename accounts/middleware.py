import json
import logging

logger = logging.getLogger(__name__)


class RegistrationDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.path == "/api/v1/accounts/auth/register/"
            and request.method == "POST"
        ):
            try:
                body = json.loads(request.body.decode("utf-8"))
                logger.error(f"🔍 MIDDLEWARE DEBUG - Raw request body: {body}")
                logger.error(f"🔍 MIDDLEWARE DEBUG - Keys: {list(body.keys())}")
            except:
                logger.error(
                    f"🔍 MIDDLEWARE DEBUG - Could not parse body: {request.body}"
                )

        response = self.get_response(request)
        return response
