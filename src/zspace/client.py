import httpx


def request(method: str, url: str, **kwargs) -> httpx.Response:
    with httpx.Client(timeout=30) as client:
        return client.request(method.upper(), url, **kwargs)
