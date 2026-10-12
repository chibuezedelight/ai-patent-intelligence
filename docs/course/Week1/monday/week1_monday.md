# Week 1, Monday: Build the Project Foundation

*AI Patent Intelligence Platform for III-V Semiconductor Lasers. Follow the steps in order, on Windows with PowerShell.*

## Before you start

- **What you will have at the end:** a GitHub project with a clear folder layout, a written project vision, a private Python workspace, and free access to the Espacenet patent data. No patent data is downloaded yet. That is Thursday.
- **Time needed:** about 3 to 4 hours. **Week 1 goal:** a first patent dataset (Thursday) and a short report (Friday). Today builds everything they need.
- **How to read each step:** *Why* tells you the reason. *Do this* is what to type or click. *It worked if* is your check. *If it goes wrong* lists the usual problems and the fix.
- **Where to type commands:** in VS Code, open the menu Terminal, then New Terminal. Always run commands from inside your project folder.

### Words you will see

| Word | Meaning |
|---|---|
| Terminal | The window where you type commands. |
| Repository (repo) | A project folder that Git tracks and GitHub stores online. |
| Commit | A saved snapshot of your files, with a short message. |
| Push | Sending your commits to GitHub. |
| PATH | The list of places Windows looks for programs. If a tool is not on it, the terminal says 'not recognized'. |
| Virtual environment | A private folder of Python libraries for this project only. |
| API key and secret | Like a username and password that let your program use a service. |
| .env file | A private text file for your key and secret. It never goes to GitHub. |

## Step 1: Install the five tools

**Why:** These tools run the whole project. You install them once. (Kind of step: setting up.)

**You need:** A Windows PC, internet, and permission to install programs.

**Do this**

- **Python 3.13**: python.org/downloads. On the first screen, tick **Add python.exe to PATH**, then click Install Now.
- **Git**: git-scm.com. Accept the default options.
- **VS Code**: code.visualstudio.com. After installing, open it and add the **Python** extension (square icon on the left).
- **Docker Desktop**: docker.com. Open it once after installing and leave it running.
- **PostgreSQL 18**: postgresql.org/download. Write down the password you set. You need it in Week 2.

**It worked if:** All five are installed. Close VS Code and open it again before Step 2.

**If it goes wrong**

- **The installer asks you to restart.** Fix: Restart the computer, then continue.

## Step 2: Check that every tool works

**Why:** Installed does not always mean usable. We test each tool from the terminal. (Kind of step: cross-checking.)

**You need:** The five tools from Step 1.

**Do this**


```powershell
python --version
git --version
docker --version
psql --version
```


**It worked if:** Each command prints a version number, for example Python 3.13.x.

**If it goes wrong**

- **'Python was not found; run without arguments to install from the Microsoft Store'** Fix: Python is missing or not on PATH. Reinstall it from python.org and tick Add python.exe to PATH. Then close and reopen VS Code.
- **'py' or 'python' is not recognized after installing** Fix: The terminal reads PATH only when it opens. Close and reopen VS Code.
- **'psql' is not recognized** Fix: PostgreSQL is installed but not on PATH. Test the fix first: in the terminal run  $env:Path += ";C:\Program Files\PostgreSQL\18\bin"  then psql --version. To keep it: Windows search, 'Edit environment variables for your account', select Path, Edit, New, paste C:\Program Files\PostgreSQL\18\bin, OK.
- **Docker cannot connect** Fix: Open Docker Desktop and wait until it says it is running.

## Step 3: Create your GitHub account and tell Git who you are

**Why:** GitHub stores your project online. Git needs your name to label your commits. You do this one time. (Kind of step: setting up.)

**You need:** An email address.

**Do this**

- Create a free account at github.com.

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global --list
```


**It worked if:** The last command shows your name and email.

**If it goes wrong**

- **Git says 'Please tell me who you are' when you commit** Fix: Run the two git config lines above, then commit again.

## Step 4: Create the repository and bring it to your computer

**Why:** The repository is the home of your project. Cloning copies it from GitHub to your PC. (Kind of step: initiating.)

**You need:** Git and your GitHub account.

**Do this**

- On github.com click **New repository**. Name: **ai-patent-intelligence**. Choose **Public**. Tick **Add a README file**. Click Create.
- Click the green **Code** button and copy the HTTPS link.

```powershell
cd Documents
git clone https://github.com/YOUR-USERNAME/ai-patent-intelligence.git
cd ai-patent-intelligence
code .
```


**It worked if:** VS Code opens your project and shows README.md in the file list. Your folder name may differ from the one in the screenshots. That is fine.

**If it goes wrong**

- **A sign-in window appears** Fix: Sign in to GitHub in the browser window. Then run the command again.
- **'git' is not recognized** Fix: Go back to Step 2.

## Step 5: Create the folders and starter files

**Why:** A clear layout keeps data, code, notes and reports apart. (Kind of step: setting up.)

**You need:** The terminal open in your project folder.

**Do this**


```powershell
New-Item -ItemType Directory -Force data/raw, data/processed, docs, notebooks, reports, src, tests
New-Item src/patent_data_collector.py -ItemType File
New-Item docs/project_vision.md -ItemType File
New-Item docs/workflow.md -ItemType File
```

- Your layout is now:

```text
ai-patent-intelligence/
  data/raw/            downloaded patent files (not uploaded to GitHub)
  data/processed/      cleaned data (not uploaded)
  docs/                project_vision.md, workflow.md
  notebooks/           analysis notebooks
  reports/             reports you produce
  src/                 patent_data_collector.py
  tests/               tests for your code
  README.md
