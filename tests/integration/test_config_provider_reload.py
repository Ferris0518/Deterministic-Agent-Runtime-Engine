from dare_framework.components.config_provider import StaticConfigProvider


def test_static_config_provider_reload_returns_new_config():
    provider = StaticConfigProvider({"llm": {"model": "m1"}})

    current = provider.current()
    reloaded = provider.reload()

    assert current is not reloaded
    assert reloaded.llm.model == "m1"
    assert provider.current() is reloaded
