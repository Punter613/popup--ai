#!/bin/bash

# ----------------------------
# Multi-Project Capacitor APK Builder
# ----------------------------
# Usage: run from a parent folder containing multiple Capacitor projects
# ----------------------------

set -e  # stop on error

PARENT_DIR=$(pwd)
BUILD_DIR="$PARENT_DIR/builds"
mkdir -p "$BUILD_DIR"

echo "🚀 Starting multi-project build in: $PARENT_DIR"

# Loop through each subfolder
for PROJECT in "$PARENT_DIR"/*; do
    [ -d "$PROJECT" ] || continue  # skip non-folders
    echo "----------------------------------------"
    echo "⚡ Processing project: $(basename "$PROJECT")"
    cd "$PROJECT"

    # 1️⃣ Ensure local git repo exists (optional)
    if [ ! -d ".git" ]; then
        git init
        git add .
        git commit -m "Initial commit"
        echo "✅ Local git repo initialized"
    else
        echo "✅ Local git repo exists"
    fi

    # 2️⃣ Ensure Android platform exists
    if [ ! -d "android" ]; then
        echo "⚡ Android platform not found, adding..."
        npx cap add android
    else
        echo "✅ Android platform already exists"
    fi

    # 3️⃣ Build APK (debug)
    echo "⚡ Building APK..."
    cd android
    ./gradlew assembleDebug

    # 4️⃣ Copy APK to parent builds folder
    APK_PATH=$(find ./app/build/outputs/apk/debug -name "*.apk" | head -n 1)
    if [ -f "$APK_PATH" ]; then
        cp "$APK_PATH" "$BUILD_DIR/$(basename "$PROJECT")-$(basename "$APK_PATH")"
        echo "✅ APK copied to $BUILD_DIR/$(basename "$PROJECT")-$(basename "$APK_PATH")"
    else
        echo "❌ APK not found for project $(basename "$PROJECT")"
    fi

    # Return to parent dir for next project
    cd "$PARENT_DIR"
done

echo "🎉 All projects processed! Check the builds folder: $BUILD_DIR"
