import json
import pytest

from lambda_alexa.{{cookiecutter.alexa_skill_name_slug}} import app


def alexa_base_intent(request_response):
    """
    Base intent
    """

    return {
        "version": "1.0",
        "session": {
            "new": true,
            "sessionId": "",
            "application": {
                "applicationId": "{{cookiecutter.alexa_skill_id}}"
            },
            "user": {
                "userId": "",
                "permissions": {
                    "consentToken": ""
                }
            }
        },
        "context": {
            "AudioPlayer": {
                "playerActivity": "IDLE"
            },
            "System": {
                "application": {
                    "applicationId": "{{cookiecutter.alexa_skill_id}}"
                },
                "user": {
                    "userId": "",
                    "permissions": {
                        "consentToken": ""
                    }
                },
                "device": {
                    "deviceId": "",
                    "supportedInterfaces": {
                        "AudioPlayer": {}
                    }
                },
                "apiEndpoint": "https://api.eu.amazonalexa.com",
                "apiAccessToken": ""
            },
            "Viewport": {
                "experiences": [
                    {
                        "arcMinuteWidth": 246,
                        "arcMinuteHeight": 144,
                        "canRotate": false,
                        "canResize": false
                    }
                ],
                "shape": "RECTANGLE",
                "pixelWidth": 1024,
                "pixelHeight": 600,
                "dpi": 160,
                "currentPixelWidth": 1024,
                "currentPixelHeight": 600,
                "touch": [
                    "SINGLE"
                ],
                "video": {
                    "codecs": [
                        "H_264_42",
                        "H_264_41"
                    ]
                }
            },
            "Viewports": [
                {
                    "type": "APL",
                    "id": "main",
                    "shape": "RECTANGLE",
                    "dpi": 160,
                    "presentationType": "STANDARD",
                    "canRotate": false,
                    "configuration": {
                        "current": {
                            "video": {
                                "codecs": [
                                    "H_264_42",
                                    "H_264_41"
                                ]
                            },
                            "size": {
                                "type": "DISCRETE",
                                "pixelWidth": 1024,
                                "pixelHeight": 600
                            }
                        }
                    }
                }
            ]
        },
        request_response
    }

@pytest.fixture()
def alexa_launch_intent_response():

    response =  {
        "request": {
            "type": "LaunchRequest",
            "requestId": "",
            "timestamp": "2020-06-01T09:00:01Z",
            "locale": "en-GB",
            "shouldLinkResultBeReturned": false
        }
    }

    return alexa_base_intent(response)


def test_alexa_launch_intent_handler(alexa_launch_intent_response, mocker):

    r = app.lambda_handler(alexa_launch_intent_response, "")

    assert r["statusCode"] == 200
    assert "text" in r["body"]["response"]["outputSpeech"]


# def test_alexa_skillinformation_intent_handler(alexa_localnews_intent_handler, mocker):

#     r = app.lambda_handler(alexa_localnews_intent_handler("Horsham"), "")

#     assert r["statusCode"] == 200
#     assert "text" in r["body"]["response"]["outputSpeech"]
