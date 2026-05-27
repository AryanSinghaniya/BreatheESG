import logging


logger = logging.getLogger("ingestion.request")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.info("%s %s", request.method, request.path)
        response = self.get_response(request)
        logger.info("%s %s -> %s", request.method, request.path, response.status_code)
        return response
