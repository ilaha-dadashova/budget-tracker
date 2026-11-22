# 💰 Budget Tracker

A personal budget tracker that runs in your web browser. You can add expenses,
see charts of where your money goes, and set a monthly budget. Everything is
saved on your own computer, so nothing goes to the internet.

---

## 🚀 How to install and run it (Windows)

### Step 1: Install Python (only once)

Python is the programming language the app is written in. Your computer needs
it to run the app.

1. Go to **https://www.python.org/downloads/** and click the big yellow
   **"Download Python 3.x"** button.
2. Open the file you downloaded.
3. ⚠️ **Important:** on the first screen of the installer, tick the box
   **"Add python.exe to PATH"** at the bottom. If you skip this, the app can't
   find Python.
4. Click **"Install Now"** and wait until it says *Setup was successful*.

### Step 2: Start the app

1. Open the folder `C:\Users\ASUS\budget_tracker` in File Explorer.
2. **Double-click `run.bat`.**
3. A black window opens. **The first time only**, it downloads the tools
   the app needs (1–3 minutes, needs internet).
4. Your web browser then opens the app at **http://localhost:8501** 🎉

> 💡 **Keep the black window open** while you use the app. When you're done,
> close the black window to stop the app. To use it again, double-click
> `run.bat`; later starts are fast.

If Windows shows a blue box saying *"Windows protected your PC"*, click
**More info → Run anyway**. Windows shows this for any file it hasn't seen before.

---

## 🧭 Using the app

| What you want | Where to find it |
|---|---|
| Add an expense | **➕ Add an Expense**: type a name, pick a category, enter the amount, click **Add Expense** |
| See this month's total | The big number at the top |
| Check your budget | The progress bar at the top: 🟢 green = fine, 🟡 yellow = over 80%, 🔴 red = over budget |
| Change your budget | Sidebar on the left → **🎯 Monthly Budget** (starts at $2,000) |
| Filter by category or date | Sidebar on the left → **🔎 Filters** |
| Delete a mistake | Under the table → **🗑️ Delete an expense** |
| Remove the example data | Sidebar → **🧹 Sample Data → Remove sample data** |
| Export to Excel | **⬇️ Download as spreadsheet (CSV)**, which opens in Excel |

The first time you open the app, it is filled with **sample expenses** so you
can see how it looks. Remove them from the sidebar when you're ready to track
your own spending.

---

## 📁 What's in this folder

| File | What it does |
|---|---|
| `run.bat` | Double-click this to start the app |
| `app.py` | The web page: the form, charts, table and sidebar |
| `database.py` | Saves and loads your expenses |
| `budget.db` | **Your data.** Created the first time you run the app. Back up this file to keep your expenses safe. |
| `requirements.txt` | List of tools the app needs (installed automatically) |
| `.streamlit/config.toml` | Colors and settings for the page |
| `.venv/` | Created automatically during setup. You don't need to touch it. |

---

## 🛠️ Something not working?

- **"Python is not installed yet"** → Do Step 1 again and make sure you tick
  **"Add python.exe to PATH"**. Restart your computer afterwards.
- **Browser didn't open** → Open your browser yourself and go to
  `http://localhost:8501`.
- **Want to start completely fresh?** → Close the app, delete `budget.db`, and
  run `run.bat` again. ⚠️ This deletes all your expenses.
- **Setup failed halfway** → Delete the `.venv` folder and double-click
  `run.bat` again.

---

## 🧑‍💻 For the curious: running it by hand

If you'd like to try the command line, open **PowerShell** in this folder and run:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Then open http://localhost:8501.
