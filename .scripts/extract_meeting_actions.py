#!/usr/bin/env python3
"""
Meeting Action Item Extractor

This script is designed to work with Claude/Cowork to:
1. Find recent meeting transcripts in Notion (pages starting with @)
2. Extract action items using pattern matching and AI
3. Create corresponding tasks in the Tasks Tracker database

Usage with Claude:
    "Run the meeting action extractor on yesterday's meeting with [Supervisor]"

Manual usage:
    python extract_meeting_actions.py --date "2026-01-14"
"""

import argparse
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from notion_helpers import (
    extract_action_patterns,
    parse_deadline_from_text,
    infer_project_from_context,
    infer_priority_from_context,
    format_task_for_notion,
)
from config import DATABASES, CONTEXT_DIR


def find_meeting_transcripts_query(since_date: Optional[str] = None) -> str:
    """
    Generate a search query to find meeting transcripts in Notion.

    Meeting transcripts are pages with titles like "@14 January 2026 14:31"
    """
    query = "@ January" if not since_date else f"@{since_date}"
    return query


def parse_meeting_title(title: str) -> Optional[datetime]:
    """
    Parse a meeting title like "@14 January 2026 14:31" into a datetime.
    """
    # Pattern: @DD Month YYYY HH:MM
    pattern = r"@(\d{1,2})\s+(\w+)\s+(\d{4})\s+(\d{1,2}):(\d{2})"
    match = re.match(pattern, title)

    if match:
        day, month, year, hour, minute = match.groups()
        month_map = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12
        }
        month_num = month_map.get(month.lower())
        if month_num:
            return datetime(int(year), month_num, int(day), int(hour), int(minute))

    return None


def identify_meeting_participants(content: str) -> List[str]:
    """
    Try to identify who was in the meeting based on content.
    """
    # Known names from context
    known_people = [
        "[Supervisor]", "[Supervisor]", "[Collaborator]", "[Collaborator]", "[Collaborator]",
        "Francois", "David", "Toby", "Walter"
    ]

    found = []
    content_lower = content.lower()

    for person in known_people:
        if person.lower() in content_lower:
            found.append(person)

    return found


def extract_actions_from_transcript(
    content: str,
    meeting_date: str,
    participants: List[str] = None
) -> List[Dict]:
    """
    Extract structured action items from meeting transcript content.

    Args:
        content: The meeting transcript text
        meeting_date: Date string of the meeting
        participants: List of people who were in the meeting

    Returns:
        List of action item dictionaries ready for task creation
    """
    # Use pattern matching to find potential actions
    raw_actions = extract_action_patterns(content)

    # Enrich each action with context
    enriched_actions = []

    for action in raw_actions:
        task_text = action["text"]

        # Clean up the task text
        task_text = task_text.strip()
        if task_text.endswith((",", ".", ";")):
            task_text = task_text[:-1]

        # Skip very short or unclear actions
        if len(task_text) < 5:
            continue

        # Infer additional context
        deadline = parse_deadline_from_text(task_text)
        project = infer_project_from_context(task_text, participants)
        is_supervisor = any(p in ["[Supervisor]", "[Supervisor]"] for p in (participants or []))
        priority = infer_priority_from_context(
            task_text,
            has_deadline=deadline is not None,
            is_supervisor_request=is_supervisor and action["type"] == "request"
        )

        enriched = {
            "task_name": f"{task_text} - from {meeting_date} meeting",
            "original_text": action["text"],
            "deadline": deadline,
            "project": project,
            "priority": priority,
            "source": "Meeting",
            "meeting_date": meeting_date,
            "participants": participants or [],
            "action_type": action["type"],
        }

        enriched_actions.append(enriched)

    return enriched_actions


def generate_task_creation_instructions(actions: List[Dict]) -> str:
    """
    Generate instructions for Claude to create tasks in Notion.

    This is the output format when used with Claude/Cowork.
    """
    if not actions:
        return "No action items found in this transcript."

    output = []
    output.append("## Extracted Action Items\n")
    output.append(f"Found {len(actions)} potential action items:\n")

    for i, action in enumerate(actions, 1):
        output.append(f"### {i}. {action['task_name']}")
        output.append(f"- **Priority:** {action['priority']}")
        if action['deadline']:
            output.append(f"- **Due:** {action['deadline']}")
        if action['project']:
            output.append(f"- **Project:** {action['project']}")
        output.append(f"- **Source:** Meeting ({action['meeting_date']})")
        if action['participants']:
            output.append(f"- **With:** {', '.join(action['participants'])}")
        output.append("")

    output.append("\n---\n")
    output.append("**To create these tasks in Notion:**")
    output.append("Use the `notion-create-pages` tool with parent:")
    output.append(f"  `{{'data_source_id': '{DATABASES['tasks_tracker_collection']}'}}`")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Extract meeting action items")
    parser.add_argument("--date", help="Meeting date (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, default=7, help="Look back N days")
    parser.add_argument("--dry-run", action="store_true", help="Don't create tasks")
    args = parser.parse_args()

    print("Meeting Action Extractor")
    print("=" * 40)
    print()
    print("This script helps extract action items from meeting transcripts.")
    print("When used with Claude/Cowork, it will:")
    print("  1. Search Notion for meeting transcripts (@DATE pages)")
    print("  2. Extract action items using pattern matching")
    print("  3. Create tasks in the Tasks Tracker database")
    print()
    print("Example usage with Claude:")
    print('  "Extract action items from my meeting yesterday with [Supervisor]"')
    print('  "Process all unprocessed meeting transcripts from this week"')
    print()

    if args.dry_run:
        # Demo with sample text
        sample_transcript = """
        the user, I know you would be operative for you, right? So when you have these events,
        you need to give a list of the names of people coming to the desk downstairs at the Shard.
        I'll send you an email about the catering costs by Friday.
        Can you also update the course guide and send it to the students?
        We agreed to meet again next Tuesday to discuss progress.
        """

        print("Demo extraction from sample text:")
        print("-" * 40)

        actions = extract_actions_from_transcript(
            sample_transcript,
            meeting_date="14 January 2026",
            participants=["[Supervisor]"]
        )

        print(generate_task_creation_instructions(actions))


if __name__ == "__main__":
    main()
