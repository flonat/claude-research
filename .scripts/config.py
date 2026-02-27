"""
Configuration for Task Management Scripts

This file contains API keys and database IDs needed for automation.
IMPORTANT: Keep this file secure and don't commit API keys to version control.
"""

import os
from pathlib import Path

# Auto-load .env file from project root
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(_env_path)
except ImportError:
    pass  # dotenv not installed, rely on environment variables

# Notion Configuration
# Get your integration token from: https://www.notion.so/my-integrations
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "your-notion-integration-token")

# Database IDs (extracted from the user's Notion workspace)
# NOTE: These are Notion page IDs (from URLs). The Notion MCP tools and
# CLAUDE.md use separate database IDs — both formats are valid.
DATABASES = {
    "tasks_tracker": "YOUR-TASKS-DATABASE-ID-HERE",
    "research_pipeline": "YOUR-PIPELINE-DATABASE-ID-HERE",
    "conferences": "YOUR-CONFERENCES-DATABASE-ID-HERE",
}

# Page IDs
PAGES = {
    "dashboard": "YOUR-DASHBOARD-PAGE-ID-HERE",
}

# Local paths
BASE_DIR = Path(__file__).parent.parent
CONTEXT_DIR = BASE_DIR / ".context"
SCRIPTS_DIR = BASE_DIR / ".scripts"

# Project mappings (for task categorisation)
# Keep in sync with .context/projects/_index.md
PROJECTS = [
    # Add your project names here — keep in sync with .context/projects/_index.md
    "Paper Revision",
    "Literature Review",
    "Conference Submission",
    "Teaching Prep",
    "Personal Admin",
]

# Source types for tasks
SOURCES = [
    "Meeting",
    "Email",
    "Supervisor request",
    "Self-initiated",
    "Deadline/calendar",
    "Idea capture",
]

# Task types
TASK_TYPES = [
    "🐞 Bug",
    "💬 Feature request",
    "💅 Polish",
    "Claim",
    "📝 Writing",
    "📚 Reading",
    "🔬 Research",
    "📅 Meeting",
    "📋 Admin",
    "📧 Communication",
]

# Priority levels
PRIORITIES = ["High", "Medium", "Low"]

# Status options (GTD-style)
STATUSES = ["Inbox", "Not started", "In progress", "Waiting", "Someday", "Done"]

# Areas of responsibility (ongoing, no end date)
AREAS = [
    "Research",
    "Teaching",
    "Career",
    "Personal",
    "Health",
    "Learning",
]

# Universities
UNIVERSITIES = [
    # Add your institutions here
    "University A", "University B",
]


def validate_config():
    """Check that essential configuration is present."""
    issues = []

    if NOTION_TOKEN == "your-notion-integration-token":
        issues.append("NOTION_TOKEN not set. Set the NOTION_TOKEN environment variable.")

    if not CONTEXT_DIR.exists():
        issues.append(f"Context directory not found: {CONTEXT_DIR}")

    return issues


if __name__ == "__main__":
    issues = validate_config()
    if issues:
        print("Configuration issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Configuration valid!")
        print(f"Context directory: {CONTEXT_DIR}")
        print(f"Scripts directory: {SCRIPTS_DIR}")