```


**It worked if:** The VS Code file list shows all the folders.

**If it goes wrong**

- **Red text says the folder already exists** Fix: The -Force option makes this harmless. Continue.
- **Folders appear in the wrong place** Fix: You are in the wrong folder. Run  pwd  and  cd  to your project folder.

## Step 6: Write the README

**Why:** The README is the front page of your repository. Anyone opening it should know what the project is. (Kind of step: documentation.)

**You need:** Nothing new.

**Do this**

- Open README.md, replace its content with this, and save with Ctrl+S:

```markdown
# AI Patent Intelligence Platform

AI-powered patent intelligence platform for III-V semiconductor laser technology.
```


**It worked if:** Press Ctrl+Shift+V to preview. You see a big title and one sentence.

## Step 7: Write the project vision

**Why:** This is your business case. Every later technical choice should link back to it. (Kind of step: documentation.)

**You need:** The file docs/project_vision.md from Step 5.

**Do this**

- Open docs/project_vision.md. Use this layout and write your own answers under each heading, as plain text:

```markdown
# AI-Powered Patent Intelligence Platform for III-V Semiconductor Lasers

## 1. Why are III-V semiconductor lasers strategically important?
3-4 sentences: the physics advantage, what it makes possible, why patents matter.

## 2. Who would pay for patent intelligence?
- Corporate R&D teams
- Innovation managers
- Legal departments
- Investors

## 3. What business decisions should this platform support?
- Licensing
- Acquisitions
- R&D prioritization
- Competitor monitoring
- Finding potential clients

## 4. Which companies should we track initially?
- Coherent
- Lumentum
- Trumpf
- ams OSRAM
- Broadcom
- Nokia Bell Labs

## 5. What would make the platform valuable enough to use?
One paragraph.

## 6. Why use AI instead of hiring a patent analyst?
Cover: speed, scale, trend detection, competitor intelligence, innovation strategy.
```


**It worked if:** In the preview (Ctrl+Shift+V), headings look like headings and lists look like lists.

**If it goes wrong**

- **A line shows as a huge heading** Fix: A # at the start of a line makes a heading. Remove it from answer lines.
- **Text appears inside [ ] brackets** Fix: Brackets print as they are. Delete them.
- **List items run into one line** Fix: Put each item on its own line and start it with '- '.

## Step 8: Write the workflow

**Why:** This shows how raw patents turn into business decisions, so every script you write has a place in the chain. (Kind of step: documentation.)

**You need:** The file docs/workflow.md.

**Do this**

- Open docs/workflow.md and write 2 or 3 sentences for each stage:

```markdown
# Patent Intelligence Workflow

Patents -> Technology Trends -> Competitor Intelligence -> Business Decisions

## 1. Patents
Raw filings: title, assignee, inventors, abstract, classification codes, dates.

## 2. Technology Trends
Counting and grouping patents over time shows what is growing.

## 3. Competitor Intelligence
Linking trends to companies shows who invests where.

## 4. Business Decisions
Licensing, R&D priorities, acquisitions, and potential clients.
```


**It worked if:** The file previews cleanly.

## Step 9: Create the Python virtual environment

**Why:** It keeps this project's libraries separate from everything else, and lets anyone rebuild the same setup. (Kind of step: setting up.)

**You need:** Python from Step 2. The terminal open in your project folder.

**Do this**


```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install requests pandas python-dotenv
pip freeze > requirements.txt
pip list
```

- **requests** calls the patent API. **pandas** works with tables of data. **python-dotenv** reads your secrets from the .env file. The other packages in the list are helpers these three need.
- pip freeze creates requirements.txt for you. You do not need to make that file first.

**It worked if:** Your prompt starts with (.venv), and pip list shows requests, pandas and python-dotenv.

**If it goes wrong**

- **Red message about 'execution policies' when activating** Fix: Run once:  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned  then activate again.
- **Prompt has no (.venv)** Fix: The environment is not active. Run the activation line again before installing.
- **requirements.txt is empty or wrong** Fix: You ran pip freeze with the environment off. Activate it, then run pip freeze again.

## Step 10: Protect your secrets and data with .gitignore

**Why:** Your repository is public. .gitignore tells Git which files never to upload. We also add .gitkeep files because Git ignores empty folders. (Kind of step: protecting.)

**You need:** The terminal open in your project folder.

**Do this**

- Create a file named **.gitignore** in the project root (the name starts with a dot) with this content:

```text
.venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
.env

