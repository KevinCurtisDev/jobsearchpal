# Backups, restores and erasure

Erased data can survive in backups. The rule that keeps this unambiguous:

1. Backups are encrypted (GPG) and kept **30 days** (`BACKUP_RETENTION_DAYS`), then deleted.
   Backups are never used for anything except disaster recovery.
2. Every erasure writes a row to `erasure_tombstones` (keyed hashes only), kept **60 days** —
   longer than any backup can exist.
3. **After any restore**, before the service is reopened, run
   `make privacy-reapply-erasures` (Stage 1 task: `reapply_tombstones`). It finds restored
   users whose `subject_ref` matches a tombstone and runs the erasure plan again.
4. The restore test (`make restore-test`) checks step 3 with a fixture user.
5. The privacy notice says: "Deleted data is removed from our backups within 30 days".

Increasing `BACKUP_RETENTION_DAYS` above 30 requires raising the tombstone retention in
`data_inventory.toml` too — the inventory test fails otherwise (Stage 1 task).
