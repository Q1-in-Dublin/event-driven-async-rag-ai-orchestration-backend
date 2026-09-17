from app.graph.nodes import classify_intent


def test_classify_detects_korean_policy_keyword():
    state = {"request_id": "1", "user_text": "휴가 정책이 어떻게 되나요?"}
    result = classify_intent(state)
    assert result["needs_rag"] is True

def test_classify_detects_english_policy_keyword():
    state = {"request_id": "2", "user_text": "What is the vacation Policy?"}
    result = classify_intent(state)
    assert result["needs_rag"] is True

def test_classify_intent_no_keyword():
    state = {"request_id": "3", "user_text": "안녕하세요!"}
    result = classify_intent(state)
    assert result["needs_rag"] is False