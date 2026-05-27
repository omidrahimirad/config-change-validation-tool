from change_validator.diff_engine import diff_configs


def test_diff_engine_detects_changed_fields() -> None:
    current = {"device_id": "RTR-1", "interfaces": {"uplink": {"mtu": 1500}}}
    planned = {"device_id": "RTR-1", "interfaces": {"uplink": {"mtu": 1600}}}

    changes = diff_configs(current, planned)

    assert len(changes) == 1
    assert changes[0].field == "interfaces.uplink.mtu"
    assert changes[0].current_value == 1500
    assert changes[0].planned_value == 1600
