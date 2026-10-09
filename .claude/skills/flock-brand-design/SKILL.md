---
name: flock-brand-design
description: >
  Flock IT brand identity: official color palette, gradients and logo files, plus how to apply them in the app UI (Streamlit theme, CSS, logos).
  Trigger: When building or styling any UI, choosing colors, adding logos/branding, theming Streamlit, or creating visual assets for Flock.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## When to Use

- Styling the chat UI or any screen of the app
- Configuring the Streamlit theme (`.streamlit/config.toml`)
- Adding the Flock logo, favicon or page icon
- Choosing colors for buttons, headers, highlights, chat bubbles
- Creating slides, diagrams or images for the Flock demo

## Critical Patterns

### Precedence over other design skills

This skill is the brand source of truth and OVERRIDES any generic design skill or default styling:

- Do NOT derive a new palette per brief — the palette below is fixed.
- The orange↔purple gradients are the official brand, NOT "AI purple glow" slop. Keep them.
- Generic skills may still guide layout, states, accessibility and copy, but never color or logos.

### Official palette — the ONLY brand colors allowed

| Token | Hex | Role |
|-------|-----|------|
| `flock-orange` | `#FF5102` | Accent: highlights, icons, borders, large CTAs |
| `flock-purple` | `#7F07C5` | Primary: buttons, links, active states |
| `flock-deep-purple` | `#44016B` | Dark surfaces: header, sidebar, footer, headings |

Neutrals (not brand colors, allowed for readability): white `#FFFFFF`, light surface `#F7F4FA`, body text `#1F1F1F`.

**NEVER** invent other hues (no blue, green, generic red). If a state color is needed (error/success), keep it subtle and let brand colors dominate.

### Official gradients (always left → right, in this order)

| Name | CSS |
|------|-----|
| `orange-to-purple` | `linear-gradient(90deg, #FF5102 0%, #7F07C5 100%)` |
| `deep-purple-to-orange` | `linear-gradient(90deg, #44016B 0%, #FF5102 100%)` |
| `purple-to-deep-purple` | `linear-gradient(90deg, #7F07C5 0%, #44016B 100%)` |

Use gradients for hero/header bands and accent bars — NOT behind long body text.

### Contrast rules (WCAG AA)

| Combination | Ratio | Use |
|-------------|-------|-----|
| White on `#44016B` | ~13:1 | Any text ✅ |
| White on `#7F07C5` | ~7.7:1 | Any text ✅ |
| White on `#FF5102` | ~3.3:1 | ONLY large/bold text (≥18px bold or ≥24px) ⚠️ |
| `#FF5102` text on white | ~3.3:1 | Never for body text ❌ |

### Logos

| File | When |
|------|------|
| `assets/flock-logo-color.png` | Default — light backgrounds |
| `assets/flock-logo-black.png` | Monochrome / print / when color clashes |
| `assets/flock-isotipo.png` | Small spaces: favicon, page icon, chat avatar, collapsed sidebar |
| `assets/flock-palette.png` | Visual reference of the palette (do not render in the app) |

- Never recolor, stretch, rotate or add effects to the logos.
- Never place the color logo over the gradients or over `#FF5102`/`#7F07C5` (it disappears) — use a white surface behind it.
- Keep clear space around the logo of at least the height of one isotype "corner".
- The palette hex values above are the source of truth for UI; logo PNGs are used as-is (their pixels may differ slightly due to compression).

## Code Examples

### Streamlit theme — `.streamlit/config.toml`

```toml
[theme]
base = "light"
primaryColor = "#7F07C5"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F7F4FA"
textColor = "#1F1F1F"
```

### Logos and page icon

```python
import streamlit as st

st.set_page_config(page_title="Flock Talent Agent", page_icon="assets/flock-isotipo.png")
st.logo("assets/flock-logo-color.png", icon_image="assets/flock-isotipo.png")
st.chat_message("assistant", avatar="assets/flock-isotipo.png").write("¡Hola!")
```

### Gradient header band (custom CSS)

```python
st.markdown(
    """
    <style>
    .flock-header {
        background: linear-gradient(90deg, #44016B 0%, #FF5102 100%);
        color: #FFFFFF;
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1.5rem;
    }
    </style>
    <div class="flock-header">Agente de Gestión de Talentos</div>
    """,
    unsafe_allow_html=True,
)
```

## Commands

```bash
# Copy brand assets into the app (run from repo root)
mkdir -p assets && cp .claude/skills/flock-brand-design/assets/flock-*.png assets/
```

## Resources

- **Logos & palette**: See [assets/](assets/)
