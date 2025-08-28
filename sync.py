import os
import json
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load Notion config
NOTION_TOKEN = os.environ["ntn_J1485670679aONpoTVR7lTLph7OLFFQ4Xq1jmd8P3eP1E3"]
NOTION_DATABASE_ID = os.environ["25d0588d8917806f8730e5aead6ceda8"]

# Load Google Classroom credentials
google_creds = json.loads(os.environ["GOOGLE_CREDENTIALS"])
SCOPES = ["https://www.googleapis.com/auth/classroom.coursework.me.readonly"]
creds = service_account.Credentials.from_service_account_info(google_creds, scopes=SCOPES)

service = build("classroom", "v1", credentials=creds)

# --- Fetch assignments ---
def get_assignments():
    results = service.courses().list().execute()
    courses = results.get("courses", [])

    tasks = []
    for course in courses:
        course_id = course["id"]
        course_name = course["name"]

        coursework = service.courses().courseWork().list(courseId=course_id).execute()
        for work in coursework.get("courseWork", []):
            tasks.append({
                "title": work["title"],
                "due": work.get("dueDate"),
                "course": course_name
            })
    return tasks

# --- Push to Notion ---
def push_to_notion(tasks):
    url = f"https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    for task in tasks:
        data = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": {
                "Name": {"title": [{"text": {"content": task["title"]}}]},
                "Course": {"rich_text": [{"text": {"content": task["course"]}}]},
                "Due Date": {"date": {"start": str(task["due"]) if task["due"] else None}}
            }
        }
        requests.post(url, headers=headers, json=data)

if __name__ == "__main__":
    assignments = get_assignments()
    push_to_notion(assignments)


