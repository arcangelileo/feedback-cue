import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_public_board_page(client: AsyncClient, authenticated_client: AsyncClient):
    # Create a board first
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Public Board"})
    slug = create_resp.json()["slug"]

    # Access public page without auth
    new_client = client
    new_client.cookies.clear()
    response = await new_client.get(f"/b/{slug}")
    assert response.status_code == 200
    assert "Public Board" in response.text


@pytest.mark.asyncio
async def test_public_board_404(client: AsyncClient):
    response = await client.get("/b/nonexistent-slug")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_submit_feedback(client: AsyncClient, authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Feedback Test"})
    slug = create_resp.json()["slug"]

    response = await client.post(
        f"/b/{slug}/submit",
        data={
            "title": "Add dark mode",
            "description": "Would love a dark theme",
            "category": "feature",
            "author_name": "John",
            "author_email": "john@test.com",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302

    # Verify feedback appears on board
    board_resp = await client.get(f"/b/{slug}")
    assert "Add dark mode" in board_resp.text


@pytest.mark.asyncio
async def test_submit_feedback_anonymous(client: AsyncClient, authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Anon Board"})
    slug = create_resp.json()["slug"]

    response = await client.post(
        f"/b/{slug}/submit",
        data={"title": "Anonymous idea", "category": "improvement"},
        follow_redirects=False,
    )
    assert response.status_code == 302
