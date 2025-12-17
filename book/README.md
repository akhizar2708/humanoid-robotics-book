# Frontend - AI-Driven Humanoid Robotics Book

Interactive technical book built with Docusaurus 3.x, featuring an embedded AI-powered RAG chatbot for answering questions about humanoid robotics.

## Overview

This frontend provides:
- **Static book site** with 4 modules on humanoid robotics
- **MDX content** supporting code blocks, diagrams, and React components
- **Embedded chatbot widget** with global and selected-text query modes
- **Hot reload development** for rapid content authoring
- **GitHub Pages deployment** for free hosting

## Tech Stack

- **Docusaurus** 3.x - React-based static site generator
- **React** 18+ - UI framework
- **TypeScript** - Type-safe JavaScript
- **@chatscope/chat-ui-kit-react** - Chatbot UI components
- **Prism** - Syntax highlighting

## Setup

### Prerequisites

- Node.js 18+ (LTS recommended)
- npm 9+ or yarn 1.22+
- Git

### Installation

```bash
# Install dependencies
npm install

# Or with yarn
yarn install
```

### Environment Variables

Create a `.env` file in the `book/` directory:

```env
# Backend API URL
REACT_APP_API_URL=http://localhost:8000
```

For production (GitHub Pages):

```env
REACT_APP_API_URL=https://your-backend.onrender.com
```

## Running Locally

### Development Mode (Hot Reload)

```bash
npm start
```

Opens http://localhost:3000 with hot reload enabled. Changes to `.md` or `.mdx` files will update the browser automatically.

### Production Build

```bash
npm run build
```

Generates static files in `build/` directory.

### Serve Production Build Locally

```bash
npm run serve
```

Serves the production build at http://localhost:3000 for testing before deployment.

## Project Structure

```
book/
├── docs/                    # Book content (MDX files)
│   ├── module-1/            # Module 1: The Robotic Nervous System
│   │   ├── _category_.json
│   │   ├── chapter-1.md
│   │   ├── chapter-2.md
│   │   └── chapter-3.md
│   ├── module-2/            # Module 2: Perception and Computer Vision
│   ├── module-3/            # Module 3: Motion Planning and Control
│   └── module-4/            # Module 4: Integration and Deployment
├── src/
│   ├── components/
│   │   └── ChatbotWidget/   # Embedded chatbot component
│   │       ├── ChatbotWidget.tsx
│   │       ├── ChatbotWidget.module.css
│   │       └── index.ts
│   ├── theme/
│   │   └── Root.tsx         # Global theme wrapper
│   └── css/
│       └── custom.css       # Custom styling
├── static/
│   └── img/                 # Static assets (logo, images)
├── docusaurus.config.js     # Docusaurus configuration
├── sidebars.js              # Sidebar configuration
├── package.json
└── README.md                # This file
```

## Content Authoring

### Creating a New Chapter

1. **Create the file**: `docs/module-X/chapter-Y.md`

2. **Add frontmatter**:

```markdown
---
title: Chapter Title
sidebar_position: 1
---

# Chapter Title

Your content here...
```

3. **Use MDX features**:

```markdown
## Code Blocks with Syntax Highlighting

```python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
        self.get_logger().info('Hello ROS 2!')
\`\`\`

## Admonitions

:::tip
This is a helpful tip!
:::

:::warning
Be careful with this!
:::

:::danger
This could break things!
:::

## Tables

| Feature | ROS 1 | ROS 2 |
|---------|-------|-------|
| Middleware | Custom | DDS |
| Python | 2.7 | 3.6+ |
```

### Content Guidelines

- **Frontmatter is required**: Every `.md` file must have `title` and `sidebar_position`
- **Use H2 for sections**: Start content with `##`, not `#` (H1 is the page title)
- **Code blocks need language**: Always specify language for syntax highlighting
- **Image paths are relative**: `![Alt text](./image.png)` or absolute `/img/image.png`
- **No HTML in MDX** (mostly): Use Markdown/MDX syntax when possible
- **Escape special characters**: Use `&lt;` for `<` in tables to avoid JSX parsing errors

### Adding Images

1. Place images in `static/img/` or next to the `.md` file
2. Reference in Markdown:

```markdown
![Robot diagram](/img/module-1/robot-diagram.png)

Or relative to file:
![Robot diagram](./robot-diagram.png)
```

### Module Organization

Each module directory needs a `_category_.json`:

```json
{
  "label": "Module 1: The Robotic Nervous System",
  "position": 1,
  "link": {
    "type": "generated-index",
    "description": "Introduction to ROS 2 fundamentals"
  }
}
```

## Chatbot Widget

The embedded chatbot appears in the bottom-right corner of every page.

### Features

