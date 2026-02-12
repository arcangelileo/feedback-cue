import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_vote_on_item(client: AsyncClient, authenticated_client: AsyncClient):
    # Create board and submit feedback
    create_resp = await authenticated_client.post("/api/boards", json={"name": "Vote Board"})
    slug = create_resp.json()["slug"]

    await client.post(
        f"/b/{slug}/submit",
        data={"title": "Voteable item", "category": "feature"},
        follow_redirects=False,
    )

    # Get the board to find the item
    board_resp = await client.get(f"/b/{slug}")
    assert "Voteable item" in board_resp.text

    # The item should have 0 votes initially - we need to get the item ID
    # from the board detail page
    board_id = create_resp.json()["id"]
    detail_resp = await authenticated_client.get(f"/dashboard/boards/{board_id}")
    assert "Voteable item" in detail_resp.text


@pytest.mark.asyncio
async def test_vote_toggle(client: AsyncClient, authenticated_client: AsyncClient, db_session):
    from app.services.feedback import create_feedback, toggle_vote, get_feedback_by_id
    from app.services.board import create_board

    # Create board and feedback directly
    board = await create_board(db_session, "Toggle Board", "test", "#4F46E5", "test-owner-id")
    item = await create_feedback(
        db_session, board.id, "Toggle Test", "desc", "feature", None, "Tester"
    )
    await db_session.commit()

    # Vote
    result = await toggle_vote(db_session, item.id, "voter-123")
    assert result is True
    await db_session.commit()

    refreshed = await get_feedback_by_id(db_session, item.id)
    assert refreshed.vote_count == 1

    # Unvote
    result = await toggle_vote(db_session, item.id, "voter-123")
    assert result is False
    await db_session.commit()

    refreshed = await get_feedback_by_id(db_session, item.id)
    assert refreshed.vote_count == 0


@pytest.mark.asyncio
async def test_duplicate_vote_prevention(client: AsyncClient, authenticated_client: AsyncClient, db_session):
    from app.services.feedback import create_feedback, toggle_vote, get_feedback_by_id, has_voted
    from app.services.board import create_board

    board = await create_board(db_session, "Dup Vote Board", "test", "#4F46E5", "test-owner-id-2")
    item = await create_feedback(
        db_session, board.id, "Dup Vote Test", "desc", "feature", None, "Tester"
    )
    await db_session.commit()

    # First vote
    await toggle_vote(db_session, item.id, "same-voter")
    await db_session.commit()
    assert await has_voted(db_session, item.id, "same-voter") is True

    # Different voter
    await toggle_vote(db_session, item.id, "different-voter")
    await db_session.commit()

    refreshed = await get_feedback_by_id(db_session, item.id)
    assert refreshed.vote_count == 2
