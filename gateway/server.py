from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import httpx

app = FastAPI(title="MCP Gateway")

ROUTES = {
    "/commerce": "http://127.0.0.1:8001",
    "/fulfillment": "http://127.0.0.1:8002",
    "/payment": "http://127.0.0.1:8003",
    "/agent": "http://127.0.0.1:9001",
}

client = httpx.AsyncClient(
    timeout=None,
    follow_redirects=True,
)


def get_upstream(path: str):
    for prefix, target in ROUTES.items():
        if path.startswith(prefix):
            remaining = path[len(prefix):]

            if not remaining:
                remaining = "/"

            return target + remaining

    return None


@app.api_route(
    "/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
)
async def proxy(request: Request, path: str):

    full_path = "/" + path

    upstream_url = get_upstream(full_path)

    if upstream_url is None:
        return Response(
            content="Unknown route",
            status_code=404,
        )

    body = await request.body()

    # Preserve incoming headers.
    headers = dict(request.headers)

    # The upstream server should generate its own Host.
    headers.pop("host", None)

    try:

        upstream_request = client.build_request(
            method=request.method,
            url=upstream_url,
            headers=headers,
            content=body,
        )

        upstream_response = await client.send(
            upstream_request,
            stream=True,
        )

        # Copy upstream response headers.
        response_headers = dict(
            upstream_response.headers
        )

        # Remove headers that should be generated
        # by the downstream server.
        for header in [
            "content-length",
            "transfer-encoding",
            "connection",
            "keep-alive",
        ]:
            response_headers.pop(
                header,
                None,
            )

        # IMPORTANT:
        # Preserve MCP session ID.
        if "mcp-session-id" in upstream_response.headers:
            response_headers[
                "mcp-session-id"
            ] = upstream_response.headers[
                "mcp-session-id"
            ]

        async def stream_response():

            try:

                async for chunk in upstream_response.aiter_raw():
                    yield chunk

            finally:

                await upstream_response.aclose()

        return StreamingResponse(
            stream_response(),
            status_code=upstream_response.status_code,
            headers=response_headers,
            media_type=upstream_response.headers.get(
                "content-type"
            ),
        )

    except Exception as e:

        return Response(
            content=f"Gateway error: {str(e)}",
            status_code=502,
        )