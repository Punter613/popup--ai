#!/bin/bash
set -e

echo "--- Automated Capacitor APK Builder Setup (No Root / No Sudo) ---"
echo "This will guide you through setting up GitHub and a build workflow for your project."
echo "Run this from inside your 'popup--ai' project directory."
echo "Press Enter to continue..."
read

# --- Step 1: Check for GitHub CLI ---
echo "--- Step 1: Checking for GitHub CLI (gh)... ---"
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found."
    echo "👉 Install it manually before running this script:"
    echo "   https://cli.github.com/manual/installation"
    exit 1
else
    echo "✅ GitHub CLI found."
fi

# --- Step 2: Log in to GitHub ---
echo "--- Step 2: Logging in to GitHub... ---"
gh auth login

# --- Step 3: Initialize Git and Create Repository ---
echo "--- Step 3: Creating GitHub repository 'popup--ai'... ---"
git init

if [ -z "$(git status --porcelain)" ]; then
    echo "No uncommitted changes detected."
else
    git add .
    git commit -m "Initial commit"
fi

gh repo create popup--ai --source=. --public --push

# --- Step 4: Create the GitHub Actions workflow ---
echo "--- Step 4: Creating GitHub Actions workflow file... ---"
mkdir -p .github/workflows

cat <<'EOF' > .github/workflows/build.yml
name: Build Capacitor Android APK

on:
  push:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm install

      - name: Build web assets
        run: npm run build

      - name: Sync Capacitor project
        run: npx cap sync android

      - name: Grant execute permission for gradlew
        run: chmod +x ./android/gradlew

      - name: Build debug APK
        run: ./android/gradlew -p ./android assembleDebug

      - name: Upload APK artifact
        uses: actions/upload-artifact@v4
        with:
          name: app-debug-apk
          path: android/app/build/outputs/apk/debug/app-debug.apk
EOF

echo "✅ Workflow file created."

# --- Step 5: Push the workflow to GitHub ---
echo "--- Step 5: Pushing workflow to GitHub... ---"
git add .github/workflows/build.yml
git commit -m "Add automated APK build workflow"
git push

echo "--- ✅ All Done! ---"
echo "Your project 'popup--ai' is live on GitHub."
echo "An automated APK build has already started."

# prevent-env-push — do not commit any .env
if git diff --cached --name-only | grep -q "\.env"; then
    echo "❌ Detected a .env file staged for commit! Commit aborted."
    exit 1
fi
