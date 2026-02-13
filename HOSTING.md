# Free hosting setup

Use **Render** to put your app on the web for free. Every push to GitHub will trigger a new deploy (CI/CD).

---

## Step 1: Create a Render account

1. Go to **[render.com](https://render.com)** and click **Get Started**.
2. Sign up with **GitHub** (so Render can see your repos).

---

## Step 2: Create a new Web Service

1. In the Render dashboard, click **New +** → **Web Service**.
2. Under **Connect a repository**, find **jgongar/HelloWorld** and click **Connect**.
   - If you don’t see it, click **Configure account** and grant Render access to your GitHub account, then try again.

---

## Step 3: Configure the service

Render will detect your **Dockerfile** automatically.

- **Name:** e.g. `hello-world-app` (or leave the default).
- **Region:** choose the one closest to you (e.g. **Oregon (US West)** or **Frankfurt (EU Central)**).
- **Branch:** `main`.
- **Runtime:** **Docker** (should be selected automatically).
- Leave the rest as default.

Click **Create Web Service**.

---

## Step 4: Wait for the first deploy

- Render will build your Docker image and start the app (usually 2–5 minutes).
- When the build finishes, you’ll see a green **Live** badge and a URL like:
  - **https://hello-world-app-xxxx.onrender.com**
- Open that URL in your browser to see your Hello World app.

---

## Step 5: Automatic deploys (CI/CD)

- Every time you **push** to the `main` branch on GitHub, Render will automatically build and deploy the new version.
- No extra configuration needed.

---

## Troubleshooting

| Issue | What to do |
|-------|------------|
| Build fails | In Render dashboard, open **Logs** and check the error. Often it’s a typo in the Dockerfile or a missing file. |
| “Application failed to respond” | Wait 1–2 minutes; the first start can be slow on the free tier. Refresh the URL. |
| Repo not listed | In Render, go to **Account Settings** → **GitHub** and make sure the **HelloWorld** repo (or your whole account) is authorized. |

---

## Optional: Fly.io

If you prefer **Fly.io** (also free tier):

1. Install the CLI: [fly.io/docs/hands-on/install-flyctl](https://fly.io/docs/hands-on/install-flyctl/)
2. In your project folder run: `fly auth signup` or `fly auth login`
3. Run: `fly launch` (choose app name and region)
4. Run: `fly deploy`

Your app will be at `https://your-app-name.fly.dev`.
