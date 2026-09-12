"""Regression checks for analytical false positives that change the narrative."""
from scripts.build_landscape_review import TOPICS, matched
from scripts.review_stats import NEURO_RULES


def test_artificial_intelligence_does_not_imply_neuroscience():
    text = "Artificial intelligence for pediatric abdominal MRI reconstruction"
    assert "Brain development / cognition" not in matched(text, TOPICS)
    assert not NEURO_RULES["diagnosis_or_neuroscience"][0].search(text)


def test_cognitive_intelligence_is_still_captured():
    text = "Prediction of intelligence quotient from pediatric brain MRI"
    assert "Brain development / cognition" in matched(text, TOPICS)
    assert NEURO_RULES["diagnosis_or_neuroscience"][0].search(text)


def test_disease_map_retains_overlapping_fetal_and_cardiac_topics():
    text = "Prenatal ultrasound detection of congenital heart disease"
    topics = matched(text, TOPICS)
    assert "Fetal assessment / prenatal" in topics
    assert "Cardiac / congenital heart" in topics
