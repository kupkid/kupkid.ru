# GitHub Changelog Setup

## What You Need

1. Create a GitHub repository named `kupkid.ru` (must be public)
2. Push your website files there
3. Make commits when you update the site

## Why

The changelog section fetches real commit history from GitHub API:
```
GET https://api.github.com/repos/kupkid/kupkid.ru/commits
```

This displays your actual deployment history automatically.

## Setup Steps

1. Go to https://github.com/new
2. Repository name: `kupkid.ru`
3. Make it **Public**
4. Initialize with README (optional)
5. Push your files:

```bash
cd /home/kupkid/code/kupkid.ru
git init
git add .
git commit -m "init commit"
git branch -M main
git remote add origin https://github.com/kupkid/kupkid.ru.git
git push -u origin main
```

## How It Works

- Each time you push a commit, changelog updates automatically
- Shows last 5 commits with date, hash, message
- No API key needed for public repos
- Works instantly after push

## Fallback

If GitHub API fails or repo doesn't exist, changelog shows:
```
loading...
```

Or falls back to static placeholder.

## Language

- Site defaults to English (en)
- Russian (ru) if browser language is ru-RU, ru, etc
- Manual toggle with [ru]/[en] button
- Fallback to English for unsupported languages
