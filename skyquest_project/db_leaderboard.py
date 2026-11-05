"""Database and Leaderboard Management Module for SkyQuest.

Configured with local MariaDB / MySQL server credentials found from HeidiSQL.
If MySQL is not available, the game will automatically fall back to SQLite.

Requirements satisfied:
  - Local SQLite / MySQL database schema to store leaderboard records.
  - Leaderboard tracks a player's highest single-run score and coins (not cumulative).
  - Initializes/creates table if it doesn't exist.
  - Inserts or updates a player's score at the end of a run only if the new score is higher.
  - Fetches and displays the top 10 leaderboard entries.
"""

import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Optional MySQL driver
try:
    import mysql.connector
    HAS_MYSQL_DRIVER = True
except ImportError:
    HAS_MYSQL_DRIVER = False

# ==============================================================================
# DATABASE CONFIGURATION
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    from db_config import DB_ENGINE, MYSQL_CONFIG, SQLITE_DB_NAME
    if not os.path.isabs(SQLITE_DB_NAME):
        SQLITE_DB_NAME = os.path.join(BASE_DIR, SQLITE_DB_NAME)
except ImportError:
    DB_ENGINE = "mysql"  # "mysql" (MariaDB / HeidiSQL) or "sqlite"
    MYSQL_CONFIG = {
        "host": "127.0.0.1",
        "port": 3306,
        "database": "db_flight_game",
        "user": "root",
        "password": "Hoang",
        "autocommit": True,
        "connection_timeout": 3
    }
    SQLITE_DB_NAME = os.path.join(BASE_DIR, "skyquest.db")


