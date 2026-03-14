# Contributing to Find The Coffee ☕

We use a **Gerrit-like** workflow within GitHub to maintain a clean, linear history. This ensures that every change on the `main` branch is an atomic, high-quality "change-set."

## 📜 Branching Strategy: GitHub Flow + Linear History

- **`main`**: Always reflects production-ready code.
- **`feat/*`** or **`fix/*`**: Temporary branches for development.

## 🛠️ The "Change-Set" Workflow (One Commit per PR)

To mimic Gerrit's atomic review style, we prefer that each Pull Request consists of **exactly one commit**.

### 1. Create a branch and make your change:
```bash
git checkout -b feat/add-new-roaster
# ... make changes ...
git add .
git commit -m "feat(roaster): implement search by location"
```

### 2. Pushing for review:
Open a Pull Request on GitHub. Ensure your branch name is descriptive.

### 3. Addressing feedback (The Gerrit Way):
Instead of adding a second commit to your branch, **amend** the existing one:
```bash
# ... make requested changes ...
git add .
git commit --amend --no-edit  # Amends your single commit
git push --force              # Updates the PR on GitHub
```
*Note: This force-push is safe because you are only pushing to your own feature branch.*

### 4. Merging:
All PRs must be **Squashed and Merged** or **Rebased and Merged** by the maintainer. This ensures the final history on `main` remains linear and readable.

## ⚙️ Recommended Local Git Config

To make this workflow smoother, run these commands in your repository:

```bash
# Ensure all pulls use rebase by default (avoids merge commits)
git config pull.rebase true

# Auto-setup remote tracking
git config push.autoSetupRemote true
```

## 🔐 Required GitHub Repository Settings

If you are the repository owner, please enable these settings on GitHub:

1. **General Settings:**
   - [x] **Allow squash merging** (Default)
   - [ ] **Allow rebase merging** (Optional)
   - [ ] **Allow merge commits** (UNCHECK THIS ❌)

2. **Branch Protection (for `main`):**
   - [x] **Require a pull request before merging**
   - [x] **Require status checks to pass before merging** (e.g., CI)
   - [x] **Require linear history** (THIS IS CRITICAL 🚨)
