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

# Output results
print(f"::set-output name=course_id::{course_id}")
print(f"::set-output name=hub_name::{hub_name}")
print(f"::set-output name=new_branch::{branch}")

# Save to vars.env
with open("vars.env", "w") as f:
    f.write(f"COURSE_ID={course_id}\n")
    f.write(f"HUB_NAME={hub_name}\n")
    f.write(f"END_DATE={end_date}\n")
    f.write(f"NEW_BRANCH={branch}\n")
