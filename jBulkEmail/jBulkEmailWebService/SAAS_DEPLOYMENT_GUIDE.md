# jBulkEmail Online SaaS Deployment Guide (Hybrid SaaS Architecture)

## Overview
This document outlines the deployment strategy for the **jBulkEmail Online SaaS Product**, utilizing the **Hybrid SaaS Architecture (Option A)**. 

Since web browsers enforce strict security sandboxes, a web application hosted on the internet cannot arbitrarily create folders or download silent payloads to a user's `Desktop`. To solve this while delivering a premium "SaaS" experience, we use a hybrid model.

## The Hybrid SaaS Architecture

1. **Cloud Web Application (The Hub)**
   - The React frontend and FastAPI backend are hosted in the cloud (e.g., Vercel + Render).
   - Users visit `https://jbulkemail.app` (or your chosen domain) to manage their profile, billing, and general SaaS settings.
   
2. **The "Desktop Connector"**
   - When the user selects "Online Mode" or "Local System Mode" from the SaaS website, they will be prompted to download the **jBulkEmail Connector Tool** (which is effectively the `start_services.bat` packaged application).
   - This local connector runs securely on their machine.
   - Because it is a local executable, it possesses the native operating system privileges required to create `Desktop/BulkEmail` folders, manage `.csv` files locally, and interact with the user's filesystem without browser sandbox restrictions.

3. **Data Synchronization**
   - The Desktop Connector synchronizes its mission logs and metadata with your cloud database (PostgreSQL) using secure REST APIs (`/api/mission/launch`).

---

## Deployment Checklist for Cloud Hosting

To put the "SaaS Hub" online, you will need to complete the following:

### 1. Cloud Database (PostgreSQL)
- Create a free PostgreSQL instance on **Supabase**, **Render**, or **Neon.tech**.
- Update the `DATABASE_URL` in `backend/database/db_setup.py` from `sqlite:///./bulkemail.db` to your cloud connection string.

### 2. Backend API Hosting (FastAPI)
- Deploy the `backend` folder to **Render.com** (as a Web Service) or **AWS App Runner**.
- Add a `Dockerfile` to the backend root or let Render automatically detect the `requirements.txt` and `main.py` entry point.
- Set the `uvicorn main:app --host 0.0.0.0 --port 10000` start command.

### 3. Frontend Web Hosting (React/Vite)
- Update the API base URL in `frontend/src/App.jsx` (and any other frontend files making fetch requests) from `http://localhost:8000` to the new Render Backend URL (e.g., `https://jbes-backend.onrender.com`).
- Deploy the `frontend` folder to **Vercel** or **Netlify**.
- Push the code to GitHub (`push_to_github.bat`). Vercel will automatically build and publish the React App online.

## Summary
By following this Hybrid SaaS pattern, you deliver the centralized, subscription-based experience of a Cloud SaaS, while leveraging the raw filesystem power of a local application to manage heavy email loads and local `Desktop/BulkEmail` logs.
