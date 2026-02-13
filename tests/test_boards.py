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


@pytest.mark.asyncio
async def test_update_board_settings(authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Update Me"})
    board_id = create_resp.json()["id"]
    response = await authenticated_client.post(
        f"/dashboard/boards/{board_id}/settings",
        data={"name": "Updated Name", "description": "New desc", "accent_color": "#FF0000", "slug": "updated-slug"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "saved=true" in response.headers["location"]

    # Verify changes persisted
    settings_resp = await authenticated_client.get(f"/dashboard/boards/{board_id}/settings")
    assert "Updated Name" in settings_resp.text
    assert "New desc" in settings_resp.text


@pytest.mark.asyncio
async def test_update_board_settings_empty_name(authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Validate Me"})
    board_id = create_resp.json()["id"]
    response = await authenticated_client.post(
        f"/dashboard/boards/{board_id}/settings",
        data={"name": "", "description": "test", "accent_color": "#4F46E5", "slug": "test"},
    )
    assert response.status_code == 422
    assert "Board name is required" in response.text


@pytest.mark.asyncio
async def test_create_board_form_empty_name(authenticated_client: AsyncClient):
    response = await authenticated_client.post(
        "/dashboard/boards",
        data={"name": "", "description": "test"},
    )
    assert response.status_code == 422
    assert "Board name is required" in response.text


@pytest.mark.asyncio
async def test_board_detail_filters(authenticated_client: AsyncClient, client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Filter Test"})
    board_id = create_resp.json()["id"]
    slug = create_resp.json()["slug"]

    # Submit some feedback
    await client.post(
        f"/b/{slug}/submit",
        data={"title": "Feature one", "category": "feature"},
        follow_redirects=False,
    )
    await client.post(
        f"/b/{slug}/submit",
        data={"title": "Bug report", "category": "bug"},
        follow_redirects=False,
    )

    # Filter by category
    response = await authenticated_client.get(f"/dashboard/boards/{board_id}?category_filter=bug")
    assert response.status_code == 200
    assert "Bug report" in response.text

    # Sort by newest
    response = await authenticated_client.get(f"/dashboard/boards/{board_id}?sort=newest")
    assert response.status_code == 200
    assert "Feature one" in response.text


@pytest.mark.asyncio
async def test_update_feedback_status(authenticated_client: AsyncClient, client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Status Test"})
    board_id = create_resp.json()["id"]
    slug = create_resp.json()["slug"]

    # Submit feedback
    await client.post(
        f"/b/{slug}/submit",
        data={"title": "Test status change", "category": "feature"},
        follow_redirects=False,
    )

    # Get the board to find feedback item
    detail_resp = await authenticated_client.get(f"/dashboard/boards/{board_id}")
    assert "Test status change" in detail_resp.text

    # Extract item_id from the form action in HTML
    import re
    match = re.search(r'/feedback/([^/]+)/status', detail_resp.text)
    assert match, "Could not find feedback item ID in page"
    item_id = match.group(1)

    # Update status
    response = await authenticated_client.post(
        f"/dashboard/boards/{board_id}/feedback/{item_id}/status",
        data={"status": "planned"},
        follow_redirects=False,
    )
    assert response.status_code == 302


@pytest.mark.asyncio
async def test_board_detail_not_found(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/dashboard/boards/nonexistent-id")
    # The exception handler returns JSON for non-HTML requests
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_dashboard_shows_board_stats(authenticated_client: AsyncClient, client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Stats Board"})
    slug = create_resp.json()["slug"]

    # Submit feedback
    await client.post(
        f"/b/{slug}/submit",
        data={"title": "Idea 1", "category": "feature"},
        follow_redirects=False,
    )

    # Check dashboard shows item count
    response = await authenticated_client.get("/dashboard")
    assert response.status_code == 200
    assert "1 items" in response.text or "1 item" in response.text


@pytest.mark.asyncio
async def test_create_board_form_success(authenticated_client: AsyncClient):
    response = await authenticated_client.post(
        "/dashboard/boards",
        data={"name": "Form Created Board", "description": "via form", "accent_color": "#FF5733"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/dashboard/boards/" in response.headers["location"]

    # Verify the board appears in the listing
    boards_resp = await authenticated_client.get("/api/boards")
    board_names = [b["name"] for b in boards_resp.json()]
    assert "Form Created Board" in board_names


@pytest.mark.asyncio
async def test_board_slug_update_persists(authenticated_client: AsyncClient, client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Slug Change"})
    board_id = create_resp.json()["id"]
    original_slug = create_resp.json()["slug"]
    assert original_slug == "slug-change"

    # Update slug
    await authenticated_client.post(
        f"/dashboard/boards/{board_id}/settings",
        data={"name": "Slug Change", "description": "", "accent_color": "#4F46E5", "slug": "new-custom-slug"},
        follow_redirects=False,
    )

    # Verify old slug no longer works
    old_resp = await client.get(f"/b/{original_slug}")
    assert old_resp.status_code == 404

    # Verify new slug works
    new_resp = await client.get("/b/new-custom-slug")
    assert new_resp.status_code == 200
    assert "Slug Change" in new_resp.text


@pytest.mark.asyncio
async def test_dashboard_shows_username(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/dashboard")
    assert response.status_code == 200
    assert "testuser" in response.text


@pytest.mark.asyncio
async def test_board_detail_empty_state(authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Empty Board"})
    board_id = create_resp.json()["id"]
    slug = create_resp.json()["slug"]

    response = await authenticated_client.get(f"/dashboard/boards/{board_id}")
    assert response.status_code == 200
    assert "No feedback yet" in response.text
    assert slug in response.text  # Slug should be visible in empty state


@pytest.mark.asyncio
async def test_delete_nonexistent_board(authenticated_client: AsyncClient):
    response = await authenticated_client.post(
        "/dashboard/boards/nonexistent-id/delete",
        follow_redirects=False,
    )
    assert response.status_code == 404
