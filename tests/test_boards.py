import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_requires_auth(client: AsyncClient):
    response = await client.get("/dashboard")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_api_create_board(authenticated_client: AsyncClient):
    response = await authenticated_client.post(
        "/api/boards",
        json={"name": "My Product", "description": "Collect feedback"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Product"
    assert data["slug"] == "my-product"
    assert data["accent_color"] == "#4F46E5"


@pytest.mark.asyncio
async def test_api_list_boards(authenticated_client: AsyncClient):
    await authenticated_client.post("/api/boards", json={"name": "Board 1"})
    await authenticated_client.post("/api/boards", json={"name": "Board 2"})
    response = await authenticated_client.get("/api/boards")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_create_board_duplicate_slug(authenticated_client: AsyncClient):
    await authenticated_client.post("/api/boards", json={"name": "Same Name"})
    response = await authenticated_client.post("/api/boards", json={"name": "Same Name"})
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "same-name-1"


@pytest.mark.asyncio
async def test_dashboard_page(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/dashboard")
    assert response.status_code == 200
    assert "Your Boards" in response.text


@pytest.mark.asyncio
async def test_board_detail_page(authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Detail Test"})
    board_id = create_resp.json()["id"]
    response = await authenticated_client.get(f"/dashboard/boards/{board_id}")
    assert response.status_code == 200
    assert "Detail Test" in response.text


@pytest.mark.asyncio
async def test_board_settings_page(authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Settings Test"})
    board_id = create_resp.json()["id"]
    response = await authenticated_client.get(f"/dashboard/boards/{board_id}/settings")
    assert response.status_code == 200
    assert "Board Settings" in response.text


@pytest.mark.asyncio
async def test_delete_board(authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "To Delete"})
    board_id = create_resp.json()["id"]
    response = await authenticated_client.post(
        f"/dashboard/boards/{board_id}/delete", follow_redirects=False
    )
    assert response.status_code == 302
    # Verify board is gone
    boards = await authenticated_client.get("/api/boards")
    assert len(boards.json()) == 0
