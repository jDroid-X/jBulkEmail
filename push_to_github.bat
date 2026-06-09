@echo off
title Push jBulkEmail to GitHub
echo ===========================================
echo Initializing Git Repository and Pushing
echo ===========================================

cd /d "%~dp0"

echo [1/4] Initializing Git...
git init

echo [2/4] Staging and Committing files...
git add .
git commit -m "Phase 3: Hybrid SaaS Deployment & Desktop Integration"

echo [3/4] Setting Branch and Remote...
git branch -M main
git remote add origin https://github.com/jDroid-X/jBulkEmail.git

echo [4/4] Pushing to GitHub (https://github.com/jDroid-X/jBulkEmail)
echo Note: A browser window may open asking you to authenticate with GitHub.
git push -u origin main -f

echo ===========================================
echo Done! Please check your GitHub repository.
echo ===========================================
pause
