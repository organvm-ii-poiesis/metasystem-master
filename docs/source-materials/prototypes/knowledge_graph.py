#!/usr/bin/env python3
"""
Knowledge Graph - Unified Metadata Layer

Single source of truth for all system state: projects, files, conversations,
decisions, tools, machines. Uses SQLite with FTS5 for semantic search.

Critical component - everything depends on this being rock-solid.
"""

import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager


class KnowledgeGraph:
    """SQLite-based knowledge graph with full-text search."""

    def __init__(self, db_path: str = None):
        """Initialize knowledge graph.

        Args:
            db_path: Path to SQLite database. Defaults to ~/.metasystem/metastore.db
        """
        if db_path is None:
            db_path = str(Path.home() / ".metasystem" / "metastore.db")

        self.db_path = db_path

        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize if needed
        if not Path(db_path).exists():
            self._init_schema()

    @contextmanager
    def _get_conn(self):
        """Get database connection with context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return dict-like rows
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_schema(self):
        """Initialize database schema."""
        with self._get_conn() as conn:
            # Main entities table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    path TEXT,
                    name TEXT,
                    metadata JSON,
                    embedding BLOB,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_seen TEXT NOT NULL
                )
            """)

            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entities_path ON entities(path)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entities_last_seen ON entities(last_seen)")

            # Full-text search table
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS entities_fts USING fts5(
                    id UNINDEXED,
                    type,
                    name,
                    content,
                    tokenize = 'porter unicode61'
                )
            """)

            # Relationships table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    rel_type TEXT NOT NULL,
                    metadata JSON,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(source_id) REFERENCES entities(id) ON DELETE CASCADE,
                    FOREIGN KEY(target_id) REFERENCES entities(id) ON DELETE CASCADE
                )
            """)

            conn.execute("CREATE INDEX IF NOT EXISTS idx_rel_source ON relationships(source_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rel_target ON relationships(target_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rel_type ON relationships(rel_type)")

            # Conversations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    tool TEXT NOT NULL,
                    thread_id TEXT,
                    started_at TEXT NOT NULL,
                    last_message_at TEXT NOT NULL,
                    context JSON,
                    summary TEXT,
                    state JSON
                )
            """)

            conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_tool ON conversations(tool)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_started ON conversations(started_at)")

            # Facts table (auto-discovered metadata)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_id TEXT NOT NULL,
                    fact_type TEXT NOT NULL,
                    value TEXT,
                    source TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    discovered_at TEXT NOT NULL,
                    FOREIGN KEY(entity_id) REFERENCES entities(id) ON DELETE CASCADE
                )
            """)

            conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_entity ON facts(entity_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_type ON facts(fact_type)")

            # Snapshots table (versioning)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_id TEXT NOT NULL,
                    snapshot JSON NOT NULL,
                    trigger TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(entity_id) REFERENCES entities(id) ON DELETE CASCADE
                )
            """)

            conn.execute("CREATE INDEX IF NOT EXISTS idx_snap_entity ON snapshots(entity_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_snap_created ON snapshots(created_at)")

            # Machines table (multi-machine sync)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS machines (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    os TEXT,
                    last_sync_at TEXT,
                    sync_metadata JSON
                )
            """)

            # Sync log
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sync_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    machine_id TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    entities_changed INTEGER DEFAULT 0,
                    conflicts_resolved INTEGER DEFAULT 0,
                    synced_at TEXT NOT NULL,
                    FOREIGN KEY(machine_id) REFERENCES machines(id)
                )
            """)

            conn.execute("CREATE INDEX IF NOT EXISTS idx_sync_machine ON sync_log(machine_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sync_at ON sync_log(synced_at)")

    # =========================================================================
    # Entity CRUD Operations
    # =========================================================================

    def insert_entity(self, entity: Dict[str, Any]) -> str:
        """Insert a new entity into the knowledge graph.

        Args:
            entity: Entity dictionary with keys: type, path (optional), name (optional),
                   metadata (optional), embedding (optional)

        Returns:
            Entity ID (UUID)
        """
        now = datetime.now().isoformat()
        entity_id = entity.get('id', str(uuid.uuid4()))

        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO entities (id, type, path, name, metadata, embedding,
                                     created_at, updated_at, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entity_id,
                entity['type'],
                entity.get('path'),
                entity.get('name'),
                json.dumps(entity.get('metadata', {})),
                entity.get('embedding'),
                now,
                now,
                now
            ))

            # Update FTS index
            content = self._extract_searchable_content(entity)
            conn.execute("""
                INSERT INTO entities_fts (id, type, name, content)
                VALUES (?, ?, ?, ?)
            """, (entity_id, entity['type'], entity.get('name', ''), content))

        return entity_id

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity by ID.

        Args:
            entity_id: Entity UUID

        Returns:
            Entity dictionary or None if not found
        """
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM entities WHERE id = ?",
                (entity_id,)
            ).fetchone()

            if row:
                return self._row_to_dict(row)
            return None

    def update_entity(self, entity_id: str, updates: Dict[str, Any]):
        """Update an existing entity.

        Args:
            entity_id: Entity UUID
            updates: Dictionary of fields to update
        """
        updates['updated_at'] = datetime.now().isoformat()

        # Build dynamic UPDATE query
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [entity_id]

        # Special handling for metadata (needs JSON serialization)
        if 'metadata' in updates:
            idx = list(updates.keys()).index('metadata')
            values[idx] = json.dumps(values[idx])

        with self._get_conn() as conn:
            conn.execute(
                f"UPDATE entities SET {set_clause} WHERE id = ?",
                values
            )

            # Update FTS if content changed
            if any(k in updates for k in ['name', 'metadata']):
                entity = self.get_entity(entity_id)
                content = self._extract_searchable_content(entity)
                conn.execute("""
                    UPDATE entities_fts
                    SET name = ?, content = ?
                    WHERE id = ?
                """, (entity.get('name', ''), content, entity_id))

    def delete_entity(self, entity_id: str):
        """Delete an entity (cascades to relationships, facts, snapshots).

        Args:
            entity_id: Entity UUID
        """
        with self._get_conn() as conn:
            conn.execute("DELETE FROM entities WHERE id = ?", (entity_id,))
            conn.execute("DELETE FROM entities_fts WHERE id = ?", (entity_id,))

    def query_entities(self,
                      type: str = None,
                      path_like: str = None,
                      name_like: str = None,
                      last_seen_since: datetime = None,
                      last_seen_hours: int = None,
                      limit: int = None,
                      offset: int = 0) -> List[Dict[str, Any]]:
        """Query entities with filters.

        Args:
            type: Filter by entity type
            path_like: SQL LIKE pattern for path
            name_like: SQL LIKE pattern for name
            last_seen_since: Only entities seen after this datetime
            last_seen_hours: Only entities seen in last N hours
            limit: Maximum results
            offset: Skip first N results

        Returns:
            List of entity dictionaries
        """
        conditions = []
        params = []

        if type:
            conditions.append("type = ?")
            params.append(type)

        if path_like:
            conditions.append("path LIKE ?")
            params.append(path_like)

        if name_like:
            conditions.append("name LIKE ?")
            params.append(name_like)

        if last_seen_since:
            conditions.append("last_seen >= ?")
            params.append(last_seen_since.isoformat())

        if last_seen_hours:
            cutoff = (datetime.now() - timedelta(hours=last_seen_hours)).isoformat()
            conditions.append("last_seen >= ?")
            params.append(cutoff)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        limit_clause = f"LIMIT {limit}" if limit else ""
        offset_clause = f"OFFSET {offset}" if offset else ""

        query = f"""
            SELECT * FROM entities
            WHERE {where_clause}
            ORDER BY last_seen DESC
            {limit_clause} {offset_clause}
        """

        with self._get_conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def search(self, query: str, types: List[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Full-text search across entities.

        Args:
            query: Search query string
            types: Filter by entity types
            limit: Maximum results

        Returns:
            List of matching entities, ranked by relevance
        """
        type_filter = ""
        if types:
            type_list = "', '".join(types)
            type_filter = f"AND entities.type IN ('{type_list}')"

        with self._get_conn() as conn:
            rows = conn.execute(f"""
                SELECT entities.*
                FROM entities
                JOIN entities_fts ON entities.id = entities_fts.id
                WHERE entities_fts MATCH ?
                {type_filter}
                ORDER BY entities_fts.rank
                LIMIT ?
            """, (query, limit)).fetchall()

            return [self._row_to_dict(row) for row in rows]

    # =========================================================================
    # Relationship Operations
    # =========================================================================

    def add_relationship(self, source_id: str, target_id: str, rel_type: str,
                        metadata: Dict[str, Any] = None) -> int:
        """Add a relationship between entities.

        Args:
            source_id: Source entity UUID
            target_id: Target entity UUID
            rel_type: Relationship type (e.g., 'contains', 'references', 'depends_on')
            metadata: Optional relationship metadata

        Returns:
            Relationship ID
        """
        with self._get_conn() as conn:
            cursor = conn.execute("""
                INSERT INTO relationships (source_id, target_id, rel_type, metadata, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (source_id, target_id, rel_type,
                  json.dumps(metadata or {}), datetime.now().isoformat()))

            return cursor.lastrowid

    def get_relationships(self, entity_id: str, rel_type: str = None,
                         direction: str = 'both') -> List[Dict[str, Any]]:
        """Get relationships for an entity.

        Args:
            entity_id: Entity UUID
            rel_type: Filter by relationship type
            direction: 'outgoing', 'incoming', or 'both'

        Returns:
            List of relationship dictionaries
        """
        conditions = []
        params = []

        if direction in ['outgoing', 'both']:
            conditions.append("source_id = ?")
            params.append(entity_id)

        if direction in ['incoming', 'both'] and direction != 'outgoing':
            conditions.append("target_id = ?")
            params.append(entity_id)

        if rel_type:
            conditions.append("rel_type = ?")
            params.append(rel_type)

        where_clause = " OR ".join(conditions) if direction == 'both' and len(conditions) > 1 else " AND ".join(conditions)

        with self._get_conn() as conn:
            rows = conn.execute(f"""
                SELECT * FROM relationships
                WHERE {where_clause}
            """, params).fetchall()

            return [self._row_to_dict(row) for row in rows]

    def delete_relationship(self, rel_id: int):
        """Delete a relationship.

        Args:
            rel_id: Relationship ID
        """
        with self._get_conn() as conn:
            conn.execute("DELETE FROM relationships WHERE id = ?", (rel_id,))

    # =========================================================================
    # Conversation Operations
    # =========================================================================

    def insert_conversation(self, conv: Dict[str, Any]) -> str:
        """Insert a new conversation.

        Args:
            conv: Conversation dict with keys: id, tool, thread_id (optional),
                 started_at, context (optional), state (optional)

        Returns:
            Conversation ID
        """
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO conversations (id, tool, thread_id, started_at,
                                         last_message_at, context, summary, state)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conv['id'],
                conv['tool'],
                conv.get('thread_id'),
                conv['started_at'],
                conv.get('last_message_at', conv['started_at']),
                json.dumps(conv.get('context', {})),
                conv.get('summary'),
                json.dumps(conv.get('state', {}))
            ))

        return conv['id']

    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by ID.

        Args:
            conv_id: Conversation UUID

        Returns:
            Conversation dictionary or None
        """
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM conversations WHERE id = ?",
                (conv_id,)
            ).fetchone()

            if row:
                return self._row_to_dict(row)
            return None

    def update_conversation(self, conv_id: str, updates: Dict[str, Any]):
        """Update conversation.

        Args:
            conv_id: Conversation UUID
            updates: Fields to update
        """
        # Serialize JSON fields
        if 'context' in updates:
            updates['context'] = json.dumps(updates['context'])
        if 'state' in updates:
            updates['state'] = json.dumps(updates['state'])

        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [conv_id]

        with self._get_conn() as conn:
            conn.execute(
                f"UPDATE conversations SET {set_clause} WHERE id = ?",
                values
            )

    def query_conversations(self, tool: str = None, active: bool = None,
                           since: datetime = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Query conversations.

        Args:
            tool: Filter by tool (e.g., 'claude-code')
            active: Filter by active status
            since: Only conversations started after this datetime
            limit: Maximum results

        Returns:
            List of conversation dictionaries
        """
        conditions = []
        params = []

        if tool:
            conditions.append("tool = ?")
            params.append(tool)

        if since:
            conditions.append("started_at >= ?")
            params.append(since.isoformat())

        if active is not None:
            # Active = last message within 24 hours
            cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
            if active:
                conditions.append("last_message_at >= ?")
            else:
                conditions.append("last_message_at < ?")
            params.append(cutoff)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        with self._get_conn() as conn:
            rows = conn.execute(f"""
                SELECT * FROM conversations
                WHERE {where_clause}
                ORDER BY last_message_at DESC
                LIMIT ?
            """, params + [limit]).fetchall()

            return [self._row_to_dict(row) for row in rows]

    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent conversations.

        Args:
            limit: Max results to return

        Returns:
            List of conversation dictionaries, most recent first
        """
        return self.query_conversations(limit=limit)

    # =========================================================================
    # Facts Operations
    # =========================================================================

    def add_fact(self, entity_id: str, fact_type: str, value: str,
                source: str, confidence: float = 1.0) -> int:
        """Add a fact about an entity.

        Args:
            entity_id: Entity UUID
            fact_type: Type of fact (e.g., 'file_size', 'dependency')
            value: Fact value
            source: How this fact was discovered (e.g., 'file-org-scan')
            confidence: Confidence level (0.0-1.0)

        Returns:
            Fact ID
        """
        with self._get_conn() as conn:
            cursor = conn.execute("""
                INSERT INTO facts (entity_id, fact_type, value, source, confidence, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (entity_id, fact_type, value, source, confidence, datetime.now().isoformat()))

            return cursor.lastrowid

    def get_facts(self, entity_id: str, fact_type: str = None) -> List[Dict[str, Any]]:
        """Get facts for an entity.

        Args:
            entity_id: Entity UUID
            fact_type: Optional filter by fact type

        Returns:
            List of fact dictionaries
        """
        query = "SELECT * FROM facts WHERE entity_id = ?"
        params = [entity_id]

        if fact_type:
            query += " AND fact_type = ?"
            params.append(fact_type)

        query += " ORDER BY discovered_at DESC"

        with self._get_conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_dict(row) for row in rows]

    # =========================================================================
    # Snapshot Operations
    # =========================================================================

    def create_snapshot(self, entity_id: str, trigger: str = 'manual') -> int:
        """Create a snapshot of an entity's current state.

        Args:
            entity_id: Entity UUID
            trigger: What triggered this snapshot

        Returns:
            Snapshot ID
        """
        entity = self.get_entity(entity_id)
        if not entity:
            raise ValueError(f"Entity {entity_id} not found")

        with self._get_conn() as conn:
            cursor = conn.execute("""
                INSERT INTO snapshots (entity_id, snapshot, trigger, created_at)
                VALUES (?, ?, ?, ?)
            """, (entity_id, json.dumps(entity), trigger, datetime.now().isoformat()))

            return cursor.lastrowid

    def get_snapshots(self, entity_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get snapshots for an entity.

        Args:
            entity_id: Entity UUID
            limit: Maximum number of snapshots to return

        Returns:
            List of snapshot dictionaries
        """
        with self._get_conn() as conn:
            rows = conn.execute("""
                SELECT * FROM snapshots
                WHERE entity_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (entity_id, limit)).fetchall()

            return [self._row_to_dict(row) for row in rows]

    # =========================================================================
    # Sync Operations
    # =========================================================================

    def register_machine(self, machine_id: str, name: str, os: str):
        """Register a machine for sync tracking.

        Args:
            machine_id: Machine UUID or hostname
            name: Human-readable machine name
            os: Operating system (darwin, linux, windows)
        """
        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO machines (id, name, os, last_sync_at, sync_metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (machine_id, name, os, datetime.now().isoformat(), json.dumps({})))

    def log_sync(self, machine_id: str, direction: str,
                entities_changed: int = 0, conflicts_resolved: int = 0):
        """Log a sync operation.

        Args:
            machine_id: Machine UUID
            direction: 'push', 'pull', or 'both'
            entities_changed: Number of entities synced
            conflicts_resolved: Number of conflicts resolved
        """
        with self._get_conn() as conn:
            # Update machine last_sync_at
            conn.execute("""
                UPDATE machines SET last_sync_at = ? WHERE id = ?
            """, (datetime.now().isoformat(), machine_id))

            # Log sync
            conn.execute("""
                INSERT INTO sync_log (machine_id, direction, entities_changed,
                                     conflicts_resolved, synced_at)
                VALUES (?, ?, ?, ?, ?)
            """, (machine_id, direction, entities_changed, conflicts_resolved,
                  datetime.now().isoformat()))

    def get_last_sync_time(self, machine_id: str = None) -> Optional[datetime]:
        """Get last sync time for a machine or globally.

        Args:
            machine_id: Optional machine UUID (if None, returns global last sync)

        Returns:
            Datetime of last sync or None
        """
        with self._get_conn() as conn:
            if machine_id:
                row = conn.execute(
                    "SELECT last_sync_at FROM machines WHERE id = ?",
                    (machine_id,)
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT MAX(synced_at) as last_sync FROM sync_log"
                ).fetchone()

            if row and row[0]:
                return datetime.fromisoformat(row[0])
            return None

    # =========================================================================
    # Health & Maintenance
    # =========================================================================

    def check_integrity(self) -> bool:
        """Check database integrity.

        Returns:
            True if database is healthy
        """
        with self._get_conn() as conn:
            result = conn.execute("PRAGMA integrity_check").fetchone()
            return result[0] == 'ok'

    def vacuum(self):
        """Optimize database (reclaim space, rebuild indexes)."""
        with self._get_conn() as conn:
            conn.execute("VACUUM")
            conn.execute("ANALYZE")

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.

        Returns:
            Dictionary with counts and size info
        """
        with self._get_conn() as conn:
            stats = {}

            # Entity counts by type
            rows = conn.execute("""
                SELECT type, COUNT(*) as count
                FROM entities
                GROUP BY type
            """).fetchall()
            stats['entities_by_type'] = {row['type']: row['count'] for row in rows}

            # Total counts
            stats['total_entities'] = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
            stats['total_relationships'] = conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
            stats['total_conversations'] = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
            stats['total_facts'] = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
            stats['total_snapshots'] = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]

            # Database size
            stats['db_size_bytes'] = Path(self.db_path).stat().st_size
            stats['db_size_mb'] = round(stats['db_size_bytes'] / (1024 * 1024), 2)

            # Recent activity
            stats['last_entity_update'] = conn.execute(
                "SELECT MAX(updated_at) FROM entities"
            ).fetchone()[0]

            stats['last_conversation'] = conn.execute(
                "SELECT MAX(last_message_at) FROM conversations"
            ).fetchone()[0]

            return stats

    def find_broken_relationships(self) -> List[Dict[str, Any]]:
        """Find relationships pointing to non-existent entities.

        Returns:
            List of broken relationships
        """
        with self._get_conn() as conn:
            rows = conn.execute("""
                SELECT r.* FROM relationships r
                LEFT JOIN entities e1 ON r.source_id = e1.id
                LEFT JOIN entities e2 ON r.target_id = e2.id
                WHERE e1.id IS NULL OR e2.id IS NULL
            """).fetchall()

            return [self._row_to_dict(row) for row in rows]

    def prune_stale_entities(self, days: int = 90) -> int:
        """Mark entities as deleted if not seen in N days.

        Args:
            days: Number of days without activity

        Returns:
            Number of entities pruned
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        with self._get_conn() as conn:
            # Get stale entities
            stale = conn.execute("""
                SELECT id FROM entities
                WHERE last_seen < ? AND type != 'decision'
            """, (cutoff,)).fetchall()

            count = len(stale)

            # Mark as deleted (add metadata flag)
            for row in stale:
                entity = self.get_entity(row['id'])
                metadata = entity.get('metadata', {})
                metadata['deleted'] = True
                metadata['deleted_at'] = datetime.now().isoformat()
                self.update_entity(row['id'], {'metadata': metadata})

            return count

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert SQLite Row to dictionary, parsing JSON fields.

        Args:
            row: SQLite Row object

        Returns:
            Dictionary with JSON fields parsed
        """
        d = dict(row)

        # Parse JSON fields
        if 'metadata' in d and d['metadata']:
            d['metadata'] = json.loads(d['metadata'])
        if 'context' in d and d['context']:
            d['context'] = json.loads(d['context'])
        if 'state' in d and d['state']:
            d['state'] = json.loads(d['state'])
        if 'snapshot' in d and d['snapshot']:
            d['snapshot'] = json.loads(d['snapshot'])
        if 'sync_metadata' in d and d['sync_metadata']:
            d['sync_metadata'] = json.loads(d['sync_metadata'])

        return d

    def _extract_searchable_content(self, entity: Dict[str, Any]) -> str:
        """Extract searchable content from entity for FTS.

        Args:
            entity: Entity dictionary

        Returns:
            String of searchable content
        """
        parts = []

        if entity.get('name'):
            parts.append(entity['name'])

        if entity.get('path'):
            parts.append(str(entity['path']))

        metadata = entity.get('metadata', {})
        if isinstance(metadata, dict):
            # Extract text values from metadata
            for value in metadata.values():
                if isinstance(value, str):
                    parts.append(value)

        return ' '.join(parts)


def main():
    """CLI for knowledge graph operations."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Knowledge Graph CLI')
    parser.add_argument('command', choices=['init', 'stats', 'query', 'vacuum', 'check'],
                       help='Command to run')
    parser.add_argument('--query', help='SQL query or search string')
    parser.add_argument('--type', help='Entity type filter')

    args = parser.parse_args()

    kg = KnowledgeGraph()

    if args.command == 'init':
        print(f"✅ Initialized knowledge graph at {kg.db_path}")

    elif args.command == 'stats':
        stats = kg.get_stats()
        print(json.dumps(stats, indent=2))

    elif args.command == 'query':
        if not args.query:
            print("Error: --query required", file=sys.stderr)
            sys.exit(1)

        # Try as search first
        results = kg.search(args.query, types=[args.type] if args.type else None)
        print(json.dumps(results, indent=2))

    elif args.command == 'vacuum':
        kg.vacuum()
        print("✅ Database optimized")

    elif args.command == 'check':
        if kg.check_integrity():
            print("✅ Database integrity OK")
        else:
            print("❌ Database integrity check FAILED", file=sys.stderr)
            sys.exit(1)

        # Check for broken relationships
        broken = kg.find_broken_relationships()
        if broken:
            print(f"⚠️  Found {len(broken)} broken relationships")
        else:
            print("✅ No broken relationships")


if __name__ == '__main__':
    main()
