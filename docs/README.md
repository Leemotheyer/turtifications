# Turtifications Documentation

This directory contains the documentation website for Turtifications, built with Jekyll and the Just the Docs theme.

## GitHub Pages Setup

To enable GitHub Pages for this documentation:

1. Go to your repository's Settings → Pages
2. Under "Source", select "Deploy from a branch"
3. Choose "main" branch and "/docs" folder
4. Click "Save"

## Configuration

The documentation is configured in `_config.yml`:

- **Theme**: Uses `just-the-docs/just-the-docs` remote theme
- **Color Scheme**: Set to `dark` mode
- **Search**: Enabled with full-text search
- **Navigation**: Hierarchical with parent/child relationships

## Local Development

To run the documentation locally:

```bash
cd docs
bundle install
bundle exec jekyll serve
```

## Troubleshooting

If the theme/styling isn't working:

1. **Check Repository Settings**: Ensure GitHub Pages is enabled and pointing to the `/docs` folder
2. **Verify Theme**: The `remote_theme: just-the-docs/just-the-docs` should be in `_config.yml`
3. **Wait for Build**: GitHub Pages can take a few minutes to rebuild after changes
4. **Check Actions**: Look at the "Pages build and deployment" actions for any errors

## Structure

```
docs/
├── _config.yml          # Jekyll configuration
├── Gemfile             # Ruby dependencies
├── index.md            # Home page
├── getting-started.md  # Getting started guide
├── configuration.md    # Configuration guide
├── troubleshooting.md  # Troubleshooting guide
├── api/                # API documentation
│   ├── api.md         # API overview
│   └── reference.md   # API reference
├── guides/            # User guides
└── reference/         # Additional reference materials
```