data/raw/*
!data/raw/.gitkeep
data/processed/*
!data/processed/.gitkeep
```

- Now add the placeholder files:

```powershell
New-Item data/raw/.gitkeep -ItemType File
New-Item data/processed/.gitkeep -ItemType File
New-Item notebooks/.gitkeep -ItemType File
New-Item reports/.gitkeep -ItemType File
New-Item tests/.gitkeep -ItemType File
git status
```


**It worked if:** git status lists .gitignore, requirements.txt, src, docs, data and the other folders. It does NOT list .venv.

**If it goes wrong**

- **.venv appears in git status** Fix: The file must be named exactly .gitignore (not .gitignore.txt) and sit in the project root.
- **Empty folders do not reach GitHub** Fix: Git skips empty folders. Each one needs a .gitkeep file.
- **The .gitkeep in data/raw is ignored** Fix: Use data/raw/* with the exception line !data/raw/.gitkeep, as shown.
- **.venv was already committed** Fix: Run  git rm -r --cached .venv  then commit.

## Step 11: Save your work to GitHub

**Why:** Committing saves a snapshot. Pushing sends it to GitHub. Think of sealing a box and posting it. (Kind of step: saving.)

**You need:** Git signed in to GitHub.

**Do this**


```powershell
git add .
git status
git commit -m "Add project structure, docs and environment setup"
git push
```


**It worked if:** Refresh your repository page on GitHub. You see data, docs, notebooks, reports, src, tests, .gitignore, README.md and requirements.txt. There is NO .venv folder.

**If it goes wrong**

- **Warning: LF will be replaced by CRLF** Fix: A harmless Windows notice. Ignore it.
- **'nothing to commit'** Fix: Nothing changed, or you are in the wrong folder. Check with git status.
- **push rejected (fetch first)** Fix: GitHub has newer changes. Run  git pull --rebase  then  git push.
- **Sign-in fails** Fix: Sign in to GitHub from VS Code (Accounts icon, bottom left), then push again.

## Step 12: Get your patent data access (EPO OPS)

**Why:** Espacenet data comes through the EPO's Open Patent Services. Your program needs a key and secret to use it. (Kind of step: setting up access.)

**You need:** A free EPO account. python-dotenv from Step 9. Step 10 must be done first, so .env is already ignored.

**Do this**

- Register at **developers.epo.org/user/register**. Confirm your email.
- Log in, create an app (any name, for example ai-patent-intelligence), and open its details. Copy the **Consumer Key** and **Consumer Secret**. Wait until the app shows as approved.
- In VS Code create a file named **.env** in the project root with these two lines (no quotes, no spaces around =):

```text
EPO_CONSUMER_KEY=paste_your_key_here
EPO_CONSUMER_SECRET=paste_your_secret_here
```

- Never share the key or secret in chats, screenshots or GitHub. Then check that Git ignores the file:

```powershell
Test-Path .env
git check-ignore -v .env
```


**It worked if:** The first command prints True. The second prints a line that mentions .gitignore and .env. git status does not list .env.

**If it goes wrong**

- **No confirmation email** Fix: Check spam, then register again.
- **The app is still pending** Fix: Wait for approval. Nothing else is blocked today.
- **git status lists .env** Fix: Stop. Check Step 10, then do not commit until .env disappears from the list.
- **You pushed the secret by mistake** Fix: Treat it as leaked. Create a new secret on developers.epo.org, update .env, and remove the old one from the repo.

## What your project should look like at the end of Monday

```text
ai-patent-intelligence/
  .venv/                      (your computer only, not on GitHub)
  .env                        (your computer only, holds your EPO key and secret)
  .gitignore
  README.md
  requirements.txt
  data/
    raw/.gitkeep
    processed/.gitkeep
  docs/
    project_vision.md
    workflow.md
  notebooks/.gitkeep
  reports/.gitkeep
  src/
    patent_data_collector.py  (empty for now, we fill it on Thursday)
  tests/.gitkeep
```

Compare this with the file list in VS Code. On GitHub you see the same, except .venv and .env, which stay on your computer. Folders can show as collapsed in VS Code, so click the arrows to open them.

## Monday is done when

- [ ] python, git, docker and psql all print versions
- [ ] The repository is on GitHub with README.md, docs, src, data, notebooks, reports, tests, .gitignore and requirements.txt
- [ ] docs/project_vision.md and docs/workflow.md are written and pushed
- [ ] The prompt shows (.venv) when you work, and requirements.txt exists
- [ ] EPO app is approved, .env holds the key and secret, and git status never lists .env
- [ ] No .venv folder and no secrets on GitHub
- [ ] Your folder list matches the layout above, including docs/workflow.md

## How it all fits together

Steps 1 to 4 gave you a working toolbox and a home for the project. Steps 5 to 8 set up the layout and wrote down what you are building and why. Steps 9 and 10 gave you a clean Python workspace and made sure secrets and data never reach GitHub. Step 12 gave you access to the data. On Thursday, your first script will use the .env key to ask the EPO for patents and save them into data/raw. Without today, that script would have no tools, no safe place to live and no data access. That first dataset is the main goal of Week 1.

## Moving forward

Next: Thursday. Connect Python to the EPO API and collect your first 50 to 100 III-V laser patents into data/raw.
