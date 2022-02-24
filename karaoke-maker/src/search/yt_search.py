from typing import Optional
from unidecode import unidecode
from pytube import Search
from rapidfuzz import fuzz


def search_song(
    song_name: str, song_artists: list[str], song_duration: int, isrc: str
) -> Optional[str]:

    # if isrc is not None then we try to find song with it
    if isrc is not None:
        isrc_results = Search(isrc).results

        if isrc_results and len(isrc_results) == 1:
            isrc_result = isrc_results[0]

            if isrc_result is not None and isrc_result.watch_url is not None:
                return isrc_result.watch_url

    joined_artists = ", ".join(song_artists)
    song_title = f"{joined_artists} - {song_name}"

    results = Search(song_title).results

    if results is None:
        return None

    result = best_result(results, song_name, song_artists, song_duration)
    return result


def create_title(song_name: str, song_artists: list[str]) -> str:
    joined_artists = ", ".join(song_artists)
    return f"{joined_artists} - {song_name}"


def best_result(
    results: list,
    song_name: str,
    song_artists: list[str],
    song_duration: int,
) -> str:

    links_with_match_value = {}

    for result in results:
        if result == {}:
            continue
        lower_song_name = song_name.lower()
        lower_result_name = result.title.lower()
        sentence_words = lower_song_name.replace("-", " ").split(" ")
        common_word = [word for word in sentence_words if word in lower_result_name]
        if not common_word:  # skip song if no common word is in its title
            continue
        if len(common_word) == len(lower_result_name):  # return perfekt result
            return result.watch_url

        artist_matches = 0
        # find matching artists
        for artist in song_artists:
            if get_score_above(
                85, unidecode(artist.lower()), unidecode(result.title).lower()
            ):
                artist_matches += 1

        # if artist_matches == 0:
        #     continue
        # compute similarity between all artists
        artist_score = (artist_matches / len(song_artists)) * 100
        joined_artists = ", ".join(song_artists)
        song_title = f"{joined_artists} - {song_name}".lower()
        # find similarity between names
        name_score = round(
            get_score_above(
                60, unidecode(result.title.lower()), unidecode(song_title)
            ),  # type:ignore
            ndigits=3,
        )

        album_score = 0.0
        # Find duration difference
        delta = result.length - song_duration
        non_match_value = (delta**2) / song_duration * 100
        time_score = 100 - non_match_value
        # compute average score
        average_score = (artist_score + album_score + name_score + time_score) / 4
        links_with_match_value[result.watch_url] = average_score
    result_items = list(links_with_match_value.items())
    sorted_results = sorted(result_items, key=lambda x: x[1], reverse=True)
    return sorted_results[0][0]


def get_score_above(cutoff: int, string1: str, string2: str):
    try:
        return fuzz.partial_ratio(string1, string2, score_cutoff=cutoff)
    except Exception as e:
        print("could not get score for song, beacause of: ", e)


if __name__ == "__main__":
    ans = search_song(
        "The Ballad of Hollywood Jack and the Rage Cage - Tenacious D",
        ["jack black"],
        240,
        None,
    )
    print(ans)
