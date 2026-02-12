import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "FeedbackCue"


@pytest.mark.asyncio
async def test_landing_page(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert "FeedbackCue" in response.text


@pytest.mark.asyncio
async def test_register_page(client: AsyncClient):
    response = await client.get("/register")
    assert response.status_code == 200
    assert "Create your account" in response.text


@pytest.mark.asyncio
async def test_login_page(client: AsyncClient):
    response = await client.get("/login")
    assert response.status_code == 200
    assert "Welcome back" in response.text


@pytest.mark.asyncio
async def test_api_register(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={"email": "new@test.com", "username": "newuser", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "new@test.com"
    assert "token" in data


@pytest.mark.asyncio
async def test_api_register_duplicate_email(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={"email": "dup@test.com", "username": "user1", "password": "password123"},
    )
    response = await client.post(
        "/api/auth/register",
        json={"email": "dup@test.com", "username": "user2", "password": "password123"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_api_register_short_password(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={"email": "short@test.com", "username": "shortpw", "password": "short"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_api_login(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={"email": "login@test.com", "username": "loginuser", "password": "password123"},
    )
    response = await client.post(
        "/api/auth/login",
        json={"email": "login@test.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert "token" in response.json()


@pytest.mark.asyncio
async def test_api_login_wrong_password(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={"email": "wrong@test.com", "username": "wrongpw", "password": "password123"},
    )
    response = await client.post(
        "/api/auth/login",
        json={"email": "wrong@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_form_register(client: AsyncClient):
    response = await client.post(
        "/register",
        data={"email": "form@test.com", "username": "formuser", "password": "password123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/dashboard" in response.headers["location"]


@pytest.mark.asyncio
async def test_form_login(client: AsyncClient):
    await client.post(
        "/register",
        data={"email": "formlogin@test.com", "username": "formloginuser", "password": "password123"},
        follow_redirects=False,
    )
    # Clear cookies to simulate a new session
    client.cookies.clear()
    response = await client.post(
        "/login",
        data={"email": "formlogin@test.com", "password": "password123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/dashboard" in response.headers["location"]


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    response = await client.get("/logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/"
