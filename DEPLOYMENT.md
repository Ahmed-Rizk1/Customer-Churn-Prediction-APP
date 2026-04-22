# 🚀 Deployment Guide — Customer Churn Prediction API

> **Reading time:** ~10 minutes  
> **Difficulty:** Beginner-friendly  
> **Goal:** Take this project from your local machine → live on the internet

---

## 🗺️ How This Guide Is Organized

```
STAGE 0 ── Prepare locally (everyone does this first)
    │
    ├── STAGE 1 ── Deploy on Vercel (main focus)
    │               ├── Way A: Deploy directly from project files
    │               └── Way B: Deploy using Docker container
    │
    └── STAGE 2 ── Other platforms in brief
                    ├── Render / Railway  (simple alternatives)
                    ├── Azure             (Microsoft cloud)
                    ├── AWS               (Amazon cloud)
                    └── Advanced shapes   (Kubernetes, CI/CD, etc.)
```

---

## 📦 STAGE 0 — Prepare Your Project Locally

> Do this **once**, before any deployment method below.

### Step 0.1 — Understand the project layout

```
MLP_practical/
└── project/                  ← this is what you will deploy
    ├── app/
    │   └── main.py           ← FastAPI backend (the API)
    ├── frontend/
    │   └── app.py            ← Streamlit frontend (the UI)
    ├── models/
    │   ├── model.pkl         ← trained model (~500 MB ⚠️)
    │   ├── encoder.pkl
    │   └── model_metadata.json
    ├── requirements.txt
    ├── Dockerfile
    └── docker-compose.yml
```

### Step 0.2 — Handle the large model file

`models/model.pkl` is ~500 MB — **Git refuses files over 100 MB by default.**

Pick **one** option:

| Option | When to use | What to do |
|--------|-------------|------------|
| **A — Skip it** | First push / demo | Add `models/*.pkl` to `.gitignore`, upload files manually later |
| **B — Force push** | You need model in repo | `git add -f models/model.pkl` (slow but works) |
| **C — Git LFS** | Long-term / team project | Install Git LFS, track large files properly |

For a quick demo, **Option A is fine** — you can upload `.pkl` files after deployment.

### Step 0.3 — Push your code to GitHub

```bash
# Open a terminal inside d:\MLP_practical\  (your local project root)

git init
git add .
git commit -m "initial commit — churn prediction project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

> **No GitHub account?** Create one free at [github.com](https://github.com). It takes 2 minutes.

✅ Your code is now on GitHub. You are ready for Stage 1.

---

---

# 🟢 STAGE 1 — Deploy on Vercel

## What is Vercel?

Think of Vercel as a **magic button** that reads your code from GitHub and puts it on the internet automatically. It's free, fast, and requires zero server knowledge.

> **Important note on Vercel:** Vercel is designed primarily for **frontend / serverless apps**.  
> Your project has a FastAPI backend — so you need a small trick: deploy it as a **Serverless Function**.  
> Both ways below handle this for you.

---

## ▶️ Way A — Deploy Directly from Project Files (Recommended for Beginners)

**How it works:** Vercel reads your `requirements.txt` and starts the API automatically.  
**No Docker needed.** Just connect GitHub → done.

---

### Step A1 — Add a Vercel config file

Create a file called **`vercel.json`** inside the `project/` folder:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ]
}
```

💡 **What this does:** Tells Vercel "my entry point is `app/main.py`, route all traffic there."

---

### Step A2 — Make sure your FastAPI app is Vercel-compatible

Open `app/main.py`. Vercel needs the FastAPI app to be importable as a module.  
Make sure the last lines look like this (do **not** put `uvicorn.run()` at module level):

```python
# ✅ CORRECT — Vercel imports this object
app = FastAPI(...)

# ❌ WRONG — remove this if it's outside an if __name__ block
uvicorn.run(app, host="0.0.0.0", port=8000)

# ✅ CORRECT way to allow local running too
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### Step A3 — Push the new file to GitHub

```bash
cd d:\MLP_practical\project

