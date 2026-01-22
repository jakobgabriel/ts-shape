# Documentation Deployment Guide

This document explains the automated documentation deployment setup for ts-shape.

## 📚 Documentation Systems

The project now has **dual documentation systems** configured:

### 1. MkDocs (Primary) ✅

**Status**: Configured and ready to deploy

**Location**:
- Configuration: `mkdocs.yml`
- Content: `docs/` directory
- Workflow: `.github/workflows/generate_docs.yml`

**Features**:
- Material theme with dark/light modes
- Auto-generated API documentation
- Search functionality
- Navigation tabs
- Responsive design

**Deployment URL**: https://jakobgabriel.github.io/ts-shape

### 2. Sphinx (Alternative)

**Status**: Configured but optional

**Location**:
- Configuration: `docs/conf.py`
- Content: `docs/*.rst` files
- Workflow: `.github/workflows/deploy-docs.yml`

## 🚀 How Automatic Deployment Works

### Current Setup (MkDocs)

The existing workflow `.github/workflows/generate_docs.yml` will automatically:

1. **Trigger on**:
   - Push to `main` branch
   - Manual workflow dispatch

2. **Build process**:
   ```yaml
   - Checkout code
   - Set up Python 3.9
   - Install dependencies from requirements-docs.txt
   - Run: mkdocs build
   - Deploy to gh-pages branch
   ```

3. **Result**:
   - Documentation published to GitHub Pages
   - Accessible at https://jakobgabriel.github.io/ts-shape

## 📋 Production Modules Documentation

The following production module documentation is now integrated:

### Navigation Structure

```
Production Modules/
├── Overview                    (New module overview)
├── Quick Start                 (5-minute getting started)
├── Daily Production Tracking   → DAILY_PRODUCTION_MODULES.md
├── Downtime & Quality          → DOWNTIME_QUALITY_MODULES.md
├── Complete Module Guide       → PRODUCTION_MODULES_SUMMARY.md
└── Future Features             → FUTURE_PRODUCTION_FEATURES.md
```

### Files Added

**Root Documentation**:
- `DAILY_PRODUCTION_MODULES.md` - PartProductionTracking, CycleTimeTracking, ShiftReporting
- `DOWNTIME_QUALITY_MODULES.md` - DowntimeTracking, QualityTracking
- `PRODUCTION_MODULES_SUMMARY.md` - Complete 5-module overview
- `FUTURE_PRODUCTION_FEATURES.md` - Roadmap (OEE, changeover tracking, etc.)

**MkDocs Integration** (`docs/production/`):
- `overview.md` - Production modules landing page
- `quick_start.md` → symlink to `user_guide/quick_start.md`
- `daily_production.md` → symlink to `../../DAILY_PRODUCTION_MODULES.md`
- `downtime_quality.md` → symlink to `../../DOWNTIME_QUALITY_MODULES.md`
- `complete_guide.md` → symlink to `../../PRODUCTION_MODULES_SUMMARY.md`
- `future_features.md` → symlink to `../../FUTURE_PRODUCTION_FEATURES.md`

## 🔧 How to Trigger Deployment

### Option 1: Merge to Main Branch

```bash
# Merge your feature branch to main
git checkout main
git merge claude/analyze-manufacturing-improvements-miI10
git push origin main
```

**This will automatically**:
1. Trigger the `generate_docs.yml` workflow
2. Build the mkdocs documentation
3. Deploy to GitHub Pages
4. Documentation available within 2-5 minutes

### Option 2: Manual Workflow Trigger

1. Go to GitHub repository
2. Click **Actions** tab
3. Select **Deploy Documentation** workflow
4. Click **Run workflow**
5. Select branch (usually `main`)
6. Click **Run workflow** button

### Option 3: Test Locally First

```bash
# Install mkdocs and dependencies
pip install -r requirements-docs.txt

# Build and serve documentation locally
mkdocs serve

# Open browser to http://127.0.0.1:8000
# Documentation will auto-reload on changes
```

## ✅ Verify Deployment

After pushing to `main` or running the workflow:

1. **Check GitHub Actions**:
   - Go to repository → Actions tab
   - Look for "Deploy Documentation" workflow
   - Should show green checkmark when complete

2. **Check GitHub Pages**:
   - Go to repository → Settings → Pages
   - Should show: "Your site is published at https://jakobgabriel.github.io/ts-shape"

3. **View Documentation**:
   - Visit: https://jakobgabriel.github.io/ts-shape
   - Navigate to "Production Modules" section
   - Verify all 6 pages are accessible

## 🐛 Troubleshooting

