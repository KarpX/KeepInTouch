---
name: Serene Pastel Minimal
colors:
  surface: '#f8f9ff'
  surface-dim: '#ccdbf4'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e6eeff'
  surface-container-high: '#dde9ff'
  surface-container-highest: '#d5e3fd'
  on-surface: '#0d1c2f'
  on-surface-variant: '#424942'
  inverse-surface: '#233144'
  inverse-on-surface: '#ebf1ff'
  outline: '#727972'
  outline-variant: '#c1c8c0'
  surface-tint: '#41674c'
  primary: '#3e644a'
  on-primary: '#ffffff'
  primary-container: '#567d62'
  on-primary-container: '#f6fff4'
  inverse-primary: '#a7d1b0'
  secondary: '#64597c'
  on-secondary: '#ffffff'
  secondary-container: '#e2d3fd'
  on-secondary-container: '#64597d'
  tertiary: '#8d4b00'
  on-tertiary: '#ffffff'
  tertiary-container: '#b15f00'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#c2edcb'
  primary-fixed-dim: '#a7d1b0'
  on-primary-fixed: '#00210f'
  on-primary-fixed-variant: '#294e36'
  secondary-fixed: '#e9ddff'
  secondary-fixed-dim: '#cec0e9'
  on-secondary-fixed: '#1f1635'
  on-secondary-fixed-variant: '#4b4163'
  tertiary-fixed: '#ffdcc3'
  tertiary-fixed-dim: '#ffb77d'
  on-tertiary-fixed: '#2f1500'
  on-tertiary-fixed-variant: '#6e3900'
  background: '#f8f9ff'
  on-background: '#0d1c2f'
  surface-variant: '#d5e3fd'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Inter
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-base:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: '0'
  body-semibold:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: '0'
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: '0'
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.06em
  stat-metric:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style

This design system embodies a peaceful, distraction-free approach to personal and professional relationship management. Moving away from aggressive, analytical CRM dashboards and cold utility sheets, it establishes a digital sanctuary that reduces cognitive fatigue and encourages deliberate interpersonal connections.

### Design Personality & Atmosphere
- **Calm & Thoughtful:** Muted, organic hues replace sterile whites and harsh black contrasts, generating a welcoming desktop canvas.
- **Minimalist Restraint:** Every border, divider, and elevation layer serves an organizational purpose; negative space is an active design element rather than an empty void.
- **Gentle Tactility:** Interactive cards and triggers lift subtly on interaction, providing soft, physical reassurance without flashy animations.

### Design Style
The aesthetic fuses **Modern Japanese-influenced Minimalism** with **Soft Scandinavian Functionalism**:
- Warm, natural base surfaces (warm cream) that ease optical strain during long working sessions.
- Crisp white floating containers structured with hairline borders and soft ambient diffusion.
- Expressive yet quiet micro-accents in calming sage green and muted lavender to designate hierarchies and categories.

## Colors

The palette is engineered around soft pastels paired with balanced typographic tones. The chromatic foundation minimizes visual noise, highlighting personal relationship milestones and contact organization.

### Palette Architecture
- **Primary (`#5B8266` - Sage Green):** The principal interactive identity. Applied to primary CTAs, active navigation states, selected filters, and focal badges. Communicates grounding, reliability, and growth.
- **Secondary (`#8E82A8` - Soft Lavender):** Designated for taxonomical structures, relationship groupings, context tags, and categorical taxonomy chips.
- **Tertiary (`#D97706` - Warm Amber):** Reserved as a selective highlight tone for bookmarking, favorite stars, upcoming birthday pings, and high-priority flags.
- **Neutral (`#334155` - Deep Muted Slate):** The typographic anchor. Replaces absolute carbon black to ensure crisp readability with softened optical contrast.

### Surface System
- **Canvas Base (`#FAF9F6`):** Warm cream canvas that grounds the full viewport.
- **Elevated Surfaces (`#FFFFFF`):** Pure white container backgrounds for cards, panels, and modals, creating contrast against the cream backdrop.
- **Muted Surfaces (`#F2EFE8`):** Subtle container fills, search enclosures, and table headers.
- **Hairline Outlines (`#E2E8F0`):** Soft, low-contrast slate borders that separate content boundaries without visual clutter.

## Typography

The typography uses Inter across all levels to maintain consistency across data fields, relationship notes, and dense tabular matrices.

### Typographic Principles
- **Tracking Discipline:** Headings and numeric display metrics feature negative tracking (`-0.01em` to `-0.025em`) to unify word shapes and prevent loose layouts.
- **Micro-Labels & Metadata:** All uppercase metadata headers (such as `PHONE`, `BIRTHDAY`, `GROUP`) employ `label-caps` with wide letter spacing (`0.06em`) to ensure scanability at tiny dimensions.
- **Text Color Hierarchy:** Primary titles and key metrics use Deep Muted Slate (`#334155`). Secondary copy, timestamps, and descriptive text use Gentle Muted Slate (`#64748B`). Placeholders use Slate at 45% opacity.

## Layout & Spacing

The layout is built for high-efficiency desktop productivity while remaining responsive across smaller viewports. It relies on a fluid grid bounded by an intentional maximum container width.

### Layout Philosophy
- **Grid Structure:** Fluid 12-column system constrained to `max-width: 1200px` centered within the viewport.
- **Card Distribution:**
  - **Desktop (1200px+):** 3-column contact directory cards (`span 4` per card), 1.5rem gutters.
  - **Laptop / Tablet (768px – 1199px):** 2-column layout (`span 6` per card), 1rem gutters.
  - **Mobile (< 768px):** Single-column stacked layout (`span 12` per card).