git add vercel.json
git commit -m "add vercel config"
git push
```

---

### Step A4 — Create a free Vercel account

Go to [vercel.com](https://vercel.com) → click **Sign Up** → choose **Continue with GitHub**.  
Vercel will ask to access your GitHub — click **Authorize**.

---

### Step A5 — Import your project

1. On the Vercel dashboard, click **"Add New… → Project"**
2. Find your GitHub repo in the list → click **Import**
3. On the configuration screen, set:

| Setting | Value |
|---------|-------|
| **Framework Preset** | `Other` |
| **Root Directory** | `project` ← **important!** |
| **Build Command** | *(leave empty — Vercel auto-detects)* |
| **Output Directory** | *(leave empty)* |

4. Click **"Deploy"**

---

### Step A6 — Watch it build

Vercel shows a live build log. It takes **2–4 minutes**. You will see:

```
✓ Installing Python dependencies from requirements.txt
✓ Building serverless function: app/main.py
✓ Deployment complete
```

---

### Step A7 — Get your live URL

After the build, Vercel gives you a URL like:

```
https://your-repo-name.vercel.app
```

Test it in your browser or terminal:

```bash
curl https://your-repo-name.vercel.app/
# → {"status": "ok", "model": "RandomForestClassifier"}

curl https://your-repo-name.vercel.app/docs
# → Opens the interactive API documentation
```

🎉 **Your API is live!**

---

### Step A8 — Set environment variables (if needed)

If your app reads secrets from `.env`, add them in Vercel:

1. Go to your project → **Settings → Environment Variables**
2. Add key-value pairs (e.g., `API_URL`, `MODEL_PATH`)
3. Click **Save** → Vercel auto-redeploys

---

### Step A9 — Every future update is automatic

Now, every time you `git push`, Vercel **automatically redeploys**. Zero effort.

```bash
# Make a change locally...
git add .
git commit -m "improved prediction endpoint"
git push
# → Vercel rebuilds and redeploys in ~2 minutes automatically
```

---

## ▶️ Way B — Deploy Using Docker (More Control)

**How it works:** You build a Docker container → Vercel runs it.  
**Use this when:** you have complex dependencies, need a specific Python version, or want identical local/production environments.

> ⚠️ **Prerequisite:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) on your machine first.

---

### Step B1 — Verify your Dockerfile is correct

Your project already has `project/Dockerfile`. It should look like this:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY models/ ./models/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

✅ This is already in your project — nothing to change.

---

### Step B2 — Test Docker locally first

Always test locally before deploying. Open a terminal in `d:\MLP_practical\project\`:

```bash
# Build the image
docker build -t churn-api .

# Run it locally
docker run -p 8000:8000 churn-api

# Test it (open a second terminal)
curl http://localhost:8000/
# → {"status": "ok", "model": "RandomForestClassifier"}
```

If this works locally → it will work on Vercel. Stop the container with `Ctrl+C`.

---

### Step B3 — Add a Vercel config for Docker

Create `project/vercel.json` for Docker mode:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "Dockerfile",
      "use": "@vercel/docker"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/"
    }
  ]
}
```

---

### Step B4 — Push to GitHub

```bash
cd d:\MLP_practical\project

git add vercel.json
git commit -m "add vercel docker config"
git push
```

---

### Step B5 — Deploy on Vercel (same as Way A, Steps A4–A7)

The import process is identical to Way A. Vercel detects the `Dockerfile` automatically and builds from it.

The build takes **4–8 minutes** (longer than Way A because Docker builds the full image).

```
✓ Building Docker image from Dockerfile
✓ Container deployed as serverless function
✓ Deployment complete → https://your-repo.vercel.app
```

---

### 📊 Way A vs Way B — Which should I choose?

| | Way A (Project Files) | Way B (Docker) |
|---|:---:|:---:|
| **Setup difficulty** | ⭐ Easy | ⭐⭐ Medium |
| **Build time** | ~3 min | ~6 min |
| **Exact env control** | ❌ | ✅ |
| **Works with complex deps** | Sometimes | Always |
| **Best for** | Quick demos | Production-like |

> 💡 **Start with Way A.** Switch to Way B only if you run into dependency issues.

---

## ⚠️ Vercel Limitations to Know

| Limitation | Detail |
|------------|--------|
| **Execution timeout** | Functions time out after 10s (free) / 60s (pro) |
| **No persistent storage** | Files written at runtime are lost — use a cloud database |
| **Serverless = stateless** | No background workers, no long-running processes |
| **Large model files** | 500 MB `.pkl` won't fit — host on S3/HuggingFace, load via URL |
| **Streamlit frontend** | Vercel doesn't run Streamlit — deploy it separately on Render/HF Spaces |

---

---

# 🔵 STAGE 2 — Other Deployment Platforms

> These are overviews. Each deserves its own deep-dive, but you'll understand the concept and know when to use each.

---

