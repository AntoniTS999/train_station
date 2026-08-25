import time

def time_measure_middleware(get_response):
    """Middleware for measuring time of proceeding request"""

    def middleware(request):
        start = time.time()
        response = get_response(request)
        end = time.time()
        print(f"Took {end - start}")

        return response

    return middleware