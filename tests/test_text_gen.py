"""Testes para modules/text_gen.py"""

import json
from modules.text_gen import _parse_json, _validate_post, _fallback_post, _REQUIRED_FIELDS


def test_parse_json_valid():
    raw = '{"titulo": "Teste", "legenda": "Legenda", "hashtags": ["#game"], "imagem_prompt": "img", "video_script": "script"}'
    result = _parse_json(raw)
    assert result is not None
    assert result["titulo"] == "Teste"


def test_parse_json_with_markdown():
    raw = '```json\n{"titulo": "Teste", "legenda": "Leg", "hashtags": ["#g"], "imagem_prompt": "i", "video_script": "s"}\n```'
    result = _parse_json(raw)
    assert result is not None
    assert result["titulo"] == "Teste"


def test_parse_json_invalid():
    assert _parse_json("not json at all") is None
    assert _parse_json("") is None


def test_validate_post_valid():
    post = {"titulo": "X", "legenda": "Y", "hashtags": ["#a"], "imagem_prompt": "Z", "video_script": "W"}
    assert _validate_post(post) is True


def test_validate_post_missing_field():
    post = {"titulo": "X", "legenda": "Y", "hashtags": ["#a"]}
    assert _validate_post(post) is False


def test_validate_post_empty_field():
    post = {"titulo": "", "legenda": "Y", "hashtags": ["#a"], "imagem_prompt": "Z", "video_script": "W"}
    assert _validate_post(post) is False


def test_validate_post_hashtags_not_list():
    post = {"titulo": "X", "legenda": "Y", "hashtags": "#a", "imagem_prompt": "Z", "video_script": "W"}
    assert _validate_post(post) is False


def test_fallback_post_returns_required_fields():
    post = _fallback_post("lançamento de jogo")
    for field in _REQUIRED_FIELDS:
        assert field in post, f"Campo {field} ausente no fallback"
        assert post[field], f"Campo {field} vazio no fallback"
    assert isinstance(post["hashtags"], list)
    assert len(post["hashtags"]) > 0


def test_fallback_post_contains_category():
    post = _fallback_post("história dos games")
    assert "história" in post["titulo"].lower() or "história" in post["legenda"].lower()
