"""
監査ログ用JSONフォーマッター（5W1H対応版）

Phase 1: 最小限の改善
- エンドポイント情報（endpoint, http_method）
- HTTPステータス（http_status）
- リソース詳細（object_repr, view_name）
"""

import re
import json
import logging


class AuditJSONFormatter(logging.Formatter):
    SANITIZE_PATTERN = re.compile(r"[\x00-\x1f\x7f-\x9f]")

    def _sanitize_value(self, value):
        """ログ出力前の最終サニタイズ"""
        if not isinstance(value, str):
            return value

        # 制御文字を除去
        value = self.SANITIZE_PATTERN.sub("", value)

        # 改行を除去
        value = value.replace("\n", "").replace("\r", "")

        return value

    """
    監査ログをJSON形式で出力するフォーマッター（5W1H対応版）

    Phase 1 出力形式:
    {
        "request_id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": "2025-01-20 15:30:45",
        "level": "WARNING",

        // Who（誰が）
        "user_id": "EMP9999",

        // When（いつ）
        "timestamp": "2025-01-20 15:30:45",

        // Where（どこで）
        "endpoint": "/api/users/EMP0001/",
        "http_method": "GET",
        "ip": "192.168.1.100",

        // What（何を）
        "action": "READ_SENSITIVE",
        "model": "User",
        "object_id": "EMP0001",
        "object_repr": "山田太郎（EMP0001）",

        // How（どのように）
        "http_status": 200,
        "view_name": "UserDetailView",

        "changes": "{}",
        "message": "機密情報閲覧: /api/users/EMP0001/"
    }
    """

    def format(self, record):
        """ログレコードをJSON形式に変換"""
        log_data = {
            # ========== 基本情報 ==========
            "request_id": getattr(record, "request_id", "N/A"),
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S"),
            # "level": record.levelname,
            # ========== Who（誰が） ==========
            "user_id": self._sanitize_value(getattr(record, "user", "unknown")),
            # ========== Where（どこで） ==========
            "endpoint": getattr(record, "endpoint", ""),
            # "http_method": getattr(record, "http_method", ""),
            "ip": getattr(record, "ip", ""),
            # ========== What（何を） ==========
            # "action": getattr(record, "action", ""),
            # "model": getattr(record, "model", ""),
            # "object_id": getattr(record, "object_id", None),
            "object_repr": getattr(record, "object_repr", ""),
            # ========== How（どのように） ==========
            # "http_status": getattr(record, "http_status", None),
            "view_name": getattr(record, "view_name", ""),
            # ========== 変更内容 ==========
            "changes": getattr(record, "changes", "{}"),
            # ========== メッセージ ==========
            "message": self._sanitize_value(record.getMessage()),
        }

        return json.dumps(log_data, ensure_ascii=False)
