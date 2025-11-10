# Deployment Checklist for AiChemist Transmutation Codex

Use this checklist to ensure everything is configured correctly before launching your paid application.

## Phase 1: Security & Keys ✅

### RSA Key Pair Generation

- [ ] Run `python scripts/generate_rsa_keys.py`
- [ ] Verify `scripts/keys/private_key.pem` created
- [ ] Verify `scripts/keys/public_key.pem` created
- [ ] Copy private key to secure storage (password manager/HSM)
- [ ] **Delete** `scripts/keys/private_key.pem` from disk
- [ ] Copy public key content to `src/transmutation_codex/core/licensing/crypto.py`
- [ ] Update `_public_key_pem` constant with your public key
- [ ] Test with `python scripts/generate_dev_license.py`
- [ ] Verify dev license activates successfully

### Gitignore Configuration

- [ ] Verify `.gitignore` includes `scripts/keys/`
- [ ] Verify `.gitignore` includes `*.pem`
- [ ] Verify `.gitignore` includes `.env`
- [ ] Verify `.gitignore` includes `.env.local`
- [ ] Run `git status` to ensure no secrets are staged
- [ ] **Never commit private keys!**

## Phase 2: Database Setup 🗄️

### Supabase Project Creation

- [ ] Create account at [supabase.com](https://supabase.com)
- [ ] Create new project (note: takes ~2 min to provision)
- [ ] Note Project URL: `https://[your-id].supabase.co`
- [ ] Note ANON key from Settings > API
- [ ] Note SERVICE_ROLE key from Settings > API (keep secret!)

### Database Schema

- [ ] Run `python scripts/setup_supabase_schema.py --print-only`
- [ ] Copy SQL output
- [ ] Open Supabase Dashboard > SQL Editor
- [ ] Paste and execute schema SQL
- [ ] Verify `licenses` table created
- [ ] Verify `activations` table created
- [ ] Verify `usage_logs` table created
- [ ] Verify indexes created (check table details)

### Row Level Security (RLS)

- [ ] Execute RLS policies from `docs/PRODUCTION_SETUP.md`
- [ ] Enable RLS on `licenses` table
- [ ] Enable RLS on `activations` table
- [ ] Enable RLS on `usage_logs` table
- [ ] Test anon user can read active licenses
- [ ] Test anon user can insert activations
- [ ] Test anon user can log usage
- [ ] Test anon user cannot modify/delete licenses

### Environment Configuration

- [ ] Copy `.env.example` to `.env`
- [ ] Update `SUPABASE_URL` in `.env`
- [ ] Update `SUPABASE_ANON_KEY` in `.env`
- [ ] **DO NOT** commit `.env` file
- [ ] For server/webhook: Set `SUPABASE_SERVICE_KEY` (keep secret!)

## Phase 3: Payment Integration 💳

### Payment Provider Setup

**If using Gumroad:**

- [ ] Create account at [gumroad.com](https://gumroad.com)
- [ ] Set up products:
  - [ ] Basic License - $49/year
  - [ ] Professional License - $99/year
  - [ ] Enterprise License - $299/year (or contact)
- [ ] Configure product settings (delivery, variants)
- [ ] Enable webhook in Settings > Advanced
- [ ] Set webhook URL: `https://[your-domain]/webhooks/gumroad`
- [ ] Note webhook secret for signature verification
- [ ] Test webhook with Gumroad's test mode

**If using Stripe:**

- [ ] Create account at [stripe.com](https://stripe.com)
- [ ] Create products and prices
- [ ] Set up Stripe Checkout or Payment Links
- [ ] Configure webhook endpoint
- [ ] Add webhook signing secret to environment variables
- [ ] Test with Stripe test mode

### License Generation Webhook

- [ ] Implement webhook handler (see `docs/PRODUCTION_SETUP.md`)
- [ ] Deploy webhook to server (AWS Lambda, Vercel, etc.)
- [ ] Verify webhook is publicly accessible via HTTPS
- [ ] Implement signature verification
- [ ] Test license generation on test purchase
- [ ] Verify license is stored in Supabase
- [ ] Set up email delivery (SendGrid, Mailgun, etc.)
- [ ] Test customer receives license email
- [ ] Implement error handling and logging
- [ ] Set up monitoring/alerts for webhook failures

### Update Purchase URL in GUI

- [ ] Open `gui/src/renderer/components/LicenseDialog.tsx`
- [ ] Update `purchaseUrl` constant (line ~57)
- [ ] Replace placeholder with actual Gumroad/Stripe URL
- [ ] Test "Purchase License" button opens correct URL

## Phase 4: Application Testing 🧪

### Backend Tests

- [ ] Run `pytest` - all tests pass
- [ ] Run `pytest tests/test_licensing_system.py` - licensing tests pass
- [ ] Test trial mode: 10 conversions, then blocked
- [ ] Test MD→PDF works in trial mode
- [ ] Test PDF→MD blocked in trial mode
- [ ] Test file size limit (5MB) in trial mode

### License Activation Tests

- [ ] Generate test license: `python scripts/generate_license.py`
- [ ] Start GUI: `cd gui && npm run dev`
- [ ] Click "Activate License" button
- [ ] Enter test license key
- [ ] Verify activation succeeds
- [ ] Check Supabase dashboard for activation record
- [ ] Test all converters work with license
- [ ] Test file size limit removed with license
- [ ] Test license survives app restart

### Offline Mode Tests

- [ ] Disconnect from internet
- [ ] Generate offline license (no Supabase needed)
- [ ] Activate offline license
- [ ] Verify activation works without internet
- [ ] Test conversions work offline
- [ ] Verify no usage logging (expected behavior)
- [ ] Reconnect internet
- [ ] Verify online features resume

### Multi-Machine Tests

- [ ] Activate license on first machine
- [ ] Activate same license on second machine
- [ ] For Basic (1 activation): verify second machine rejected
- [ ] For Professional (3 activations): verify up to 3 work
- [ ] Test deactivation on one machine frees slot
- [ ] Verify remote deactivation in Supabase dashboard

## Phase 5: Production Build 🏗️

### Python Package Build

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md`
- [ ] Run `uv sync --all-groups`
- [ ] Run `pytest` - all tests pass
- [ ] Run `ruff check` - no errors
- [ ] Build: `python -m build`
- [ ] Verify `dist/` contains wheel and tar.gz

### Electron App Build

- [ ] Update version in `gui/package.json`
- [ ] Update version in `package.json` (root)
- [ ] Run `cd gui && npm install`
- [ ] Run `npm run build`
- [ ] Run `npm run electron:build`
- [ ] Verify installers created in `gui/dist-electron/`
- [ ] Test installer on clean machine

### Code Signing

**Windows:**

- [ ] Obtain Authenticode certificate
- [ ] Sign executable: `signtool sign /f cert.pfx /p password ...`
- [ ] Verify signature: `signtool verify /pa AiChemist-Setup.exe`
- [ ] Test installer doesn't trigger SmartScreen warnings

**macOS:**

- [ ] Enroll in Apple Developer Program
- [ ] Obtain Developer ID Application certificate
- [ ] Sign app: `codesign --deep --force --sign "Dev ID" AiChemist.app`
- [ ] Verify signature: `codesign --verify --verbose AiChemist.app`
- [ ] Notarize with Apple: `xcrun altool --notarize-app ...`
- [ ] Staple notarization: `xcrun stapler staple AiChemist.app`
- [ ] Test app runs without Gatekeeper warnings

**Linux:**

- [ ] Build AppImage, deb, and rpm packages
- [ ] Test on Ubuntu, Fedora, Arch
- [ ] Verify dependencies are bundled correctly

## Phase 6: Documentation 📚

### User Documentation

- [ ] Update `README.md` with installation instructions
- [ ] Document system requirements
- [ ] Add screenshots of GUI
- [ ] Document all conversion types
- [ ] Document license activation process
- [ ] Document trial limitations
- [ ] Add FAQ section
- [ ] Add troubleshooting section

### Developer Documentation

- [ ] Update `AGENTS.md` for future maintainers
- [ ] Update `CLAUDE.md` with new features
- [ ] Document API changes in `docs/`
- [ ] Generate API docs: `cd docs && python build_docs.py`
- [ ] Review generated HTML docs

### Legal Documents

- [ ] Create `LICENSE_AGREEMENT.md` with terms of use
- [ ] Define refund policy (e.g., 30-day money-back)
- [ ] Create `PRIVACY_POLICY.md` for GDPR compliance
- [ ] Add data retention policy
- [ ] Add data export/deletion procedures
- [ ] Review with legal counsel (recommended)

## Phase 7: Marketing & Distribution 🚀

### Website Setup

- [ ] Create landing page with features
- [ ] Add pricing table
- [ ] Add screenshots/demo video
- [ ] Add testimonials (if available)
- [ ] Implement download page
- [ ] Add support/contact form
- [ ] Set up analytics (Google Analytics, Plausible, etc.)
- [ ] Set up SEO (meta tags, sitemap, etc.)

### Product Listing

- [ ] Create Gumroad product listing
- [ ] Write compelling product description
- [ ] Upload product screenshots
- [ ] Set pricing tiers
- [ ] Configure license delivery
- [ ] Test purchase flow end-to-end

### Marketing Materials

- [ ] Create promotional graphics
- [ ] Write launch announcement
- [ ] Prepare email to existing users (if any)
- [ ] Create social media posts
- [ ] Write blog post about features
- [ ] Prepare Product Hunt launch (if applicable)

### SEO & Discovery

- [ ] Submit to software directories:
  - [ ] AlternativeTo
  - [ ] SourceForge (if open-source)
  - [ ] Capterra
  - [ ] G2
- [ ] Create GitHub repository (if open-source/public)
- [ ] Add project to relevant subreddits
- [ ] List on Indie Hackers

## Phase 8: Monitoring & Support 📊

### Monitoring Setup

- [ ] Set up Supabase monitoring/alerts
- [ ] Monitor license activation rate
- [ ] Monitor trial-to-paid conversion rate
- [ ] Monitor usage by converter type
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Set up uptime monitoring for webhook

### Support Channels

- [ ] Set up support email: support@[your-domain].com
- [ ] Create support portal or ticket system
- [ ] Prepare canned responses for common issues
- [ ] Set up Discord/Slack community (optional)
- [ ] Create knowledge base/FAQ

### Analytics Dashboard

- [ ] Create Supabase analytics queries (see `PRODUCTION_SETUP.md`)
- [ ] Set up Metabase/Grafana dashboard (optional)
- [ ] Track key metrics:
  - [ ] Daily active users
  - [ ] Trial conversions
  - [ ] License activations
  - [ ] Revenue (via payment provider)
  - [ ] Churn rate

### Alerts Configuration

- [ ] Alert on webhook failures
- [ ] Alert on license validation errors spike
- [ ] Alert on trial abuse patterns
- [ ] Alert on payment processor issues
- [ ] Alert on server/database downtime

## Phase 9: Legal & Compliance ⚖️

### GDPR Compliance (EU)

- [ ] Implement data export functionality
- [ ] Implement data deletion functionality
- [ ] Add consent checkboxes for analytics
- [ ] Document data retention periods
- [ ] Appoint DPO if required (>250 employees)
- [ ] Register with supervisory authority if required

### Tax Compliance

- [ ] Configure sales tax collection (if in US)
- [ ] Configure VAT collection (if selling in EU)
- [ ] Gumroad handles this automatically
- [ ] Stripe: enable Stripe Tax
- [ ] Consult with accountant for tax requirements

### Business Registration

- [ ] Register business entity (LLC, Ltd, etc.)
- [ ] Obtain EIN/tax ID
- [ ] Open business bank account
- [ ] Set up accounting software (QuickBooks, Xero)

## Phase 10: Launch Day 🎉

### Pre-Launch (24 hours before)

- [ ] Final test of entire purchase flow
- [ ] Verify webhook is working
- [ ] Verify emails are being sent
- [ ] Check all download links work
- [ ] Verify pricing is correct
- [ ] Clear any test data from database
- [ ] Prepare launch announcement

### Launch

- [ ] Make product public on Gumroad/payment processor
- [ ] Publish website/landing page
- [ ] Send launch email (if you have list)
- [ ] Post on social media
- [ ] Post on Product Hunt (if planned)
- [ ] Post on relevant communities (Reddit, HN, etc.)
- [ ] Monitor support channels closely

### Post-Launch (First Week)

- [ ] Monitor for critical bugs
- [ ] Respond to all support requests within 24h
- [ ] Monitor activation success rate
- [ ] Check webhook logs for errors
- [ ] Review user feedback
- [ ] Address urgent issues ASAP
- [ ] Thank early customers
- [ ] Request reviews/testimonials

## Emergency Contacts 🚨

Keep these handy for launch day:

- **Payment Processor Support:** [Link]
- **Hosting Provider Support:** [Link]
- **Domain Registrar:** [Link]
- **Supabase Support:** <help@supabase.com>
- **Your Developer:** [Contact]
- **Your Accountant:** [Contact]
- **Your Lawyer:** [Contact]

## Rollback Plan 🔄

If critical issues are discovered:

1. [ ] Disable new purchases on Gumroad/Stripe
2. [ ] Put maintenance notice on website
3. [ ] Email affected customers
4. [ ] Issue refunds if necessary
5. [ ] Fix critical issues
6. [ ] Deploy hotfix
7. [ ] Test thoroughly
8. [ ] Re-enable purchases
9. [ ] Notify customers issue is resolved

## Success Metrics 📈

Track these KPIs:

- **Week 1 Targets:**
  - [ ] 50 downloads
  - [ ] 10% trial-to-paid conversion
  - [ ] <1% refund rate
  - [ ] <5% support ticket rate

- **Month 1 Targets:**
  - [ ] 200 downloads
  - [ ] 20 paid customers
  - [ ] $1,000 MRR
  - [ ] 4+ star average rating

- **Month 3 Targets:**
  - [ ] 500 downloads
  - [ ] 50 paid customers
  - [ ] $3,000 MRR
  - [ ] Featured on 2+ software directories

## Notes

- **Don't rush launch:** It's better to delay than to launch with critical bugs
- **Start small:** Focus on core features that work perfectly
- **Listen to users:** Early feedback is invaluable
- **Iterate quickly:** Plan for frequent updates in the first month
- **Celebrate milestones:** First sale, first 10 customers, first $1k MRR!

---

**Ready to launch?** Check every box above, then go for it! 🚀

Good luck! 🍀
