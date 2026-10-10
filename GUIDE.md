# Setup Guide

## Repository Secret Names

You only need **3 secrets** now (NO PAT_TOKEN needed):

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

---

## Workflow Permissions (Required for Auto-Restart without PAT)

1. Open **Settings** -> **Actions** -> **General**
2. Under **Workflow permissions**, choose **Read and write permissions**
3. Check **Allow GitHub Actions to create and approve pull requests**
4. Click **Save**

---

## Run

1. Go to **Actions** tab in GitHub
2. Select **Discord Loop Bot**
3. Click **Run workflow** -> **Run workflow**
