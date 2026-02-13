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
async def test_api_register_duplicate_username(client: AsyncClient):
    await client.post(
        "/api/auth/register",
        json={"email": "user1@test.com", "username": "sameuser", "password": "password123"},
    )
    response = await client.post(
        "/api/auth/register",
        json={"email": "user2@test.com", "username": "sameuser", "password": "password123"},
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
async def test_api_login_nonexistent_user(client: AsyncClient):
    response = await client.post(
        "/api/auth/login",
        json={"email": "nobody@test.com", "password": "password123"},
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
async def test_form_register_validation(client: AsyncClient):
    # Missing email
    response = await client.post(
        "/register",
        data={"email": "", "username": "nomail", "password": "password123"},
    )
    assert response.status_code == 422
    assert "Email is required" in response.text


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
async def test_form_login_wrong_password(client: AsyncClient):
    await client.post(
        "/register",
        data={"email": "wrongform@test.com", "username": "wrongformuser", "password": "password123"},
        follow_redirects=False,
    )
    client.cookies.clear()
    response = await client.post(
        "/login",
        data={"email": "wrongform@test.com", "password": "badpassword"},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.text


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    response = await client.get("/logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/"


@pytest.mark.asyncio
async def test_register_redirects_when_logged_in(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/register", follow_redirects=False)
    assert response.status_code == 302
    assert "/dashboard" in response.headers["location"]


@pytest.mark.asyncio
async def test_login_redirects_when_logged_in(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/login", follow_redirects=False)
    assert response.status_code == 302
    assert "/dashboard" in response.headers["location"]


@pytest.mark.asyncio
async def test_404_returns_json_for_api(client: AsyncClient):
    response = await client.get("/nonexistent-page")
    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"


@pytest.mark.asyncio
async def test_404_returns_html_for_browser(client: AsyncClient):
    response = await client.get(
        "/nonexistent-page",
        headers={"accept": "text/html"},
    )
    assert response.status_code == 404
    assert "404" in response.text
    assert "doesn&#x27;t exist" in response.text or "doesn't exist" in response.text or "Page Not Found" in response.text


@pytest.mark.asyncio
async def test_401_redirects_to_login_for_browser(client: AsyncClient):
    response = await client.get(
        "/dashboard",
        headers={"accept": "text/html"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/login" in response.headers["location"]


@pytest.mark.asyncio
async def test_form_register_short_password(client: AsyncClient):
    response = await client.post(
        "/register",
        data={"email": "test@test.com", "username": "testshort", "password": "short"},
    )
    assert response.status_code == 422
    assert "Password must be at least 8 characters" in response.text


@pytest.mark.asyncio
async def test_form_register_duplicate_email(client: AsyncClient):
    await client.post(
        "/register",
        data={"email": "dup2@test.com", "username": "dupuser1", "password": "password123"},
        follow_redirects=False,
    )
    client.cookies.clear()
    response = await client.post(
        "/register",
        data={"email": "dup2@test.com", "username": "dupuser2", "password": "password123"},
    )
    assert response.status_code == 422
    assert "Email already registered" in response.text


@pytest.mark.asyncio
async def test_landing_page_shows_login_for_anonymous(client: AsyncClient):
    client.cookies.clear()
    response = await client.get("/")
    assert response.status_code == 200
    assert "Get Started" in response.text
    assert "Log in" in response.text


@pytest.mark.asyncio
async def test_landing_page_shows_dashboard_for_logged_in(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/")
    assert response.status_code == 200
    assert "Go to Dashboard" in response.text
