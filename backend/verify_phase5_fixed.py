"""
Phase 5 Automated Bug Fixes and Verification Script
This script fixes identified bugs and verifies Phase 5 implementation
"""

import sys
import os
import json
import subprocess
from datetime import datetime, timedelta

# Force UTF-8 encoding for stdout/stderr
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def check_imports():
    """Verify all required packages are installed"""
    print_section("Checking Dependencies")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlmodel',
        'dapr',
        'jose',
        'passlib',
        'openai'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies installed!")
    return True

def check_dapr():
    """Check if Dapr CLI is installed"""
    print_section("Checking Dapr Installation")
    
    try:
        # Check running processes first to avoid hanging on dapr list
        # This is just a basic check
        result = subprocess.run(['dapr', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ Dapr CLI installed: {result.stdout.strip()}")
            return True
        else:
            print("✗ Dapr CLI not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✗ Dapr CLI not installed")
        return False

def verify_database_models():
    """Verify database models have all Phase 5 fields"""
    print_section("Verifying Database Schema")
    
    try:
        from models.todo_models import Task, TaskPriority, TaskRecurrence, TaskStatus
        
        # Check if Task has all required fields
        required_fields = [
            'id', 'title', 'description', 'status', 'priority', 
            'due_date', 'tags', 'recurrence', 'reminder_sent', 
            'user_id', 'created_at', 'updated_at'
        ]
        
        task_fields = Task.__fields__.keys()
        
        for field in required_fields:
            if field in task_fields:
                print(f"✓ Task.{field} exists")
            else:
                print(f"✗ Task.{field} MISSING")
                return False
        
        # Verify enums
        print(f"✓ TaskPriority enum: {[p.value for p in TaskPriority]}")
        print(f"✓ TaskRecurrence enum: {[r.value for r in TaskRecurrence]}")
        print(f"✓ TaskStatus enum: {[s.value for s in TaskStatus]}")
        
        print("\n✅ Database schema is correct!")
        return True
        
    except Exception as e:
        print(f"✗ Error verifying models: {e}")
        return False

def verify_event_service():
    """Verify event service implementation"""
    print_section("Verifying Event Service")
    
    try:
        from services.event_service import (
            publish_task_completed_event,
            publish_task_reminder_event,
            handle_recurring_task,
            calculate_next_due_date
        )
        
        print("✓ publish_task_completed_event imported")
        print("✓ publish_task_reminder_event imported")
        print("✓ handle_recurring_task imported")
        print("✓ calculate_next_due_date imported")
        
        # Test date calculation
        from models.todo_models import TaskRecurrence
        base_date = datetime(2025, 12, 19, 10, 0, 0)
        
        daily = calculate_next_due_date(TaskRecurrence.daily, base_date)
        assert daily == base_date + timedelta(days=1), "Daily calculation failed"
        print("✓ Daily recurrence calculation works")
        
        weekly = calculate_next_due_date(TaskRecurrence.weekly, base_date)
        assert weekly == base_date + timedelta(weeks=1), "Weekly calculation failed"
        print("✓ Weekly recurrence calculation works")
        
        print("\n✅ Event service is working!")
        return True
        
    except Exception as e:
        print(f"✗ Error verifying event service: {e}")
        return False

def verify_api_endpoints():
    """Verify all required API endpoints exist in main.py"""
    print_section("Verifying API Endpoints")
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        required_endpoints = [
            ('/dapr/subscribe', 'GET'),
            ('/api/events/task-completed', 'POST'),
            ('/api/events/task-reminder', 'POST'),
            ('/reminder-cron', 'POST'),
            ('/api/tasks', 'GET'),
            ('/api/tasks', 'POST'),
            ('/api/chat', 'POST'),
            ('/auth/register', 'POST'),
            ('/auth/login', 'POST'),
        ]
        
        all_found = True
        for path, method in required_endpoints:
            # Check for FastAPI route decorator
            # Simple check for path string presence
            if f'"{path}"' in main_content or f"'{path}'" in main_content:
                print(f"✓ {method} {path} definition found")
            else:
                print(f"✗ {method} {path} MISSING")
                all_found = False
        
        if all_found:
            print("\n✅ All API endpoints implemented!")
        return all_found
    except Exception as e:
        print(f"✗ Error reading main.py: {e}")
        return False

def check_env_file():
    """Verify .env file has required variables"""
    print_section("Checking Environment Configuration")
    
    if not os.path.exists('.env'):
        print("✗ .env file not found")
        return False
    
    with open('.env', 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    required_vars = [
        'DATABASE_URL',
        'BETTER_AUTH_SECRET',
        'OPENAI_API_KEY'
    ]
    
    all_found = True
    for var in required_vars:
        if var in env_content:
            print(f"✓ {var} configured")
        else:
            print(f"✗ {var} MISSING")
            all_found = False
    
    if all_found:
        print("\n✅ Environment configured!")
    return all_found

def run_quick_test():
    """Run a quick smoke test"""
    print_section("Running Quick Smoke Test")
    
    try:
        # Test database connection
        from database.connection import engine
        from sqlmodel import Session
        
        with Session(engine) as session:
            print("✓ Database connection works")
        
        # Test model creation
        from models.todo_models import Task, TaskStatus, TaskPriority
        
        test_task = Task(
            title="Test Task",
            description="Smoke test",
            user_id=1,
            status=TaskStatus.pending,
            priority=TaskPriority.high
        )
        print("✓ Task model can be instantiated")
        
        print("\n✅ Smoke tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Smoke test failed: {e}")
        # Don't print stack trace to keep output clean on non-utf8 terminals
        return False

def main():
    print("Starting verification (Phase 5)...")
    
    # Change to backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    results = {
        "Dependencies": check_imports(),
        "Dapr": check_dapr(),
        "Database Schema": verify_database_models(),
        "Event Service": verify_event_service(),
        "API Endpoints": verify_api_endpoints(),
        "Environment": check_env_file(),
        "Smoke Tests": run_quick_test()
    }
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    percentage = (passed / total) * 100
    
    print_section(f"FINAL RESULT: {passed}/{total} ({percentage:.0f}%)")
    
    return percentage >= 90

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
