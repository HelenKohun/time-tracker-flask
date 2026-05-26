# Time Tracker

#### Description:

Time Tracker is a web application designed to help users **manage tasks, track time spent, evaluate satisfaction, and plan long-term work.** The app combines task management with daily reflection and visual analytics to provide meaningful insights into productivity.
By allowing users to vizualize their task completion patterns and plan thier workload effectively, Time Tracker supports better personal time management and self-reflection on task efficiency and satisfaction.

## Features

- **User Authentication:**
- Secure registration and login
- Password hashing using `werkzeug.security`
- Session-based authentication to keep users logged in safely

- **Task Management:**
- Create new tasks with name, type, and planned hours
- Delete tasks when no longer needed
- Mark tasks as completed with recorded satisfaction and time spent
- **Task Completion Tracking:**
- Record actul time spent on each task
- Rate satisfaction from 1 to 5
- Only one progress entry per task per day, enforced by a UNIQUE database constraint
- **Planner:**
- Plan long-term tasks and automatically calculate the number of days required
- Distribute hours per day for better workload management
- Generate start and end dates dynamically
- **Analytics Dashboard:**
- Visualize satisfaction and time spent over time
- Interactive charts powered by Chart.js for easy interpretation of daily performance
- **Secure:**
- User data isolation ensures users can only access their own tasks
- Access control for all routes using `login_required` decorator
- Database constraints to prevent inconsistent or duplicate data

## Technologies

- **Backend:** Python, Flask, CS50 SQL
- **Frontend:** HTML, CSS, JavaScript, Chart.js
- **Database:** SQLite
- **Security:**
- Password hashing (`werkzeug.security`)
- Session-based authentication
- UNIQUE constraint in `daily_progress` to prevent duplication entries

## Project Structure

/time-tracker

│
|- /templates # HTML templates
│ |- layout.html # Base layout for consistent header/footer
│ |- index.html # Main dashboard displaying task progress and charts
│ |- login.html # User login page
│ |- register.html # User registration page
│ |- tasks.html # Task management page with forms, task list, and completion modal
│ |- planner.html # Planner page for long-term tasks with daily distribution
│ |- apology.html # Error page for user-friendly error messages
│
|- /static # CSS, images, favicon
│ |- styles.css # Main styles for dashboard and planner
│ |- login.css # Login page styles
│ |- register.css # Registration page styles
│ |- favicon.ico # Website favicon
| |- photo_authors.txt # Photo credits for images used
│
|- app.py # Main Flask application containing routes and core logic
|- helpers.py # Helper functions such as login_required decorator
|- requirements.txt # Python dependencies required to run the project
|- time_tracker.db # SQLite database storing all user, task, planner, and progress data
|- README.md # Project documentation

## How it works

### Authentication & Sessions

- Users must register or log in to access the application.
- Authentication is handled via server-side sessions.
- All protected routes use a `login_required` decorator.
- Navigation elements are rendered conditionally based on login status.
- This data is saved in the `users` table.

### Task Lifecycle

1. Creating a task

- The user provides:
- task name
- task type
- planned time (in hours)
- Tasks are stored per user and remain active until completed or deleted.
- This data is saved in the `tasks` table.

2. Completing a task

- Tasks are marked as completed through a modal window.
- The user records:
- satisfaction score (1–5)
- time spent (hours)
- This data is saved in the `daily_progress` table.

> [!IMPORTANT]
> Each user can only create one progress entry per task per day, enforced by a database **UNIQUE** constraint.

### Daily Progress Tracking

- Every completion entry stores:
- date
- satisfaction score
- time spent
- These entries form the basis for analytics and visualizations.

### Planner Logic (Long-term Tasks)

1. The user selects a task and specifies hours per day.
2. The system calculates:

- total days needed (rounded up)
- daily hour distribution

3. The plan is saved in the `planner` table.
4. Start and end dates are calculated dynamically.

This allows users to break down large tasks into manageable daily workloads.

### Analytics & Visualization

- The dashboard aggregates:
- satisfaction scores
- time spent
- Data is grouped by date and task.
- Results are visualized using interactive bar charts.
- This helps users reflect on productivity and workload balance.

## Error Handling

- All forms validate required fields and correct value types
- Tasks and planner inputs are validated
- Errors show a user-friendly apology page
- All routes check that the task belongs to the logged-in user

## Possible improvements

- Responsive mobile design
- Flash messages for better UX
- More detailed charts and graphs
- Advanced analytics (weekly/monthly summaries)
- Task editing and history view

## Acknowledgments

I used ChatGPT as a helper during this project.

## Author

Helen Kohun
