# Phase 1 Prompt — Backend Foundation & Business Memory

```text
You are a Senior Backend Engineer and System Architect.

Build the backend foundation for an AI-powered SME Business Operating System using FastAPI.

The goal of this phase is NOT AI. It is to build a scalable backend that can support future AI modules.

Tech Stack:

- FastAPI
- SQLAlchemy
- Alembic
- SQLite (easy to migrate later)
- Pydantic
- Python 3.12

Architecture should be production ready.

Create the following folder structure:

backend/
    app.py
    config/
    database/
    models/
    schemas/
    routers/
    services/
    utils/

Implement:

1. Database
- SQLAlchemy models
- Alembic migrations
- Proper relationships

Tables

Company

Customer

Supplier

Product

Invoice

Sales

Inventory

Employee

BusinessEvent

RecommendationHistory

DecisionHistory

Each table should contain realistic business fields.

----------------------------

2. CRUD APIs

Create complete CRUD operations for

Customers

Products

Suppliers

Inventory

Sales

Invoices

Use proper validation.

----------------------------

3. File Upload

Implement

POST /upload/invoice

POST /upload/gst

POST /upload/bank

POST /upload/excel

Store uploaded files.

Don't parse them yet.

----------------------------

4. Dashboard APIs

GET /dashboard

GET /business-health

GET /alerts

GET /timeline

Return realistic dummy values calculated from database.

----------------------------

5. Business Memory

Create a Business Memory service.

It should support

Store Events

Retrieve Events

Company Profile

Business History

Recent Decisions

No AI yet.

Just architecture.

----------------------------

Use dependency injection.

Separate routers, services and models properly.

Write clean code with comments.

Do NOT implement AI.

Only backend foundation.
```

---

# Phase 2 Prompt — Gemma Intelligence + Business Understanding

```text
Continue from Phase 1.

Now implement the AI Intelligence Layer.

Gemma should understand the business rather than simply answer questions.

Tech

FastAPI

Gemma API / Ollama Gemma

PyMuPDF

pdfplumber

pytesseract

Pandas

Implement:

-----------------------------------

1. Document Intelligence

Parse

Invoices

GST Reports

Purchase Orders

Bills

Excel files

Extract

Vendor

Products

GST

Amount

Dates

Invoice Number

Taxes

Convert every document into structured business events.

-----------------------------------

2. Business Memory

Expand Business Memory.

Support

Semantic Memory

Business Facts

Company Profile

Customer Information

Supplier Information

Product Information

Episodic Memory

Business Events

Price Changes

Customer Complaints

Supplier Delays

Decision Memory

Store previous AI recommendations.

-----------------------------------

3. Context Builder

Build a Context Builder.

When the user asks a question

Collect

Recent Events

Business Metrics

Relevant Customers

Relevant Suppliers

Relevant Products

Company Profile

Generate one optimized context object.

This context is passed to Gemma.

-----------------------------------

4. Chat API

POST /chat

Pipeline

User Question

↓

Context Builder

↓

Gemma

↓

Response

-----------------------------------

5. Executive Brief

Generate

Morning Summary

Critical Alerts

Top Opportunities

Business Health Summary

Top 5 Actions

Endpoint

GET /executive-brief

-----------------------------------

Code should be modular.

Business Memory should be reusable.

Avoid hardcoded prompts.

Create PromptBuilder class.
```

---

# Phase 3 Prompt — Predictive Intelligence

```text
Continue from previous phases.

Now implement Predictive Intelligence.

The objective is to predict the future state of the business.

Create separate ML services.

Do not mix ML with FastAPI routes.

Implement

---------------------------------

Revenue Forecast

Input

Sales history

Seasonality

Price

Marketing

Output

Next 90 days revenue

---------------------------------

Cash Flow Forecast

Inputs

Invoices

Expenses

Payroll

GST

Sales

Predict

Cash balance over time

---------------------------------

Demand Forecast

Predict future product demand.

Recommend reorder quantity.

---------------------------------

Customer Risk Model

Predict

Late Payment Probability

Customer Churn

Customer Lifetime Value

---------------------------------

Supplier Risk

Predict

Late Deliveries

Reliability

Price Increase Risk

---------------------------------

Inventory Forecast

Predict

Stockout

Dead Inventory

Reorder Date

---------------------------------

Pricing Recommendation

Recommend

Optimal Price

Expected Profit

Expected Revenue

Demand Impact

---------------------------------

Create APIs

/forecast/revenue

/forecast/cashflow

/forecast/demand

/risk/customers

/risk/suppliers

/pricing

---------------------------------

Each prediction should return

Prediction

Confidence Score

Important Features

Business Impact

Suggested Action

Keep ML modules independent from API layer.
```

---

# Phase 4 Prompt — Multi-Agent Decision Intelligence

```text
Continue from previous phases.

Now implement the Decision Intelligence Engine.

This is the brain of the SME Operating System.

Instead of one AI, implement multiple business agents.

-----------------------------------

Agents

Finance Agent

Operations Agent

Marketing Agent

Supplier Agent

Customer Agent

Risk Agent

CEO Agent

Each agent receives

Business Context

Historical Memory

Predictions

Current Metrics

Each agent returns

Analysis

Recommendations

Confidence

Supporting Evidence

-----------------------------------

CEO Agent

The CEO Agent collects reports from every agent.

It produces

Executive Summary

Top Priorities

Strategic Decisions

Business Risks

Growth Opportunities

-----------------------------------

Decision Engine

Collect

Predictions

Business Memory

Knowledge Graph

Agent Reports

Generate

Prioritized Recommendations

Every recommendation should include

ROI

Risk

Confidence

Supporting Data

Reasoning

-----------------------------------

Digital Twin

Create

POST /simulate

Input

Price Changes

Hiring

Supplier Changes

Inventory Decisions

Loan Decisions

Output

Revenue

Profit

Cash Flow

Risk

Inventory

Business Health

-----------------------------------

Decision Memory

Store

Recommendation

User Action

Business Outcome

Improve future recommendations.

-----------------------------------

Explainability Engine

Every AI recommendation must include

Reason

Evidence

Confidence

Business Impact

Affected Departments

-----------------------------------

Create APIs

/agents

/recommendations

/simulate

/decision-history

/explain

Architecture must be modular.

Each agent should be an independent Python class.

CEO Agent orchestrates every other agent.

Avoid monolithic code.
```

---

# 🚀 Bonus Prompt (Use After All 4 Phases)

Once you've completed all phases, use this to **refactor and polish** the project:

```text
Act as a Principal Software Architect at Google.

Review the entire codebase.

Refactor it into production-quality architecture.

Focus on:

- SOLID principles
- Dependency Injection
- Async FastAPI
- Error Handling
- Logging
- Configuration Management
- API Versioning
- Security
- Performance
- Clean Folder Structure
- Reusable Services
- Type Hinting
- Pydantic V2
- Unit Test Skeletons
- Docker Support
- Environment Variables
- Background Tasks
- Caching where appropriate

Identify architectural issues and improve them without changing the public API.

The final code should resemble a production-grade backend suitable for an enterprise AI SaaS platform.
```

---

These prompts are intentionally scoped so each phase builds on the previous one, and by the end you'll have a backend that resembles an enterprise AI system rather than a typical hackathon prototype.
