#!/usr/bin/env python3
"""
Daily Digest Generator

Generates a morning briefing to help with daily planning.
Designed to work with Claude/Cowork for interactive planning sessions.

Usage with Claude:
    "Help me plan my day" -> Triggers this workflow

The digest includes:
- Overdue tasks
- Tasks due today
- Upcoming deadlines (next 7 days)
- Current focus from context library
- Questions to help prioritise
"""

import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from config import CONTEXT_DIR, DATABASES


def load_current_focus() -> Optional[str]:
    """
    Load the current-focus.md file from the context library.
    """
    focus_file = CONTEXT_DIR / "current-focus.md"
    if focus_file.exists():
        return focus_file.read_text()
    return None


def generate_planning_questions(
    overdue_count: int = 0,
    due_today_count: int = 0,
    has_meetings: bool = False,
) -> List[str]:
    """
    Generate contextual questions to help with daily planning.
    """
    questions = []

    # Always start with energy check
    questions.append("How are you feeling today - high energy for deep work, or better suited for lighter tasks?")

    if has_meetings:
        questions.append("You have meetings today. What do you need to prepare?")

    if overdue_count > 0:
        questions.append(f"You have {overdue_count} overdue task(s). Which of these is most important to address today?")

    if due_today_count > 3:
        questions.append(f"You have {due_today_count} tasks due today. That's a lot - which 2-3 are truly non-negotiable?")

    questions.append("What were you working on yesterday? Should you continue, or switch focus?")
    questions.append("Is anything weighing on your mind that we should capture or address?")

    return questions


def format_task_summary(tasks: List[Dict]) -> str:
    """
    Format a list of tasks into a readable summary.
    """
    if not tasks:
        return "_None_"

    lines = []
    for task in tasks[:10]:  # Limit to 10
        priority = task.get("Priority", "")
        due = task.get("Due date", "")
        project = task.get("Project", "")

        priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(priority, "⚪")

        line = f"- {priority_emoji} **{task.get('Task name', 'Untitled')}**"
        if project:
            line += f" [{project}]"
        if due:
            line += f" (due: {due})"

        lines.append(line)

    if len(tasks) > 10:
        lines.append(f"_...and {len(tasks) - 10} more_")

    return "\n".join(lines)


def generate_digest_template(
    date: str,
    overdue_tasks: List[Dict] = None,
    due_today: List[Dict] = None,
    upcoming: List[Dict] = None,
    current_focus: Optional[str] = None,
) -> str:
    """
    Generate the full daily digest document.
    """
    today = datetime.now()
    day_name = today.strftime("%A")

    digest = []

    digest.append(f"# Daily Planning - {day_name}, {date}")
    digest.append("")

    # Planning Questions
    digest.append("## Let's Plan Your Day")
    digest.append("")
    digest.append("Before diving in, let me ask a few questions:")
    digest.append("")

    questions = generate_planning_questions(
        overdue_count=len(overdue_tasks or []),
        due_today_count=len(due_today or []),
        has_meetings=False,  # Would need calendar integration
    )

    for i, q in enumerate(questions, 1):
        digest.append(f"{i}. {q}")

    digest.append("")
    digest.append("---")
    digest.append("")

    # Overdue Tasks
    digest.append("## ⚠️ Overdue Tasks")
    digest.append("")
    digest.append(format_task_summary(overdue_tasks or []))
    digest.append("")

    # Due Today
    digest.append("## 📅 Due Today")
    digest.append("")
    digest.append(format_task_summary(due_today or []))
    digest.append("")

    # Upcoming (next 7 days)
    digest.append("## 🔮 Upcoming (Next 7 Days)")
    digest.append("")
    digest.append(format_task_summary(upcoming or []))
    digest.append("")

    # Current Focus
    if current_focus:
        digest.append("## 🎯 Current Focus")
        digest.append("")
        # Extract just the key parts
        digest.append("_From your context library:_")
        digest.append("")
        # Include first 500 chars of current focus
        preview = current_focus[:500]
        if len(current_focus) > 500:
            preview += "..."
        digest.append(preview)
        digest.append("")

    digest.append("---")
    digest.append("")

    # Daily Plan Template
    digest.append("## Today's Plan")
    digest.append("")
    digest.append("Based on your answers, here's a suggested structure:")
    digest.append("")
    digest.append("### Must Do (non-negotiable)")
    digest.append("1. ")
    digest.append("")
    digest.append("### Should Do (important but flexible)")
    digest.append("2. ")
    digest.append("3. ")
    digest.append("")
    digest.append("### Could Do (if time permits)")
    digest.append("4. ")
    digest.append("")
    digest.append("### Parking Lot (explicitly deferred)")
    digest.append("- ")
    digest.append("")

    return "\n".join(digest)


def generate_claude_instructions() -> str:
    """
    Generate instructions for Claude on how to use this for daily planning.
    """
    return """
## How to Help the user Plan His Day

When the user asks for help with daily planning, follow this workflow:

### Step 1: Ask Orientation Questions
Don't just dump a task list. Start with questions:
- "How's your energy today?"
- "Any meetings or fixed commitments?"
- "What were you working on yesterday?"
- "Anything weighing on your mind?"

### Step 2: Query Notion for Tasks
Use the Notion tools to get:
1. **Overdue tasks**: Status != Done AND Due date < today
2. **Due today**: Due date = today
3. **Upcoming**: Due date within next 7 days

Query the Tasks Tracker database:
- Data source: `collection://YOUR-TASKS-DATABASE-ID-HERE`

### Step 3: Read Context
Check `.context/current-focus.md` for:
- What the user was working on
- Current priorities
- Open loops

### Step 4: Help Prioritise
Based on answers and data:
- Suggest 3-5 realistic tasks
- Flag blocking items
- Consider energy level
- Mix different types of work

### Step 5: Create the Plan
Format as:
- **Must Do**: Non-negotiable items
- **Should Do**: Important but flexible
- **Could Do**: If time permits
- **Parking Lot**: Explicitly deferred

### Remember:
- the user prefers questions over lists
- Don't overwhelm - be realistic
- It's OK to suggest removing tasks
- Update current-focus.md at end of session
"""


def main():
    parser = argparse.ArgumentParser(description="Generate daily planning digest")
    parser.add_argument("--date", help="Date for digest (YYYY-MM-DD)")
    parser.add_argument("--instructions", action="store_true", help="Show Claude instructions")
    args = parser.parse_args()

    if args.instructions:
        print(generate_claude_instructions())
        return

    date = args.date or datetime.now().strftime("%d %B %Y")

    print("Daily Digest Generator")
    print("=" * 40)
    print()

    # Load current focus
    current_focus = load_current_focus()

    # Generate template (without actual Notion data - Claude will fill this in)
    print("When used with Claude/Cowork, this generates a daily planning session.")
    print()
    print("Example usage:")
    print('  "Help me plan my day"')
    print('  "What should I focus on today?"')
    print('  "Morning briefing please"')
    print()
    print("-" * 40)
    print()

    # Show template structure
    print(generate_digest_template(
        date=date,
        overdue_tasks=[
            {"Task name": "[Claude will query Notion]", "Priority": "High", "Project": "..."}
        ],
        due_today=[
            {"Task name": "[Tasks due today]", "Priority": "Medium"}
        ],
        upcoming=[
            {"Task name": "[Upcoming tasks]", "Priority": "Low", "Due date": "..."}
        ],
        current_focus=current_focus,
    ))


if __name__ == "__main__":
    main()
