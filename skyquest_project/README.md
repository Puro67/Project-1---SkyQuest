# ✈️ SkyQuest Flight Simulator & SQL Leaderboard

SkyQuest is a multi-stage procedural airplane survival game built with **Python** and **Pygame**, featuring collectible coins, an automatic airframe repair system, and a persistent **SQL Database Leaderboard** (supporting MariaDB / MySQL with an automatic SQLite fallback).

---

## 📋 Table of Contents
1. [Quick Start](#-quick-start)
2. [Configuring SQL Database Credentials](#-configuring-sql-database-credentials)
3. [Setting Up MariaDB / MySQL (HeidiSQL / XAMPP)](#-setting-up-mariadb--mysql-heidisql--xampp)
4. [Automatic SQLite Fallback](#-automatic-sqlite-fallback)
5. [Game Mechanics & Controls](#-game-mechanics--controls)
6. [Testing & Troubleshooting](#-testing--troubleshooting)

---

## 🚀 Quick Start

### 1. Requirements
Ensure you have Python 3.10+ installed along with the required libraries:
```powershell
pip install pygame mysql-connector-python
```

### 2. Run the Game
```powershell
python skyquest_real_final.py
```

---

## 🔑 Configuring SQL Database Credentials

All database connection parameters are centralized in [**`db_config.py`**](file:///d:/myproject/python-assignments/skyquest_project/db_config.py). 

Open `db_config.py` in your code editor to enter your SQL username, password, host, and database name:

```python
# Select database engine: "mysql" (MariaDB / HeidiSQL) or "sqlite"
DB_ENGINE = "mysql"

# MySQL / MariaDB Connection Parameters
MYSQL_CONFIG = {
    "host": "127.0.0.1",           # Server hostname or IP (default: "127.0.0.1" or "localhost")
    "port": 3306,                  # MySQL port (default: 3306)
    "database": "db_flight_game",  # Name of the database to store scores
    "user": "root",                # Your MySQL username (e.g., "root")
    "password": "YOUR_PASSWORD",   # Your MySQL password (enter your password here)
    "autocommit": True,
    "connection_timeout": 3
}

# SQLite database filename (used automatically as fallback if MySQL is unreachable)
SQLITE_DB_NAME = "skyquest.db"
```

### Parameter Breakdown:
| Parameter | Description | Default / Example |
| :--- | :--- | :--- |
| `DB_ENGINE` | Set to `"mysql"` to use MariaDB/MySQL, or `"sqlite"` for local file storage | `"mysql"` |
| `host` | IP address or hostname of your MySQL server | `"127.0.0.1"` |
| `port` | Network port for MySQL / MariaDB | `3306` |
| `database` | The target database where the `leaderboard` table lives | `"db_flight_game"` |
| `user` | Your database user account | `"root"` |
| `password` | Your database user's password | `"Hoang"` *(replace with your own)* |
| `autocommit` | Automatically commits score records to disk | `True` |

---

## 🗄️ Setting Up MariaDB / MySQL (HeidiSQL / XAMPP)

### Step 1: Start your SQL Server
- If using **HeidiSQL / MariaDB**: Make sure the MariaDB Windows service is running.
- If using **XAMPP**: Start the **MySQL** module in the XAMPP Control Panel.

### Step 2: Create the Database
Open **HeidiSQL** (or phpMyAdmin / MySQL CLI) and run this SQL query once to create the database:
```sql
CREATE DATABASE IF NOT EXISTS db_flight_game;
```

### Step 3: Automatic Table Initialization
You do **not** need to manually create the `leaderboard` table! The game automatically creates the table and performance indexes on launch.

For reference, the schema automatically created by `db_leaderboard.py` is:
```sql
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
```

---

## 🛡️ Automatic SQLite Fallback

If:
- Your MySQL/MariaDB service is stopped,
- The network connection times out, or
- `mysql-connector-python` is not installed,

SkyQuest **automatically falls back to a local SQLite database** ([`skyquest.db`](file:///d:/myproject/python-assignments/skyquest_project/skyquest.db)). The game will **never crash** due to a database connection failure.

---

## 🎮 Game Mechanics & Controls

### Flight Controls:
- **Steer Plane**: <kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> or <kbd>Arrow Keys</kbd>
- **Start Flight / Advance**: <kbd>SPACE</kbd> or <kbd>ENTER</kbd>
- **View Leaderboard**: <kbd>L</kbd> (from Main Menu or Win screens)
- **Quit Game / Back**: <kbd>ESC</kbd>

### 🪙 Procedural Coin System:
- Collectible gold coins spawn ahead of the aircraft in randomized formations (*singles, flight lines, parabolic arcs*).
- Spawns intelligently calculate safe altitudes to avoid overlapping oncoming obstacles.

### 🔧 Automatic Airframe Repair:
- Every **10 HP lost costs 10 coins**.
- When you take damage, the plane **automatically consumes 10 coins to restore back to 100 HP**.
- If you have fewer than 10 coins when hit, the damage remains until you gather enough coins, at which point auto-repair triggers immediately.

### 🏆 Leaderboard & Scoring:
- When the flight concludes (either on **Victory** in Level 3 or **Game Over**):
  1. The game prompts: `ENTER PILOT NAME FOR THE LEADERBOARD:`.
  2. Type your pilot callsign and press <kbd>ENTER</kbd>.
  3. The database saves your run if it beats your **Personal Best**.
  4. The **Top 10 Hall of Fame** table is displayed with ranks, high scores, coins, and dates.

---

## 🧪 Testing & Troubleshooting

### Test the Database Connection Standalone:
To test your credentials without starting the full game:
```powershell
python db_leaderboard.py
```
- If successful, it prints:
  ```text
  [Database] Leaderboard schema initialized successfully using [MYSQL].
  ```
- If it cannot connect to MySQL, it prints a warning and confirms fallback:
  ```text
  [Database] Warning: MySQL connection failed (...). Falling back to SQLite.
  ```

---

## 📁 Project File Structure

```text
skyquest_project/
├── Image/                  # Plane, Coin, Sun, Cloud, and Obstacle sprites
├── db_config.py            # 👈 EDIT SQL USERNAME & PASSWORD HERE
├── db_leaderboard.py       # MariaDB / MySQL / SQLite database manager
├── skyquest.db             # Local SQLite database fallback file
├── skyquest_real_final.py  # Main game executable (includes embedded Coin System)
└── README.md               # Setup & configuration guide
```
