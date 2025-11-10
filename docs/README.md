# AiChemist Transmutation Codex - Documentation

**Version:** 1.0.0
**Last Updated:** October 22, 2025

---

## 📚 Documentation Structure

### For End Users

**Essential Reading:**

- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete user manual with installation, usage, and troubleshooting
- **[FAQ.md](FAQ.md)** - Frequently asked questions (50+ Q&A)
- **[PRIVACY_POLICY.md](PRIVACY_POLICY.md)** - Privacy policy and data handling
- **[TERMS_OF_SERVICE.md](TERMS_OF_SERVICE.md)** - Terms of service and licensing
- **[EULA.md](EULA.md)** - End-user license agreement

### For Developers & Deployment

**Production Deployment:**

- **[PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)** - Complete deployment guide for all platforms
- **[PRODUCTION_READINESS_FINAL_STATUS.md](PRODUCTION_READINESS_FINAL_STATUS.md)** - Detailed status of production readiness
- **[PRODUCTION_READINESS_COMPLETE.md](PRODUCTION_READINESS_COMPLETE.md)** - Final completion summary

### Technical Documentation

**API & Code Documentation:**

- **[source/](source/)** - Sphinx documentation source files
- **[build/](build/)** - Built HTML documentation (run `make html` to generate)

**Build & Setup Scripts:**

- `build_docs.py` - Script to build Sphinx documentation
- `generate_api_docs.py` - Auto-generate API documentation
- `Makefile` / `make.bat` - Sphinx build commands

### Additional Resources

**Guides:**

- [guides/](guides/) - Specific setup guides (Tesseract, Ghostscript, Pandoc, etc.)

**Troubleshooting:**

- [troubleshooting/](troubleshooting/) - Known issues and solutions

**Archive:**

- [archive/](archive/) - Older documentation and development notes

**Completed Milestones:**

- [completed/](completed/) - Historical implementation summaries

---

## 🚀 Quick Start

### For Users

Start with **[USER_GUIDE.md](USER_GUIDE.md)** for installation and usage instructions.

### For Developers

1. Read **[PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)**
2. Check **[PRODUCTION_READINESS_COMPLETE.md](PRODUCTION_READINESS_COMPLETE.md)** for current status
3. Review build scripts in `../scripts/build/`

### For Legal/Compliance

- **[PRIVACY_POLICY.md](PRIVACY_POLICY.md)** - GDPR-compliant privacy policy
- **[TERMS_OF_SERVICE.md](TERMS_OF_SERVICE.md)** - Legal terms
- **[EULA.md](EULA.md)** - End-user agreement

---

## 📖 Building API Documentation

To build the full API documentation:

```bash
# Install Sphinx and dependencies
pip install sphinx sphinx-rtd-theme

# Build HTML docs
cd docs
make html

# View docs
# Open docs/build/html/index.html in your browser
```

Or use the Python scripts:

```bash
python docs/build_docs.py
python docs/generate_api_docs.py
```

---

## 📝 Documentation Guidelines

When updating documentation:

1. **User-facing docs** (USER_GUIDE.md, FAQ.md) - Use simple, clear language
2. **Legal docs** (PRIVACY_POLICY.md, TERMS_OF_SERVICE.md, EULA.md) - Review with legal counsel before changes
3. **Technical docs** (guides, API docs) - Include code examples and clear steps
4. **Keep in sync** - Update version numbers and dates when making changes

---

## 🔗 External Links

- **Website:** <https://aichemist.app>
- **Support:** <support@aichemist.app>
- **GitHub:** <https://github.com/savagelysubtle/AiChemistTransmutations>
- **Purchase:** <https://aichemist.gumroad.com/l/transmutation-codex>

---

## 📞 Contact

**Developer:** Shaun (@savagelysubtle)
**Email:** <simpleflowworks@gmail.com>
**Support:** <support@aichemist.app>

---

**Last Updated:** October 22, 2025
**Documentation Version:** 1.0.0
