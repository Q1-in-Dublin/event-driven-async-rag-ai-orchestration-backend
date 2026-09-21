import json
import hmac
import hashlib
import time
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)


def generate_slack_signature(body: bytes, timestamp: str) -> str:
    """테스트용 Slack 서명 생성"""
    sig_basestring = f"v0:{timestamp}:{body.decode()}"
    return "v0=" + hmac.new(
        settings.slack_signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()


class TestSlackSignatureVerification:
    """Slack 서명 검증 테스트"""

    def test_slack_events_valid_signature(self):
        """유효한 서명 → 200 OK"""
        payload = {
            "type": "event_callback",
            "event": {
                "type": "app_mention",
                "user": "U123456",
                "text": "휴가 정책?",
                "channel": "C123456",
                "ts": "1234567890.123456"
            }
        }
        body = json.dumps(payload).encode()
        timestamp = str(int(time.time()))
        signature = generate_slack_signature(body, timestamp)

        response = client.post(
            "/slack/events",
            content=body,
            headers={
                "X-Slack-Request-Timestamp": timestamp,
                "X-Slack-Signature": signature,
                "Content-Type": "application/json"
            }
        )
        assert response.status_code == 200

    def test_slack_events_invalid_signature(self):
        """잘못된 서명 → 401 Unauthorized"""
        payload = {"type": "event_callback", "event": {"type": "app_mention"}}
        body = json.dumps(payload).encode()
        timestamp = str(int(time.time()))

        response = client.post(
            "/slack/events",
            content=body,
            headers={
                "X-Slack-Request-Timestamp": timestamp,
                "X-Slack-Signature": "v0=wrongsignature",
                "Content-Type": "application/json"
            }
        )
        assert response.status_code == 401

    def test_slack_events_old_timestamp(self):
        """5분 이상 된 timestamp → 401 (replay attack 방어)"""
        payload = {"type": "event_callback", "event": {"type": "app_mention"}}
        body = json.dumps(payload).encode()
        old_timestamp = str(int(time.time()) - 400)  # 6분 40초 전
        signature = generate_slack_signature(body, old_timestamp)

        response = client.post(
            "/slack/events",
            content=body,
            headers={
                "X-Slack-Request-Timestamp": old_timestamp,
                "X-Slack-Signature": signature,
                "Content-Type": "application/json"
            }
        )
        assert response.status_code == 401

    def test_slack_events_missing_headers(self):
        """헤더 누락 → 401"""
        payload = {"type": "event_callback"}
        body = json.dumps(payload).encode()

        response = client.post(
            "/slack/events",
            content=body,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 401

    def test_slack_events_challenge_verification(self):
        """Challenge 응답 테스트"""
        payload = {
            "type": "url_verification",
            "challenge": "test-challenge-12345"
        }
        body = json.dumps(payload).encode()
        timestamp = str(int(time.time()))
        signature = generate_slack_signature(body, timestamp)

        response = client.post(
            "/slack/events",
            content=body,
            headers={
                "X-Slack-Request-Timestamp": timestamp,
                "X-Slack-Signature": signature,
                "Content-Type": "application/json"
            }
        )
        assert response.status_code == 200
        assert response.json()["challenge"] == "test-challenge-12345"


class TestAPIKeyAuthentication:
    """API Key 인증 테스트"""

    def test_get_request_with_valid_api_key(self):
        """유효한 API Key → 인증 통과"""
        test_id = str(uuid.uuid4())
        response = client.get(
            f"/requests/{test_id}",
            headers={"Authorization": f"Bearer {settings.api_key}"}
        )
        # 실제 요청이 없으면 404지만, 인증은 통과
        assert response.status_code in [200, 404]

    def test_get_request_no_api_key(self):
        """API Key 없음 → 401"""
        test_id = str(uuid.uuid4())
        response = client.get(f"/requests/{test_id}")
        assert response.status_code == 401

    def test_get_request_invalid_api_key(self):
        """잘못된 API Key → 401"""
        test_id = str(uuid.uuid4())
        response = client.get(
            f"/requests/{test_id}",
            headers={"Authorization": "Bearer wrong-key"}
        )
        assert response.status_code == 401

    def test_get_request_invalid_bearer_format(self):
        """Bearer 형식 오류 → 401"""
        test_id = str(uuid.uuid4())
        response = client.get(
            f"/requests/{test_id}",
            headers={"Authorization": f"Basic {settings.api_key}"}
        )
        assert response.status_code == 401
