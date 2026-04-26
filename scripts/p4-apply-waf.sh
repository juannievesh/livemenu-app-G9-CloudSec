#!/usr/bin/env bash
#
# scripts/p4-apply-waf.sh
# ----------------------------------------------------------------------
# Aplica Google Cloud Armor (WAF) sobre los backend services del LB
# `livemenu-map`, calzando con la configuración descrita en
# docs/waf-config.md.
#
# Pensado para ejecutarse en Google Cloud Shell (proyecto livemenu-project).
# Es idempotente: si la política o las reglas ya existen, las actualiza.
#
# Uso:
#   bash scripts/p4-apply-waf.sh           # aplicar
#   bash scripts/p4-apply-waf.sh --dry-run # solo imprimir comandos
# ----------------------------------------------------------------------

set -euo pipefail

PROJECT_ID="${PROJECT_ID:-livemenu-project}"
POLICY_NAME="${POLICY_NAME:-livemenu-waf-policy}"
BACKEND_SVC_API="${BACKEND_SVC_API:-backend-backend}"
BACKEND_SVC_FRONT="${BACKEND_SVC_FRONT:-frontend-backend}"
RATE_LIMIT_PATH_PREFIX="${RATE_LIMIT_PATH_PREFIX:-/api/}"
RATE_LIMIT_RPM="${RATE_LIMIT_RPM:-100}"

DRY=""
if [[ "${1:-}" == "--dry-run" ]]; then DRY="echo [DRY-RUN]"; fi

echo ">>> Proyecto activo: $PROJECT_ID"
$DRY gcloud config set project "$PROJECT_ID" >/dev/null

# ----------------------------------------------------------------------
# 1. Crear (o reutilizar) la política
# ----------------------------------------------------------------------
echo ">>> Asegurando policy '$POLICY_NAME' ..."
if ! gcloud compute security-policies describe "$POLICY_NAME" >/dev/null 2>&1; then
  $DRY gcloud compute security-policies create "$POLICY_NAME" \
    --description="LiveMenu WAF - OWASP Top 10 + Rate Limiting" \
    --type=CLOUD_ARMOR
else
  echo "    Policy ya existe, se reutiliza."
fi

# Habilitar logs verbose
$DRY gcloud compute security-policies update "$POLICY_NAME" \
  --log-level=VERBOSE >/dev/null

# ----------------------------------------------------------------------
# 2. Reglas OWASP pre-configuradas (CRS v3.3)
# ----------------------------------------------------------------------
declare -A RULES=(
  ["1000"]="sqli-v33-stable|OWASP: SQL Injection"
  ["1001"]="xss-v33-stable|OWASP: Cross-Site Scripting"
  ["1002"]="lfi-v33-stable|OWASP: Local File Inclusion"
  ["1003"]="rfi-v33-stable|OWASP: Remote File Inclusion"
  ["1004"]="rce-v33-stable|OWASP: Remote Code Execution"
  ["1005"]="scannerdetection-v33-stable|Scanner Detection"
  ["1006"]="protocolattack-v33-stable|Protocol Attack"
  ["1007"]="sessionfixation-v33-stable|Session Fixation"
)

for PRIORITY in "${!RULES[@]}"; do
  IFS='|' read -r EXPR DESC <<< "${RULES[$PRIORITY]}"
  echo ">>> Asegurando regla $PRIORITY ($DESC) ..."

  # Si existe, actualiza; si no, crea.
  if gcloud compute security-policies rules describe "$PRIORITY" \
       --security-policy="$POLICY_NAME" >/dev/null 2>&1; then
    $DRY gcloud compute security-policies rules update "$PRIORITY" \
      --security-policy="$POLICY_NAME" \
      --expression="evaluatePreconfiguredExpr('${EXPR}')" \
      --action=deny-403 \
      --description="$DESC"
  else
    $DRY gcloud compute security-policies rules create "$PRIORITY" \
      --security-policy="$POLICY_NAME" \
      --expression="evaluatePreconfiguredExpr('${EXPR}')" \
      --action=deny-403 \
      --description="$DESC"
  fi
done

# ----------------------------------------------------------------------
# 3. Rate limiting perimetral
# ----------------------------------------------------------------------
echo ">>> Asegurando rate limit ${RATE_LIMIT_RPM} req/min en ${RATE_LIMIT_PATH_PREFIX}* ..."
RATE_PRIORITY=2000
RATE_EXPR="request.path.startsWith('${RATE_LIMIT_PATH_PREFIX}')"

if gcloud compute security-policies rules describe "$RATE_PRIORITY" \
     --security-policy="$POLICY_NAME" >/dev/null 2>&1; then
  $DRY gcloud compute security-policies rules update "$RATE_PRIORITY" \
    --security-policy="$POLICY_NAME" \
    --expression="$RATE_EXPR" \
    --action=throttle \
    --rate-limit-threshold-count="$RATE_LIMIT_RPM" \
    --rate-limit-threshold-interval-sec=60 \
    --conform-action=allow \
    --exceed-action=deny-429 \
    --enforce-on-key=IP \
    --description="Rate limit perimetral ${RATE_LIMIT_RPM} req/min por IP"
else
  $DRY gcloud compute security-policies rules create "$RATE_PRIORITY" \
    --security-policy="$POLICY_NAME" \
    --expression="$RATE_EXPR" \
    --action=throttle \
    --rate-limit-threshold-count="$RATE_LIMIT_RPM" \
    --rate-limit-threshold-interval-sec=60 \
    --conform-action=allow \
    --exceed-action=deny-429 \
    --enforce-on-key=IP \
    --description="Rate limit perimetral ${RATE_LIMIT_RPM} req/min por IP"
fi

# ----------------------------------------------------------------------
# 4. Asociar a los backend services del LB
# ----------------------------------------------------------------------
for SVC in "$BACKEND_SVC_API" "$BACKEND_SVC_FRONT"; do
  echo ">>> Asociando policy al backend service '$SVC' ..."
  $DRY gcloud compute backend-services update "$SVC" \
    --security-policy="$POLICY_NAME" --global

  echo ">>> Habilitando logging en '$SVC' ..."
  $DRY gcloud compute backend-services update "$SVC" \
    --enable-logging --logging-sample-rate=1.0 --global
done

# ----------------------------------------------------------------------
# 5. Resumen
# ----------------------------------------------------------------------
echo ""
echo "============================================================"
echo "WAF aplicado. Verifica con:"
echo "  gcloud compute security-policies describe $POLICY_NAME"
echo "  gcloud compute backend-services describe $BACKEND_SVC_API --global \\"
echo "    --format='value(securityPolicy)'"
echo ""
echo "Pruebas de bloqueo (sustituye \$LB por la IP/dominio del LB):"
echo "  curl -i \"\$LB/api/v1/menu/test'%20OR%201=1--\"   # 403"
echo "  curl -i \"\$LB/api/v1/menu/test?q=<script>alert(1)</script>\"   # 403"
echo "============================================================"
