"""
Quick start script for Campus Event Management Platform.
This script will set up the database and create sample data.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False


def quick_start():
    """Quick start setup with database and sample data."""
    print("🚀 Quick Start - Campus Event Management Platform")
    print("=" * 50)
    
    # Check if virtual environment exists
    if not Path("venv").exists():
        print("❌ Virtual environment not found. Please run setup.py first.")
        return False
    
    # Determine the correct Python path
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/MacOS
        python_cmd = "venv/bin/python"
    
    # Run migrations
    if not run_command(f"{python_cmd} manage.py migrate", "Running database migrations"):
        print("💡 Make sure PostgreSQL is running and the database 'campus_events' exists")
        print("   You can create it with: createdb campus_events")
        return False
    
    # Create superuser (optional)
    print("\n👤 Creating superuser account...")
    print("   Username: admin")
    print("   Email: admin@example.com")
    print("   Password: admin123")
    
    superuser_script = """
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"""
    
    with open("temp_create_superuser.py", "w") as f:
        f.write(superuser_script)
    
    run_command(f"{python_cmd} manage.py shell < temp_create_superuser.py", "Creating superuser")
    os.remove("temp_create_superuser.py")
    
    # Create sample data
    if not run_command(f"{python_cmd} manage.py create_sample_data --colleges 3 --students-per-college 50 --events-per-college 10", "Creating sample data"):
        return False
    
    print("\n🎉 Quick start completed successfully!")
    print("\n📊 Sample data created:")
    print("   - 3 colleges")
    print("   - 150 students (50 per college)")
    print("   - 30 events (10 per college)")
    print("   - Event registrations, attendance, and feedback")
    
    print("\n🌐 Access the application:")
    print("   - Home: http://localhost:8000/")
    print("   - Admin Portal: http://localhost:8000/admin/dashboard/")
    print("   - Student Portal: http://localhost:8000/student/dashboard/")
    print("   - Django Admin: http://localhost:8000/admin/")
    
    print("\n🔑 Login credentials:")
    print("   - Username: admin")
    print("   - Password: admin123")
    
    print("\n🚀 Start the development server:")
    print("   python manage.py runserver")
    
    return True


if __name__ == "__main__":
    quick_start()

