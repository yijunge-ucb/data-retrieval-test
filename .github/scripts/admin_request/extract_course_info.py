import os
import re
import sys

def read_issue_body(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
def extract_issue_fields(issue_body: str):
    lines = issue_body.splitlines()
    data = {}
    current_field = None

    for line in lines:
        line = line.strip()

        if line.startswith("### "):
            # Found a new field header
            current_field = line[4:].strip()
            data[current_field] = None  # Reset for this field
            continue

        # Skip until we get a non-empty value for current field
        if current_field and data[current_field] is None and line:
            data[current_field] = line

    hub_url = data.get("Hub URL", "").strip()
    course_id = data.get("bCourses ID", "").strip()
    end_date = data.get("End Date", "").strip()

    return {
        "hub_url": hub_url,
        "course_id": course_id,
        "end_date": end_date,
    }


def main():
    issue_id = os.getenv("ISSUE_NUMBER")
    issue_file_path = sys.argv[1]
    body = read_issue_body(issue_file_path)

    print(f"Extracting course info from issue #{issue_id}")
    print(f"Issue body:\n{body}\n")

    course_info = extract_issue_fields(body)
    url = course_info.get("hub_url", "")
    course_id = course_info.get("course_id", "")        
    end_date = course_info.get("end_date", "")
     
    hub_name = url.split(".")[0] 
    branch = f"issue_{issue_id}"

    print(f"Extracted hub name: {hub_name}, course ID: {course_id}, end date: {end_date}")

    outputs = {
        "new_branch": branch,
        "hub_name": hub_name,
        "course_id": course_id,
        "end_date": end_date,
    }

    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a") as f:
            for key, value in outputs.items():
                f.write(f"{key}={value}\n")


if __name__ == "__main__":
    main()