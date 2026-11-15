"""How the banner sync reads paimon.moe's banner list."""

import pytest

from scripts.sync_banners import _key, character_banners

NAMES = {"venti": "Venti", "klee": "Klee", "hu_tao": "Hu Tao", "raiden_shogun": "Raiden Shogun"}

LIST = """export const banners = {
  standard: [
    { name: 'Wanderlust Invocation', start: '2000-01-01 00:00:00', end: '2200-01-01 00:00:00' },
  ],
  characters: [
    {
      name: 'Ballad in Goblets',
      start: '2020-09-28 00:00:00',
      end: '2020-10-18 18:00:00',
      timezoneDependent: true,
      featured: ['venti'],
      featuredRare: ['barbara', 'fischl', 'xiangling'],
    },
    // {
    //   name: 'Not yet',
    //   start: '2030-01-01 00:00:00',
    //   end: '2030-01-21 17:59:59',
    //   featured: ['klee'],
    // },
    {
      name: 'Moment of Bloom',
      start: '2021-03-02 18:00:00',
      end: '2021-03-16 15:00:00',
      timezoneDependentEnd: true,
      featured: ['hu_tao', 'raiden_shogun'],
    },
  ],
  weapons: [
    { name: 'Epitome Invocation', start: '2020-09-28 00:00:00', end: '2020-10-18 18:00:00',
      featured: ['amos_bow'] },
  ],
};
"""


def test_reads_each_character_banner_with_its_featured_names() -> None:
    assert character_banners(LIST, NAMES) == [
        {
            "start": "2020-09-28 00:00:00",
            "end": "2020-10-18 18:00:00",
            "startAsia": True,
            "endAsia": False,
            "featured": ["Venti"],
        },
        {
            "start": "2021-03-02 18:00:00",
            "end": "2021-03-16 15:00:00",
            "startAsia": False,
            "endAsia": True,
            "featured": ["Hu Tao", "Raiden Shogun"],
        },
    ]


def test_a_featured_key_with_no_known_character_stops_the_sync() -> None:
    with pytest.raises(ValueError, match="nahida"):
        character_banners(LIST.replace("'venti'", "'nahida'"), NAMES)


@pytest.mark.parametrize(
    ("name", "key"),
    [
        ("Hu Tao", "hu_tao"),
        ("Kamisato Ayaka", "kamisato_ayaka"),
        ("Raiden Shogun", "raiden_shogun"),
    ],
)
def test_names_become_the_keys_the_list_uses(name: str, key: str) -> None:
    assert _key(name) == key


def test_a_date_that_cannot_be_stops_the_sync() -> None:
    with pytest.raises(ValueError, match="2020-02-30"):
        character_banners(LIST.replace("2020-09-28 00:00:00", "2020-02-30 25:00:00", 1), NAMES)


def test_a_banner_without_dates_stops_the_sync() -> None:
    with pytest.raises(ValueError, match="Ballad"):
        character_banners(LIST.replace("start: '2020-09-28 00:00:00',\n      end", "end"), NAMES)
