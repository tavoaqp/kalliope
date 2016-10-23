import requests
import re
from core import FileManager
from core.TTS.TTSModule import TTSModule, FailToLoadSoundFile
import logging

logging.basicConfig()
logger = logging.getLogger("kalliope")

TTS_URL = "http://www.acapela-group.com/demo-tts/DemoHTML5Form_V2_fr.php"
TTS_CONTENT_TYPE = "audio/mpeg"
TTS_TIMEOUT_SEC = 30


class Acapela(TTSModule):
    def __init__(self, **kwargs):
        super(Acapela, self).__init__(**kwargs)

    def say(self, words):

        self.generate_and_play(words, self._generate_audio_file)

    @classmethod
    def _generate_audio_file(cls):

        # Prepare payload
        payload = cls.get_payload()

        # Get the mp3 URL from the page
        url = Acapela.get_audio_link(cls.TTS_URL, payload)

        # getting the mp3
        r = requests.get(url, params=payload, stream=True, timeout=TTS_TIMEOUT_SEC)
        content_type = r.headers['Content-Type']

        logger.debug("Trying to get url: %s response code: %s and content-type: %s",
                     r.url,
                     r.status_code,
                     content_type)
        # Verify the response status code and the response content type
        if r.status_code != requests.codes.ok or content_type != TTS_CONTENT_TYPE:
            raise FailToLoadSoundFile("Fail while trying to remotely access the audio file")

        # OK we get the audio we can write the sound file
        FileManager.write_in_file(cls.file_path, r.content)

    @classmethod
    def get_payload(cls):
        return {
            "MyLanguages": cls.language,
            "MySelectedVoice": cls.voice,
            "MyTextForTTS": cls.words,
            "t": "1",
            "SendToVaaS": ""
        }

    @staticmethod
    def get_audio_link(url, payload, timeout_expected=TTS_TIMEOUT_SEC):
        r = requests.post(url, payload, timeout=timeout_expected)
        data = r.content
        return re.search("(?P<url>https?://[^\s]+).mp3", data).group(0)
