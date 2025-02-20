from app.constants import HEADERS
import os
import requests
from typing import Optional, Union, Literal

DEEZER_ARL = os.getenv("DEEZER_ARL")


class Deezer:
    def __init__(self):
        self.headers = HEADERS
        self.session = requests.Session()
        cookie_obj = requests.cookies.create_cookie(
            domain='.deezer.com',
            name='arl',
            value=DEEZER_ARL,
            path="/",
            rest={'HttpOnly': True}
        )
        self.session.cookies.set_cookie(cookie_obj)
        self.api_token = None
        self.base_url = "http://www.deezer.com/ajax/gw-light.php"
        self.params = {}
        self.get_api_token()
        self.user_data = self.get_user_data()

    def get_api_token(self) -> None:
        p = {
            'api_version': "1.0",
            'api_token': 'null',
            'method': 'deezer.getUserData'
        }
        response = self.session.post(
            self.base_url,
            params=p,
            headers=self.headers
        ).json()
        self.api_token = response['results']['checkForm']

    def gw_api_call(
        self,
        method: str,
        args: Optional[dict] = None,
        params: Optional[dict] = None
    ) -> dict:
        if params is None:
            params = {}
        if args is None:
            args = {}
        p = {
            'api_version': "1.0",
            'api_token': self.api_token,
            'method': method
        }
        p.update(params)
        response = self.session.post(
            self.base_url,
            params=p,
            headers=self.headers,
            json=args
        ).json()
        return response['results']

    def get_track_page(self, sng_id: Union[int, str]) -> dict:
        return self.gw_api_call('deezer.pageTrack', {'SNG_ID': sng_id})

    def get_tracks(self, track_ids: list[Union[int, str]]) -> dict:
        return self.gw_api_call('song.getListData', {'SNG_IDS': track_ids})

    def get_user_data(self) -> dict:
        return self.gw_api_call('deezer.getUserData')

    def can_stream_lossless(self) -> bool:
        return self.user_data["USER"]["OPTIONS"]["web_lossless"] or self.user_data["USER"]["OPTIONS"]["mobile_lossless"]

    def get_track_urls(self, tracks_format: Literal['MP3_128', 'MP3_320', 'FLAC'], track_tokens: list) -> list[str]:
        license_token = self.user_data["USER"]["OPTIONS"]["license_token"]
        if not license_token:
            return []
        if not self.can_stream_lossless() and tracks_format == 'FLAC':
            raise ValueError

        request = self.session.post(
            "https://media.deezer.com/v1/get_url",
            json={
                'license_token': license_token,
                'media': [{
                    'type': "FULL",
                    'formats': [
                        {'cipher': "BF_CBC_STRIPE", 'format': tracks_format}
                    ]
                }],
                'track_tokens': track_tokens
            },
            headers=self.headers
        )
        request.raise_for_status()
        response = request.json()
        result = []
        for data in response['data']:
            if 'media' in data and len(data['media']):
                result.append(data['media'][0]['sources'][0]['url'])
            else:
                result.append(None)
        return result


if __name__ == '__main__':
    api = Deezer()
