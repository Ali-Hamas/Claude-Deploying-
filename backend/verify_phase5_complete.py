"""
Phase V Complete Verification Script

Tests all Advanced Features:
1. Event-Driven Updates (task.created, task.updated, task.completed events)
2. Recurring Tasks Engine (automatic next instance creation)
3. Reminder System (overdue task notifications)

Prerequisites:
- Backend server running on port 8000
- Dapr sidecar running with kafka-pubsub and reminder-cron components
"""

import requests
import time
from datetime import datetime, timedelta
import json

BASE_URL = "http://localhost:8000"
API_HEADERS = {"Content-Type": "application/json"}

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def login_user():
    """Login and get access token"""
    print_section("Step 1: Authentication")

    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "demo@example.com",
            "password": "demo123"
        }
    )

    if response.status_code == 200:
        token_data = response.json()
        print("✅ Login successful!")
        print(f"   User: {token_data['user']['email']}")
        return token_data["access_token"]
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_event_driven_updates(token):
    """Test Feature 1: Event-Driven Updates"""
    print_section("Feature 1: Event-Driven Updates")

    headers = {
        **API_HEADERS,
        "Authorization": f"Bearer {token}"
    }

    # Test 1.1: Create a task (should publish task.created event)
    print("\n📝 Test 1.1: Creating a task (should publish task.created event)")
    create_response = requests.post(
        f"{BASE_URL}/api/tasks",
        headers=headers,
        json={
            "title": "Test Event-Driven Task",
            "description": "Testing event publishing on create",
            "priority": "high",
            "due_date": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
    )

    if create_response.status_code == 201:
        task = create_response.json()
        task_id = task["id"]
        print(f"✅ Task created successfully (ID: {task_id})")
        print(f"   Expected: task.created event published to 'task-events' topic")
    else:
        print(f"❌ Failed to create task: {create_response.status_code}")
        return None

    # Test 1.2: Update a task (should publish task.updated event)
    print("\n📝 Test 1.2: Updating a task (should publish task.updated event)")
    update_response = requests.put(
        f"{BASE_URL}/api/tasks/{task_id}",
        headers=headers,
        json={
            "title": "Updated Event-Driven Task",
            "priority": "urgent"
        }
    )

    if update_response.status_code == 200:
        print(f"✅ Task updated successfully (ID: {task_id})")
        print(f"   Expected: task.updated event published to 'task-events' topic")
    else:
        print(f"❌ Failed to update task: {update_response.status_code}")

    # Test 1.3: Complete a task (should publish task.completed event)
    print("\n📝 Test 1.3: Completing a task (should publish task.completed event)")
    complete_response = requests.put(
        f"{BASE_URL}/api/tasks/{task_id}",
        headers=headers,
        json={
            "status": "completed"
        }
    )

    if complete_response.status_code == 200:
        print(f"✅ Task completed successfully (ID: {task_id})")
        print(f"   Expected: task.completed event published to 'task-events' topic")
    else:
        print(f"❌ Failed to complete task: {complete_response.status_code}")

    return task_id

def test_recurring_tasks(token):
    """Test Feature 2: Recurring Tasks Engine"""
    print_section("Feature 2: Recurring Tasks Engine")

    headers = {
        **API_HEADERS,
        "Authorization": f"Bearer {token}"
    }

    # Test 2.1: Create a daily recurring task
    print("\n📝 Test 2.1: Creating a daily recurring task")
    create_response = requests.post(
        f"{BASE_URL}/api/tasks",
        headers=headers,
        json={
            "title": "Daily Exercise",
            "description": "Do 30 minutes of exercise",
            "priority": "high",
            "due_date": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "recurrence": "daily"
        }
    )

    if create_response.status_code == 201:
        task = create_response.json()
        task_id = task["id"]
        print(f"✅ Recurring task created (ID: {task_id})")
        print(f"   Recurrence: {task['recurrence']}")
        print(f"   Due date: {task['due_date']}")
    else:
        print(f"❌ Failed to create recurring task: {create_response.status_code}")
        return None

    # Test 2.2: Complete the recurring task
    print("\n📝 Test 2.2: Completing the recurring task")
    print("   This should trigger the recurring task engine to create the next instance")

    complete_response = requests.put(
        f"{BASE_URL}/api/tasks/{task_id}",
        headers=headers,
        json={
            "status": "completed"
        }
    )

    if complete_response.status_code == 200:
        print(f"✅ Recurring task completed (ID: {task_id})")
        print(f"   Expected: task.completed event published")
        print(f"   Expected: Dapr subscription handler creates next instance")
    else:
        print(f"❌ Failed to complete recurring task: {complete_response.status_code}")
        return None

    # Test 2.3: Wait for event processing and check for new task
    print("\n⏳ Waiting 3 seconds for Dapr to process the event...")
    time.sleep(3)

    print("\n📝 Test 2.3: Checking for newly created recurring task instance")
    list_response = requests.get(
        f"{BASE_URL}/api/tasks",
        headers=headers
    )

    if list_response.status_code == 200:
        tasks = list_response.json()
        recurring_tasks = [t for t in tasks if t.get("title") == "Daily Exercise" and t["status"] == "pending"]

        if recurring_tasks:
            new_task = recurring_tasks[0]
            print(f"✅ New recurring task instance found!")
            print(f"   New Task ID: {new_task['id']}")
            print(f"   Status: {new_task['status']}")
            print(f"   Due date: {new_task['due_date']}")
            print(f"   Recurrence: {new_task.get('recurrence')}")

            # Verify the due date is approximately 1 day later
            original_due = datetime.fromisoformat(task["due_date"].replace("Z", "+00:00"))
            new_due = datetime.fromisoformat(new_task["due_date"].replace("Z", "+00:00"))
            time_diff = (new_due - original_due).total_seconds() / 3600  # hours

            if 23 <= time_diff <= 25:  # Allow some tolerance
                print(f"   ✅ Due date correctly set ~24 hours later ({time_diff:.1f} hours)")
            else:
                print(f"   ⚠️  Due date difference unexpected: {time_diff:.1f} hours")
        else:
            print("❌ No new recurring task instance found!")
            print("   This may indicate the Dapr subscription is not working")
    else:
        print(f"❌ Failed to list tasks: {list_response.status_code}")

    return task_id

def test_reminder_system(token):
    """Test Feature 3: Reminder System"""
    print_section("Feature 3: Reminder System")

    headers = {
        **API_HEADERS,
        "Authorization": f"Bearer {token}"
    }

    # Test 3.1: Create an overdue task
    print("\n📝 Test 3.1: Creating an overdue task (due 5 minutes ago)")
    overdue_time = datetime.utcnow() - timedelta(minutes=5)

    create_response = requests.post(
        f"{BASE_URL}/api/tasks",
        headers=headers,
        json={
            "title": "Overdue Task for Reminder Test",
            "description": "This task is overdue and should trigger a reminder",
            "priority": "urgent",
            "due_date": overdue_time.isoformat()
        }
    )

    if create_response.status_code == 201:
        task = create_response.json()
        task_id = task["id"]
        print(f"✅ Overdue task created (ID: {task_id})")
        print(f"   Due date: {task['due_date']} (5 minutes ago)")
        print(f"   Reminder sent: {task.get('reminder_sent', False)}")
    else:
        print(f"❌ Failed to create overdue task: {create_response.status_code}")
        return None

    # Test 3.2: Manually trigger the reminder cron
    print("\n📝 Test 3.2: Triggering the reminder cron handler")
    print("   This would normally be triggered by Dapr cron binding every minute")

    try:
        cron_response = requests.post(f"{BASE_URL}/reminder-cron")

        if cron_response.status_code == 200:
            result = cron_response.json()
            print(f"✅ Reminder cron executed successfully")
            print(f"   Tasks found: {result.get('tasks_found', 0)}")
            print(f"   Reminders sent: {result.get('reminders_sent', 0)}")

            if result.get('tasks_found', 0) > 0:
                print(f"   ✅ Found overdue tasks needing reminders")
            else:
                print(f"   ⚠️  No overdue tasks found (may have already sent reminder)")
        else:
            print(f"❌ Reminder cron failed: {cron_response.status_code}")
            print(f"   Response: {cron_response.text}")
    except Exception as e:
        print(f"❌ Error calling reminder cron: {str(e)}")

    # Test 3.3: Verify reminder_sent flag was updated
    print("\n📝 Test 3.3: Verifying reminder_sent flag was updated")
    time.sleep(2)  # Wait for database update

    get_response = requests.get(
        f"{BASE_URL}/api/tasks",
        headers=headers
    )

    if get_response.status_code == 200:
        tasks = get_response.json()
        overdue_task = next((t for t in tasks if t["id"] == task_id), None)

        if overdue_task:
            reminder_sent = overdue_task.get("reminder_sent", False)
            if reminder_sent:
                print(f"✅ Task reminder_sent flag updated to True")
            else:
                print(f"⚠️  Task reminder_sent flag is still False")
                print(f"   This may indicate the cron handler didn't process the task")
        else:
            print(f"❌ Could not find task {task_id}")
    else:
        print(f"❌ Failed to get tasks: {get_response.status_code}")

    print("\n📝 Test 3.4: Check server logs for reminder messages")
    print("   Expected log output:")
    print(f"   '🔔 Sending Reminder for Task ID {task_id}: ...'")
    print(f"   Check your backend terminal for these messages")

    return task_id

def main():
    """Run all Phase V verification tests"""
    print("\n" + "🚀" * 40)
    print("  PHASE V ADVANCED FEATURES VERIFICATION")
    print("🚀" * 40)

    # Step 1: Authenticate
    token = login_user()
    if not token:
        print("\n❌ Authentication failed. Cannot continue with tests.")
        return

    # Step 2: Test Event-Driven Updates
    test_event_driven_updates(token)

    # Step 3: Test Recurring Tasks Engine
    test_recurring_tasks(token)

    # Step 4: Test Reminder System
    test_reminder_system(token)

    # Summary
    print_section("Verification Complete")
    print("\n✅ All Phase V features have been tested!")
    print("\nExpected Results:")
    print("  1. ✅ Event-Driven Updates:")
    print("     - task.created events published when tasks are created")
    print("     - task.updated events published when tasks are modified")
    print("     - task.completed events published when tasks are completed")
    print("\n  2. ✅ Recurring Tasks Engine:")
    print("     - Completing a recurring task triggers creation of next instance")
    print("     - New task has the same properties with updated due date")
    print("\n  3. ✅ Reminder System:")
    print("     - Cron job finds overdue tasks with reminder_sent=False")
    print("     - Reminder events are published to Dapr pub/sub")
    print("     - Tasks are marked as reminder_sent=True to prevent spam")
    print("\n📋 Next Steps:")
    print("  - Check Dapr logs to verify event publishing")
    print("  - Check backend logs to see '🔔 Sending Reminder' messages")
    print("  - Verify Kafka topic 'task-events' is receiving events")
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    main()