## 🟡 Quick Alternatives (Similar to Vercel)

### Render

- **Concept:** Connect GitHub → auto-deploy. Like Vercel but designed for backends.
- **Best for:** Always-on APIs, free tier with sleep after 15 min inactivity.
- **How:** New Web Service → set Root Directory to `project` → Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Cost:** Free tier available, $7/mo for always-on.

### Railway

- **Concept:** Same idea, slightly more reliable free tier.
- **Best for:** Quick demo deployments, background workers.
- **How:** New Project → Deploy from GitHub → auto-detects Python → set start command.
- **Cost:** Free $5/month credit, then usage-based.

### Hugging Face Spaces

- **Concept:** Platform specifically for ML demos. Runs Streamlit/Gradio natively.
- **Best for:** Sharing your Streamlit frontend publicly.
- **How:** New Space → choose Streamlit SDK → push your `frontend/app.py`.
- **Cost:** Free for public spaces.

---

## 🔷 Microsoft Azure

### What it is
Azure is Microsoft's enterprise cloud platform. If your company uses Microsoft products (Office 365, Teams), Azure is likely already available to you.

### Deployment options on Azure

```
Azure
├── Azure App Service       ← Easiest: like Render but enterprise-grade
├── Azure Container Apps    ← Run your Docker container with auto-scaling
├── Azure Functions         ← Serverless like Vercel (pay per call)
└── Azure Kubernetes Service (AKS) ← Advanced: manage many containers
```

### Simple Azure path (App Service)

1. Install Azure CLI: `winget install Microsoft.AzureCLI`
2. Login: `az login`
3. Create a web app:
   ```bash
   az group create --name churn-rg --location eastus
   az appservice plan create --name churn-plan --resource-group churn-rg --sku F1
   az webapp create --name churn-api --resource-group churn-rg --plan churn-plan --runtime "PYTHON:3.11"
   az webapp up --name churn-api --resource-group churn-rg
   ```
4. Your API is live at: `https://churn-api.azurewebsites.net`

### When to choose Azure
- Your organization is already on Microsoft ecosystem
- You need enterprise compliance (HIPAA, SOC2)
- You want to integrate with Azure ML for model hosting

---

## 🟠 Amazon Web Services (AWS)

### What it is
AWS is the world's largest cloud platform. More complex but extremely powerful and flexible.

### Deployment options on AWS

```
AWS
├── Elastic Beanstalk    ← Easiest: upload zip → auto-deploys
├── App Runner           ← Like Vercel but AWS (Docker/GitHub → auto-deploy)
├── ECS (Fargate)        ← Run Docker containers, serverless compute
├── EC2                  ← Raw virtual machine (full control, most setup)
└── Lambda               ← Serverless functions (pay per execution)
```

### Simplest AWS path (App Runner)

