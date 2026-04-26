def compare_document_and_selfie(document_image_path, selfie_image_path):
    """Mock face comparison. Replace with a real KYC provider in production."""
    return {
        "match_score": 0.87,
        "is_match": True,
        "provider": "mock",
        "message": "Mock verification result. Replace with a real provider in production.",
    }
