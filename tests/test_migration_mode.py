from genesis_framework.migration_mode import normalize_migration_mode, resolve_migration_mode


def test_migration_mode_normalizes_human_labels() -> None:
    assert normalize_migration_mode("Production E2E App") == "production_e2e_app"
    assert normalize_migration_mode("local demo") == "local_demo_app"
    assert normalize_migration_mode("Hybrid Pilot") == "hybrid_pilot_app"


def test_migration_mode_defaults_to_hybrid_when_unspecified() -> None:
    decision = resolve_migration_mode({}, {}, app_name="Demo", primary_source_type="document")
    assert decision["selected_mode"] == "hybrid_pilot_app"
    assert decision["requires_human_confirmation"] is True


def test_delivery_mode_maps_to_production_without_extra_confirmation() -> None:
    decision = resolve_migration_mode(
        {},
        {"selected_delivery_mode": "production_procode"},
        app_name="Demo",
        primary_source_type="document",
    )
    assert decision["selected_mode"] == "production_e2e_app"
    assert decision["requires_human_confirmation"] is False
