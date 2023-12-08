import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status


@pytest.mark.anyio
async def test_health(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Checks the health endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    url = fastapi_app.url_path_for("health_check")
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.text == '{"message":"OK"}'


@pytest.mark.anyio
async def test_encode_fail(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Check that only http urls are allowed to be encode
    """
    url = fastapi_app.url_path_for("encode_url")
    response = await client.post(
        url,
        json={"url": "ftp://example.com/"},
        headers={"Content-Type": "application/json", "accept": "application/json"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_encode(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Check if encoding works
    """
    original_url = "https://example.com/"
    url = fastapi_app.url_path_for("encode_url")
    response = await client.post(
        url,
        json={"url": original_url},
        headers={"Content-Type": "application/json", "accept": "application/json"},
    )
    assert response.status_code == status.HTTP_200_OK
    res_obj = response.json()
    assert res_obj.get("url") == original_url
    assert res_obj.get("short")


@pytest.mark.anyio
async def test_forward_nonexistent(client: AsyncClient, fastapi_app: FastAPI) -> None:
    url = fastapi_app.url_path_for("forward", shorturl_id="DOESNOTEXIST")
    response = await client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_forward_match(client: AsyncClient, fastapi_app: FastAPI) -> None:
    # create a shorturl first
    original_url = "https://example.com/foobar123"
    encode_url = fastapi_app.url_path_for("encode_url")
    encode_resp = await client.post(encode_url, json={"url": original_url})
    assert encode_resp.status_code == status.HTTP_200_OK
    existing_shorturl = encode_resp.json().get("short")
    existing_shorturl_id = existing_shorturl[-8:]

    # test
    url = fastapi_app.url_path_for("forward", shorturl_id=existing_shorturl_id)
    response = await client.get(url)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT


@pytest.mark.anyio
async def test_decode(client: AsyncClient, fastapi_app: FastAPI) -> None:
    # create a shorturl first
    original_url = "https://example.com/foobar123/"
    encode_url = fastapi_app.url_path_for("encode_url")
    encode_resp = await client.post(encode_url, json={"url": original_url})
    assert encode_resp.status_code == status.HTTP_200_OK
    existing_shorturl = encode_resp.json().get("short")
    existing_shorturl_id = existing_shorturl[-8:]

    # test
    url = fastapi_app.url_path_for("decode_url", shorturl_id=existing_shorturl_id)
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_message = response.json()
    assert response_message.get("short") == existing_shorturl
    assert response_message.get("url") == original_url


@pytest.mark.anyio
async def test_decode_fail(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """Failing test for decode. A shorturl that doesn't exist should return 404"""
    url = fastapi_app.url_path_for("decode_url", shorturl_id="DOESNOTEXIST")
    response = await client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
