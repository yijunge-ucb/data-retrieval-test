import os
from pathlib import Path


def insert_role_at_end_of_loadroles(yaml_path: Path, course_id: str):
    role_key = f"course-staff-{course_id}"

    with yaml_path.open("r") as f:
        lines = f.readlines()

    jupyterhub_indent = None
    hub_indent = None
    loadroles_indent = None

    loadroles_start = None
    insert_pos = None

    # Find loadRoles and its indent
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
        raise ValueError("Could not find the jupyterhub -> hub -> loadRoles section.")

    # Find the first line after loadRoles where indentation == loadroles_indent (sibling key)
    for j in range(loadroles_start + 1, len(lines)):
        line = lines[j]
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if indent == loadroles_indent and stripped:
            insert_pos = j
            break

    # If not found, insert at EOF
    if insert_pos is None:
        insert_pos = len(lines)

    # Check if role already exists inside loadRoles block (between loadroles_start+1 and insert_pos)
    for k in range(loadroles_start + 1, insert_pos):
        if lines[k].lstrip().startswith(role_key + ":"):
            print(f"Role '{role_key}' already exists. Skipping insertion.")
            return

    # Prepare role block lines with correct indentation
    entry_indent = loadroles_indent + 2
    subentry_indent = entry_indent + 2

    role_block = [
        " " * entry_indent + f"{role_key}:\n",
        " " * subentry_indent + "description: Enable course staff to view and access servers.\n",
        " " * subentry_indent + "scopes:\n",
        " " * (subentry_indent + 2) + "- admin-ui\n",
        " " * (subentry_indent + 2) + f"- list:users!group=course::{course_id}\n",
        " " * (subentry_indent + 2) + f"- admin:servers!group=course::{course_id}\n",
        " " * (subentry_indent + 2) + f"- access:servers!group=course::{course_id}\n",
        " " * subentry_indent + "groups:\n",
        " " * (subentry_indent + 2) + f"- course::{course_id}::group::Admins\n",
    ]

    # Insert the role block before the found line
    lines = lines[:insert_pos] + role_block + lines[insert_pos:]

    with yaml_path.open("w") as f:
        f.writelines(lines)

    print(f"Inserted role '{role_key}' before line {insert_pos}, preserving indentation.")




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
    
    insert_role_at_end_of_loadroles(yaml_path, course_id)


if __name__ == "__main__":
    main()