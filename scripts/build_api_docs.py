import os
import httpx
import yaml
from pathlib import Path

API_URL = os.getenv("FASTAPI_DOCS_URL", "http://localhost:8000/openapi.json")
MCP_URL = os.getenv(
    "MCP_DOCS_URL", "http://localhost:8000/openapi.json"
)  # could be separate

DOCS_OUTPUT = Path("docs/API_AUTO.md")


async def fetch_docs(url):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


def write_markdown(spec: dict, filename: Path):
    with open(filename, "w") as f:
        f.write(f"# 📚 Auto-Generated API Documentation ({filename})\n\n")
        for path, pathinfo in spec.get("paths", {}).items():
            f.write(f"## {path}\n\n")
            for method, methodinfo in pathinfo.items():
                f.write(f"### `{method.upper()}` {path}\n")
                desc = methodinfo.get("description") or methodinfo.get("summary") or ""
                f.write(f"{desc}\n\n")
                if "parameters" in methodinfo:
                    f.write("#### Parameters:\n")
                    for param in methodinfo["parameters"]:
                        f.write(
                            f"- `{param['name']}`: {param.get('description', '')}\n"
                        )
                if "responses" in methodinfo:
                    f.write("#### Responses:\n")
                    for code, resp in methodinfo["responses"].items():
                        f.write(f"- {code}: {resp.get('description', '')}\n")
                f.write("\n")


if __name__ == "__main__":
    import asyncio

    spec = asyncio.run(fetch_docs(API_URL))
    write_markdown(spec, DOCS_OUTPUT)
    print(f"API documentation written to {DOCS_OUTPUT}")
