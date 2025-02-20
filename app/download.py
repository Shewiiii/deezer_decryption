from app.api import Deezer
from app.chunked_input_stream import ChunkedInputStream
from app.constants import EXTENSION
from app.crypto import decrypt_chunk
import logging
from typing import Union, Literal


class Download:
    def __init__(self):
        self.dz = Deezer()

    def tracks(self, tracks_format: Literal['MP3_128', 'MP3_320', 'FLAC'], track_ids: list[Union[int, str]]) -> None:
        track_apis: list = self.dz.get_tracks(track_ids).get('data', [])
        track_urls = self.dz.get_track_urls(
            tracks_format, [track['TRACK_TOKEN'] for track in track_apis])

        for i in range(len(track_urls)):
            input_ = ChunkedInputStream(track_ids[i], track_urls[i])
            api = track_apis[i]
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