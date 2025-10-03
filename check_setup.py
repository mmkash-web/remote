#!/usr/bin/env python
"""
Setup verification script for MikroTik Billing System.
Checks if all requirements are met and helps troubleshoot issues.
"""
import sys
import os

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python version: {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"✗ Python version: {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def check_pip():
    """Check if pip is installed."""
    try:
        import pip
        print(f"✓ pip is installed (version {pip.__version__})")
        return True
    except ImportError:
        print("✗ pip is not installed")
        return False

def check_venv():
    """Check if running in virtual environment."""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if in_venv:
        print("✓ Running in virtual environment")
        return True
    else:
        print("⚠ Not running in virtual environment (recommended)")
        return False

def check_django():
    """Check if Django is installed."""
    try:
        import django
        print(f"✓ Django is installed (version {django.get_version()})")
        return True
    except ImportError:
        print("✗ Django is not installed")
        print("  Run: pip install -r requirements.txt")
        return False

def check_librouteros():
    """Check if librouteros is installed."""
    try:
        import librouteros
        print("✓ librouteros is installed (MikroTik API library)")
        return True
    except ImportError:
        print("✗ librouteros is not installed")
        print("  Run: pip install -r requirements.txt")
        return False

def check_database():
    """Check if database is configured."""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrotik_billing.settings')
        import django
        django.setup()
        
        from django.db import connection
        connection.ensure_connection()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        print("  Run: python manage.py migrate")
        return False

def check_migrations():
    """Check if migrations are applied."""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrotik_billing.settings')
        import django
        django.setup()
        
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connection
        
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if not plan:
            print("✓ All migrations are applied")
            return True
        else:
            print(f"⚠ {len(plan)} migration(s) need to be applied")
            print("  Run: python manage.py migrate")
            return False
    except Exception as e:
        print(f"⚠ Could not check migrations: {str(e)}")
        return False

def check_superuser():
    """Check if superuser exists."""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrotik_billing.settings')
        import django
        django.setup()
        
        from django.contrib.auth.models import User
        if User.objects.filter(is_superuser=True).exists():
            print("✓ Superuser exists")
            return True
        else:
            print("⚠ No superuser found")
            print("  Run: python setup_admin.py")
            return False
    except Exception as e:
        print(f"⚠ Could not check superuser: {str(e)}")
        return False

def check_directories():
    """Check if required directories exist."""
    dirs = ['static', 'media', 'staticfiles']
    all_exist = True
    
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name}/ directory exists")
        else:
            print(f"⚠ {dir_name}/ directory missing (will be created)")
            try:
                os.makedirs(dir_name)
                print(f"  Created {dir_name}/ directory")
            except Exception as e:
                print(f"  Could not create {dir_name}/: {str(e)}")
                all_exist = False
    
    return all_exist

def check_env_file():
    """Check if .env file exists."""
    if os.path.exists('.env'):
        print("✓ .env file exists")
        return True
    else:
        print("⚠ .env file not found (using defaults)")
        print("  Create .env file for production settings")
        return False

def check_redis():
    """Check if Redis is available (for Celery)."""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Redis is running (for Celery tasks)")
        return True
    except ImportError:
        print("⚠ redis-py not installed (optional)")
        return False
    except Exception:
        print("⚠ Redis server not running (optional, needed for Celery)")
        return False

def check_optional_dependencies():
    """Check optional dependencies."""
    optional = {
        'celery': 'Background task processing',
        'crispy_forms': 'Form rendering',
        'rest_framework': 'API framework',
    }
    
    for package, description in optional.items():
        try:
            __import__(package.replace('_', '-'))
            print(f"✓ {package} is installed ({description})")
        except ImportError:
            print(f"⚠ {package} not installed ({description})")

def main():
    """Run all checks."""
    print_header("MikroTik Billing System - Setup Check")
    print("\nChecking your installation...\n")
    
    results = []
    
    print_header("Core Requirements")
    results.append(check_python_version())
    results.append(check_pip())
    check_venv()  # Warning only, not critical
    
    print_header("Python Packages")
    results.append(check_django())
    results.append(check_librouteros())
    
    print_header("Database")
    results.append(check_database())
    check_migrations()  # Warning only
    check_superuser()  # Warning only
    
    print_header("File System")
    check_directories()  # Warning only
    check_env_file()  # Warning only
    
    print_header("Optional Components")
    check_redis()  # Optional
    check_optional_dependencies()  # Optional
    
    # Summary
    print_header("Summary")
    
    if all(results):
        print("\n✓ All critical checks passed!")
        print("\nYou're ready to start the server:")
        print("  python manage.py runserver")
        print("\nThen visit: http://127.0.0.1:8000")
    else:
        print("\n✗ Some critical checks failed.")
        print("\nPlease fix the issues above before starting the server.")
        print("\nQuick fix commands:")
        print("  pip install -r requirements.txt")
        print("  python manage.py migrate")
        print("  python setup_admin.py")
    
    print("\n" + "="*60)
    print()

if __name__ == '__main__':
    main()

