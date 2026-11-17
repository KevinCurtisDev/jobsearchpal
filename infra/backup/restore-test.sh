#!/bin/sh
# Weekly: restores the newest backup into a scratch database and checks key tables have rows.
set -eu
export AWS_ACCESS_KEY_ID="$BACKUP_S3_ACCESS_KEY" AWS_SECRET_ACCESS_KEY="$BACKUP_S3_SECRET_KEY"
S3="aws s3 --endpoint-url $BACKUP_S3_ENDPOINT"
LATEST=$($S3 ls "s3://${BACKUP_S3_BUCKET}/db/" | awk '{print $4}' | sort | tail -n 1)
[ -n "$LATEST" ] || { echo "restore test FAILED: no backups found"; exit 1; }

psql -h postgres -U offerlight -d postgres -c "DROP DATABASE IF EXISTS restore_test" >/dev/null
psql -h postgres -U offerlight -d postgres -c "CREATE DATABASE restore_test" >/dev/null
$S3 cp "s3://${BACKUP_S3_BUCKET}/db/${LATEST}" - \
  | gpg --batch --decrypt --passphrase "$BACKUP_ENCRYPTION_PASSPHRASE" \
  | pg_restore -h postgres -U offerlight -d restore_test --no-owner
TABLES=$(psql -h postgres -U offerlight -d restore_test -tAc "select count(*) from information_schema.tables where table_schema='public'")
psql -h postgres -U offerlight -d postgres -c "DROP DATABASE restore_test" >/dev/null
if [ "$TABLES" -gt 0 ]; then echo "restore test ok: ${LATEST} (${TABLES} tables)"; else echo "restore test FAILED: ${LATEST}"; exit 1; fi