class LeaderboardManager:
    """Manages leaderboard schema, personal best scores, and top-10 queries."""

    def __init__(self, engine: str = DB_ENGINE):
        self.engine = engine.lower()
        self.active_engine = "sqlite"
        self._connection_tested = False
        self.init_database()

    def _get_connection(self) -> Tuple[Any, str]:
        """Returns active connection and parameter placeholder ('%s' or '?')."""
        if self.engine == "mysql" and HAS_MYSQL_DRIVER:
            try:
                conn = mysql.connector.connect(**MYSQL_CONFIG)
                self.active_engine = "mysql"
                return conn, "%s"
            except Exception as e:
                if not self._connection_tested:
                    print(f"[Database] Warning: MySQL connection failed ({e}). Falling back to SQLite.")
                    self._connection_tested = True

        # SQLite fallback
        conn = sqlite3.connect(SQLITE_DB_NAME)
        conn.row_factory = sqlite3.Row
        self.active_engine = "sqlite"
        return conn, "?"

    def init_database(self) -> None:
        """Requirement 2: Initializes the leaderboard table if it doesn't exist."""
        conn, ph = self._get_connection()
        cursor = conn.cursor()

        try:
            if self.active_engine == "mysql":
                # Matches standard Metropolia / HeidiSQL flight game schema
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS leaderboard (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    player_name VARCHAR(50) NOT NULL,
                    score INT NOT NULL,
                    coins INT NOT NULL,
                    hp INT DEFAULT 100,
                    stages_cleared INT DEFAULT 1,
                    status VARCHAR(20) DEFAULT 'LANDED',
                    flight_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_player (player_name),
                    INDEX idx_score (score DESC)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
            else:
                # SQLite Schema
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS leaderboard (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    coins INTEGER NOT NULL,
                    hp INTEGER DEFAULT 100,
                    stages_cleared INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'LANDED',
                    flight_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_lb_player ON leaderboard (player_name);
                """)
                cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_lb_score ON leaderboard (score DESC);
                """)
                conn.commit()

            print(f"[Database] Leaderboard schema initialized successfully using [{self.active_engine.upper()}].")
        except Exception as e:
            print(f"[Database] Error initializing database: {e}")
        finally:
            cursor.close()
            conn.close()

    def record_run_score(
        self,
        player_name: str,
        run_score: int,
        run_coins: int,
        hp: int = 100,
        stages_cleared: int = 3,
        status: str = "VICTORY"
    ) -> Dict[str, Any]:
        """Requirement 2: Inserts or updates a player's single-run score.

        Only updates if the new score is higher than their previous personal best.
        """
        clean_name = (player_name or "Pilot").strip()[:20] or "Pilot"
        conn, ph = self._get_connection()
        cursor = conn.cursor()

        result = {
            "player_name": clean_name,
            "run_score": run_score,
            "run_coins": run_coins,
            "is_personal_best": False,
            "previous_best": 0,
            "status": "NO_CHANGE"
        }

        try:
            # 1. Query the player's existing best single-run record
            query_check = f"""
            SELECT id, score, coins 
            FROM leaderboard 
            WHERE player_name = {ph}
            ORDER BY score DESC 
            LIMIT 1;
            """
            cursor.execute(query_check, (clean_name,))
            row = cursor.fetchone()

            if row is None:
                # 2. First flight record for this pilot -> INSERT
                query_insert = f"""
                INSERT INTO leaderboard (player_name, score, coins, hp, stages_cleared, status, flight_date)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, CURRENT_TIMESTAMP);
                """
                cursor.execute(query_insert, (clean_name, run_score, run_coins, hp, stages_cleared, status))
                if self.active_engine == "sqlite":
                    conn.commit()

                result["is_personal_best"] = True
                result["previous_best"] = 0
                result["status"] = "NEW_PLAYER_RECORD"
                print(f"[Database] First record logged for '{clean_name}': {run_score:,} pts, {run_coins} coins.")

            else:
                # 3. Existing record found
                rec_id = row[0] if isinstance(row, (tuple, list)) else row["id"]
                prev_high = row[1] if isinstance(row, (tuple, list)) else row["score"]
                result["previous_best"] = prev_high

                if run_score > prev_high:
                    # New run beats previous personal best -> UPDATE
                    query_update = f"""
                    UPDATE leaderboard 
                    SET score = {ph}, coins = {ph}, hp = {ph}, stages_cleared = {ph}, status = {ph}, flight_date = CURRENT_TIMESTAMP
                    WHERE id = {ph};
                    """
                    cursor.execute(query_update, (run_score, run_coins, hp, stages_cleared, status, rec_id))
                    if self.active_engine == "sqlite":
                        conn.commit()

                    result["is_personal_best"] = True
                    result["status"] = "NEW_PERSONAL_BEST"
                    print(f"[Database] ★ NEW PERSONAL BEST for '{clean_name}'! Beat {prev_high:,} -> {run_score:,} pts.")
                else:
                    # New run is lower or equal -> DO NOT UPDATE
                    result["is_personal_best"] = False
                    result["status"] = "BEST_NOT_BEATEN"
                    print(f"[Database] Run score ({run_score:,}) did not beat personal best ({prev_high:,}).")

        except Exception as e:
            print(f"[Database] Error recording score: {e}")
            result["status"] = "ERROR"
        finally:
            cursor.close()
            conn.close()

        return result

    def fetch_top_10(self) -> List[Dict[str, Any]]:
        """Requirement 2: Fetches top 10 unique pilot high scores (single-run bests)."""
        conn, ph = self._get_connection()
        cursor = conn.cursor()
        top_entries = []

        try:
            # Group by player_name to guarantee 1 entry per pilot (their best single-run)
            query = """
            SELECT player_name, MAX(score) as high_score, MAX(coins) as coins_collected, MAX(flight_date) as achieved_at
            FROM leaderboard
            GROUP BY player_name
            ORDER BY high_score DESC, coins_collected DESC
            LIMIT 10;
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                if isinstance(row, (tuple, list)):
                    name, score, coins, achieved_at = row[0], row[1], row[2], row[3]
                else:
                    name = row["player_name"]
                    score = row["high_score"]
                    coins = row["coins_collected"]
                    achieved_at = row["achieved_at"]

                # Format timestamp
                if isinstance(achieved_at, datetime):
                    date_str = achieved_at.strftime("%Y-%m-%d %H:%M")
                else:
                    date_str = str(achieved_at)[:16] if achieved_at else "N/A"

                top_entries.append({
                    "player_name": name,
                    "high_score": score,
                    "coins_collected": coins,
                    "achieved_at": date_str
                })
        except Exception as e:
            print(f"[Database] Query error fetching leaderboard: {e}")
        finally:
            cursor.close()
            conn.close()

        return top_entries

    def display_leaderboard(self) -> None:
        """Requirement 2: Fetches and displays formatted Top 10 Leaderboard table in console."""
        entries = self.fetch_top_10()

        print("\n" + "=" * 74)
        print(f"             SKYQUEST LEADERBOARD (TOP 10 PILOTS) [{self.active_engine.upper()}]")
        print("=" * 74)
        print(f" {'Rank':<5} | {'Pilot Callsign':<18} | {'Personal Best':>13} | {'Run Coins':>9} | {'Date':<16} ")
        print("-" * 74)

        if not entries:
            print("  No flight records found. Complete a flight to enter the Hall of Fame!")
        else:
            medals = {1: "1st", 2: "2nd", 3: "3rd"}
            for idx, entry in enumerate(entries, 1):
                rank_str = medals.get(idx, f"#{idx}")
                print(
                    f" {rank_str:<5} | {entry['player_name']:<18} | "
                    f"{entry['high_score']:>10,} pts | {entry['coins_collected']:>9} | "
                    f"{entry['achieved_at']:<16} "
                )

        print("=" * 74 + "\n")


# Global manager instance
db_manager = LeaderboardManager()


if __name__ == "__main__":
    print("[Leaderboard Self-Test] Running verification on local database...")
    db_manager.display_leaderboard()
