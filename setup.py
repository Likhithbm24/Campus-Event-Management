"""
Setup script for Campus Event Management Platform.
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


def setup_environment():
    """Set up the development environment."""
    print("🚀 Setting up Campus Event Management Platform...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        return False
    
    # Create virtual environment
    if not run_command("python -m venv venv", "Creating virtual environment"):
        return False
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/MacOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        return False
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_content = """# Django Settings
SECRET_KEY=django-insecure-change-me-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_NAME=campus_events
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis Settings
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
"""
        env_file.write_text(env_content)
        print("✅ .env file created")
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print("✅ Logs directory created")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Set up PostgreSQL database:")
    print("   createdb campus_events")
    print("2. Run migrations:")
    print("   python manage.py migrate")
    print("3. Create sample data (optional):")
    print("   python manage.py create_sample_data")
    print("4. Start the development server:")
    print("   python manage.py runserver")
    print("\n🌐 Access the application:")
    print("   - Home: http://localhost:8000/")
    print("   - Admin Portal: http://localhost:8000/admin/dashboard/")
    print("   - Student Portal: http://localhost:8000/student/dashboard/")
    
    return True


if __name__ == "__main__":
    setup_environment()

