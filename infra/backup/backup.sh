#!/bin/sh
# Dumps the database, encrypts it, uploads it to off-site object storage, prunes old copies.
set -eu
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
KEY="db/offerlight-${STAMP}.dump.gpg"
export AWS_ACCESS_KEY_ID="$BACKUP_S3_ACCESS_KEY" AWS_SECRET_ACCESS_KEY="$BACKUP_S3_SECRET_KEY"
S3="aws s3 --endpoint-url $BACKUP_S3_ENDPOINT"

pg_dump -Fc -h postgres -U offerlight offerlight \
  | gpg --batch --yes --symmetric --cipher-algo AES256 --passphrase "$BACKUP_ENCRYPTION_PASSPHRASE" \
  | $S3 cp - "s3://${BACKUP_S3_BUCKET}/${KEY}"
echo "backup ok: ${KEY}"

CUTOFF=$(date -u -d "@$(( $(date +%s) - ${BACKUP_RETENTION_DAYS:-30} * 86400 ))" +%Y%m%d)
$S3 ls "s3://${BACKUP_S3_BUCKET}/db/" | awk '{print $4}' | while read -r f; do
  d=$(echo "$f" | sed -n 's/offerlight-\([0-9]\{8\}\).*/\1/p')
  if [ -n "$d" ] && [ "$d" -lt "$CUTOFF" ]; then $S3 rm "s3://${BACKUP_S3_BUCKET}/db/$f"; fi
done
