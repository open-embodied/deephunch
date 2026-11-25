"""SQLite 持久层（纯标准库实现，规避受策略限制的编译扩展）"""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS datasets(
  id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, domain TEXT DEFAULT 'robotics',
  video_count INTEGER DEFAULT 0, hours REAL DEFAULT 0.0, status TEXT DEFAULT 'active',
  license TEXT DEFAULT 'proprietary', created_at TEXT);
CREATE TABLE IF NOT EXISTS curator_jobs(
  id INTEGER PRIMARY KEY AUTOINCREMENT, dataset_id INTEGER, source_uri TEXT,
  stages TEXT, stage_progress INTEGER DEFAULT 0, logs TEXT DEFAULT '',
  clips_out INTEGER DEFAULT 0, status TEXT DEFAULT 'queued', created_at TEXT);
CREATE TABLE IF NOT EXISTS tokenize_jobs(
  id INTEGER PRIMARY KEY AUTOINCREMENT, dataset_id INTEGER, tokenizer TEXT,
  direction TEXT DEFAULT 'encode', clips_in INTEGER DEFAULT 0, tokens_out TEXT DEFAULT '',
  compression TEXT DEFAULT '', status TEXT DEFAULT 'queued', created_at TEXT);
CREATE TABLE IF NOT EXISTS gen_jobs(
  id INTEGER PRIMARY KEY AUTOINCREMENT, job_type TEXT, prompt TEXT DEFAULT '',
  model TEXT DEFAULT 'dh-predict-2b', seed INTEGER DEFAULT 0, duration_s INTEGER DEFAULT 5,
  backend TEXT DEFAULT 'mock', artifact TEXT DEFAULT '', status TEXT DEFAULT 'queued', created_at TEXT);
CREATE TABLE IF NOT EXISTS posttrain_jobs(
  id INTEGER PRIMARY KEY AUTOINCREMENT, base_model TEXT, preset TEXT, dataset_id INTEGER,
  config_json TEXT DEFAULT '{}', epoch INTEGER DEFAULT 0, loss REAL DEFAULT 0.0,
  artifact TEXT DEFAULT '', status TEXT DEFAULT 'queued', created_at TEXT);
CREATE TABLE IF NOT EXISTS model_artifacts(
  id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, family TEXT, size_b REAL DEFAULT 0,
  version TEXT DEFAULT '1.0', license TEXT DEFAULT 'dh-open-model-license',
  uri TEXT DEFAULT '', notes TEXT DEFAULT '', created_at TEXT);
CREATE TABLE IF NOT EXISTS guardrail_events(
  id INTEGER PRIMARY KEY AUTOINCREMENT, phase TEXT, action TEXT,
  reason TEXT DEFAULT '', created_at TEXT);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(SCHEMA)


def get_db():
    """FastAPI 依赖：每请求一个连接，退出时提交并关闭"""
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


@contextmanager
def session():
    """非 FastAPI 场景（后台线程/脚本）使用的上下文管理器"""
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def q(conn, sql: str, params: tuple = ()) -> list[dict]:
    """查询，返回字典列表"""
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def one(conn, sql: str, params: tuple = ()) -> dict | None:
    rows = q(conn, sql, params)
    return rows[0] if rows else None


def run(conn, sql: str, params: tuple = ()) -> int:
    """执行写语句，返回 lastrowid"""
    cur = conn.execute(sql, params)
    conn.commit()
    return cur.lastrowid