- **Global queries**: Ask questions across the entire book
- **Selected-text queries**: Highlight text, then ask for clarification
- **Citations**: Clickable links to source chapters
- **Session tracking**: Conversations persist during a browser session

### Using Selected-Text Mode

1. Highlight any text on the page
2. Click the chatbot widget (a badge appears when text is selected)
3. Ask your question - it will search within the selected context

### Widget Configuration

Edit `src/components/ChatbotWidget/ChatbotWidget.tsx` to customize:
- Welcome message
- API endpoint
- UI styling
- Error handling

## Customization

### Theme Colors

Edit `src/css/custom.css`:

```css
:root {
  --ifm-color-primary: #667eea;
  --ifm-color-primary-dark: #4c63e8;
  /* ... */
}

[data-theme='dark'] {
  --ifm-color-primary: #8099ec;
  /* ... */
}
```

### Logo

Replace `static/img/logo.svg` with your logo (SVG or PNG).

Update `docusaurus.config.js`:

```js
navbar: {
  logo: {
    alt: 'Your Logo Alt Text',
    src: 'img/logo.svg',
  },
}
```

### Footer

Edit `docusaurus.config.js`:

```js
footer: {
  style: 'dark',
  links: [
    {
      title: 'Links',
      items: [
        { label: 'GitHub', href: 'https://github.com/...' },
      ],
    },
  ],
  copyright: `Copyright © ${new Date().getFullYear()} Your Name.`,
}
```

### Fonts

Add custom fonts in `src/css/custom.css`:

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

:root {
  --ifm-font-family-base: 'Inter', sans-serif;
}
```

## Deployment

### GitHub Pages (Automated)

1. Update `docusaurus.config.js`:

```js
url: 'https://your-username.github.io',
baseUrl: '/repository-name/',
organizationName: 'your-username',
projectName: 'repository-name',
```

2. Push to GitHub - deployment happens automatically via GitHub Actions (see `.github/workflows/deploy-book.yml`)

### Manual Deployment

```bash
# Build the site
npm run build

# Deploy to GitHub Pages
GIT_USER=your-username npm run deploy
```

### Other Hosting Platforms

**Netlify**:
- Build command: `npm run build`
- Publish directory: `build`

**Vercel**:
- Framework preset: Docusaurus
- Build command: `npm run build`
- Output directory: `build`

## Development Tips

### Hot Reload Not Working?

- Ensure you're using `npm start` (not `npm run build`)
- Check that files are saved (some editors don't auto-save)
- Restart the dev server

### Build Failing?

Common issues:
- **Broken links**: Fix links in `.md` files or set `onBrokenLinks: 'warn'` in config
- **Missing frontmatter**: Every `.md` needs `title` at minimum
- **JSX parse errors**: Escape `<` in Markdown tables (`&lt;`)

### Slow Build Times?

- Clear the cache: `rm -rf .docusaurus`
- Reduce image sizes (compress PNGs, convert to WebP)
- Use pagination for large sidebars

## Testing

### Visual Testing

```bash
npm start
# Manually test:
# - All pages load
# - Chatbot opens/closes
# - Code blocks render with syntax highlighting
# - Images load
# - Links work
```

### Accessibility

```bash
npm run build
npm run serve
# Run Lighthouse audit in Chrome DevTools
```

### Cross-Browser

Test in:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### Mobile Responsive

Test at these breakpoints:
- 320px (mobile small)
- 768px (tablet)
- 1024px (desktop)

## Troubleshooting

### "Module not found" errors

```bash
rm -rf node_modules package-lock.json
npm install
```

### Chatbot not connecting

1. Check `.env` has correct `REACT_APP_API_URL`
2. Verify backend is running: `curl http://localhost:8000/health`
3. Check browser console for CORS errors

### Syntax highlighting not working

Ensure language is listed in `docusaurus.config.js`:

```js
prism: {
  additionalLanguages: ['python', 'bash', 'json', 'yaml', 'sql'],
}
```

## Performance Optimization

- **Image optimization**: Use WebP format, compress images
- **Code splitting**: Docusaurus does this automatically
- **Lazy loading**: Images lazy load by default
- **CDN**: GitHub Pages uses CDN automatically

## Contributing

### Content Contributions

1. Fork the repository
2. Create a branch: `git checkout -b module-X-chapter-Y`
3. Add/edit `.md` files in `docs/`
4. Test locally: `npm start`
5. Submit a PR

### UI Contributions

1. Modify components in `src/components/`
2. Update styles in `src/css/custom.css`
3. Test build: `npm run build && npm run serve`
4. Submit a PR

## Resources

- [Docusaurus Documentation](https://docusaurus.io/docs)
- [MDX Documentation](https://mdxjs.com/)
- [Infima CSS Framework](https://infima.dev/)
- [React Documentation](https://react.dev/)

## License

MIT License - see [../LICENSE](../LICENSE)
