"""
Notion API Helper Functions

Utilities for interacting with Notion databases.
Note: For use with Claude/Cowork, these functions describe the intended
operations that Claude can execute via its Notion MCP tools.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


def format_task_for_notion(
    task_name: str,
    project: Optional[str] = None,
    source: Optional[str] = None,
    priority: str = "Medium",
    due_date: Optional[str] = None,
    task_type: Optional[List[str]] = None,
    uni: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Format a task for creation in Notion Tasks Tracker.

    Args:
        task_name: The task title (action verb + object + context)
        project: Which project this belongs to (e.g., "Journal Revision")
        source: Where the task came from (e.g., "Meeting")
        priority: "High", "Medium", or "Low"
        due_date: ISO format date string (YYYY-MM-DD)
        task_type: List of types (e.g., ["📝 Writing", "📅 Meeting"])
        uni: Related university
        description: Additional context

    Returns:
        Dictionary ready for Notion create-pages API
    """
    properties = {
        "Task name": task_name,
        "Status": "Not started",
        "Priority": priority,
    }

    if project:
        properties["Project"] = project

    if source:
        properties["Source"] = source

    if due_date:
        properties["date:Due date:start"] = due_date
        properties["date:Due date:is_datetime"] = 0

    if task_type:
        properties["Task type"] = task_type

    if uni:
        properties["Uni"] = uni

    if description:
        properties["Description"] = description

    return properties


def parse_deadline_from_text(text: str) -> Optional[str]:
    """
    Extract deadline from natural language text.

    Examples:
        "by Friday" -> next Friday's date
        "by end of month" -> last day of current month
        "by next Tuesday" -> next Tuesday's date

    Returns:
        ISO format date string or None
    """
    text_lower = text.lower()
    today = datetime.now()

    # Day names
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    for i, day in enumerate(days):
        if day in text_lower:
            # Calculate days until that day
            current_day = today.weekday()
            target_day = i
            days_ahead = target_day - current_day
            if days_ahead <= 0:
                days_ahead += 7
            if "next" in text_lower:
                days_ahead += 7
            target_date = today + timedelta(days=days_ahead)
            return target_date.strftime("%Y-%m-%d")

    if "end of month" in text_lower or "end of the month" in text_lower:
        # Get last day of current month
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        last_day = next_month - timedelta(days=1)
        return last_day.strftime("%Y-%m-%d")

    if "end of week" in text_lower:
        # Friday of current week
        days_until_friday = 4 - today.weekday()
        if days_until_friday < 0:
            days_until_friday += 7
        target_date = today + timedelta(days=days_until_friday)
        return target_date.strftime("%Y-%m-%d")

    if "tomorrow" in text_lower:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    if "today" in text_lower:
        return today.strftime("%Y-%m-%d")

    return None


def infer_project_from_context(text: str, people: List[str] = None) -> Optional[str]:
    """
    Infer which project a task belongs to based on keywords and people mentioned.

    Args:
        text: The task description or context
        people: List of people mentioned

    Returns:
        Project name or None
    """
    text_lower = text.lower()

    # Keyword mapping
    project_keywords = {
        # Map keywords to project names for auto-categorisation
        # "Paper Revision": ["revision", "referee", "resubmit"],
        # "Teaching Prep": ["teaching", "students", "course", "marking"],
    }

    # People mapping
    people_projects = {
        # Map collaborator names (lowercase) to projects
        # "supervisor_name": "Paper Revision",
        # "collaborator_name": "Joint Project",
    }

    # Check keywords
    for project, keywords in project_keywords.items():
        if any(kw in text_lower for kw in keywords):
            return project

    # Check people
    if people:
        for person in people:
            person_lower = person.lower()
            for name, project in people_projects.items():
                if name in person_lower:
                    return project

    return None


