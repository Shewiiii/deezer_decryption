from app.api import Deezer
from app.chunked_input_stream import ChunkedInputStream
from app.constants import EXTENSION
from app.crypto import decrypt_chunk
import logging
from app.search import get_closest_string
from typing import Union, Literal


class Download:
    def __init__(self):
        self.dz = Deezer()

    def tracks(self, track_apis: list[dict], tracks_format: Literal['MP3_128', 'MP3_320', 'FLAC'] = 'FLAC') -> None:
        track_urls = self.dz.get_track_urls(
            [track['TRACK_TOKEN'] for track in track_apis],
            tracks_format
        )

        for i in range(len(track_urls)):
            api = track_apis[i]
            input_ = ChunkedInputStream(api['SNG_ID'], track_urls[i])
            display_name = f"{api['ART_NAME']} - {api['SNG_TITLE']}"

            with open(f'{display_name}.{EXTENSION[tracks_format]}', 'wb') as file:
                while True:
                    chunk = next(input_.stream.iter_content(2048 * 3), None)
                    if chunk is None:
                        input_.close()
                        break
                    if len(chunk) >= 2048:
                        decrypted = decrypt_chunk(
                            input_.blowfish_key,
                            chunk[:2048]
                        )
                        chunk = decrypted + chunk[2048:]

                    file.write(chunk)

            logging.info(f"Downloaded {display_name}")

    def track_from_query(self, query: str, tracks_format: Literal['MP3_128', 'MP3_320', 'FLAC'] = 'FLAC') -> None:
        track_apis = self.dz.search(query)['TRACK']['data']
        if not track_apis:
            return
        artist_track_strings = [f'{track_api['ART_NAME']} {track_api['SNG_TITLE']}'
                                for track_api in track_apis]
        i = get_closest_string(query, artist_track_strings)
        track_api = track_apis[i]
        self.tracks([track_api], tracks_format)
