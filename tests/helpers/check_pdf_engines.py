"""Quick diagnostic to check PDF engine availability."""

import platform
import subprocess

engines = ["pdflatex", "xelatex", "lualatex", "wkhtmltopdf"]

print("Checking PDF engines...\n")

for engine in engines:
    try:
        cmd = ["where", engine] if platform.system() == "Windows" else ["which", engine]
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False, timeout=5
        )
        if result.returncode == 0:
            print(f"✓ {engine}: FOUND")
            print(f"  Path: {result.stdout.strip()}\n")
        else:
            print(f"✗ {engine}: NOT FOUND\n")
    except Exception as e:
        print(f"✗ {engine}: ERROR - {e}\n")

print("\nMiKTeX bin directory should contain pdflatex.exe, xelatex.exe, lualatex.exe")
print("Common MiKTeX location: C:\\Program Files\\MiKTeX\\miktex\\bin\\x64\\")
