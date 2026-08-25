#!/bin/bash
set -e
cd /root/chitatelstvo
docker compose exec -T api python - <<'PY'
from api.routes.early_trial import EarlyTrialLead
from notifications.email_templates import build_early_trial_email
print("fields", sorted(EarlyTrialLead.model_fields.keys()))
print(build_early_trial_email(
    parent_name="Test",
    child_name="Kid",
    child_age=5,
    trial_title="X",
    trial_lesson_url="https://example.com/l",
    trial_slug="early-letters-trial-lesson-01",
)[:120])
PY
curl -s -o /tmp/et.json -w "%{http_code}\n" -X POST http://127.0.0.1:8000/api/early/trial \
  -H "Content-Type: application/json" \
  -d '{"parent_name":"Test","parent_email":"nobody@example.com","child_name":"Kid","child_age":5,"trial_slug":"early-letters-trial-lesson-01","consent_privacy":false,"consent_offer":false}'
cat /tmp/et.json; echo
