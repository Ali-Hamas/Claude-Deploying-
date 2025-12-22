# Database Schema - Phase III

## Tables

### users
- `id`: integer (primary key)
- `email`: string (unique, indexed)
- `name`: string
- `password`: string (hashed)
- `created_at`: timestamp
- `updated_at`: timestamp

### tasks
- `id`: integer (primary key)
- `title`: string (required)
- `description`: string (optional)
- `status`: string (enum: "pending", "completed", default: "pending")
- `priority`: string (enum: "low", "medium", "high", "urgent", default: "medium")
- `due_date`: timestamp (optional)
- `tags`: JSON array of strings (default: [])
- `recurrence`: string (enum: "daily", "weekly", "monthly", "yearly", optional)
- `reminder_sent`: boolean (default: false) - tracks if reminder notification has been sent
- `user_id`: integer (foreign key -> users.id)
- `created_at`: timestamp
- `updated_at`: timestamp

### conversations
- `id`: integer (primary key)
- `user_id`: integer (foreign key -> users.id)
- `created_at`: timestamp
- `updated_at`: timestamp

### messages
- `id`: integer (primary key)
- `conversation_id`: integer (foreign key -> conversations.id)
- `role`: string (enum: "user", "assistant")
- `content`: text
- `created_at`: timestamp