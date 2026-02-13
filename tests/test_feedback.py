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


@pytest.mark.asyncio
async def test_submit_feedback_empty_title(client: AsyncClient, authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Empty Title Board"})
    slug = create_resp.json()["slug"]

    response = await client.post(
        f"/b/{slug}/submit",
        data={"title": "", "category": "feature"},
        follow_redirects=False,
    )
    # Empty title redirects back without creating
    assert response.status_code == 302

    # Verify no items were created
    board_resp = await client.get(f"/b/{slug}")
    assert "No feedback yet" in board_resp.text


@pytest.mark.asyncio
async def test_submit_feedback_to_nonexistent_board(client: AsyncClient):
    response = await client.post(
        "/b/nonexistent/submit",
        data={"title": "Orphan idea", "category": "feature"},
        follow_redirects=False,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_public_board_filters(client: AsyncClient, authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Filter Public"})
    slug = create_resp.json()["slug"]

    # Submit bug and feature
    await client.post(
        f"/b/{slug}/submit",
        data={"title": "Bug item", "category": "bug"},
        follow_redirects=False,
    )
    await client.post(
        f"/b/{slug}/submit",
        data={"title": "Feature item", "category": "feature"},
        follow_redirects=False,
    )

    # Filter by category
    response = await client.get(f"/b/{slug}?category_filter=bug")
    assert response.status_code == 200
    assert "Bug item" in response.text

    # Sort by newest
    response = await client.get(f"/b/{slug}?sort=newest")
    assert response.status_code == 200
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_public_board_shows_item_count(client: AsyncClient, authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Count Board"})
    slug = create_resp.json()["slug"]

    await client.post(
        f"/b/{slug}/submit",
        data={"title": "First idea", "category": "feature"},
        follow_redirects=False,
    )
    await client.post(
        f"/b/{slug}/submit",
        data={"title": "Second idea", "category": "feature"},
        follow_redirects=False,
    )

    response = await client.get(f"/b/{slug}")
    assert "2 items" in response.text


@pytest.mark.asyncio
async def test_submit_feedback_shows_success_banner(client: AsyncClient, authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Success Banner Board"})
    slug = create_resp.json()["slug"]

    # Submit feedback and follow redirect
    response = await client.post(
        f"/b/{slug}/submit",
        data={"title": "My great idea", "category": "feature"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "submitted=true" in response.headers["location"]

    # Verify success banner appears
    board_resp = await client.get(f"/b/{slug}?submitted=true")
    assert "Thanks for your feedback" in board_resp.text


@pytest.mark.asyncio
async def test_public_board_sets_voter_cookie(client: AsyncClient, authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Cookie Board"})
    slug = create_resp.json()["slug"]

    # Clear cookies and visit board
    client.cookies.clear()
    response = await client.get(f"/b/{slug}")
    assert response.status_code == 200
    # Check voter_id cookie was set
    assert "voter_id" in response.cookies


@pytest.mark.asyncio
async def test_public_board_form_collapsed_with_items(client: AsyncClient, authenticated_client: AsyncClient):
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Collapsed Form"})
    slug = create_resp.json()["slug"]

    # Submit an item first
    await client.post(
        f"/b/{slug}/submit",
        data={"title": "Existing item", "category": "feature"},
        follow_redirects=False,
    )

    # Visit board - form should be hidden
    response = await client.get(f"/b/{slug}")
    assert response.status_code == 200
    # Form should have "hidden" class when items exist
    assert 'id="feedback-form"' in response.text
    assert 'class="space-y-4 mt-4 hidden"' in response.text
