# Troubleshooting Guide

Complete guide for diagnosing and fixing common issues with Metasystem Core.

---

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Daemon Issues](#daemon-issues)
- [Database Problems](#database-problems)
- [Sync Issues](#sync-issues)
- [Context Management](#context-management)
- [Dotfile Problems](#dotfile-problems)
- [Performance Issues](#performance-issues)
- [Recovery Procedures](#recovery-procedures)

---

## Quick Diagnostics

### Run System Health Check

```bash
cd /Users/4jp/Workspace/metasystem-core
source .venv/bin/activate
python3 agents/maintainer.py
```

**Interpreting Results**:
- ✓ = Everything OK
- ⚠️ = Warning (system still functional)
- ✗ = Critical issue (needs attention)

### Check All Daemons

```bash
launchctl list | grep metasystem

# Expected output (3 daemons running):
# -    0    com.metasystem.sorting-daemon
# -    0    com.metasystem.sync-daemon
# -    0    com.metasystem.maintenance-daemon
```

### View Recent Logs

```bash
# All logs
ls -lt ~/.metasystem/logs/

# Most recent errors
tail -f ~/.metasystem/logs/*.log | grep -i error

# Maintenance summary
tail -50 ~/.metasystem/logs/maintenance.log
```

---

## Daemon Issues

### Sorting Daemon Not Running

**Symptoms**:
- Downloads folder not getting organized
- Files piling up
- No entries in sorting-daemon.log

**Diagnosis**:
```bash
# Check if loaded
launchctl list | grep sorting-daemon

# Check for errors
tail -50 ~/.metasystem/logs/sorting-daemon.log
```

**Solutions**:

**1. Reload daemon**:
```bash
launchctl unload ~/Library/LaunchAgents/com.metasystem.sorting-daemon.plist
launchctl load ~/Library/LaunchAgents/com.metasystem.sorting-daemon.plist
```

**2. Check plist file**:
```bash
plutil -lint ~/Library/LaunchAgents/com.metasystem.sorting-daemon.plist

# Should output: "OK"
```

**3. Verify Python path**:
```bash
# Check if venv exists
ls /Users/4jp/Workspace/metasystem-core/.venv/bin/python3

# If missing, recreate venv:
cd /Users/4jp/Workspace/metasystem-core
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**4. Test manually**:
```bash
cd /Users/4jp/Workspace/metasystem-core
source .venv/bin/activate
python3 sorting_daemon.py scan
```

### Sync Daemon Failing

**Symptoms**:
- iCloud sync not happening
- Sync status shows stale timestamp
- Sync errors in logs

**Diagnosis**:
```bash
# Check sync status
python3 sync_engine.py status

# View sync logs
tail -100 ~/.metasystem/logs/sync-daemon.log | grep -i error
```

**Solutions**:

**1. Check iCloud Drive status**:
```bash
# Verify iCloud is accessible
ls ~/Library/Mobile\ Documents/com~apple~CloudDocs/

# Check space available
df -h ~/Library/Mobile\ Documents/com~apple~CloudDocs/
```

**2. Manual sync to identify issue**:
```bash
cd /Users/4jp/Workspace/metasystem-core
source .venv/bin/activate
python3 sync_engine.py sync
```

**3. Clear conflicted files**:
```bash
# List backup files
ls -la ~/.metasystem/*.backup-*

# If too many backups, clean old ones (>30 days)
find ~/.metasystem -name "*.backup-*" -mtime +30 -delete
```

**4. Reset sync state**:
```bash
# Backup current state
cp ~/.metasystem/metastore.db ~/.metasystem/metastore.db.manual-backup

# Force fresh sync
python3 sync_engine.py sync --force
```

### Maintenance Daemon Not Running

**Symptoms**:
- No daily maintenance happening
- Documentation not updating
- No discovery scans

**Diagnosis**:
```bash
# Check if loaded
launchctl list | grep maintenance-daemon

# Check when last run
stat ~/.metasystem/logs/maintenance-daemon.log
```

**Solutions**:

**1. Trigger manual run**:
```bash
cd /Users/4jp/Workspace/metasystem-core
source .venv/bin/activate
python3 maintenance_daemon.py daily
```

**2. Verify schedule**:
```bash
# Check plist for schedule
plutil -p ~/Library/LaunchAgents/com.metasystem.maintenance-daemon.plist | grep -A5 StartCalendarInterval

# Should show Hour: 2, Minute: 0
```

**3. Reload daemon**:
```bash
launchctl unload ~/Library/LaunchAgents/com.metasystem.maintenance-daemon.plist
launchctl load ~/Library/LaunchAgents/com.metasystem.maintenance-daemon.plist
```

---

## Database Problems

### Database Locked Error

**Error**: `database is locked`

**Cause**: Multiple processes trying to write simultaneously

**Solutions**:

**1. Wait and retry**:
```bash
# Usually resolves in < 5 seconds
sleep 5
python3 <command>
```

**2. Check for hung processes**:
```bash
# Find processes using database
lsof ~/.metasystem/metastore.db

# Kill if necessary (use PID from lsof output)
kill <PID>
```

**3. Increase timeout** (if frequent):
Edit `knowledge_graph.py`:
```python
conn = sqlite3.connect(db_path, timeout=30)  # Increase from 5 to 30
```

### Database Corruption

**Error**: `database disk image is malformed` or `integrity_check: *** in database main ***`

**Diagnosis**:
```bash
# Check integrity
sqlite3 ~/.metasystem/metastore.db "PRAGMA integrity_check"

# Should output: "ok"
# If not, database is corrupted
```

**Solutions**:

**1. Restore from iCloud backup**:
```bash
# Check iCloud backup exists
ls ~/Library/Mobile\ Documents/com~apple~CloudDocs/.metasystem/metastore.db

# Backup corrupt database
mv ~/.metasystem/metastore.db ~/.metasystem/metastore.db.corrupt

# Restore from iCloud
cp ~/Library/Mobile\ Documents/com~apple~CloudDocs/.metasystem/metastore.db ~/.metasystem/

# Verify integrity
sqlite3 ~/.metasystem/metastore.db "PRAGMA integrity_check"
```

**2. Rebuild from scratch** (last resort):
```bash
# Backup corrupt database
mv ~/.metasystem/metastore.db ~/.metasystem/metastore.db.corrupt

# Recreate fresh database
cd /Users/4jp/Workspace/metasystem-core
source .venv/bin/activate
python3 knowledge_graph.py init

# Rediscover all projects
python3 discovery_engine.py discover
```

### FTS Index Corruption

**Symptom**: Search returns no results or errors

**Diagnosis**:
```bash
sqlite3 ~/.metasystem/metastore.db "SELECT * FROM entities_fts WHERE entities_fts MATCH 'test'"
# If error, FTS index is corrupt
```

**Solution**:
```bash
# Rebuild FTS index
sqlite3 ~/.metasystem/metastore.db <<EOF
INSERT INTO entities_fts(entities_fts) VALUES('rebuild');
.quit
EOF

# Verify
python3 knowledge_graph.py search --query="test" --type=project
```

---

## Sync Issues

### Sync Status Stale

**Symptom**: Last sync time > 1 hour ago

**Diagnosis**:
```bash
python3 sync_engine.py status

# Check sync daemon logs
tail -50 ~/.metasystem/logs/sync-daemon.log
```

**Solutions**:

**1. Trigger manual sync**:
```bash
python3 sync_engine.py sync
```

**2. Check sync daemon**:
```bash
launchctl list | grep sync-daemon

# If not running, load it
launchctl load ~/Library/LaunchAgents/com.metasystem.sync-daemon.plist
```

**3. Verify iCloud connectivity**:
```bash
# Test write to iCloud
touch ~/Library/Mobile\ Documents/com~apple~CloudDocs/.test-file
sleep 5
rm ~/Library/Mobile\ Documents/com~apple~CloudDocs/.test-file
```

### Sync Conflicts

**Symptom**: Multiple `.backup-YYYYMMDD-HHMMSS` files

**Diagnosis**:
```bash
# List conflict backups
ls -lt ~/.metasystem/*.backup-*
```

**Solutions**:

**1. Review conflict**:
```bash
# Compare conflicted files
diff ~/.metasystem/metastore.db ~/.metasystem/metastore.db.backup-YYYYMMDD-HHMMSS
```

**2. Choose which to keep**:
```bash
# Keep local (discard backup)
rm ~/.metasystem/metastore.db.backup-*

# Or keep backup (discard local)
mv ~/.metasystem/metastore.db.backup-YYYYMMDD-HHMMSS ~/.metasystem/metastore.db
```

**3. Merge data** (advanced):
```bash
# Export from backup
sqlite3 ~/.metasystem/metastore.db.backup-YYYYMMDD-HHMMSS ".dump" > backup.sql

# Review and manually import needed data
sqlite3 ~/.metasystem/metastore.db < backup.sql
```

### External Drive Sync Failing

**Symptom**: External drive shows 0 files synced

**Diagnosis**:
```bash
# Check if drive mounted
ls /Volumes/4444-iivii/

# Check sync status
python3 sync_engine.py status
```

**Solutions**:

**1. Mount drive**:
```bash
# Physically connect drive
# macOS should auto-mount to /Volumes/4444-iivii/

# Verify
ls /Volumes/4444-iivii/
```

**2. Manually sync to external**:
```bash
# Create directory if needed
mkdir -p /Volumes/4444-iivii/.metasystem

# Manual sync
rsync -av ~/.metasystem/ /Volumes/4444-iivii/.metasystem/
```

---

## Context Management

### Context Not Persisting

**Symptom**: Can't resume previous conversations

**Diagnosis**:
```bash
# Check for recent conversations
python3 context_manager.py recent

# If empty, context not being logged
```

**Solutions**:

**1. Verify conversation logging**:
```bash
# Check database has conversations
python3 knowledge_graph.py search --type=conversation

# Should show recent conversations
```

**2. Manually log current session**:
```bash
# Start conversation tracking
python3 context_manager.py start

# Log a decision
python3 context_manager.py log-decision \
  --decision="Test decision" \
  --rationale="Testing context persistence"
```

**3. Check database permissions**:
```bash
ls -la ~/.metasystem/metastore.db

# Should be writable by you
# If not, fix permissions:
chmod 644 ~/.metasystem/metastore.db
```

### Can't Resume Conversation

**Error**: `Conversation ID not found`

**Diagnosis**:
```bash
# List all conversations
python3 context_manager.py recent

# Verify ID exists
python3 knowledge_graph.py search --type=conversation | grep <ID>
```

**Solutions**:

**1. Use correct ID format**:
```bash
# ID should be UUID format: abc123de-f456-7890-abcd-ef1234567890
python3 context_manager.py resume --conv-id=<full-UUID>
```

**2. Search by content instead**:
```bash
# Find conversation by what you worked on
python3 context_manager.py search --query="authentication"
```

---

## Dotfile Problems

### Chezmoi Apply Errors

**Error**: `[ERROR] could not read secret...`

**Diagnosis**:
```bash
# Check what would change
chezmoi diff

# Dry-run to see errors
chezmoi apply --dry-run 2>&1 | grep ERROR
```

**Solutions**:

**1. Verify 1Password CLI**:
```bash
# Check op is installed
op --version

# Check signed in
op whoami

# If not signed in:
eval $(op signin)
```

**2. Fix missing 1Password items**:
```bash
# Check what items exist
op item list --vault Personal | grep -i <item-name>

# Create missing item (example for AWS):
op item create --category='API Credential' \
  --title='AWS Personal' \
  --vault='Personal' \
  'access_key_id[password]=YOUR_KEY' \
  'secret_access_key[password]=YOUR_SECRET' \
  'region[text]=us-east-1'
```

**3. Skip problematic templates**:
```bash
# Add to .chezmoiignore
echo "private_dot_aws/credentials" >> ~/.local/share/chezmoi/.chezmoiignore

# Apply without that file
chezmoi apply
```

### Dotfile Changes Not Tracked

**Symptom**: `python3 agents/dotfile_watcher.py query` shows no changes

**Diagnosis**:
```bash
# Check chezmoi git log
cd ~/.local/share/chezmoi
git log --since="7 days ago"

# If empty, changes not committed
```

**Solutions**:

**1. Commit changes to chezmoi**:
```bash
cd ~/.local/share/chezmoi
git status
git add .
git commit -m "Update dotfiles"
```

**2. Re-track changes**:
```bash
cd /Users/4jp/Workspace/metasystem-core
source .venv/bin/activate
python3 agents/dotfile_watcher.py track --days=7
```

### Secrets Exposed in Dotfiles

**Security Issue**: Plaintext tokens/passwords in config files

**Diagnosis**:
```bash
# Scan for exposed secrets
grep -r "ghp_\|aws_secret\|password" ~/.config ~/.zshrc

# Check git config
grep -i "token" ~/.config/git/config
```

**Solutions**:

**1. Move to 1Password**:
```bash
# Remove from dotfile
chezmoi edit ~/.config/git/config

# Delete [github] section with token
# Commit change
cd ~/.local/share/chezmoi
git add .
git commit -m "Remove exposed GitHub token"
chezmoi apply
```

**2. Verify removal**:
```bash
grep -i "ghp_" ~/.config/git/config
# Should return nothing
```

**3. Use gh CLI instead**:
```bash
# Authenticate via gh
gh auth login

# Verify working
gh auth status
```

---

## Performance Issues

### Slow Discovery Scans

**Symptom**: `discovery_engine.py` takes > 5 minutes

**Diagnosis**:
```bash
# Time the scan
time python3 discovery_engine.py discover
```

**Solutions**:

**1. Reduce scan scope**:
```yaml
# Edit discovery config (if exists)
scan_paths:
  - ~/Workspace  # Only scan workspace, not entire home
```

**2. Use incremental scans**:
```bash
# Cataloger maintains state for faster scans
python3 agents/cataloger.py scan
# Only processes changed projects
```

**3. Exclude large directories**:
```bash
# Add to .gitignore equivalent for discovery
echo "node_modules/" >> ~/Workspace/.discovery-ignore
echo ".git/" >> ~/Workspace/.discovery-ignore
```

### Database Queries Slow

**Symptom**: Search takes > 2 seconds

**Diagnosis**:
```bash
# Enable query timing
sqlite3 ~/.metasystem/metastore.db <<EOF
.timer ON
SELECT * FROM entities WHERE type = 'project';
.quit
EOF
```

**Solutions**:

**1. Rebuild FTS index**:
```bash
sqlite3 ~/.metasystem/metastore.db "INSERT INTO entities_fts(entities_fts) VALUES('optimize')"
```

**2. Vacuum database**:
```bash
sqlite3 ~/.metasystem/metastore.db "VACUUM"
```

**3. Add index for common queries**:
```bash
sqlite3 ~/.metasystem/metastore.db <<EOF
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
CREATE INDEX IF NOT EXISTS idx_entities_created ON entities(created_at);
.quit
EOF
```

### High Disk Usage

**Symptom**: `~/.metasystem` using > 1 GB

**Diagnosis**:
```bash
# Check disk usage
du -sh ~/.metasystem/*

# List large files
find ~/.metasystem -type f -size +10M -exec ls -lh {} \;
```

**Solutions**:

**1. Clean old backups**:
```bash
# Remove backups older than 30 days
find ~/.metasystem -name "*.backup-*" -mtime +30 -delete
```

**2. Clean old logs**:
```bash
# Truncate large log files
find ~/.metasystem/logs -type f -size +100M -exec truncate -s 0 {} \;

# Or delete old logs
find ~/.metasystem/logs -name "*.log" -mtime +90 -delete
```

**3. Vacuum database**:
```bash
# Reclaim space from deleted records
sqlite3 ~/.metasystem/metastore.db "VACUUM"
```

---

## Recovery Procedures

### Complete System Reset

**When**: Total system failure, fresh start needed

**Warning**: ⚠️ This deletes all local data. Restore from iCloud if available.

```bash
# 1. Stop all daemons
launchctl unload ~/Library/LaunchAgents/com.metasystem.*.plist

# 2. Backup everything
tar -czf ~/metasystem-backup-$(date +%Y%m%d).tar.gz ~/.metasystem

# 3. Remove local data
rm -rf ~/.metasystem

# 4. Restore from iCloud (if available)
cp -R ~/Library/Mobile\ Documents/com~apple~CloudDocs/.metasystem ~/.metasystem

# 5. Or rebuild from scratch
cd /Users/4jp/Workspace/metasystem-core
source .venv/bin/activate
python3 knowledge_graph.py init
python3 discovery_engine.py discover

# 6. Restart daemons
launchctl load ~/Library/LaunchAgents/com.metasystem.sorting-daemon.plist
launchctl load ~/Library/LaunchAgents/com.metasystem.sync-daemon.plist
launchctl load ~/Library/LaunchAgents/com.metasystem.maintenance-daemon.plist
```

### Restore from Backup

**When**: Need to recover from specific point in time

```bash
# 1. List available backups
ls -lt ~/.metasystem/*.backup-* | head -10

# 2. Choose backup to restore
BACKUP_FILE=~/.metasystem/metastore.db.backup-20251231-140000

# 3. Stop daemons
launchctl unload ~/Library/LaunchAgents/com.metasystem.*.plist

# 4. Backup current state (just in case)
cp ~/.metasystem/metastore.db ~/.metasystem/metastore.db.pre-restore

# 5. Restore
cp $BACKUP_FILE ~/.metasystem/metastore.db

# 6. Verify integrity
sqlite3 ~/.metasystem/metastore.db "PRAGMA integrity_check"

# 7. Restart daemons
launchctl load ~/Library/LaunchAgents/com.metasystem.*.plist
```

### Fix Orphaned Entities

**When**: Health check shows orphaned entities

```bash
# Run maintainer with auto-repair
python3 agents/maintainer.py

# If that doesn't fix it, manual cleanup:
sqlite3 ~/.metasystem/metastore.db <<EOF
DELETE FROM entities WHERE type = 'file' AND json_extract(metadata, '$.file_exists') = 'false';
.quit
EOF
```

---

## Getting Help

### Enable Debug Logging

```bash
# Edit daemon plists to add debug flag
# Example for sorting daemon:
nano ~/Library/LaunchAgents/com.metasystem.sorting-daemon.plist

# Add --debug to ProgramArguments:
<string>--debug</string>

# Reload daemon
launchctl unload ~/Library/LaunchAgents/com.metasystem.sorting-daemon.plist
launchctl load ~/Library/LaunchAgents/com.metasystem.sorting-daemon.plist
```

### Collect Diagnostic Info

```bash
# Run this script to collect all diagnostics
cat > /tmp/metasystem-diag.sh <<'EOF'
#!/bin/bash
echo "=== Daemon Status ==="
launchctl list | grep metasystem

echo -e "\n=== Disk Usage ==="
du -sh ~/.metasystem/*

echo -e "\n=== Database Integrity ==="
sqlite3 ~/.metasystem/metastore.db "PRAGMA integrity_check"

echo -e "\n=== Recent Errors (last 50 lines) ==="
tail -50 ~/.metasystem/logs/*.log | grep -i error

echo -e "\n=== System Info ==="
sw_vers
python3 --version
sqlite3 --version
EOF

chmod +x /tmp/metasystem-diag.sh
/tmp/metasystem-diag.sh > ~/metasystem-diagnostics.txt
cat ~/metasystem-diagnostics.txt
```

---

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `database is locked` | Multiple writers | Wait 5 seconds, retry |
| `database disk image is malformed` | Corruption | Restore from backup |
| `could not read secret` | 1Password item missing | Create item or skip template |
| `No such file or directory: seed.yaml` | Project not discoverable | Add seed.yaml to project |
| `Permission denied` | Wrong file permissions | `chmod 644 <file>` |
| `Connection refused` | iCloud not accessible | Check iCloud status |
| `Conversation ID not found` | Wrong UUID format | Use full UUID from `recent` |

---

**Still having issues?** Review phase completion documents or check README for common workflows.