### Documentation Not Building

**Symptom**: Workflow fails with "mkdocs: command not found"

**Solution**:
```bash
# Check requirements-docs.txt includes all dependencies
cat requirements-docs.txt

# Should contain:
# mkdocs-literate-nav
# mkdocs-material
# mkdocs-gen-files
# mkdocs-callouts
# mkdocstrings-python
```

### Missing Dependencies

**Symptom**: Build fails with import errors

**Solution**: Ensure `requirements-docs.txt` contains:
```
mkdocs-literate-nav
mkdocs-material
mkdocs-gen-files
mkdocs-callouts
mkdocstrings-python
```

### Broken Links

**Symptom**: Links show 404 errors

**Solution**: Check symlinks are valid:
```bash
cd docs/production
ls -la  # Verify symlinks point to existing files
```

### GitHub Pages Not Enabled

**Symptom**: Documentation URL shows 404

**Solution**:
1. Go to repository Settings → Pages
2. Source: Deploy from a branch
3. Branch: `gh-pages` / (root)
4. Click Save

## 📝 Adding New Documentation

### Add a New Page

1. **Create the markdown file**:
   ```bash
   echo "# New Page Content" > docs/new_page.md
   ```

2. **Update mkdocs.yml**:
   ```yaml
   nav:
   - Production Modules:
     - New Page: production/new_page.md
   ```

3. **Test locally**:
   ```bash
   mkdocs serve
   ```

4. **Commit and push**:
   ```bash
   git add docs/new_page.md mkdocs.yml
   git commit -m "docs: add new documentation page"
   git push
   ```

### Update Existing Documentation

Documentation files in the root directory will automatically update:

- `DAILY_PRODUCTION_MODULES.md`
- `DOWNTIME_QUALITY_MODULES.md`
- `PRODUCTION_MODULES_SUMMARY.md`
- `FUTURE_PRODUCTION_FEATURES.md`

Just edit these files and push to main - no mkdocs.yml changes needed!

## 🎨 Documentation Theme

The mkdocs setup uses **Material for MkDocs** with:

- **Colors**: Teal primary, purple/lime accents
- **Features**:
  - Navigation tabs
  - Instant search
  - Dark/light mode toggle
  - Code syntax highlighting
  - Mermaid diagrams support
  - Task lists
  - Admonitions

## 📦 Dependencies

**mkdocs** packages (`requirements-docs.txt`):
- `mkdocs-literate-nav` - Navigation from markdown
- `mkdocs-material` - Material theme
- `mkdocs-gen-files` - Generate pages from scripts
- `mkdocs-callouts` - Callout boxes
- `mkdocstrings-python` - Auto API docs from docstrings

## 🔄 Continuous Integration

The workflow runs on:
- ✅ Every push to `main` branch
- ✅ Manual trigger via Actions tab
- ❌ Does NOT run on feature branches

To test on feature branch:
```bash
# Run locally
mkdocs build
mkdocs serve
```

## 📊 Current Status

| Item | Status | Notes |
|------|--------|-------|
| MkDocs config | ✅ Complete | mkdocs.yml updated |
| Production docs | ✅ Complete | All 4 main docs linked |
| Overview page | ✅ Complete | docs/production/overview.md |
| Quick start | ✅ Complete | Linked from user_guide |
| Workflow | ✅ Ready | Triggers on push to main |
| GitHub Pages | ⚠️ Pending | Enable after merge to main |

## 🎯 Next Steps

1. **Merge to main branch**:
   ```bash
   git checkout main
   git merge claude/analyze-manufacturing-improvements-miI10
   git push origin main
   ```

2. **Wait for workflow** (2-5 minutes):
   - Check Actions tab for green checkmark

3. **Enable GitHub Pages** (if not already):
   - Settings → Pages
   - Source: gh-pages branch
   - Save

4. **Verify deployment**:
   - Visit https://jakobgabriel.github.io/ts-shape
   - Check "Production Modules" section
   - Verify all links work

5. **Share the docs**:
   - Update README.md badges
   - Share with team
   - Reference in PyPI description

## 🎉 Success Criteria

Documentation deployment is successful when:

- ✅ Workflow completes without errors
- ✅ GitHub Pages shows the site
- ✅ Production Modules section is visible
- ✅ All 6 pages are accessible
- ✅ API reference works
- ✅ Search functionality works
- ✅ Dark/light mode toggle works

---

**Questions?** Check `.github/workflows/generate_docs.yml` for workflow details.

**Issues?** Verify `mkdocs.yml` configuration and `requirements-docs.txt` dependencies.
