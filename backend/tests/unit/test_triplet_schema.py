from backend.app.services.extraction.triplet_schema import (
    Triplet,
    validate_triplet,
    EXAMPLES,
)


def test_triplet_examples_validate():
    for name, triplet in EXAMPLES.items():
        errors = validate_triplet(triplet)
        assert not errors, f"Triplet failed validation [{name}]: {errors}"


def test_triplet_field_types():
    triplet = EXAMPLES["donor"]
    assert triplet.subject.label == "Donor"
    assert isinstance(triplet.subject.properties["name"], str)
    assert triplet.metadata.extraction_confidence > 0
