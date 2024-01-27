import typing

import pytest

from .banner_engine import (
    BannerStat, Banner, BannerStorage, EmptyBannerStorageError, EpsilonGreedyBannerEngine
)

TEST_DEFAULT_CTR = 0.1


@pytest.fixture(scope="function")
def test_banners() -> list[Banner]:
    return [
        Banner("b1", cost=1, stat=BannerStat(10, 20)),
        Banner("b2", cost=250, stat=BannerStat(20, 20)),
        Banner("b3", cost=100, stat=BannerStat(0, 20)),
        Banner("b4", cost=100, stat=BannerStat(1, 20)),
    ]


@pytest.mark.parametrize("clicks, shows, expected_ctr", [(1, 1, 1.0), (20, 100, 0.2), (5, 100, 0.05)])
def test_banner_stat_ctr_value(clicks: int, shows: int, expected_ctr: float) -> None:
    bs: BannerStat = BannerStat(clicks, shows)
    res = bs.compute_ctr(0)
    assert res == expected_ctr


def test_empty_stat_compute_ctr_returns_default_ctr() -> None:
    for args in ((1, 0, 5), (1, 0, 10), (0, 0, 20.0)):
        clicks: int = args[0]
        shows: int = args[1]
        default_ctr: float = args[2]
        bs: BannerStat = BannerStat(clicks, shows)
        res = bs.compute_ctr(default_ctr)
        assert res == default_ctr


def test_banner_stat_add_show_lowers_ctr() -> None:
    for args in ((1, 0), (10, 0), (120, 10)):
        clicks: int = args[0]
        shows: int = args[1]
        bs: BannerStat = BannerStat(clicks, shows)
        bs.add_show()

        assert bs.__getattribute__("clicks") == clicks
        assert bs.clicks == clicks
        assert bs.__getattribute__("shows") == shows + 1
        assert bs.shows == shows + 1


def test_banner_stat_add_click_increases_ctr() -> None:
    for args in ((1, 0), (10, 0), (120, 10)):
        clicks: int = args[0]
        shows: int = args[1]
        bs: BannerStat = BannerStat(clicks, shows)
        bs.add_click()
        assert bs.__getattribute__("clicks") == clicks + 1
        assert bs.clicks == clicks + 1
        assert bs.__getattribute__("shows") == shows
        assert bs.shows == shows


def test_get_banner_with_highest_cpc_returns_banner_with_highest_cpc(test_banners: list[Banner]) -> None:
    if len(test_banners) != 0:
        storage: BannerStorage = BannerStorage(test_banners)
        sorted_banners = sorted(test_banners, key=lambda x: x.cost * x.stat.compute_ctr(0), reverse=True)
        assert storage.banner_with_highest_cpc() == sorted_banners[0]


def test_banner_engine_raise_empty_storage_exception_if_constructed_with_empty_storage() -> None:
    with pytest.raises(EmptyBannerStorageError):
        BannerStorage([])


def test_engine_send_click_not_fails_on_unknown_banner(test_banners: list[Banner]) -> None:
    storage: BannerStorage = BannerStorage(test_banners)
    greedy_engine: EpsilonGreedyBannerEngine = EpsilonGreedyBannerEngine(storage, 0.5)
    try:
        greedy_engine.send_click("aboba")
    except BaseException:
        pytest.fail("Unexpected error in sending click on unknown banner")


def test_engine_with_zero_random_probability_shows_banner_with_highest_cpc(test_banners: list[Banner]) -> None:
    storage: BannerStorage = BannerStorage(test_banners)
    greedy_engine: EpsilonGreedyBannerEngine = EpsilonGreedyBannerEngine(storage, 0)
    res = greedy_engine.show_banner()
    assert res == storage.banner_with_highest_cpc().banner_id


@pytest.mark.parametrize("expected_random_banner", ["b1", "b2", "b3", "b4"])
def test_engine_with_1_random_banner_probability_gets_random_banner(
        expected_random_banner: str,
        test_banners: list[Banner],
        monkeypatch: typing.Any
) -> None:
    storage: BannerStorage = BannerStorage(test_banners)
    engine: EpsilonGreedyBannerEngine = EpsilonGreedyBannerEngine(storage, 1)
    monkeypatch.setattr("random.choice", lambda _: expected_random_banner)
    res = engine.show_banner()
    assert res == expected_random_banner


def test_total_cost_equals_to_cost_of_clicked_banners(test_banners: list[Banner]) -> None:
    storage: BannerStorage = BannerStorage(test_banners)
    engine: EpsilonGreedyBannerEngine = EpsilonGreedyBannerEngine(storage, 1)
    total_cost: float = 0
    for _ in range(5):
        banner_ind: str = engine.show_banner()
        engine.send_click(banner_ind)
        banner_showed: Banner = storage.get_banner(banner_ind)
        total_cost += banner_showed.cost
    assert engine.total_cost == total_cost


def test_engine_show_increases_banner_show_stat(test_banners: list[Banner]) -> None:
    storage: BannerStorage = BannerStorage(test_banners)
    engine: EpsilonGreedyBannerEngine = EpsilonGreedyBannerEngine(storage, 0)
    for _ in range(4):
        shows_before = storage.banner_with_highest_cpc().stat.shows
        banner_ind: str = engine.show_banner()
        assert storage.get_banner(banner_ind).stat.shows == shows_before + 1


def test_engine_click_increases_banner_click_stat(test_banners: list[Banner]) -> None:
    storage: BannerStorage = BannerStorage(test_banners)
    engine: EpsilonGreedyBannerEngine = EpsilonGreedyBannerEngine(storage, 0)
    for _ in range(4):
        clicks_before = storage.banner_with_highest_cpc().stat.clicks
        banner_ind: str = engine.show_banner()
        engine.send_click(banner_ind)
        assert storage.get_banner(banner_ind).stat.clicks == clicks_before + 1