def infer_priority_from_context(
    text: str,
    has_deadline: bool = False,
    is_supervisor_request: bool = False,
    is_blocking: bool = False,
) -> str:
    """
    Infer task priority based on context clues.

    Returns:
        "High", "Medium", or "Low"
    """
    text_lower = text.lower()

    # High priority signals
    high_signals = [
        "urgent", "asap", "immediately", "critical", "important",
        "deadline", "overdue", "waiting on", "blocking"
    ]

    # Low priority signals
    low_signals = [
        "when you have time", "no rush", "eventually", "nice to have",
        "optional", "someday", "maybe"
    ]

    if any(signal in text_lower for signal in high_signals):
        return "High"

    if is_supervisor_request or is_blocking:
        return "High"

    if has_deadline:
        return "Medium"  # At least medium if there's a deadline

    if any(signal in text_lower for signal in low_signals):
        return "Low"

    return "Medium"  # Default


def extract_action_patterns(text: str) -> List[Dict[str, Any]]:
    """
    Extract potential action items from meeting transcript text.

    Looks for patterns like:
    - "I'll do X"
    - "I'm going to..."
    - "I need to..."
    - "Can you send..."
    - "We agreed to..."

    Returns:
        List of dictionaries with 'text', 'assignee', 'type' keys
    """
    actions = []

    # Patterns that indicate commitments from speaker
    commitment_patterns = [
        r"I'll ([^.!?]+)",
        r"I'm going to ([^.!?]+)",
        r"I need to ([^.!?]+)",
        r"I should ([^.!?]+)",
        r"I can ([^.!?]+)",
        r"I will ([^.!?]+)",
        r"Let me ([^.!?]+)",
    ]

    # Patterns that indicate requests/asks
    request_patterns = [
        r"[Cc]an you ([^.!?]+)",
        r"[Cc]ould you ([^.!?]+)",
        r"[Pp]lease ([^.!?]+)",
        r"[Ww]ould you ([^.!?]+)",
    ]

    # Patterns that indicate agreements
    agreement_patterns = [
        r"[Ww]e agreed to ([^.!?]+)",
        r"[Ll]et's ([^.!?]+)",
        r"[Nn]ext step is to ([^.!?]+)",
        r"[Aa]ction item[s]?: ([^.!?]+)",
    ]

    import re

    for pattern in commitment_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            actions.append({
                "text": match.strip(),
                "assignee": "the user",
                "type": "commitment"
            })

    for pattern in request_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            actions.append({
                "text": match.strip(),
                "assignee": "the user",  # Assume requests are to the user
                "type": "request"
            })

    for pattern in agreement_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            actions.append({
                "text": match.strip(),
                "assignee": "the user",
                "type": "agreement"
            })

    return actions


# Utility functions for Claude integration
def create_task_prompt(action_items: List[Dict]) -> str:
    """
    Generate a prompt for Claude to create tasks in Notion.

    Args:
        action_items: List of extracted action items

    Returns:
        Formatted prompt string
    """
    if not action_items:
        return "No action items to create."

    prompt = "Please create the following tasks in the Tasks Tracker database:\n\n"

    for i, item in enumerate(action_items, 1):
        prompt += f"{i}. **{item.get('text', 'Unknown task')}**\n"
        if item.get('deadline'):
            prompt += f"   - Due: {item['deadline']}\n"
        if item.get('project'):
            prompt += f"   - Project: {item['project']}\n"
        if item.get('context'):
            prompt += f"   - Context: {item['context']}\n"
        prompt += "\n"

    return prompt


if __name__ == "__main__":
    # Test the functions
    print("Testing deadline parsing:")
    print(f"  'by Friday' -> {parse_deadline_from_text('by Friday')}")
    print(f"  'by next Tuesday' -> {parse_deadline_from_text('by next Tuesday')}")
    print(f"  'by end of month' -> {parse_deadline_from_text('by end of month')}")

    print("\nTesting project inference:")
    print(f"  'journal revision section 4' -> {infer_project_from_context('journal revision section 4')}")
    print(f"  'project keyword test' -> {infer_project_from_context('project keyword test')}")

    print("\nTesting priority inference:")
    print(f"  'urgent review needed' -> {infer_priority_from_context('urgent review needed')}")
    print(f"  'when you have time' -> {infer_priority_from_context('when you have time')}")