1. Build and push your Docker image to ECR (Amazon's image registry):
   ```bash
   aws ecr create-repository --repository-name churn-api
   docker build -t churn-api .
   docker tag churn-api:latest YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/churn-api:latest
   docker push YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/churn-api:latest
   ```
2. Go to **AWS App Runner** in the console → Create Service → pick your ECR image
3. Set port to `8000` → Deploy → get your URL in ~5 minutes

### EC2 path (full control)

1. Launch an EC2 instance (t3.micro = free tier eligible)
2. SSH into it: `ssh -i key.pem ec2-user@YOUR_IP`
3. Install Docker, copy your project files, run `docker-compose up -d`
4. Your API is at `http://YOUR_IP:8000`

### When to choose AWS
- You need massive scale (millions of requests)
- You want fine-grained cost optimization
- You're integrating with other AWS services (S3 for model storage, SageMaker for ML)

---

## ⚙️ Advanced Deployment Shapes

Once your project grows, you'll encounter these patterns. Here's what they mean:

---

### 🔄 CI/CD Pipeline (Continuous Integration / Delivery)

**Concept:** Every time you push code, tests run automatically → if tests pass → deploys automatically. No manual steps ever.

**Tools:** GitHub Actions, GitLab CI, CircleCI

**Simple GitHub Actions example** (create `.github/workflows/deploy.yml`):
```yaml
on: push
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest tests/
      - name: Deploy to Vercel
        run: vercel --prod --token ${{ secrets.VERCEL_TOKEN }}
```

**When to use:** When working in a team, or when manual deployments become error-prone.

---

### 🐳 Kubernetes (Container Orchestration)

**Concept:** Run many copies of your Docker container across multiple servers. Kubernetes automatically restarts crashed containers, balances traffic, and scales up/down based on demand.

**Think of it as:** Docker Compose but for 100 servers instead of 1.

**Managed services:** AWS EKS, Azure AKS, Google GKE

**When to use:** When you have 10,000+ users and a single server isn't enough, or when you have multiple services (API, frontend, model server, database) that need to talk to each other reliably.

---

### 📦 Model Serving (ML-specific)

**Concept:** Instead of loading your `.pkl` model inside the API, you host the model on a dedicated server optimized for ML inference.

**Tools:**
- **BentoML** — Package your model + API together, deploy anywhere
- **MLflow Models** — Serve models directly from your MLflow tracking server
- **AWS SageMaker** — Fully managed ML model hosting on AWS
- **Triton Inference Server** — High-performance inference (NVIDIA, used at scale)

**When to use:** When your model is >1GB, when you need GPU inference, or when many different apps need to share the same model.

---

### 🌐 CDN + Edge Deployment

**Concept:** Instead of running your app in one city, run it in 30+ cities worldwide. Users connect to the nearest location — ultra-low latency.

**Tools:** Vercel Edge Functions, Cloudflare Workers, AWS Lambda@Edge

**When to use:** Global user base where latency matters (e.g., real-time predictions).

---

---

## 📊 Full Platform Comparison

| Platform | Difficulty | Cost | Best For | ML-Friendly |
|----------|:----------:|------|----------|:-----------:|
| **Vercel** | ⭐ | Free / $20/mo | APIs, serverless | ⚠️ size limits |
| **Render** | ⭐ | Free / $7/mo | Always-on APIs | ✅ |
| **Railway** | ⭐ | ~$5/mo | Quick deploys | ✅ |
| **HF Spaces** | ⭐ | Free | ML demos (Streamlit) | ✅✅ |
| **Azure App Service** | ⭐⭐ | ~$10/mo | Enterprise apps | ✅ |
| **AWS App Runner** | ⭐⭐ | Pay-per-use | Docker apps | ✅ |
| **AWS EC2** | ⭐⭐⭐ | ~$5-15/mo | Full control | ✅ |
| **Kubernetes** | ⭐⭐⭐⭐⭐ | Varies | Large-scale prod | ✅✅ |

---

## 🐛 Common Errors & Fixes

### `Model artifact not found`
**Cause:** `.pkl` files weren't included in the deployment  
**Fix:** Upload model files manually, or set `MODEL_PATH` env variable to a cloud URL (e.g., S3 or HuggingFace)

### `Application startup failed`
**Cause:** Running `uvicorn` from the wrong directory  
**Fix:** Always run from inside `project/`:
```bash
cd d:\MLP_practical\project
uvicorn app.main:app --reload --port 8000
```

### `API unreachable` in Streamlit
**Cause:** `API_URL` is wrong (pointing to localhost instead of the deployed URL)  
**Fix:** Set the environment variable to your deployed API URL:
```bash
# On Vercel/Render: set in dashboard → Environment Variables
API_URL=https://your-app.vercel.app
```

### `Function timeout` on Vercel
**Cause:** Loading a 500 MB model on every cold start takes >10 seconds  
**Fix:** Cache the model at module level (load once, reuse), or use a dedicated model server

### `Cannot import 'uvicorn'` on Vercel
**Cause:** Vercel's Python runtime doesn't use `uvicorn` the same way  
**Fix:** Ensure `uvicorn.run()` is inside `if __name__ == "__main__":` block only

---

## 🧭 Decision Guide — Which Path Should I Take?

```
START HERE
    │
    ├─ "I just want to share a demo quickly"
    │       └─▶ Vercel Way A  OR  Render  (5-10 min)
    │
    ├─ "I have complex dependencies / large model"
    │       └─▶ Vercel Way B (Docker)  OR  Railway  (10-20 min)
    │
    ├─ "I need the Streamlit frontend live too"
    │       └─▶ Backend → Vercel/Render │ Frontend → Hugging Face Spaces
    │
    ├─ "This is a real product for real users"
    │       └─▶ AWS App Runner  OR  Azure App Service  (1-2 hrs)
    │
    └─ "This needs to handle thousands of users"
            └─▶ AWS ECS/Kubernetes + CI/CD pipeline  (days of setup)
```

---

*Guide written for the MLP Practical — Customer Churn Prediction project.*  
*Project structure: FastAPI backend + Streamlit frontend + scikit-learn model.*
