"""API tests for the read-only endpoints, against a seeded throwaway database."""

import pytest

ENDPOINT_COUNTS = [
    ("/api/repair-orders", 40),
    ("/api/technicians", 12),
    ("/api/bays", 7),
    ("/api/inventory", 72),
    ("/api/appointments", 28),
    ("/api/disruptions", 14),
]


@pytest.mark.parametrize("path,expected", ENDPOINT_COUNTS)
def test_list_endpoints_return_all_rows(client, path, expected) -> None:
    response = client.get(path)
    assert response.status_code == 200
    assert len(response.json()) == expected


def test_repair_order_shape_and_hero_values(client) -> None:
    body = client.get("/api/repair-orders/48240").json()
    assert body["ro_id"] == "48240"
    assert body["required_parts"] == [{"part_id": "P-001", "quantity": 1}]
    assert body["required_skills"] == ["cooling_system"]
    assert body["promised_at"] == "2026-03-11T12:00:00"
    assert body["assigned_technician_id"] == "T03"
    assert body["status"] == "waiting"
    assert body["is_synthetic"] is True


def test_repair_orders_filter_by_status_and_technician(client) -> None:
    waiting = client.get("/api/repair-orders", params={"status": "waiting"}).json()
    assert waiting and all(ro["status"] == "waiting" for ro in waiting)
    t03 = client.get("/api/repair-orders", params={"assigned_technician_id": "T03"}).json()
    assert sorted(ro["ro_id"] for ro in t03) == ["48213", "48220", "48231", "48240"]


def test_invalid_filter_value_is_rejected(client) -> None:
    assert client.get("/api/repair-orders", params={"status": "exploded"}).status_code == 422


@pytest.mark.parametrize("path", [
    "/api/repair-orders/99999", "/api/technicians/T99", "/api/bays/BAY-99",
    "/api/appointments/APT-999", "/api/disruptions/D-999",
])
def test_unknown_ids_return_404(client, path) -> None:
    response = client.get(path)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_technician_detail_lists_skills(client) -> None:
    body = client.get("/api/technicians/T03").json()
    assert body["skills"] == ["cooling_system", "diagnostics", "engine"]
    absent = client.get("/api/technicians", params={"availability": "absent"}).json()
    assert [t["technician_id"] for t in absent] == ["T11"]


def test_bays_filter_and_detail(client) -> None:
    assert client.get("/api/bays/BAY-02").json()["bay_id"] == "BAY-02"
    occupied = client.get("/api/bays", params={"status": "occupied"}).json()
    assert all(b["status"] == "occupied" for b in occupied)


def test_inventory_shows_the_three_pump_sources(client) -> None:
    rows = client.get("/api/inventory", params={"part_id": "P-001"}).json()
    by_location = {r["location_id"]: r for r in rows}
    assert set(by_location) == {"LOC-A", "LOC-B", "LOC-C"}
    assert by_location["LOC-A"]["quantity_on_hand"] == 0
    assert by_location["LOC-B"]["quantity_on_hand"] == 1
    assert by_location["LOC-B"]["stock_confidence"] == "unverified"
    assert by_location["LOC-C"]["available_quantity"] == 1
    assert by_location["LOC-C"]["part_name"] == "OEM Coolant Pump Assembly"
    assert "Store C" in by_location["LOC-C"]["location_name"]


def test_inventory_available_quantity_is_on_hand_minus_reserved(client) -> None:
    for row in client.get("/api/inventory").json():
        assert row["available_quantity"] == row["quantity_on_hand"] - row["reserved_quantity"]
        assert row["available_quantity"] >= 0


def test_inventory_filter_by_location(client) -> None:
    rows = client.get("/api/inventory", params={"location_id": "LOC-B"}).json()
    assert len(rows) == 24 and all(r["location_id"] == "LOC-B" for r in rows)


def test_hero_appointment_awaits_consent(client) -> None:
    rows = client.get("/api/appointments", params={"ro_id": "48240"}).json()
    assert len(rows) == 1
    assert rows[0]["consent_status"] == "pending"
    assert rows[0]["customer_preference"] == "OEM parts only"
    pending = client.get("/api/appointments", params={"consent_status": "pending"}).json()
    assert all(a["consent_status"] == "pending" for a in pending)


def test_hero_disruptions_are_visible_and_dormant(client) -> None:
    d1 = client.get("/api/disruptions/D-001").json()
    assert d1["disruption_type"] == "part_backorder" and d1["status"] == "scheduled"
    assert d1["start_time"] == "2026-03-10T09:40:00"
    assert d1["details"]["new_expected_arrival"] == "2026-03-11T10:00:00"
    d2 = client.get("/api/disruptions/D-002").json()
    assert d2["start_time"] == "2026-03-10T10:38:00"
    assert d2["details"]["actual_quantity"] == 0
    scheduled = client.get("/api/disruptions", params={"status": "scheduled"}).json()
    assert {"D-001", "D-002"} <= {d["disruption_id"] for d in scheduled}


def test_dashboard_counts_are_consistent(client) -> None:
    body = client.get("/api/dashboard").json()
    assert body["scenario_clock"] == "09:40" and body["is_synthetic"] is True
    assert body["repair_orders_total"] == 40
    assert sum(body["repair_orders_by_status"].values()) == 40
    assert body["technicians_total"] == 12
    assert body["technicians_by_availability"]["absent"] == 1
    assert body["bays_total"] == 7
    assert body["appointments_total"] == 28
    assert body["disruptions_total"] == 14
    assert body["parts_total"] == 24
    assert 0 < body["waiting_customers"] <= 40


def test_openapi_documents_every_endpoint(client) -> None:
    paths = client.get("/openapi.json").json()["paths"]
    for expected in ("/api/health", "/api/dashboard", "/api/repair-orders", "/api/technicians",
                     "/api/bays", "/api/inventory", "/api/appointments", "/api/disruptions"):
        assert expected in paths
