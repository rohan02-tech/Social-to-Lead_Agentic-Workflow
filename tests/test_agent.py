from src.intents import classify_intent, extract_lead_fields, missing_lead_fields


def test_intent_detection_for_pricing_question():
    intent, _ = classify_intent("Hi, can you explain your pricing plans?")
    assert intent == "product_pricing_inquiry"


def test_intent_detection_for_high_intent_message():
    intent, _ = classify_intent("I want to try the Pro plan for my YouTube channel.")
    assert intent == "high_intent_lead"


def test_intent_detection_for_followup_details_request():
    intent, _ = classify_intent("ok give me details")
    assert intent == "high_intent_lead"


def test_intent_detection_for_thanks_message():
    intent, _ = classify_intent("thanks")
    assert intent == "casual_greeting"


def test_lead_fields_are_not_complete_until_all_values_exist():
    lead_info = extract_lead_fields("My name is Rohan")
    lead_info = extract_lead_fields("rohan@example.com", lead_info)
    assert missing_lead_fields(lead_info) == ["platform"]


def test_all_lead_fields_can_be_collected_across_turns():
    lead_info = extract_lead_fields("My name is Rohan Rajak")
    lead_info = extract_lead_fields("My email is rohan@example.com", lead_info)
    lead_info = extract_lead_fields("I create on YouTube", lead_info)
    assert missing_lead_fields(lead_info) == []
