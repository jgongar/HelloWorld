# Hello World Web App

**What this file is:** Project overview and step-by-step instructions (GitHub, Docker, hosting). Read this first if you’re new to the project.

A simple Hello World web application that runs in Docker, with CI/CD using GitHub Actions.

---

## What’s in this project

| File / folder      | Purpose |
|--------------------|--------|
| `index.html`       | The main page (“Hello, World!”). |
| `style.css`        | Simple styling for the page. |
| `Dockerfile`       | Instructions to build a Docker image that serves the app. |
| `.github/workflows/ci-cd.yml` | GitHub Actions workflow: builds the Docker image and runs a quick test on every push. |

---

## 1. Put your code on GitHub

You need Git installed. If you don’t have it: [Download Git](https://git-scm.com/downloads).

### Create a new repository on GitHub

1. Go to [github.com](https://github.com) and sign in (or create an account).
2. Click the **+** (top right) → **New repository**.
3. Name it (e.g. `hello-world-app`).
4. Choose **Public**.
5. Do **not** check “Add a README” (you already have files locally).
6. Click **Create repository**.

### Push your local project to GitHub

In a terminal (PowerShell or Command Prompt), go to this project folder and run:

```powershell
cd "c:\Users\jgong\OneDrive\Escritorio\Cursor Projects\Hello world"
git init
git add .
git commit -m "First commit: Hello World app with Docker and CI/CD"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username and `YOUR_REPO_NAME` with the repository name you chose. When asked, sign in with your GitHub account.

After this, your code is on GitHub and the **CI/CD workflow will run automatically** on every push (you’ll see it under the **Actions** tab in your repo).

---

## 2. Run the app with Docker (on your PC)

Install Docker: [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/).

In the project folder:

```powershell
docker build -t hello-world-app .
docker run -p 8080:80 hello-world-app
```

Open a browser and go to: **http://localhost:8080**

You should see “Hello, World!”.

---

## 3. Host the app on the web for free (Docker)

These platforms have free tiers and can run your Docker app by connecting to your GitHub repo. After you connect the repo, they usually **build and deploy automatically** on every push (that’s your CI/CD in action).

### Option A: Render

1. Go to [render.com](https://render.com) and sign up (e.g. with GitHub).
2. **New** → **Web Service**.
3. Connect your GitHub account and select this repository.
4. Render will detect the **Dockerfile**.
5. Leave defaults and click **Create Web Service**.
6. After the build finishes, you get a URL like `https://your-app-name.onrender.com`.

### Option B: Fly.io

1. Install Fly CLI: [fly.io/docs/hands-on/install-flyctl](https://fly.io/docs/hands-on/install-flyctl/).
2. Sign up: run `fly auth signup` (or `fly auth login` if you have an account).
3. In your project folder run: `fly launch` and follow the prompts (choose your app name and region).
4. Deploy: `fly deploy`.
5. Your app will be at `https://your-app-name.fly.dev`.

You can also connect the repo in the Fly.io dashboard so that pushes to `main` trigger a deploy automatically.

---

## 4. What the CI/CD does

The file `.github/workflows/ci-cd.yml` defines a **GitHub Action** that:

1. Runs on every **push** and **pull request** to the `main` (or `master`) branch.
2. **Checks out** your code.
3. **Builds** the Docker image.
4. **Runs** the container and checks that the site responds (a simple test).

So every time you push to GitHub, the workflow verifies that the app still builds and runs. If you use Render or Fly.io and connect the repo, they handle the “deploy” part; GitHub Actions handles the “test that the build works” part.

---

## Next steps

- Edit `index.html` or `style.css`, then run `git add .`, `git commit -m "Your message"`, and `git push`. Watch the **Actions** tab and your hosted site update.
- Change the workflow in `.github/workflows/ci-cd.yml` to try more steps (e.g. add another test or deploy step).

Enjoy your first Hello World app with GitHub, Docker, and CI/CD.
