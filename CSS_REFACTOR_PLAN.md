# CSS Refactoring and Consolidation Plan

## 1. Introduction

This document outlines a strategic plan to refactor the application's CSS. The current implementation suffers from disorganization, including a mix of CDN-based frameworks (DaisyUI), embedded styles in `base.html`, and an external stylesheet (`custom.css`) that relies heavily on `!important` overrides. This plan aims to create a more maintainable, scalable, and organized CSS architecture.

## 2. Goals

*   **Consolidate** all custom styles into a single, well-structured stylesheet.
*   **Eliminate** embedded styles and redundant CSS files.
*   **Reduce or remove** the dependency on `!important` overrides.
*   **Improve** maintainability and developer experience by establishing a clear CSS structure.

## 3. Refactoring Steps

### Step 1: Create a New Primary Stylesheet

1.  Create a new file named `main.css` inside the `app/static/css/` directory. This file will become the single source of truth for all custom application styles.
2.  In `base.html`, replace the link to `custom.css` with a link to the new `main.css`:
    ```html
    <!-- In app/templates/base.html -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    ```

### Step 2: Consolidate Styles

1.  **Migrate Embedded Styles:** Copy the entire content of the `<style>` block (lines 21-97) from `app/templates/base.html` and paste it into the new `app/static/css/main.css`.
2.  **Migrate Custom Styles:** Copy the entire content of `app/static/css/custom.css` and append it to the end of `app/static/css/main.css`.

### Step 3: Cleanup and Removal

1.  **Remove Embedded Styles:** Delete the entire `<style>` block from `app/templates/base.html`.
2.  **Delete Unused Files:** Delete the following redundant or unused CSS files:
    *   `app/static/css/custom.css`
    *   `app/static/css/style.css`
    *   `app/static/css/input.css`

### Step 4: Structure the New Stylesheet

Organize the contents of `main.css` to improve readability and maintainability. A recommended structure is as follows:

```css
/* app/static/css/main.css */

/* -----------------------------------------------------------------------------
   1. FONT DECLARATIONS
      - All @font-face rules.
   ----------------------------------------------------------------------------- */

/* Font-face rules will be moved here from custom.css */


/* -----------------------------------------------------------------------------
   2. BASE & TYPOGRAPHY
      - Global styles (body, html).
      - Default typography (h1-h6, p, a, etc.).
      - Font overrides that were previously using !important.
   ----------------------------------------------------------------------------- */

/* Base typography rules will be moved here */


/* -----------------------------------------------------------------------------
   3. LAYOUT & CORE COMPONENTS
      - Styles for major layout elements like the navbar, footer, and main container.
      - Styles migrated from the <style> block in base.html.
   ----------------------------------------------------------------------------- */

/* Core layout styles will be moved here */


/* -----------------------------------------------------------------------------
   4. REUSABLE COMPONENTS
      - Styles for cards, buttons, badges, forms, tables, etc.
   ----------------------------------------------------------------------------- */

/* Component styles will be moved here */


/* -----------------------------------------------------------------------------
   5. PAGE-SPECIFIC STYLES
      - Styles that apply only to specific pages or sections (e.g., dashboard, reports).
   ----------------------------------------------------------------------------- */

/* Page-specific styles will be moved here */


/* -----------------------------------------------------------------------------
   6. UTILITIES & ANIMATIONS
      - Helper classes, animations (keyframes), and other utilities.
   ----------------------------------------------------------------------------- */

/* Utilities and animations will be moved here */
```

### Step 5: Eliminate `!important` Overrides

With all styles consolidated, the use of `!important` can be minimized. The primary strategy is to leverage CSS specificity.

**Guideline:** Instead of using `!important`, increase the specificity of the selector. Since the application uses DaisyUI, which relies on utility classes, custom overrides should be more specific.

**Example:**

*   **Problem:**
    ```css
    h1, h2, h3, h4, h5, h6 {
      font-weight: 700 !important;
    }
    ```
*   **Solution:**
    If DaisyUI applies a different font-weight via a class like `.title`, a more specific selector can override it without `!important`.
    ```css
    /* Example of a more specific selector */
    .prose h1, .prose h2, .card-title, h1 {
        font-weight: 700;
    }

    /* Or, if targeting a specific area */
    main h1, main h2 {
        font-weight: 700;
    }
    ```
The developer should inspect the elements in the browser to understand which DaisyUI or Tailwind classes are being applied and write a more specific selector to override them naturally. The new, consolidated `main.css` file is loaded *after* the DaisyUI CDN, so its rules will take precedence if the specificity is equal or greater.

## 4. Verification

After implementing these changes, the developer should:

1.  Thoroughly test the application across different pages and components to ensure all styles are applied correctly.
2.  Verify that there are no visual regressions.
3.  Confirm that the unused CSS files have been deleted and the embedded style block is gone.
4.  Use browser developer tools to check for and resolve any remaining style conflicts.
