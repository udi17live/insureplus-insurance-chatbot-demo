# 24 — Compliance Considerations

*Skipped for showcase — this is a fictional company with demo data.*

## Production Requirements (Reference Only)

### Regulatory
- **FCA authorisation** required to sell insurance products in the UK
- **Broker vs direct insurer** distinction affects underwriting obligations
- **ICO registration** required for processing personal data (GDPR)

### Data
- **Data residency:** Must confirm Azure region aligns with regulatory requirements
- **Retention policy:** Insurance records typically 5–7 years minimum
- **Right to erasure:** GDPR right to be forgotten — conflicts with retention obligations
- **PII handling:** Customer data (DOB, vehicle reg, health info for life) requires data processing agreements with all processors including Azure/OpenAI

### AI-Specific
- **Prompt logging:** Confirm Azure OpenAI zero-data-retention agreement in place
- **Explainability:** AI-influenced decisions (quote pricing, eligibility) may require explainability under EU AI Act
- **Human in the loop:** Required for high-value or high-risk policy decisions

### Payments
- **PCI DSS:** Stripe handles card data directly — our scope is minimal. Confirm Stripe's PCI compliance documentation.
- **Consumer credit regulation:** If offering premium financing, FCA consumer credit licence required

## What This Showcase Does Instead
- Synthetic data only — no real customer PII
- Auto-approval on all policies — no actual underwriting
- Sandbox payments only
- These simplifications are explicitly noted throughout the spec as production gaps
