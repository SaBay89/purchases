import subprocess
import json
import tempfile
import os
import sys
import shutil
from pathlib import Path

def analyze_images_mcp(
    image_paths: list[str],
    prompt: str = "Analysiere dieses Bild und gib das Ergebnis als JSON zurück.",
    api_key: str = None
) -> list[dict]:
    """
    Führt den MiniMax MCP Server in einem echten Subprozess aus.
    Umgeht den Jupyter-fileno-Bug auf Windows & Linux gleichermaßen.
    """
    if api_key is None:
        api_key = LLM_API_KEY
    UVX_PATH = shutil.which("uvx")

    # Pfade für Windows normalisieren (\ statt /)
    normalized_paths = [os.path.normpath(p) for p in image_paths]
    
    # Alles JSON-sicher serialisieren
    imgs = json.dumps(normalized_paths)
    prmpt = json.dumps(prompt)
    key = json.dumps(api_key)
    uvx = json.dumps(UVX_PATH)  # Absoluter Pfad zu uvx

    # --- Dynamisches Skript (wird temporär erzeugt) ---
    script = f'''import asyncio
import os
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command={uvx},
        args=["minimax-coding-plan-mcp", "-y"],
        env={{
            "MINIMAX_API_KEY": {key},
            "MINIMAX_API_HOST": "https://api.minimax.io",
            "PATH": os.environ.get("PATH", ""),
            "USERPROFILE": os.environ.get("USERPROFILE", ""),
            "HOME": os.environ.get("USERPROFILE", "")  # Fallback für manche Tools
        }}
    )

    image_paths = {imgs}
    prompt = {prmpt}
    results = []

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    results.append({{"path": img_path, "text": None, "error": "Datei nicht gefunden"}})
                    continue
                try:
                    result = await session.call_tool(
                        "understand_image",
                        arguments={{"prompt": prompt, "image_source": img_path}}
                    )
                    text = "".join(c.text for c in result.content if c.type == "text")
                    results.append({{"path": img_path, "text": text, "error": None}})
                except Exception as e:
                    results.append({{"path": img_path, "text": None, "error": str(e)}})

    print("___MCP_RESULTS_START___")
    print(json.dumps(results, ensure_ascii=False))
    print("___MCP_RESULTS_END___")

if __name__ == "__main__":
    asyncio.run(main())
'''

    # Temporäre Datei erzeugen (Windows braucht delete=False)
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8")
    try:
        tmp.write(script)
        tmp.close()

        # WICHTIG: sys.executable = der aktuelle Python-Interpreter (z.B. C:\Users\...\python.exe)
        proc = subprocess.run(
            [sys.executable, tmp.name],
            capture_output=True,
            text=True,
            env=os.environ.copy()
        )

        if proc.returncode != 0:
            print("STDOUT:", proc.stdout)
            print("STDERR:", proc.stderr)
            raise RuntimeError(f"MCP-Prozess fehlgeschlagen (Exit Code {proc.returncode})")

        # Ergebnis parsen
        out = proc.stdout
        start = out.find("___MCP_RESULTS_START___")
        end = out.find("___MCP_RESULTS_END___")
        
        if start == -1 or end == -1:
            print("Raw Output:\n", out)
            raise RuntimeError("Konnte Ergebnis-Marker nicht finden.")

        json_str = out[start + len("___MCP_RESULTS_START___"):end].strip()
        return json.loads(json_str)

    finally:
        # Auf Windows müssen wir explizit aufräumen
        try:
            os.unlink(tmp.name)
        except PermissionError:
            pass  # Windows manchmal etwas zickig mit Temp-Dateien