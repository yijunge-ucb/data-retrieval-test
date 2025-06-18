import os
import re
from pathlib import Path


def remove_group_profile(yaml_path: Path, course_id: str):
    with yaml_path.open("r") as f:
        lines = f.readlines()

    course_key = f"course::{course_id}:"

    jupyterhub_indent = None
    jupyterhub_start = None
    jupyterhub_end = None
    custom_start = None
    group_profiles_start = None
    group_profiles_end = None

    # Step 1: Locate jupyterhub:
    for i, line in enumerate(lines):
        if line.lstrip().startswith("jupyterhub:"):
            jupyterhub_indent = len(line) - len(line.lstrip())
            jupyterhub_start = i
            break

    if jupyterhub_start is None:
        print("No 'jupyterhub:' block found.")
        return

    for i in range(jupyterhub_start + 1, len(lines)):
        indent = len(lines[i]) - len(lines[i].lstrip())
        if lines[i].strip() and indent <= jupyterhub_indent:
            jupyterhub_end = i
            break
    else:
        jupyterhub_end = len(lines)

    # Step 2: Find 'custom:' under jupyterhub:
    custom_indent = jupyterhub_indent + 2
    for i in range(jupyterhub_start + 1, jupyterhub_end):
        if lines[i].lstrip().startswith("custom:"):
            custom_start = i
            break

    if custom_start is None:
        print("No 'custom:' block found under 'jupyterhub:'")
        return

    # Step 3: Find group_profiles:
    group_profiles_indent = custom_indent + 2
    for i in range(custom_start + 1, jupyterhub_end):
        if lines[i].lstrip().startswith("group_profiles:"):
            group_profiles_start = i
            break

    if group_profiles_start is None:
        print("No 'group_profiles:' block found under 'custom:'")
        return

    for i in range(group_profiles_start + 1, len(lines)):
        indent = len(lines[i]) - len(lines[i].lstrip())
        if lines[i].strip() and indent <= group_profiles_indent:
            group_profiles_end = i
            break
    else:
        group_profiles_end = len(lines)

    # Step 4: Find course block
    group_indent = group_profiles_indent + 2
    found_course_start = None
    found_course_end = None

    for i in range(group_profiles_start + 1, group_profiles_end):
        if lines[i].lstrip().startswith(course_key):
            found_course_start = i
            j = i + 1
            while j < group_profiles_end:
                if lines[j].strip() and (len(lines[j]) - len(lines[j].lstrip())) <= group_indent:
                    break
                j += 1
            found_course_end = j
            break

    if found_course_start is None:
        print(f"No block found for course::{course_id}")
        return

    # Step 5: Remove the block
    lines = lines[:found_course_start] + lines[found_course_end:]
    with yaml_path.open("w") as f:
        f.writelines(lines)

    print(f"Removed group profile block for course::{course_id}")


def main():
    # Get environment variables
    hub_name = os.getenv("hub_name")
    course_id = os.getenv("course_id")

    if not hub_name or not course_id:
        raise ValueError("Missing required environment variables: hub_name, course_id")

    # Path to the YAML config
    yaml_path = Path(f"../../../deployments/{hub_name}/config/common.yaml")

    if not yaml_path.exists():
        raise FileNotFoundError(f"Config file not found: {yaml_path}")
    
    for c_id in re.split(r"[,\s:;]+", course_id):
        if c_id:  # skip empty strings
            remove_group_profile(yaml_path, c_id)


if __name__ == "__main__":
    main()



