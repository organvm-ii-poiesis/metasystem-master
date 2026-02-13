#!/usr/bin/env python3
"""
Integration between my--father-mother and Metasystem Knowledge Graph

Bridges clipboard data into the central knowledge graph for unified context:
- Clipboard clips → KG entities with metadata
- Tags → KG relationships
- Copilot conversations → KG conversation records
- Annotations → KG decision entities

This enables agents to learn from clipboard history and make context-informed decisions.
"""

import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import contextmanager

from knowledge_graph import KnowledgeGraph


logger = logging.getLogger('MFMIntegration')


class MFMIntegration:
    """
    Bridge my--father-mother clipboard database to metasystem knowledge graph.
    """

    def __init__(self):
        """Initialize integration bridge."""
        self.mfm_db_path = Path.home() / '.my-father-mother' / 'mfm.db'
        self.kg = KnowledgeGraph()
        
        if not self.mfm_db_path.exists():
            logger.warning(f"my--father-mother database not found: {self.mfm_db_path}")
            self.mfm_db = None
        else:
            self.mfm_db = self.mfm_db_path

    @contextmanager
    def _get_mfm_connection(self):
        """Get connection to my--father-mother database."""
        if not self.mfm_db:
            raise RuntimeError("my--father-mother database not found")
        
        conn = sqlite3.connect(self.mfm_db)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def import_clips_to_kg(self, limit: int = 100, force: bool = False) -> Dict[str, Any]:
        """
        Import recent clipboard clips from my--father-mother to KG.
        
        Args:
            limit: Maximum number of clips to import
            force: Force re-import even if already imported
            
        Returns:
            Import results with counts and timestamps
        """
        if not self.mfm_db:
            return {'status': 'error', 'error': 'my--father-mother database not found'}

        try:
            with self._get_mfm_connection() as conn:
                cursor = conn.cursor()
                
                # Get recent clips
                cursor.execute('''
                    SELECT id, created_at, source_app, window_title, content, title, pinned
                    FROM clips
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (limit,))
                
                clips = cursor.fetchall()
                imported = 0
                
                for clip in clips:
                    # Check if already imported (to avoid duplicates)
                    if not force:
                        existing = self.kg.search(f'clipboard_{clip["id"]}', limit=1)
                        if existing:
                            continue
                    
                    # Create KG entity for clip
                    entity = {
                        'id': f"clipboard_{clip['id']}",
                        'type': 'clipboard_content',
                        'path': f"clipboard://{clip['source_app']}/{clip['id']}",
                        'name': clip['title'] or clip['source_app'],
                        'metadata': {
                            'source_app': clip['source_app'],
                            'window_title': clip['window_title'],
                            'content_preview': clip['content'][:200] if clip['content'] else '',
                            'pinned': bool(clip['pinned']),
                            'original_id': clip['id'],
                            'imported_from': 'my--father-mother'
                        },
                        'created_at': clip['created_at'],
                        'last_seen': datetime.now().isoformat()
                    }
                    
                    self.kg.insert_entity(entity)
                    imported += 1
                
                # Get clip tags and create relationships
                cursor.execute('''
                    SELECT DISTINCT ct.clip_id, t.name as tag_name
                    FROM clip_tags ct
                    JOIN tags t ON ct.tag_id = t.id
                    LIMIT ? * 5
                ''', (limit,))
                
                tag_links = 0
                for row in cursor.fetchall():
                    source_id = f"clipboard_{row['clip_id']}"
                    target_id = f"tag_{row['tag_name']}"
                    
                    try:
                        # Create tag entity if doesn't exist
                        existing = self.kg.search(target_id, limit=1)
                        if not existing:
                            self.kg.insert_entity({
                                'id': target_id,
                                'type': 'tag',
                                'name': row['tag_name'],
                                'metadata': {'source': 'my--father-mother'}
                            })
                        
                        # Create relationship
                        self.kg.add_relationship(source_id, target_id, 'has_tag')
                        tag_links += 1
                    except Exception as e:
                        logger.warning(f"Error creating tag relationship: {e}")
                
                logger.info(f"Imported {imported} clips, created {tag_links} tag relationships")
                
                return {
                    'status': 'success',
                    'clips_imported': imported,
                    'tag_relationships': tag_links,
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Error importing clips: {e}")
            return {'status': 'error', 'error': str(e)}

    def import_conversations_to_kg(self, limit: int = 50) -> Dict[str, Any]:
        """
        Import copilot conversations from my--father-mother to KG.
        
        Args:
            limit: Maximum number of conversations to import
            
        Returns:
            Import results
        """
        if not self.mfm_db:
            return {'status': 'error', 'error': 'my--father-mother database not found'}

        try:
            with self._get_mfm_connection() as conn:
                cursor = conn.cursor()
                
                # Get recent conversations
                try:
                    cursor.execute('''
                        SELECT id, created_at as started_at, updated_at as last_message_at
                        FROM copilot_chats
                        ORDER BY created_at DESC
                        LIMIT ?
                    ''', (limit,))
                except Exception:
                    # Fallback: just get basic info
                    cursor.execute('''
                        SELECT id
                        FROM copilot_chats
                        LIMIT ?
                    ''', (limit,))
                
                conversations = cursor.fetchall()
                imported = 0
                
                for conv in conversations:
                    conv_id = f"mfm_conversation_{conv['id']}"
                    
                    # Check if already imported
                    try:
                        existing = self.kg.search(conv_id, limit=1)
                        if existing:
                            continue
                    except Exception:
                        pass  # If search fails, continue anyway
                    
                    # Create conversation entity in KG
                    self.kg.insert_conversation(
                        tool='my--father-mother',
                        thread_id=str(conv['id']),
                        context={
                            'source': 'copilot_chat',
                            'started_at': conv['started_at'],
                            'last_activity': conv['last_message_at']
                        }
                    )
                    imported += 1
                
                logger.info(f"Imported {imported} conversations")
                
                return {
                    'status': 'success',
                    'conversations_imported': imported,
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Error importing conversations: {e}")
            return {'status': 'error', 'error': str(e)}

    def get_clipboard_context(self, limit: int = 20) -> Dict[str, Any]:
        """
        Get recent clipboard context for agent use.
        
        Returns clipboard clips, tags, and related metadata that can be
        injected into agent prompts for better context-aware decisions.
        
        Args:
            limit: Maximum clips to return
            
        Returns:
            Dictionary with clips, tags, and metadata
        """
        if not self.mfm_db:
            return {'status': 'error', 'error': 'my--father-matter database not found'}

        try:
            with self._get_mfm_connection() as conn:
                cursor = conn.cursor()
                
                # Get recent clips
                cursor.execute('''
                    SELECT id, created_at, source_app, content, title
                    FROM clips
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (limit,))
                
                clips = []
                for row in cursor.fetchall():
                    clips.append({
                        'id': row['id'],
                        'timestamp': row['created_at'],
                        'app': row['source_app'],
                        'title': row['title'] or row['source_app'],
                        'preview': row['content'][:150] if row['content'] else ''
                    })
                
                # Get most common tags
                cursor.execute('''
                    SELECT t.name, COUNT(ct.id) as count
                    FROM tags t
                    LEFT JOIN clip_tags ct ON t.id = ct.tag_id
                    GROUP BY t.id
                    ORDER BY count DESC
                    LIMIT 10
                ''')
                
                tags = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'status': 'success',
                    'recent_clips': clips,
                    'common_tags': tags,
                    'total_clips': len(clips),
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Error getting clipboard context: {e}")
            return {'status': 'error', 'error': str(e)}

    def search_clipboard(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search my--father-mother clipboard for relevant content.
        
        Args:
            query: Search query text
            limit: Maximum results
            
        Returns:
            List of matching clips
        """
        if not self.mfm_db:
            return []

        try:
            with self._get_mfm_connection() as conn:
                cursor = conn.cursor()
                
                # Search using FTS5 if available, otherwise use simple LIKE
                try:
                    cursor.execute('''
                        SELECT c.id, c.created_at, c.source_app, c.content, c.title
                        FROM clips c
                        WHERE c.id IN (
                            SELECT rowid FROM clips_fts
                            WHERE clips_fts MATCH ?
                        )
                        ORDER BY c.created_at DESC
                        LIMIT ?
                    ''', (query, limit))
                except Exception:
                    # Fallback to LIKE search if FTS5 not available
                    cursor.execute('''
                        SELECT id, created_at, source_app, content, title
                        FROM clips
                        WHERE content LIKE ? OR title LIKE ?
                        ORDER BY created_at DESC
                        LIMIT ?
                    ''', (f'%{query}%', f'%{query}%', limit))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'id': row['id'],
                        'timestamp': row['created_at'],
                        'app': row['source_app'],
                        'title': row['title'],
                        'content': row['content'][:200] if row['content'] else ''
                    })
                
                return results

        except Exception as e:
            logger.error(f"Error searching clipboard: {e}")
            return []

    def sync_bidirectional(self) -> Dict[str, Any]:
        """
        Synchronize bidirectionally between my--father-mother and KG.
        
        - Import clips from MFM to KG
        - Sync conversations
        - Update timestamps
        
        Returns:
            Sync results
        """
        results = {}
        
        # Import clips
        results['clips'] = self.import_clips_to_kg(limit=100)
        
        # Import conversations
        results['conversations'] = self.import_conversations_to_kg(limit=50)
        
        results['status'] = 'success'
        results['timestamp'] = datetime.now().isoformat()
        
        return results


def main():
    """Test the integration."""
    integration = MFMIntegration()
    
    # Test importing clips
    print("Importing clips...")
    result = integration.import_clips_to_kg(limit=50)
    print(json.dumps(result, indent=2))
    
    # Test getting clipboard context
    print("\nGetting clipboard context...")
    context = integration.get_clipboard_context(limit=10)
    print(json.dumps(context, indent=2))
    
    # Test searching
    print("\nSearching clipboard...")
    results = integration.search_clipboard("TypeScript", limit=5)
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
