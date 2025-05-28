# Document Generator - Migration Guide

## Overview

Simple migration from complex UI to simplified version. No backwards compatibility, no feature flags - just move old aside and build new.

## Migration Steps

### Step 1: Preserve Old UI
```bash
cd apps/document-generator/document_generator_app/
mv ui/ ui_old/
```

### Step 2: Create New UI Structure
```bash
mkdir ui/
touch ui/__init__.py
touch ui/components.py
touch ui/callbacks.py
touch ui/layout.py
touch ui/utils.py  # Copy some utilities from old
```

### Step 3: Copy Reusable Parts
```python
# Copy these from ui_old/utils.py to ui/utils.py:
# - build_outline_data()
# - Any other data transformation functions
# But skip the complex UI state management functions

### Step 4: Build New Components

**ui/components.py:**
```python
# Simple, direct components
# No complex state management
# Just UI elements that return values
```

**ui/callbacks.py:**
```python
# Just 5 main callbacks:
# - select_item()
# - add_resource() 
# - add_section(as_subsection=False)
# - save_item()
# - remove_selected()
```

**ui/layout.py:**
```python
# Two-column layout
# Direct wiring of callbacks
# No complex state synchronization
```

### Step 5: Test Everything Works

```bash
# Run the app with new UI
cd apps/document-generator/
python -m document_generator_app.main

# Test all features:
# - Create resources/sections
# - Add subsections (up to 4 levels)
# - Edit items
# - Upload/download outlines
# - Generate documents
```

### Step 6: Clean Up

```bash
# Once everything works, remove old UI
rm -rf document_generator_app/ui_old/

# Update imports if any other code referenced old UI
# (But there shouldn't be any - UI should be self-contained)
```

## What Changes for Users

1. **Click items to edit** instead of using dropdowns
2. **"+Sub" button** for adding subsections
3. **Cleaner layout** with editor on right
4. Everything else works the same

## Benefits

- **50% less code**
- **5 callbacks instead of 15+**
- **No complex state management**
- **Much easier to maintain and modify**

## Simple Rollback Plan

If something doesn't work:
```bash
# Just swap directories back
mv ui/ ui_new/
mv ui_old/ ui/
# Fix the issue in ui_new/, then try again
```

## That's It!

No complex rollout strategy. No feature flags. No A/B testing.

Just:
1. Move old aside
2. Build new in place  
3. Test it works
4. Delete old

This approach embodies our philosophy: ruthlessly simple, direct, and effective.