from pathlib import Path


PROJECT_GITIGNORE_FILES = (
    "pawn.lock",
    "log.txt",
    "bans.json",
    ".spawn/",
)


def ensure_project_gitignore(project_path: str) -> None:
    project_dir = Path(project_path)
    gitignore_path = project_dir / ".gitignore"

    if not gitignore_path.is_file():
        return

    try:
        text = gitignore_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
    except OSError:
        return

    lines = {
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    missing = [
        filename
        for filename in PROJECT_GITIGNORE_FILES
        if filename not in lines
    ]

    if not missing:
        return

    try:
        with gitignore_path.open(
            "a",
            encoding="utf-8",
            newline="",
        ) as file:
            if text and not text.endswith(("\n", "\r")):
                file.write("\n")

            file.write("\n# Spawn / server files\n")

            for filename in missing:
                file.write(f"{filename}\n")

    except OSError:
        pass
