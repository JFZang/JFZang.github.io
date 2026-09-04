"""Export the canonical CV DOCX to the website PDF using Microsoft Word.

The Word document in ``tools/cv/source`` is the single source of truth. This
wrapper delegates to the PowerShell exporter so the Python and PowerShell entry
points cannot produce different CV layouts or content.
"""

from pathlib import Path
import subprocess


TOOL_DIR = Path(__file__).resolve().parent
EXPORT_SCRIPT = TOOL_DIR / "export_cv_pdf.ps1"


def main() -> None:
    completed = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(EXPORT_SCRIPT),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    if completed.stdout.strip():
        print(completed.stdout.strip())


if __name__ == "__main__":
    main()
