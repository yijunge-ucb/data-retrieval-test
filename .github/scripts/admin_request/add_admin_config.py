import os
from pathlib import Path
from ruamel.yaml import YAML

# Get environment variables
hub_name = os.getenv("hub_name")
course_id = os.getenv("course_id")

if not hub_name or not course_id:
    raise ValueError("Missing required environment variables: hub_name and course_id")

# Path to the YAML config
yaml_path = Path(f"deployments/{hub_name}/config/common.yaml")

if not yaml_path.exists():
    raise FileNotFoundError(f"Config file not found: {yaml_path}")

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)

with yaml_path.open("r") as f:
    config = yaml.load(f)


jupyterhub = config.setdefault("jupyterhub", {})
hub = jupyterhub.setdefault("hub", {})
load_roles = hub.setdefault("loadRoles", {})

# Insert new role
role_key = f"course-staff-{course_id}"
load_roles[role_key] = {
    "description": "Enable course staff to view and access servers.",
    "scopes": [
        "admin-ui",
        f"list:users!group=course::{course_id}",
        f"admin:servers!group=course::{course_id}",
        f"access:servers!group=course::{course_id}"
    ],
    "groups": [
        f"course::{course_id}::group::Admins"
    ]
}


with yaml_path.open("w") as f:
    yaml.dump(config, f)

print(f"Added role '{role_key}' to {yaml_path}")
