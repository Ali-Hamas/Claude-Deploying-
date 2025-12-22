# Feature: Advanced Task Management

## Goal
Extend the basic task management system with advanced features including task priority, due dates, tags, and recurring tasks.

## New Task Fields

### 1. Priority
- **Type:** Enum (low, medium, high, urgent)
- **Default:** medium
- **Purpose:** Allow users to prioritize their tasks
- **API Field:** `priority` (string)

### 2. Due Date
- **Type:** DateTime (nullable)
- **Default:** None
- **Purpose:** Set deadlines for tasks
- **API Field:** `due_date` (ISO 8601 datetime string, optional)

### 3. Tags
- **Type:** Array of strings
- **Default:** Empty array
- **Purpose:** Categorize and filter tasks by custom labels
- **API Field:** `tags` (array of strings)
- **Examples:** ["work", "personal", "urgent", "shopping"]

### 4. Recurrence
- **Type:** String (nullable)
- **Default:** None
- **Purpose:** Define repeating task patterns
- **API Field:** `recurrence` (string, optional)
- **Supported Values:**
  - `"daily"` - repeats every day
  - `"weekly"` - repeats every week
  - `"monthly"` - repeats every month
  - `"yearly"` - repeats every year
  - `null` - one-time task (default)

## Database Schema Changes

### tasks table additions:
- `priority`: string (enum: "low", "medium", "high", "urgent"), default: "medium"
- `due_date`: timestamp (nullable)
- `tags`: JSON array of strings (default: [])
- `recurrence`: string (nullable, values: "daily", "weekly", "monthly", "yearly")

## MCP Tool Updates

### add_task
Additional parameters:
- `priority` (string, optional, default: "medium")
- `due_date` (string ISO 8601, optional)
- `tags` (array of strings, optional, default: [])
- `recurrence` (string, optional)

### update_task
Additional parameters:
- `priority` (string, optional)
- `due_date` (string ISO 8601, optional)
- `tags` (array of strings, optional)
- `recurrence` (string, optional)

### list_tasks
Additional filter parameters:
- `priority_filter` (string, optional) - filter by priority level
- `tag_filter` (string, optional) - filter by tag
- `due_before` (string ISO 8601, optional) - filter tasks due before this date
- `due_after` (string ISO 8601, optional) - filter tasks due after this date

## User Stories
- "Add a high priority task to submit report by Friday" -> Agent creates task with priority=high and due_date set
- "Tag this task as work" -> Agent updates task tags to include "work"
- "Show me all urgent tasks" -> Agent filters by priority="urgent"
- "Create a daily task to exercise" -> Agent creates task with recurrence="daily"
- "What tasks are due this week?" -> Agent filters by due_date range
