# Deployment Guide

## Prerequisites
- GitHub account
- Vercel account (sign up at https://vercel.com with GitHub)

## Step 1: Update Configuration

Before deploying, update `book/docusaurus.config.js`:

```javascript
// Replace these values:
url: 'https://your-vercel-domain.vercel.app',  // Your Vercel URL
baseUrl: '/',
organizationName: 'YOUR_GITHUB_USERNAME',
projectName: 'ai-humanoid-robotics-book',
```

## Step 2: Push to GitHub

```bash
# 1. Check status
git status

# 2. Add all changes
git add .

# 3. Commit
git commit -m "Add professional frontend with chatbot widget"

# 4. Create GitHub repo at https://github.com/new
# Name: ai-humanoid-robotics-book
# Visibility: Public (for free Vercel hosting)

# 5. Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/ai-humanoid-robotics-book.git

# 6. Push
git push -u origin 001-docusaurus-infrastructure
```

## Step 3: Deploy to Vercel

### Method 1: Vercel Dashboard (Easiest)

1. Go to https://vercel.com
2. Click "Add New Project"
3. Import your GitHub repository
4. **Configure settings:**
   - **Root Directory:** `book` ← CRITICAL!
   - **Framework:** Docusaurus
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`
   - **Install Command:** `npm install`
5. Click "Deploy"

### Method 2: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to book folder
cd book

# Deploy
vercel

# Deploy to production
vercel --prod
```

## Step 4: Environment Variables (Optional)

If you have a backend API, add this environment variable in Vercel:

- **Key:** `REACT_APP_API_URL`
- **Value:** `https://your-backend-api.com`

Go to: Project Settings → Environment Variables

## Step 5: Custom Domain (Optional)

1. Go to Vercel project settings
2. Click "Domains"
3. Add your custom domain
4. Update DNS records as instructed

## Troubleshooting

### Build Fails

**Error:** "Cannot find module 'intro.module.css'"
- **Fix:** Ensure file exists at `book/docs/intro.module.css`

**Error:** "Root directory not found"
- **Fix:** Set Root Directory to `book` in Vercel settings

### Blank Page After Deploy

**Issue:** White screen on deployed site
- **Fix:** Check browser console for errors
- Ensure `baseUrl: '/'` in docusaurus.config.js
- Check that all CSS modules are properly imported

### Chatbot Not Working

**Issue:** "Failed to fetch" error
- **Fix:** Add backend API URL as environment variable
- Ensure backend is deployed and CORS is configured

## Automatic Deployments

Vercel automatically deploys when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "Update content"
git push

# Vercel will auto-deploy!
```

## Production URLs

After deployment, you'll get:
- **Preview URL:** `https://your-project-git-branch.vercel.app`
- **Production URL:** `https://your-project.vercel.app`
- **Custom Domain:** `https://yourdomain.com` (if configured)

## Next Steps

1. ✅ Deploy frontend to Vercel
2. 🔄 Deploy backend API (Railway, Render, or AWS)
3. 🔗 Connect frontend to backend API
4. 📝 Add your OpenAI API key to backend
5. 🎨 Customize domain name

---

Need help? Check:
- Vercel Docs: https://vercel.com/docs
- Docusaurus Deployment: https://docusaurus.io/docs/deployment
