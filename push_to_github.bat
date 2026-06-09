@echo off
title Push jBulkEmailSender to GitHub
echo ===========================================
echo Initializing Git Repository and Pushing
echo ===========================================

cd /d "%~dp0"

echo [1/3] Adding all files...
git add .
git commit -m "Phase 3: Hybrid SaaS Deployment & Desktop Integration"

echo [2/3] Setting Remote...
git branch -M main
git remote add origin https://github.com/jDroid-X/jBulkEmail.git

echo [3/3] Pushing to GitHub (https://github.com/jDroid-X/jBulkEmail)
echo Note: A browser window may open asking you to authenticate with GitHub.
git push -u origin main -f

echo ===========================================
echo Done! Please check your GitHub repository.
echo ===========================================
pause
