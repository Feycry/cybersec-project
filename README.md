# Cybersecurity Base 2025 - Project 1: Unsafe Notes App

**Link**: placeholder

This project is a Django-based personal notes app (very original I know :D) that demonstrates common web security vulnerabilities from the OWASP Top 10 list (2021). This project was made for completing a module of the Cyber Security Base MOOC by the University of Helsinki.
## Installation Instructions

### Setup Instructions

- Clone the repo to your local machine
- Navigate to the project root directory:
- Create and activate virtual environment:
```bash

python3 -m venv venv
source venv/bin/activate

```
- Install the required packages:
```bash

python3 -m pip install django "selenium<4" "urllib3<2" beautifulsoup4 requests

```
- Run the app:
```bash

python3 manage.py runserver

```
- Access the application at http://127.0.0.1:8000/

### Test Users

The repository contains a sample database. In addition to a few sample notes, two test users are provided:
```bash

admin:admin

user:user

```

### Database

You can reset the database by deleting it and then running
```bash

python3 manage.py migrate

```
You can add users with
```bash

python3 manage.py createsuperuser

```

## Security Flaws

This application contains five purposefully implemented security vulnerabilities. Each flaw demonstrates common security issues commonly found in web applications. Screenshots of each flaw before and after fixing can be found in the screenshots folder.

### FLAW 1: A01 (Broken Access Control)

**Source**: placeholder

The application suffers from a broken access control vulnerability. Any user can navigate to `http://127.0.0.1:8000/notes/{id}/delete/` to delete any note they know the id of. Finding out a note's id is trivial since they are simply sequential, starting from one.

This is problematic because the user might not be the owner of the note they are deleting, essentially allowing any user to remove notes they should not have access to.
#### Fix:

Changing one line of code fixes the issue.

`get_object_or_404(Note, id=note_id)`

The issue can be mitigated simply by checking that the note being deleted belongs to the currently logged in user. This can be achieved simply by checking that the notes owner field matches request.user.

`get_object_or_404(Note, id=note_id, owner=request.user)`
  

### FLAW 2: A02 (Cryptographic Failure)

**Source**: placeholder

The application includes a severe vulnerability where the passwords for each user are stored in plain text. This is done by replacing Django's default functions for creating and checking passwords. The way this happens in the app doesn't really resemble any real-world scenario, but is still mostly analogous to, for example, an insecure custom user model being used in models.py. The unrealistic monkey wrench approach was used to keep the demonstration contained to a single file where it is easily toggled on and off.

When enabled, by looking into the database with a viewer or visiting the debug page (at `http://127.0.0.1:8000/debug/`) from flaw 5, the passwords of each user can be seen and read as plain text. This would be catastrophic in the event of a data breach where the database falls into the wrong hands.

#### Fix:

The fix is very straightforward. Instead of brainlessly disabling hashing, we comment out the dangerous password override. This enables Django's default password hashing which uses PBKDF2 with SHA256. This means our passwords are stored in a cryptographically secure fashion. The application should rely on Django's built-in authentication that properly hashes and salts passwords with industry standard algorithms.

### FLAW 3: A03 (Injection)

**Source**: placeholder

The application has a classic SQL injection vulnerability in the functionality for searching notes. The query for the search is constructed using string formatting without any sort of input sanitization or parameterization. The query is simply made from user input in the search field using f-string.

For example, the vulnerability can be exploited by typing `%' OR '1'='1' --` into the search field on the notes page. This is equivelant to visiting `http://127.0.0.1:8000/notes/?search=%25%27+OR+%271%27%3D%271%27+--`. Doing so reveals every note of every user in the search results. Other exploits could be crafted to, for example, drop tables from the database of to reveal user information.

#### Fix:

Fixing the issue is very straightforward. We could use an SQL query with templates, but it's even simpler just to replace the query altogether with Django's ORM, which automatically handles parameterization. This fully prevents any injection attacks, relying on Django's built-in protections.

### FLAW 4: A07 (Identification and Authentication Failures)

**Source**: placeholder

The application's session management is flawed. Currently, the cookie keeping the user logged in expires after a year, which is not in line with common security practices. The provided screenshots show the difference in the cookies duration between the current and the fixed implementation. Such an extended lifetime increases the window of opportunity for session hijacking and unauthorised access from shared computers.

#### Fix:

The issue can be fixed by removing or commenting out insecure configuration lines and instead relying on Django's default settings.


### FLAW 5: A05 (Security Misconfiguration)

**Source**: placeholder

The application provides an insecure debug endpoint without any sort of authentication needed. The page can be seen over at `http://127.0.0.1:8000/debug/`. The page lists the secret key, debug mode status, all user information including passwords and every note in the system. Even with authentication, having a page that shows the secret key and user passwords is pretty much never a good idea.

#### Fix:

The issue is addressed by entirely removing the page from views or simply by removing the url mapping from urls.py. Debugging functionality should never be exposed in any sort of production environment.