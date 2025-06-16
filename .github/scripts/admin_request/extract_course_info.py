import os
import re

issue_id = os.getenv("ISSUE_NUMBER")
body = os.getenv("ISSUE_BODY")


# Function to extract a field value by its ID
def extract_field_value(body: str, field_id: str) -> str:
    pattern = rf"<!-- id: {field_id} -->\s*(.*?)\s*(?=\n###|\Z)"
    match = re.search(pattern, body, re.DOTALL)
    return match.group(1).strip() if match else ""

print(f"Extracting course info from issue #{issue_id}")
print(f"Issue body:\n{body}\n")
# Extract values
url = extract_field_value(body, "hub_url")
course_id = extract_field_value(body, "course_id")
end_date = extract_field_value(body, "end_date")

print(f"Extracted values:\n"
      f"  Hub URL: {url}\n"
      f"  Course ID: {course_id}\n"
      f"  End Date: {end_date}\n")
# Parse hub_name from URL
hub_name = url.split(".")[0] 


branch = f"issue_{issue_id}"


outputs = {
    "new_branch": branch,
    "hub_name": hub_name,
    "course_id": course_id,
}

output_path = os.environ.get("GITHUB_OUTPUT")
if output_path:
    with open(output_path, "a") as f:
        for key, value in outputs.items():
            f.write(f"{key}={value}\n")


