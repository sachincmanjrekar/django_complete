import time

from django.conf import settings
from django.http import HttpResponse


class TimingMiddleware:
    # Runs around EVERY request: measures how long the rest of the chain (other middleware + view) takes

    def __init__(self, get_response):
        # Called ONCE, when the server starts. get_response = the next layer (eventually the view)
        self.get_response = get_response

    def __call__(self, request):
        # Called for EVERY request
        start = time.perf_counter()                       # Before the view: the request on its way in

        response = self.get_response(request)             # Hand over to the next layer -> ... -> view

        duration_ms = (time.perf_counter() - start) * 1000  # After the view: the response on its way out
        response["X-Response-Time"] = f"{duration_ms:.1f}ms"  # Add a header to every response
        print(f"[timing] {request.method} {request.path} -> {response.status_code} in {duration_ms:.1f}ms")
        return response


class MaintenanceModeMiddleware:
    # Short-circuit: when MAINTENANCE_MODE is on, answer 503 WITHOUT calling the view (admin stays reachable)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, "MAINTENANCE_MODE", False) and not request.path.startswith("/admin"):
            return HttpResponse("Site under maintenance, back soon.", status=503)  # Never calls get_response -> view never runs

        return self.get_response(request)
