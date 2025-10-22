"""
監査ログ用JSONフォーマッター
"""

import json
import logging


class AuditJSONFormatter(logging.Formatter):
    """
    監査ログをJSON形式で出力するフォーマッター

    出力形式:
    {
        "timestamp": "2025-01-20 15:30:45",
        "level": "INFO",
        "user": "9999",
        "action": "LOGIN",
        "model": "Auth",
        "object_id": null,
        "ip": "192.168.1.100",
        "changes": "{}",
        "message": "ユーザーがログインしました"
    }
    """

    def format(self, record):
        """ログレコードをJSON形式に変換"""
        log_data = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "user": getattr(record, "user", "unknown"),
            "action": getattr(record, "action", ""),
            "model": getattr(record, "model", ""),
            "object_id": getattr(record, "object_id", None),
            "ip": getattr(record, "ip", ""),
            "changes": getattr(record, "changes", "{}"),
            "message": record.getMessage(),
        }

        return json.dumps(log_data, ensure_ascii=False)
