#!/bin/bash

# ================================================
# Push Socializer 1.0 to GitHub
# ================================================

echo "=================================================="
echo "🚀 Pushing Socializer 1.0 to GitHub"
echo "=================================================="

# GitHub details
GITHUB_USERNAME="LeroyLeeRoySheep"
REPO_NAME="Socializer1.0"
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo ""
echo "Repository: ${REPO_URL}"
echo ""

# Check if remote already exists
if git remote | grep -q "origin"; then
    echo "⚠️  Remote 'origin' already exists, removing..."
    git remote remove origin
fi

# Add GitHub remote
echo "1️⃣  Adding GitHub remote..."
git remote add origin "${REPO_URL}"
echo "   ✅ Remote added"

# Verify remote
echo ""
echo "2️⃣  Verifying remote..."
git remote -v

# Push to main branch
echo ""
echo "3️⃣  Pushing to GitHub..."
echo "   This will push all commits to: ${REPO_URL}"
echo ""
read -p "   Press ENTER to continue or Ctrl+C to cancel..."

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "   ✅ Code pushed successfully!"
    
    # Create release tag
    echo ""
    echo "4️⃣  Creating release tag v1.0.0..."
    git tag -a v1.0.0 -m "Socializer 1.0 - Stable Local Version"
    git push origin v1.0.0
    
    echo ""
    echo "=================================================="
    echo "✅ SUCCESS!"
    echo "=================================================="
    echo ""
    echo "Your repository is now live at:"
    echo "🔗 ${REPO_URL%.git}"
    echo ""
    echo "Next steps:"
    echo "1. Visit your repository on GitHub"
    echo "2. Go to 'Releases' → 'Create a new release'"
    echo "3. Select tag: v1.0.0"
    echo "4. Title: 'Socializer 1.0 - Stable Local Version'"
    echo "5. Description: Copy from QUICK_START.md"
    echo "6. Publish release"
    echo ""
    echo "Users can now clone with:"
    echo "git clone ${REPO_URL}"
    echo ""
    echo "=================================================="
else
    echo ""
    echo "❌ Push failed!"
    echo ""
    echo "Make sure you:"
    echo "1. Created the repository on GitHub: ${REPO_URL%.git}"
    echo "2. Set up authentication (SSH key or Personal Access Token)"
    echo ""
    echo "Need help? Check: https://docs.github.com/en/authentication"
    echo ""
fi
