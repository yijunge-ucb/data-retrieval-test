import os
import re

body = """${{ github.event.issue.body }}""" 

# Function to extract a field value by its ID
def extract_field_value(body: str, field_id: str) -> str:
    pattern = rf"<!-- id: {field_id} -->\s*(.*?)\s*(?=\n###|\Z)"
    match = re.search(pattern, body, re.DOTALL)
    return match.group(1).strip() if match else ""

# Extract values
url = extract_field_value(body, "hub_url")
course_id = extract_field_value(body, "course_id")
end_date = extract_field_value(body, "end_date")

# Parse hub_name from URL
hub_name = url.split(".")[0] 

# Get issue number
issue_id = os.getenv("GITHUB_EVENT_ISSUE_NUMBER", "unknown")
branch = f"issue_{issue_id}"


outputs = {
    "NEW_BRANCH": branch,
    "HUB_NAME": hub_name,
    "COURSE_ID": course_id,
}

output_path = os.environ.get("GITHUB_OUTPUT")
if output_path:
    with open(output_path, "a") as f:
        for key, value in outputs.items():
            f.write(f"{key}={value}\n")


