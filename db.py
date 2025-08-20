"""
Database module for CiteGraph
Handles SQLite operations for storing and retrieving paper metadata and citations
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
import hashlib
import secrets


class CitationDatabase:
    """SQLite database handler for CiteGraph"""
    
    def __init__(self, db_path: str = "citegraph.db"):
        """Initialize database connection and create tables if they don't exist"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    email TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    password_iters INTEGER NOT NULL DEFAULT 200000,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)

            # Papers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    doi TEXT PRIMARY KEY,
                    title TEXT,
                    authors TEXT,
                    year INTEGER,
                    journal TEXT,
                    abstract TEXT,
                    citation_count INTEGER DEFAULT 0,
                    reference_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Citations table (who cites whom)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS citations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    citing_doi TEXT,
                    cited_doi TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (citing_doi) REFERENCES papers (doi),
                    FOREIGN KEY (cited_doi) REFERENCES papers (doi),
                    UNIQUE(citing_doi, cited_doi)
                )
            """)
            
            # References table (who references whom)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS paper_references (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paper_doi TEXT,
                    reference_doi TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (paper_doi) REFERENCES papers (doi),
                    FOREIGN KEY (reference_doi) REFERENCES papers (doi),
                    UNIQUE(paper_doi, reference_doi)
                )
            """)
            
            # Keywords table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS keywords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paper_doi TEXT,
                    keyword TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (paper_doi) REFERENCES papers (doi)
                )
            """)
            
            conn.commit()
    
    def save_paper(self, paper_data: Dict) -> bool:
        """Save paper metadata to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Extract authors as JSON string
                authors_json = json.dumps(paper_data.get('authors', []))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO papers 
                    (doi, title, authors, year, journal, abstract, citation_count, reference_count, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    paper_data['doi'],
                    paper_data.get('title', ''),
                    authors_json,
                    paper_data.get('year'),
                    paper_data.get('journal', ''),
                    paper_data.get('abstract', ''),
                    paper_data.get('citation_count', 0),
                    paper_data.get('reference_count', 0),
                    datetime.now()
                ))
                
                # Save keywords if available
                if 'keywords' in paper_data:
                    self._save_keywords(paper_data['doi'], paper_data['keywords'])
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving paper: {e}")
            return False
    
    def _save_keywords(self, doi: str, keywords: List[str]):
        """Save keywords for a paper"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Remove existing keywords
                cursor.execute("DELETE FROM keywords WHERE paper_doi = ?", (doi,))
                
                # Insert new keywords
                for keyword in keywords:
                    cursor.execute("""
                        INSERT INTO keywords (paper_doi, keyword)
                        VALUES (?, ?)
                    """, (doi, keyword))
                
                conn.commit()
        except Exception as e:
            print(f"Error saving keywords: {e}")
    
    def save_citations(self, citing_doi: str, cited_dois: List[str]):
        """Save citation relationships"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for cited_doi in cited_dois:
                    cursor.execute("""
                        INSERT OR IGNORE INTO citations (citing_doi, cited_doi)
                        VALUES (?, ?)
                    """, (citing_doi, cited_doi))
                
                conn.commit()
        except Exception as e:
            print(f"Error saving citations: {e}")
    
    def save_references(self, paper_doi: str, reference_dois: List[str]):
        """Save reference relationships"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for reference_doi in reference_dois:
                    cursor.execute("""
                        INSERT OR IGNORE INTO paper_references (paper_doi, reference_doi)
                        VALUES (?, ?)
                    """, (paper_doi, reference_doi))
                
                conn.commit()
        except Exception as e:
            print(f"Error saving references: {e}")
    
    # --- Authentication helpers ---
    def _hash_password(self, password: str, salt: Optional[str] = None, iters: int = 200000) -> Tuple[str, str, int]:
        """Hash a password with PBKDF2-HMAC-SHA256. Returns (hash_hex, salt_hex, iterations)."""
        if not salt:
            salt = secrets.token_hex(16)
        # Derive key
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), iters)
        return dk.hex(), salt, iters

    def create_user(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """Create a user account. Returns (success, message)."""
        try:
            password_hash, salt, iters = self._hash_password(password)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO users (username, email, password_hash, password_salt, password_iters)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (username.strip(), email.strip().lower(), password_hash, salt, iters)
                )
                conn.commit()
            return True, "User created successfully."
        except sqlite3.IntegrityError as e:
            if 'users.username' in str(e).lower():
                return False, "Username already exists."
            if 'users.email' in str(e).lower():
                return False, "Email already in use."
            return False, "Integrity error while creating user."
        except Exception as e:
            return False, f"Error creating user: {e}"

    def verify_user_credentials(self, username_or_email: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """Verify credentials and return user dict on success."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                key = username_or_email.strip()
                # Find by username or email
                cursor.execute(
                    """
                    SELECT id, username, email, password_hash, password_salt, password_iters
                    FROM users
                    WHERE username = ? OR email = ?
                    """,
                    (key, key.lower())
                )
                row = cursor.fetchone()
                if not row:
                    return False, None
                user_id, username, email, stored_hash, salt, iters = row
                # Verify password
                check_hash, _, _ = self._hash_password(password, salt=salt, iters=iters)
                if secrets.compare_digest(check_hash, stored_hash):
                    # Update last_login
                    cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now(), user_id))
                    conn.commit()
                    return True, {"id": user_id, "username": username, "email": email}
                return False, None
        except Exception:
            return False, None

    def get_paper(self, doi: str) -> Optional[Dict]:
        """Retrieve paper metadata by DOI"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT doi, title, authors, year, journal, abstract, 
                           citation_count, reference_count, created_at, updated_at
                    FROM papers WHERE doi = ?
                """, (doi,))
                
                row = cursor.fetchone()
                if row:
                    paper = {
                        'doi': row[0],
                        'title': row[1],
                        'authors': json.loads(row[2]) if row[2] else [],
                        'year': row[3],
                        'journal': row[4],
                        'abstract': row[5],
                        'citation_count': row[6],
                        'reference_count': row[7],
                        'created_at': row[8],
                        'updated_at': row[9]
                    }
                    
                    # Get keywords
                    paper['keywords'] = self.get_keywords(doi)
                    return paper
                
                return None
                
        except Exception as e:
            print(f"Error retrieving paper: {e}")
            return None
    
    def get_keywords(self, doi: str) -> List[str]:
        """Get keywords for a paper"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT keyword FROM keywords WHERE paper_doi = ?", (doi,))
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Error retrieving keywords: {e}")
            return []
    
    def get_citations(self, doi: str) -> List[str]:
        """Get papers that cite the given DOI"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT citing_doi FROM citations WHERE cited_doi = ?", (doi,))
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Error retrieving citations: {e}")
            return []
    
    def get_references(self, doi: str) -> List[str]:
        """Get papers that the given DOI references"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT reference_doi FROM paper_references WHERE paper_doi = ?", (doi,))
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Error retrieving references: {e}")
            return []
    
    def get_papers_by_year(self, start_year: int, end_year: int) -> List[Dict]:
        """Get papers within a year range"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT doi, title, authors, year, journal, citation_count
                    FROM papers 
                    WHERE year BETWEEN ? AND ?
                    ORDER BY year DESC, citation_count DESC
                """, (start_year, end_year))
                
                papers = []
                for row in cursor.fetchall():
                    papers.append({
                        'doi': row[0],
                        'title': row[1],
                        'authors': json.loads(row[2]) if row[2] else [],
                        'year': row[3],
                        'journal': row[4],
                        'citation_count': row[5]
                    })
                
                return papers
                
        except Exception as e:
            print(f"Error retrieving papers by year: {e}")
            return []
    
    def get_citation_graph_data(self, root_doi: str, max_depth: int = 2) -> Dict:
        """Get citation graph data for visualization"""
        try:
            graph_data = {
                'nodes': [],
                'edges': [],
                'root_doi': root_doi
            }
            
            # Get root paper
            root_paper = self.get_paper(root_doi)
            if not root_paper:
                return graph_data
            
            # Add root node
            graph_data['nodes'].append({
                'id': root_doi,
                'label': root_paper['title'][:50] + '...' if len(root_paper['title']) > 50 else root_paper['title'],
                'title': root_paper['title'],
                'year': root_paper['year'],
                'citation_count': root_paper['citation_count'],
                'group': 'root'
            })
            
            # Get references (papers this paper cites)
            references = self.get_references(root_doi)
            for ref_doi in references[:15]:  # Limit to first 15 references
                ref_paper = self.get_paper(ref_doi)
                if ref_paper:
                    graph_data['nodes'].append({
                        'id': ref_doi,
                        'label': ref_paper['title'][:50] + '...' if len(ref_paper['title']) > 50 else ref_paper['title'],
                        'title': ref_paper['title'],
                        'year': ref_paper['year'],
                        'citation_count': ref_paper['citation_count'],
                        'group': 'reference'
                    })
                    graph_data['edges'].append({
                        'from': root_doi,
                        'to': ref_doi,
                        'arrows': 'to',
                        'color': '#ff7675'
                    })
            
            # Get citations (papers that cite this paper)
            citations = self.get_citations(root_doi)
            for cit_doi in citations[:15]:  # Limit to first 15 citations
                cit_paper = self.get_paper(cit_doi)
                if cit_paper:
                    graph_data['nodes'].append({
                        'id': cit_doi,
                        'label': cit_paper['title'][:50] + '...' if len(cit_paper['title']) > 50 else cit_paper['title'],
                        'title': cit_paper['title'],
                        'year': cit_paper['year'],
                        'citation_count': cit_paper['citation_count'],
                        'group': 'citation'
                    })
                    graph_data['edges'].append({
                        'from': cit_doi,
                        'to': root_doi,
                        'arrows': 'to',
                        'color': '#74b9ff'
                    })
            
            # Get related papers (papers that share references or are cited together)
            related_papers = self.get_related_papers(root_doi)
            for rel_doi in related_papers[:10]:  # Limit to first 10 related papers
                rel_paper = self.get_paper(rel_doi)
                if rel_paper and rel_doi not in [n['id'] for n in graph_data['nodes']]:
                    graph_data['nodes'].append({
                        'id': rel_doi,
                        'label': rel_paper['title'][:50] + '...' if len(rel_paper['title']) > 50 else rel_paper['title'],
                        'title': rel_paper['title'],
                        'year': rel_paper['year'],
                        'citation_count': rel_paper['citation_count'],
                        'group': 'related'
                    })
                    # Add edge to show relationship (dashed line)
                    graph_data['edges'].append({
                        'from': root_doi,
                        'to': rel_doi,
                        'arrows': 'none',
                        'color': '#00b894',
                        'dashes': True
                    })
            
            return graph_data
            
        except Exception as e:
            print(f"Error getting citation graph data: {e}")
            return {'nodes': [], 'edges': [], 'root_doi': root_doi}
    
    def get_timeline_data(self, root_doi: str) -> Dict:
        """Get timeline data for knowledge evolution visualization"""
        try:
            # Get all connected papers
            graph_data = self.get_citation_graph_data(root_doi, max_depth=3)
            
            # Group papers by year
            year_counts = {}
            for node in graph_data['nodes']:
                year = node.get('year', 0)
                if year > 0:
                    year_counts[year] = year_counts.get(year, 0) + 1
            
            # Convert to sorted list
            timeline_data = sorted(year_counts.items())
            
            return {
                'years': [item[0] for item in timeline_data],
                'counts': [item[1] for item in timeline_data],
                'total_papers': len(graph_data['nodes'])
            }
            
        except Exception as e:
            print(f"Error getting timeline data: {e}")
            return {'years': [], 'counts': [], 'total_papers': 0}
    
    def search_papers(self, query: str) -> List[Dict]:
        """Search papers by title, author, or keyword"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                search_term = f"%{query}%"
                
                cursor.execute("""
                    SELECT DISTINCT p.doi, p.title, p.authors, p.year, p.journal, p.citation_count
                    FROM papers p
                    LEFT JOIN keywords k ON p.doi = k.paper_doi
                    WHERE p.title LIKE ? OR p.authors LIKE ? OR k.keyword LIKE ?
                    ORDER BY p.citation_count DESC, p.year DESC
                    LIMIT 50
                """, (search_term, search_term, search_term))
                
                papers = []
                for row in cursor.fetchall():
                    papers.append({
                        'doi': row[0],
                        'title': row[1],
                        'authors': json.loads(row[2]) if row[2] else [],
                        'year': row[3],
                        'journal': row[4],
                        'citation_count': row[5]
                    })
                
                return papers
                
        except Exception as e:
            print(f"Error searching papers: {e}")
            return []
    
    def get_related_papers(self, doi: str) -> List[str]:
        """Get papers that are related through shared references or citations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Find papers that share references with the given paper
                cursor.execute("""
                    SELECT DISTINCT pr1.paper_doi
                    FROM paper_references pr1
                    JOIN paper_references pr2 ON pr1.reference_doi = pr2.reference_doi
                    WHERE pr2.paper_doi = ? AND pr1.paper_doi != ?
                    ORDER BY (
                        SELECT COUNT(*) 
                        FROM paper_references pr3 
                        WHERE pr3.paper_doi = pr1.paper_doi
                    ) DESC
                    LIMIT 10
                """, (doi, doi))
                
                related_dois = [row[0] for row in cursor.fetchall()]
                
                # Also find papers that are frequently cited together
                cursor.execute("""
                    SELECT DISTINCT c1.citing_doi
                    FROM citations c1
                    JOIN citations c2 ON c1.citing_doi = c2.citing_doi
                    WHERE c2.cited_doi = ? AND c1.cited_doi != ?
                    ORDER BY (
                        SELECT COUNT(*) 
                        FROM citations c3 
                        WHERE c3.citing_doi = c1.citing_doi
                    ) DESC
                    LIMIT 10
                """, (doi, doi))
                
                co_cited_dois = [row[0] for row in cursor.fetchall()]
                
                # Combine and remove duplicates
                all_related = list(set(related_dois + co_cited_dois))
                
                return all_related[:15]  # Return top 15 related papers
                
        except Exception as e:
            print(f"Error getting related papers: {e}")
            return []
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count papers
                cursor.execute("SELECT COUNT(*) FROM papers")
                paper_count = cursor.fetchone()[0]
                
                # Count citations
                cursor.execute("SELECT COUNT(*) FROM citations")
                citation_count = cursor.fetchone()[0]
                
                # Count references
                cursor.execute("SELECT COUNT(*) FROM paper_references")
                reference_count = cursor.fetchone()[0]
                
                # Year range
                cursor.execute("SELECT MIN(year), MAX(year) FROM papers WHERE year IS NOT NULL")
                year_range = cursor.fetchone()
                min_year = year_range[0] if year_range[0] else 0
                max_year = year_range[1] if year_range[1] else 0
                
                return {
                    'total_papers': paper_count,
                    'total_citations': citation_count,
                    'total_references': reference_count,
                    'year_range': (min_year, max_year)
                }
                
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {
                'total_papers': 0,
                'total_citations': 0,
                'total_references': 0,
                'year_range': (0, 0)
            }
