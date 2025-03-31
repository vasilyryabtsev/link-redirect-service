from src.links.schemas import Url


def test_url_serealize_link():
    url = Url(link="https://example.com/")
    serialized_link = url.serealize_link(url.link)
    assert serialized_link == "https://example.com/"
