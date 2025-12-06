# Contributing to SEO Gap Analyzer

Thank you for considering contributing to SEO Gap Analyzer! 🎉

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your configuration (sanitized, no API keys!)
- Python version and OS

### Suggesting Enhancements

We love new ideas! Please create an issue with:
- Clear description of the enhancement
- Use case and benefits
- Example configuration or code (if applicable)

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Add docstrings to functions
- Keep functions focused and single-purpose
- Add comments for complex logic
- Use type hints where helpful

### Testing

Before submitting:
- Test with at least 2 different config files
- Ensure all scripts run without errors
- Verify generated reports look correct
- Check that no API keys are exposed

### Configuration Examples

When adding features that require configuration:
- Update `config.example.yaml`
- Add example to README
- Document in configuration section

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/seo-gap-analyzer.git
cd seo-gap-analyzer

# Install dependencies
pip install -r requirements.txt

# Create test config
cp config.example.yaml config.yaml
# Edit config.yaml with test data

# Create .env
cp .env.example .env
# Add your DataForSEO credentials
```

## Questions?

Feel free to open an issue for questions or join discussions!

Thank you for contributing! 🙏