- **Focused Forms:** Single, centered cards spanning `col-12 col-md-8 col-lg-6` to eliminate peripheral distractions during contact entry.

### Spacing Rhythm
Built upon a strict 4px baseline (`0.25rem`):
- Internal card padding is spacious (`space-lg` to `space-xl`) to frame contact details with clear negative space.
- Element clusters (avatar next to name, icon beside phone number) use tight pairings (`space-xs` to `space-sm`).
- Structural section stacks maintain comfortable breathing room (`space-xl` to `3rem`).

## Elevation & Depth

Visual hierarchy is established using soft ambient diffusion combined with low-contrast outlines rather than heavy drop shadows. This creates a lightweight, floating feel across the interface.

### Depth Architecture
1. **Layer 0 (Canvas Base):** Warm Cream (`#FAF9F6`), completely flat.
2. **Layer 1 (Card & Module Foundation):** Pure White (`#FFFFFF`) containers paired with a 1px slate perimeter outline (`#E2E8F0`) and an ambient, low-opacity drop shadow:
   `box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03), 0 1px 2px rgba(0, 0, 0, 0.02)`
3. **Layer 2 (Interactive Hover & Lift):** Interactive contact cards transition upward by 2px (`transform: translateY(-2px)`) with expanded ambient diffusion tinted by deep slate:
   `box-shadow: 0 6px 16px rgba(51, 65, 85, 0.07)`
4. **Layer 3 (Modals, Flyouts & Menus):** Pure White elevated surfaces surrounded by a smooth atmospheric blur:
   `box-shadow: 0 12px 32px rgba(51, 65, 85, 0.12), 0 2px 6px rgba(51, 65, 85, 0.04)`

### Focus Glows
Interactive controls (inputs, buttons) use brand-tinted ambient rings rather than generic blue browser rings:
`box-shadow: 0 0 0 0.2rem rgba(91, 130, 102, 0.16)`

## Shapes

The design uses balanced, rounded geometry (`roundedness: 2`) to balance friendly, approachable curves with structured dashboard precision.

### Geometric Application
- **Buttons & Form Fields:** Standard `0.5rem` (`rounded-md`) corner radius.
- **Cards, Modals & Metric Panels:** Generous `0.75rem` to `1rem` (`rounded-lg` / `rounded-xl`) rounding to soften high-density information cards.
- **Pills & Badges:** Fully rounded (`9999px`) pill structures for classification badges, tags, and status chips, visually distinguishing them from rectangular data blocks.
- **Avatar Badges:** Fully circular (`50%` radius) containers for profile images and initial monograms.

## Components

### Buttons
- **Primary:** Solid Calming Sage Green (`#5B8266`) background with white text. `0.5rem` radius, padding `0.625rem 1.25rem`. On hover: `#4E7257` with ambient sage glow (`0 4px 10px rgba(91, 130, 102, 0.25)`).
- **Secondary / Outline:** Transparent fill with a 1.5px border in `#CBD5E1` or `#5B8266`. Text matches the border color. On hover: transitions smoothly to a pastel container fill (`#E3EDE6`).
- **Destructive:** Soft coral tint (`#DC3545` or `#FEE2E2` container with `#7F1D1D` text) reserved for deletions.

### Input Fields & Search Bars
- **Surface:** Pure White (`#FFFFFF`) with 1px border in `#CBD5E1` and `0.5rem` radius.
- **Typography:** Body base in `#334155`; placeholders in `#6C757D` at 45% opacity.
- **Focus:** Border transitions to `#5B8266` with a soft sage ring (`0 0 0 0.2rem rgba(91, 130, 102, 0.15)`).
- **Search Compound Component:** Integrated input group with an icon badge prefix, text input, and an inline group filtering dropdown.

### Cards (Contact & KPI)
- **Contact Card:** Crisp White container with a 1px outline in `#E2E8F0`, `0.75rem` radius, and Layer 1 ambient shadow. Features contact name in Deep Slate, group pill, amber favorite toggle, icon-prefixed phone and birthday info, and a hover lift to Layer 2.
- **KPI Summary Card:** Contains an oversized 60x60px rounded icon badge in pastel tints (sage, amber, lavender) paired with a bold `stat-metric` counter.

### Chips & Badges
- **Group Badges:** Lavender tint (`#EDE8F5`) container with deep lavender text (`#312747`) and full pill curvature (`rounded-pill`).
- **Tag Chips:** Off-white container (`#F8FAFC`) with hairline border `#E2E8F0`, slate text (`#475569`), and subtle `+` affordance for adding tags.
- **Favorite Star:** Interactive toggle button shifting between muted slate outline (`#94A3B8`) and warm amber fill (`#D97706`).

### Checkboxes & Radio Buttons
- **Base:** 1px border in `#CBD5E1` on white surface with `0.25rem` radius for checkboxes, circular for radios.
- **Checked State:** Background fill in Sage Green (`#5B8266`) with crisp white interior iconography.

### Lists & Tables
- **Table Container:** Pure White container with rounded top and bottom perimeters.
- **Header Row:** Muted Cream (`#F2EFE8`) background with uppercase `label-caps` in `#64748B`.
- **Data Rows:** Separated by hairline borders (`#E2E8F0`). On row hover: background transitions to warm cream tint (`#F7F5F0`).