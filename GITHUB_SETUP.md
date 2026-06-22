# GitHub Repository Setup Guide

This guide will help you create a GitHub repository for the Video Reencoder project.

## 📋 Prerequisites

1. GitHub account (create one at https://github.com if you don't have one)
2. Git installed on your computer
3. This project directory

## 🚀 Quick Setup (Recommended)

### Step 1: Initialize Git Repository

Open a terminal in your project directory and run:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Video Reencoder v2.0.0 with 7 enhancements"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Fill in the details:
   - **Repository name**: `video-reencoder` (or your preferred name)
   - **Description**: `Automated video reencoding tool with HEVC/H.265, GPU acceleration, parallel processing, and more`
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
3. Click "Create repository"

### Step 3: Connect and Push

GitHub will show you commands. Use these (replace `YOUR_USERNAME` with your GitHub username):

```bash
# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/video-reencoder.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## 🔐 Authentication Options

### Option 1: Personal Access Token (Recommended)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name: "Video Reencoder"
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)
7. When pushing, use the token as your password

### Option 2: SSH Key

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
```

Then use SSH URL:
```bash
git remote add origin git@github.com:YOUR_USERNAME/video-reencoder.git
```

## 📝 Detailed Step-by-Step

### 1. Check Git Installation

```bash
git --version
```

If not installed:
- **Windows**: Download from https://git-scm.com/
- **macOS**: `brew install git` or install Xcode Command Line Tools
- **Linux**: `sudo apt install git` (Ubuntu/Debian)

### 2. Configure Git (First Time Only)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. Initialize Repository

```bash
# Navigate to project directory
cd "c:/Users/JDHill/OneDrive - IBM/Documents/VSCode Workspaces/Video Reencoding Project"

# Initialize git
git init

# Check status
git status
```

### 4. Stage Files

```bash
# Add all files
git add .

# Or add specific files
git add video_reencoder.py
git add README.md
git add requirements.txt
# ... etc

# Check what will be committed
git status
```

### 5. Create Initial Commit

```bash
git commit -m "Initial commit: Video Reencoder v2.0.0

Features:
- HEVC/H.265 encoding with HandBrake
- Resume capability
- Skip already-encoded files
- Progress bar with tqdm
- Backup before delete
- Quality presets (fast/balanced/best)
- Parallel processing (2-6x faster)
- GPU acceleration (5-10x faster)
"
```

### 6. Create GitHub Repository

1. Go to https://github.com/new
2. Repository settings:
   ```
   Name: video-reencoder
   Description: Automated video reencoding to HEVC/H.265 with GPU acceleration and parallel processing
   Public/Private: Your choice
   Initialize: Leave all unchecked
   ```
3. Click "Create repository"

### 7. Connect to GitHub

```bash
# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/video-reencoder.git

# Verify remote
git remote -v

# Push to GitHub
git push -u origin main
```

## 🏷️ Add Topics/Tags

After creating the repository, add topics for discoverability:

1. Go to your repository on GitHub
2. Click the gear icon next to "About"
3. Add topics:
   - `video-encoding`
   - `hevc`
   - `h265`
   - `handbrake`
   - `video-compression`
   - `gpu-acceleration`
   - `parallel-processing`
   - `python`
   - `automation`

## 📄 Repository Settings

### Enable Features

Go to Settings → General:
- ✅ Issues
- ✅ Projects
- ✅ Wiki (optional)
- ✅ Discussions (optional)

### Add Description and Website

In the "About" section:
- Description: `Automated video reencoding to HEVC/H.265 with GPU acceleration, parallel processing, resume capability, and more`
- Website: (leave blank or add if you have one)
- Topics: (add the tags mentioned above)

## 🎨 Add Repository Badges

Add these to the top of your README.md:

```markdown
# Video Reencoder

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
```

## 📦 Create a Release

### Step 1: Tag the Version

```bash
# Create annotated tag
git tag -a v2.0.0 -m "Release v2.0.0: Major enhancements

- Resume capability
- Skip already-encoded files
- Progress bar with tqdm
- Backup before delete
- Quality presets
- Parallel processing
- GPU acceleration
"

# Push tag to GitHub
git push origin v2.0.0
```

### Step 2: Create Release on GitHub

1. Go to your repository → Releases → "Create a new release"
2. Choose tag: `v2.0.0`
3. Release title: `v2.0.0 - Major Enhancements Release`
4. Description: Copy from CHANGELOG.md
5. Click "Publish release"

## 🔄 Future Updates

### Making Changes

```bash
# Make your changes to files

# Stage changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push
```

### Creating New Releases

```bash
# Create new tag
git tag -a v2.1.0 -m "Release v2.1.0: Description"

# Push tag
git push origin v2.1.0

# Then create release on GitHub
```

## 🌟 Promote Your Repository

### Share On

- Reddit: r/Python, r/DataHoarder, r/selfhosted
- Twitter/X: Use hashtags #Python #VideoEncoding #HEVC
- Hacker News: https://news.ycombinator.com/
- Dev.to: Write an article about it

### Write a Blog Post

Create a blog post explaining:
- Why you created it
- How it works
- Performance improvements
- Use cases

## 📊 Repository Structure

Your repository will look like this:

```
video-reencoder/
├── .gitignore
├── LICENSE
├── README.md
├── CHANGELOG.md
├── QUICKSTART.md
├── HANDBRAKE_INSTALLATION.md
├── ENHANCEMENTS_GUIDE.md
├── ENHANCEMENT_SUGGESTIONS.md
├── GPU_ACCELERATION_GUIDE.md
├── PROJECT_SUMMARY.md
├── GITHUB_SETUP.md (this file)
├── journal.md
├── requirements.txt
├── config.json
├── examples.sh
├── video_reencoder.py
└── logs/ (created at runtime)
```

## 🐛 Issue Templates (Optional)

Create `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. See error

**Expected behavior**
What you expected to happen.

**System Information:**
- OS: [e.g., Windows 11, macOS 14, Ubuntu 22.04]
- Python version: [e.g., 3.11]
- HandBrake version: [e.g., 1.7.0]
- GPU: [e.g., NVIDIA RTX 3060]

**Additional context**
Add any other context about the problem here.
```

## 🎯 Next Steps

1. ✅ Initialize git repository
2. ✅ Create GitHub repository
3. ✅ Push code to GitHub
4. ✅ Add topics/tags
5. ✅ Create v2.0.0 release
6. ✅ Add badges to README
7. ✅ Share with community

## 📞 Support

If you encounter issues:
1. Check GitHub's documentation: https://docs.github.com/
2. GitHub CLI tool: https://cli.github.com/
3. Git documentation: https://git-scm.com/doc

---

**Congratulations! Your project is now on GitHub! 🎉**