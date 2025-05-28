# Document Generator Simplified UI Plans

This directory contains planning documents for simplifying the Document Generator UI following our ruthless simplicity philosophy.

## Plan Documents

### 1. [Simplified UI Plan](simplified-ui-plan.md)
Core design vision:
- Problems with current complex UI (dropdowns, 15+ callbacks)
- New two-column layout with direct selection
- Support for subsections with "+Sub" button (up to 4 levels)
- Benefits of the simplified approach

### 2. [Technical Implementation](technical-implementation.md)
Simple technical approach:
- Move old UI aside: `mv ui/ ui_old/`
- Create new UI directly in `ui/`
- Just 5 callbacks instead of 15+
- Minimal state tracking

### 3. [Visual Design Mockup](visual-design-mockup.md)
Visual mockups showing:
- Clean two-column layout
- Subsection handling with indentation
- Direct click-to-select interaction

### 4. [Migration Guide](migration-guide.md)
Dead simple migration:
- No feature flags or gradual rollout
- Just move old aside, build new, test, delete old
- Simple rollback if needed

## Key Changes

### Before (Complex)
- Dropdown selectors with hidden panels
- 15+ interconnected callbacks
- Complex state synchronization
- Confusing user flow

### After (Simple)
- Click items to select and edit
- 5 total callbacks
- Minimal state (just track selection)
- Clear two-column layout
- "+Sub" button for subsections

## Implementation Approach

```bash
# Step 1: Move old UI aside
mv ui/ ui_old/

# Step 2: Build new UI
# Create simple components directly in ui/

# Step 3: Test it works

# Step 4: Delete old
rm -rf ui_old/
```

## Benefits

- **50% less code**
- **Much cleaner UX**
- **Easier to maintain**
- **Ready for AI regeneration**

No over-engineering. No unnecessary features. Just a clean, simple UI that does exactly what users need.