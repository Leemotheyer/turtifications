# Turtifications Documentation

This directory contains the complete documentation for Turtifications, built with Jekyll and designed for GitHub Pages hosting.

## Documentation Structure

```
docs/
├── _config.yml          # Jekyll configuration
├── Gemfile              # Ruby dependencies
├── index.md             # Main documentation homepage
├── getting-started.md   # Installation and setup guide
├── configuration.md     # Configuration and deployment
├── troubleshooting.md   # Troubleshooting guide
├── guides/              # User guides
│   ├── notification-flows.md  # Creating notification flows
│   ├── templates.md           # Using templates
│   └── api.md                 # API usage guide
├── api/                 # API reference
│   └── reference.md     # Complete API documentation
└── reference/           # Reference materials
    └── variables.md     # Template variables reference
```

## Features

- **Complete coverage** of all Turtifications features
- **Step-by-step guides** with practical examples
- **Comprehensive API documentation** with code samples
- **Troubleshooting guide** for common issues
- **Template variables reference** for customization
- **Production deployment** instructions
- **Dark theme** optimized for developers
- **Search functionality** for quick navigation

## Local Development

To run the documentation locally:

1. **Install Ruby and Bundler**
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install ruby-full build-essential zlib1g-dev
   
   # On macOS
   brew install ruby
   ```

2. **Install dependencies**
   ```bash
   cd docs
   bundle install
   ```

3. **Run Jekyll**
   ```bash
   bundle exec jekyll serve
   ```

4. **Open in browser**
   ```
   http://localhost:4000
   ```

## GitHub Pages Setup

To host this documentation on GitHub Pages:

1. **Enable GitHub Pages** in repository settings
2. **Select source**: Deploy from a branch
3. **Choose branch**: `main` (or your default branch)
4. **Select folder**: `/docs`
5. **Save configuration**

The documentation will be available at: `https://yourusername.github.io/turtifications/`

## Customization

### Update Repository Links

Update the repository links in `_config.yml`:

```yaml
# Update these with your actual repository information
aux_links:
  "GitHub Repository":
    - "//github.com/yourusername/turtifications"

gh_edit_repository: "https://github.com/yourusername/turtifications"
```

### Customize Theme

The documentation uses the `just-the-docs` theme. You can customize:

- **Colors**: Modify CSS in `_sass/custom/custom.scss`
- **Navigation**: Update `nav_order` in page front matter
- **Footer**: Change `footer_content` in `_config.yml`
- **Search**: Configure search options in `_config.yml`

### Add New Pages

To add new documentation pages:

1. **Create markdown file** in appropriate directory
2. **Add front matter**:
   ```yaml
   ---
   layout: default
   title: Page Title
   parent: Parent Section (optional)
   nav_order: 5
   ---
   ```
3. **Write content** using standard markdown
4. **Update navigation** links if needed

## Content Guidelines

### Writing Style

- **Use clear, concise language**
- **Provide practical examples** for all features
- **Include code samples** with proper syntax highlighting
- **Add screenshots** for UI-related content
- **Link between related sections**

### Code Examples

Use fenced code blocks with language specification:

````markdown
```bash
# Bash commands
curl http://localhost:5000/api/status
```

```python
# Python code
import requests
response = requests.get("http://localhost:5000/api/status")
```

```yaml
# YAML configuration
name: "Example Flow"
trigger_type: "timer"
url: "https://api.example.com/status"
```
````

### Navigation

The documentation uses hierarchical navigation:

- **Top-level pages**: `nav_order` determines position
- **Child pages**: Use `parent:` to nest under sections
- **Grandchild pages**: Use both `parent:` and `grand_parent:`

Example:
```yaml
---
title: API Reference
parent: API
grand_parent: Guides
nav_order: 1
---
```

## Maintenance

### Regular Updates

1. **Keep examples current** with latest Turtifications features
2. **Update API documentation** when endpoints change
3. **Add new templates** and use cases
4. **Fix broken links** and outdated information
5. **Improve clarity** based on user feedback

### Version Management

For major version releases:

1. **Tag documentation** versions in git
2. **Create version-specific branches** if needed
3. **Update compatibility** information
4. **Archive old versions** if necessary

## Contributing

To contribute to the documentation:

1. **Fork the repository**
2. **Create a feature branch** for your changes
3. **Edit markdown files** in the `docs/` directory
4. **Test locally** with Jekyll
5. **Submit a pull request** with clear description

### Content Checklist

When adding new content:

- [ ] Clear, descriptive title
- [ ] Proper front matter with navigation
- [ ] Table of contents for long pages
- [ ] Working code examples
- [ ] Links to related sections
- [ ] Consistent formatting and style
- [ ] Tested locally with Jekyll

## Troubleshooting

### Common Issues

**Jekyll build fails**
: Check Ruby version and dependencies in `Gemfile`

**Navigation not working**
: Verify `nav_order` and `parent` in front matter

**Search not finding content**
: Ensure pages have proper titles and content structure

**GitHub Pages not updating**
: Check repository settings and build status

### Getting Help

- **Jekyll Documentation**: https://jekyllrb.com/docs/
- **Just the Docs Theme**: https://just-the-docs.github.io/just-the-docs/
- **GitHub Pages**: https://docs.github.com/en/pages
- **Markdown Guide**: https://www.markdownguide.org/

## License

This documentation is part of the Turtifications project and follows the same license terms.