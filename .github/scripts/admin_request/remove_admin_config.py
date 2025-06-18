import os
import re
from pathlib import Path

def remove_role_from_loadroles(yaml_path: Path, course_id: str):
    role_key = f"course-staff-{course_id}"

    with yaml_path.open("r") as f:
        lines = f.readlines()

    jupyterhub_indent = None
    hub_indent = None
    loadroles_indent = None

    loadroles_start = None
    loadroles_end = None

    # Find loadRoles and its indentation
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if stripped.startswith("jupyterhub:") and (jupyterhub_indent is None or indent < jupyterhub_indent):
            jupyterhub_indent = indent
            hub_indent = None
            loadroles_indent = None
            continue

        if jupyterhub_indent is not None and indent > jupyterhub_indent:
            if stripped.startswith("hub:") and (hub_indent is None or indent < hub_indent):
                hub_indent = indent
                loadroles_indent = None
                continue

            if hub_indent is not None and indent > hub_indent:
                if stripped.startswith("loadRoles:") and (loadroles_indent is None or indent < loadroles_indent):
                    loadroles_indent = indent
                    loadroles_start = i
                    continue

    if loadroles_start is None:
        print("No loadRoles section found. Nothing removed.")
        return

    # Find loadRoles block end: first line with indent == loadroles_indent after loadroles_start, or EOF
    for j in range(loadroles_start + 1, len(lines)):
        line = lines[j]
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if indent == loadroles_indent and stripped:
            loadroles_end = j
            break
    else:
        loadroles_end = len(lines)

    # Role keys are indented 2 spaces more than loadRoles
    role_indent = loadroles_indent + 2

    remove_start = None
    remove_end = None

    i = loadroles_start + 1
    while i < loadroles_end:
        line = lines[i]
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if indent == role_indent and stripped.startswith(role_key + ":"):
            remove_start = i
            # Find end of this role block: next line with indent <= role_indent or EOF
            remove_end = i + 1
            while remove_end < loadroles_end:
                next_line = lines[remove_end]
                next_stripped = next_line.lstrip()
                next_indent = len(next_line) - len(next_stripped)

                if next_indent <= role_indent and next_stripped:
                    break
                remove_end += 1
            break
        i += 1

    if remove_start is None:
        print(f"Role '{role_key}' not found under loadRoles. Nothing removed.")
        return

    # Delete the role block lines
    del lines[remove_start:remove_end]

    # Write back
    with yaml_path.open("w") as f:
        f.writelines(lines)

    print(f"Removed role '{role_key}' from loadRoles.")


def main():
    # Get environment variables
    hub_name = os.getenv("hub_name")
    course_id = os.getenv("course_id")

    if not hub_name or not course_id:
        raise ValueError("Missing required environment variables: hub_name and course_id")

    # Path to the YAML config
    yaml_path = Path(f"deployments/{hub_name}/config/common.yaml")

    if not yaml_path.exists():
        raise FileNotFoundError(f"Config file not found: {yaml_path}")
    
    for c_id in re.split(r"[,\s:;]+", course_id):
        if c_id:  # skip empty strings
            remove_role_from_loadroles(yaml_path, c_id)

if __name__ == "__main__":
    main()