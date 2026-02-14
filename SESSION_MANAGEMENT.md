# Smart Library System - Session Management

## Automatic Session Closure Features

### 1. Cross-Day Session Handling
When a student has an open "IN" session from a previous day and taps their RFID card again:
- The system automatically closes the previous day's session with an "OUT" entry
- Then proceeds to create a new "IN" entry for the current day

### 2. Daily Auto-Closure at 6 PM
Every day at 6 PM, the system automatically closes all open "IN" sessions that haven't been manually checked out.

## Setup Instructions

### Windows Task Scheduler Setup

1. Open Task Scheduler (search for "Task Scheduler" in Windows)
2. Click "Create Basic Task"
3. Name: "Library Session Auto-Close"
4. Trigger: Daily at 6:00 PM
5. Action: Start a program
6. Program/script: `C:\Users\Keith\Desktop\smart_library\close_sessions.bat`
7. Click Finish

### Manual Testing

To test the auto-closure manually:
```bash
cd C:\Users\Keith\Desktop\smart_library
.venv\Scripts\activate
cd backend
python manage.py close_sessions
```

## How It Works

### RFID Tap Logic
1. Student taps RFID card
2. System checks last attendance log
3. If last action was "IN" from today → Go to rating page (checkout)
4. If last action was "IN" from previous day → Auto-create "OUT" for yesterday, then go to reason page (new checkin)
5. If last action was "OUT" or no logs → Go to reason page (checkin)

### Daily Auto-Closure
- Runs every day at 6 PM via Windows Task Scheduler
- Finds all students with "IN" actions from the current day that don't have corresponding "OUT" actions
- Creates "OUT" entries for all open sessions
- Logs the action to `session_closure.log`

## Benefits

- **No forgotten checkouts**: Students can't stay "IN" indefinitely
- **Accurate attendance**: Previous sessions are properly closed
- **Clean daily resets**: Fresh start every morning
- **User-friendly**: Seamless experience even if students forget to checkout