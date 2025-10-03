# Windows Setup Guide

**Quick setup guide specifically for Windows users.**

## 🚀 Automated Setup (Easiest)

### Option 1: Run Setup Script

Just double-click `setup_windows.bat` or run:

```cmd
setup_windows.bat
```

This will:
- ✅ Create virtual environment
- ✅ Install all packages
- ✅ Setup Supabase database
- ✅ Create admin user
- ✅ Run tests

**Time**: 5-10 minutes (depending on internet speed)

---

## 🔧 Manual Setup (Step-by-Step)

### Step 1: Create Virtual Environment

```cmd
python -m venv venv
```

**What it does**: Creates isolated Python environment in `venv` folder

---

### Step 2: Activate Virtual Environment

```cmd
venv\Scripts\activate
```

**You should see**: `(venv)` appear at start of command prompt

**If using PowerShell instead of CMD:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

---

### Step 3: Upgrade pip

```cmd
python -m pip install --upgrade pip
```

---

### Step 4: Install Django and Core Packages

```cmd
pip install Django==4.2.7
pip install djangorestframework==3.14.0
pip install python-decouple==3.8
pip install librouteros==3.2.1
pip install django-crispy-forms==2.1
pip install crispy-tailwind==0.5.0
pip install celery==5.3.4
pip install redis==5.0.1
pip install requests==2.31.0
pip install python-dateutil==2.8.2
pip install pytz==2023.3
```

---

### Step 5: Install PostgreSQL Driver

```cmd
pip install psycopg2-binary
```

**If this fails** (common on Python 3.13), try:
```cmd
pip install psycopg2
```

**Still fails?** You can use SQLite for development:
- Skip this step
- In `.env` file, use:
  ```env
  DATABASE_ENGINE=django.db.backends.sqlite3
  DATABASE_NAME=db.sqlite3
  ```

---

### Step 6: Setup Supabase Database

```cmd
python setup_supabase.py
```

This creates `.env` file and runs migrations.

**If this fails:**
```cmd
# Create .env manually
copy env_supabase_template.txt .env

# Run migrations manually
python manage.py migrate
```

---

### Step 7: Create Admin User

```cmd
python setup_admin.py
```

Creates admin user: `admin` / `admin123`

---

### Step 8: Start Server

```cmd
python manage.py runserver
```

**Visit**: http://127.0.0.1:8000

---

## ✅ Verify Installation

```cmd
python check_setup.py
```

Should show all checks passing ✓

---

## 🎯 Quick Commands Reference

### Always Activate Virtual Environment First!

```cmd
# Activate venv (do this every time you open new terminal)
venv\Scripts\activate

# You should see (venv) at start of prompt
```

### Common Commands

```cmd
# Start server
python manage.py runserver

# Run tests
python run_tests.py

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Access Django shell
python manage.py shell
```

---

## 🐛 Common Windows Issues

### Issue 1: "python not recognized"

**Solution**: Install Python from https://www.python.org/downloads/

✅ Check "Add Python to PATH" during installation

---

### Issue 2: Virtual environment won't activate

**CMD Solution:**
```cmd
venv\Scripts\activate.bat
```

**PowerShell Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

---

### Issue 3: psycopg2-binary fails to install

**This is common on Windows with Python 3.13!**

**Solution A**: Install prebuilt wheel
```cmd
pip install psycopg2-binary --only-binary :all:
```

**Solution B**: Use alternative package
```cmd
pip install psycopg2
```

**Solution C**: Use SQLite instead (for development)
```cmd
# Skip psycopg2 installation
# In .env file use:
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
```

---

### Issue 4: "Defaulting to user installation"

This means virtual environment is **not activated**.

**Solution:**
```cmd
# Activate first!
venv\Scripts\activate

# Then install
pip install -r requirements.txt
```

---

### Issue 5: Port 8000 already in use

**Find and kill process:**
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

---

### Issue 6: Can't connect to Supabase

**Check internet connection:**
```cmd
ping db.seuzxvthbxowmofxalmm.supabase.co
```

**Test port:**
```cmd
Test-NetConnection -ComputerName db.seuzxvthbxowmofxalmm.supabase.co -Port 5432
```

---

## 📦 All-in-One Installation

Copy and paste this (make sure you're in the `mikrotikvpn` folder):

```cmd
python -m venv venv && venv\Scripts\activate && python -m pip install --upgrade pip && pip install Django==4.2.7 djangorestframework==3.14.0 python-decouple==3.8 librouteros==3.2.1 django-crispy-forms==2.1 crispy-tailwind==0.5.0 && pip install psycopg2-binary && python setup_supabase.py && python setup_admin.py && python manage.py runserver
```

---

## 🎬 Video Guide (Text Version)

```
┌─────────────────────────────────────────┐
│  STEP-BY-STEP VISUAL GUIDE              │
└─────────────────────────────────────────┘

1. Open Command Prompt
   - Press Win + R
   - Type: cmd
   - Press Enter

2. Navigate to project
   > cd C:\Users\A\Desktop\mikrotikvpn

3. Create virtual environment
   > python -m venv venv
   [Wait 30 seconds]

4. Activate it
   > venv\Scripts\activate
   [You'll see (venv) appear]

5. Install packages
   > pip install Django djangorestframework python-decouple
   [Wait 1-2 minutes]

6. Install PostgreSQL driver
   > pip install psycopg2-binary
   [If fails, try: pip install psycopg2]

7. Setup database
   > python setup_supabase.py
   [Creates .env, runs migrations]

8. Create admin
   > python setup_admin.py
   [admin / admin123]

9. Start server
   > python manage.py runserver
   [Opens on http://127.0.0.1:8000]

10. Open browser
    [Visit http://127.0.0.1:8000]
    [Login with admin / admin123]

✓ DONE!
```

---

## 🆘 Still Having Problems?

### Check Your Setup

```cmd
python --version
pip --version
python -c "import sys; print(sys.executable)"
```

### Get Help

1. Run diagnostic: `python check_setup.py`
2. Check for errors in output
3. Share error messages

---

## 🎉 Success Checklist

- [x] Virtual environment created
- [x] Virtual environment activated (see `(venv)`)
- [x] Django installed
- [x] psycopg2 installed (or using SQLite)
- [x] Database migrated
- [x] Admin user created
- [x] Server starts successfully
- [x] Can access http://127.0.0.1:8000
- [x] Can login with admin/admin123

**All checked?** You're ready to start building! 🚀

---

## 💡 Pro Tips

1. **Always activate venv first**: `venv\Scripts\activate`
2. **One terminal per session**: Keep one terminal open for the server
3. **Use CMD not PowerShell**: CMD is simpler for Django
4. **Check for (venv)**: Make sure it's always visible before running commands

---

**Next Steps:**
- Follow [QUICKSTART.md](QUICKSTART.md) for first-time configuration
- See [TESTING_GUIDE.md](TESTING_GUIDE.md) for testing instructions
- Read [README.md](README.md) for complete documentation

