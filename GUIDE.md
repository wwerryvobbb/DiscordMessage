# Setup Guide

## Repository Secret Names

Add these in **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**:

```text
USER_TOKEN
```

```text
CHANNEL_ID
```

For `CHANNEL_ID` value use one of these formats:

Single channel:
```text
C=0000000000000000000
```

Entire server (spams ALL channels simultaneously):
```text
G=0000000000000000000
```

```text
MESSAGES_PER_SECOND
```

```text
PAT_TOKEN
```

---

## Workflow Permissions

1. Open **Settings** -> **Actions** -> **General**
2. Under **Workflow permissions**, choose **Read and write permissions**
3. Check **Allow GitHub Actions to create and approve pull requests**
4. Click **Save**

---

## Push To GitHub

```bash
git init
git add .
git commit -m "bot"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

---

## Run

1. Go to **Actions** tab in GitHub
2. Select **Discord Loop Bot**
3. Click **Run workflow** -> **Run workflow**
