# Multi-Tenant Client Onboarding System — Odoo

A production-deployed client onboarding portal built on Odoo, serving three separate companies from a single instance. Each company gets a fully branded experience — logo, colours, contact details, and relevant form fields — all driven by one Python controller.

## The Problem

A business group operating three companies (logistics, security, and technology) needed a way to onboard clients and subcontractors without:
- Manual data entry from email or PDF forms
- Separate systems per company
- Requiring clients to log in to Odoo

## The Solution

A token-authenticated public portal where:
1. A unique URL is generated per onboarding record (server action in Odoo)
2. The client opens the link — no login required
3. They fill in their details, upload documents, and submit
4. All data lands directly in the Odoo record — no manual handling

## Architecture

```
Odoo Server Action
  └── Generates unique token per record
  └── Builds public URL: /onboarding/<token>

Public Portal (this controller)
  ├── GET  /onboarding/<token>         → renders branded form
  └── POST /onboarding/<token>/submit  → saves submission to Odoo record

Form handles three field types:
  ├── Text fields    → written only if submitted (no overwriting with blanks)
  ├── Boolean fields → always written (handles unchecked checkboxes correctly)
  └── Binary fields  → base64-encoded file uploads stored directly on record
```

## Key Technical Decisions

**Multi-company context** — Odoo restricts record access by company by default. The controller explicitly sets `allowed_company_ids` so the public route can reach records regardless of which company they belong to.

**Token-based auth** — No login required. Each record has a unique token; the URL is only shared with the intended recipient. Invalid tokens return a 404.

**CSRF protection** — POST route uses `csrf=True`. The token is injected into the form via QWeb template and validated automatically by Odoo.

**Boolean handling** — HTML checkboxes only appear in POST data when checked. Using `bool(post.get(fname))` ensures unchecked fields write `False` rather than being skipped entirely.

**Single write operation** — All field values are collected into a `vals` dict first, then written to the record in one `record.sudo().write(vals)` call for efficiency.

## Stack

- Python 3 (Odoo 16/17 HTTP controller)
- Odoo QWeb templates (XML)
- Odoo Server Actions
- Bootstrap 5 (frontend form styling)

## Project Structure

```
onboarding_form/
├── controllers/
│   └── main.py          # This file — HTTP controller
├── views/
│   └── templates.xml    # QWeb form and thank you page templates
├── data/
│   └── onboarding_data.xml  # Token field + server action definition
└── __manifest__.py
```

## What I Learned Building This

This was built during my first two weeks learning Python. The concepts that clicked through this project:

- How Odoo's HTTP controller layer works vs standard Python web frameworks
- Why multi-company context needs to be set explicitly on public routes
- The difference between `sudo()` for permission bypass vs normal user context
- How binary file uploads work at the HTTP level (multipart form data → base64)
- Why boolean fields need special handling in HTML form submissions

---

*Built by Mervin T. Oclima — [linkedin.com/in/mervin-oclima](https://linkedin.com/in/mervin-oclima)*
  
