# ============================================================
#  VHS Tape — Generate a new project from
#  aws-cdk-python-lambda-copier-template
#  Usage: vhs demo.tape
# ============================================================

Output demo.gif

# --- Appearance ---
Set Theme    "Dracula"
Set FontSize 14
Set Width    900
Set Height   550
Set Margin   20
Set MarginFill "#282a36"
Set BorderRadius 8
Set WindowBar "Colorful"
Set TypingSpeed 60ms

# ============================================================
# STEP 0 — Hidden setup (not shown in the GIF)
# ============================================================
Hide
Type "clear"
Enter
Sleep 300ms
Show

# ============================================================
# STEP 1 — Generate the project
# ============================================================
Type "# Step 1: Generate a new project from the template"
Enter
Sleep 500ms

Type "copier copy gh:myarik/aws-cdk-python-lambda-copier-template my-lambda-service"
Sleep 400ms
Enter
Sleep 2500ms

# Answer the Copier prompts
# project_name
Enter
Sleep 800ms

# author_name
Enter
Sleep 800ms

# author_email
Enter
Sleep 800ms

# copyright_holder  (accept default = author name)
Enter
Sleep 800ms

# copyright_date  (accept default = 2026)
Enter
Sleep 800ms

# copyright_license (accept default = MIT)
Enter
Sleep 2500ms

Type "clear"
Enter
Sleep 300ms

# ============================================================
# STEP 2 — Explore the generated project
# ============================================================
Type "# Step 2: Explore the generated project"
Enter
Sleep 500ms

Type "cd my-lambda-service && tree -L 2"
Sleep 400ms
Enter
Sleep 2500ms

Type "clear"
Enter
Sleep 300ms

# ============================================================
# STEP 3 — Set up the virtual environment
# ============================================================
Type "# Step 3: Create venv and install dependencies"
Enter
Sleep 500ms

Type "make dev"
Sleep 400ms
Enter
Sleep 5s

Type "clear"
Enter
Sleep 300ms


# ============================================================
# STEP 4 — Deploy (show command only — requires AWS credentials)
# ============================================================
Type "# Step 4: Deploy to AWS (requires configured AWS credentials)"
Enter
Sleep 500ms

Type "make deploy"
Enter
Sleep 800ms
# Don't press Enter — just show the command
Sleep 3s

# Final pause for the viewer
Sleep 2s
