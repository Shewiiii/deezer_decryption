from app.constants import HEADERS, CHUNK_SIZE
from app.crypto import generate_blowfish_key, decrypt_chunk
from typing import Union
import requests


class ChunkedInputStream:
    def __init__(self, track_id: Union[int, str], stream_url: str) -> None:
        self.stream_url: str = stream_url
        self.buffer: bytes = b''
        self.blowfish_key: bytes = generate_blowfish_key(str(track_id))
        self.headers: dict = HEADERS
        self.chunk_size: int = CHUNK_SIZE
        self.finished: bool = False
        self.current_position: int = 0
        self.get_stream()

    def get_stream(self) -> None:
        self.stream: requests.Response = requests.get(
            self.stream_url,
            headers=self.headers,
            stream=True,
            timeout=10
        )
        self.chunks = self.stream.iter_content(self.chunk_size)

    def close(self):
        """Close the stream and mark as finished."""
        self.finished = True
        if self.stream:
            self.stream.close()
        self.chunks = None
        del self.buffer
