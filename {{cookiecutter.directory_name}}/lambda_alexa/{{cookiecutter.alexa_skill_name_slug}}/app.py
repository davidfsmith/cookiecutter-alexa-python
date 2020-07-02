import os
import sys
import logging
import boto3
import inflect
import pendulum

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.utils import (
    is_request_type, is_intent_name,
    get_api_access_token, get_device_id)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_dynamodb.adapter import DynamoDbAdapter
from ask_sdk_model.ui import (
    AskForPermissionsConsentCard, SimpleCard)
from ask_sdk_model import Response
from ask_sdk_model.services import ServiceException
from ask_sdk_model.services.directive import (
    Header, SendDirectiveRequest, SpeakDirective)

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr


ENV = os.environ['ENV']

if ENV == 'LOCAL':
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url='http://dynamodb:8000'
    )
elif ENV == 'TEST':
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url='http://localhost:8000'
    )
else:
    from aws_xray_sdk.core import patch_all  # noqa
    patch_all()

    dynamodb = boto3.resource('dynamodb')

PERMISSIONS = [
    'alexa::profile:given_name:read',
    'read::alexa:device:all:address',
]

# ------------------------------ #
SKILL_NAME = "{{cookiecutter.alexa_skill_name}}"
WELCOME = f"Welcome to {SKILL_NAME}"
GOODBYE = f"Goodbye, thank's for spending time with {SKILL_NAME} today."
FALLBACK = "I'm not sure I can do that at the moment.... sorry."
ERROR = "Sorry, I'm not sure what you are asking me. Can you please ask again!!"
ERROR_SKILL = "There was an error with the skill, please check the logs."
HELP = "You can ask me about your {{cookiecutter.alexa_skill_summary}}"

NOTIFY_MISSING_PERMISSIONS = f"{SKILL_NAME} would like to access your details.  To turn share these details, please go to your Alexa app, and follow the instructions."
NOTIFY_ADDRESS_PROBLEM = "There was a problem with your address, please state your town when asking for local news"

DATA_CHECKING = "Just checking the data for you now"
WHATS_NEW = "We're just getting start and this skill is still a work in progress."
# ------------------------------ #

sb = CustomSkillBuilder(api_client=DefaultApiClient())

logger = logging.getLogger(__name__)
logger.setLevel(os.environ['LOGGING'])

# Persistence and data store
table = os.environ['DYNAMODB']
dynamodb = boto3.resource('dynamodb')
dynamodb_table = dynamodb.Table(table)
adapter = DynamoDbAdapter(
    table, partition_key_name = 'uuid', dynamodb_resource = dynamodb)

p = inflect.engine()

# TODO move speech to locale files
# TODO better code re-use, less C&P

'''
Generic handlers
'''
@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    '''
    Occurs when the skill is invovked without an intent
    type: (HandlerInput) -> Response
    '''
    logger.debug('location: {}'.format(whoami()))

    request_envelope = handler_input.request_envelope
    response_builder = handler_input.response_builder

    # TODO Check if we have a returning user
    try:
        dt = pendulum.now()
        attr = {
            'last_request_time': dt,
        }
        adapter.save_attributes(request_envelope, attr)
        logger.debug('Persistence (save): {}'.format(attr))
    except Exception as e:
        logger.error('Error reported by saving persistence data : {}'.format(e))

    # TODO Get the users given name if we have permissions
    # TODO Move to a function
    try:
        user_preferences_client = handler_input.service_client_factory.get_ups_service()
        profile_given_name = user_preferences_client.get_profile_given_name()
        speech_text = f"Welcome to {SKILL_NAME} {profile_given_name}."
    except Exception as e:
        logger.error('Error reported by user preferences client : {}'.format(e))
        speech_text = WELCOME

    response_builder.speak(speech_text).ask(speech_text).set_card(
        SimpleCard(SKILL_NAME, speech_text))
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    logger.debug('location: {}'.format(whoami()))

    response_builder = handler_input.response_builder

    speech_text = HELP

    response_builder.speak(speech_text).ask(speech_text).set_card(
        SimpleCard(SKILL_NAME, speech_text))
    return response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_intent_handler(handler_input):
    '''
    Fallback Intent (Catch all)
    type: (HandlerInput) -> Response
    '''
    logger.debug('location: {}'.format(whoami()))

    response_builder = handler_input.response_builder

    speech_text = FALLBACK

    response_builder.speak(speech_text).ask(speech_text).set_card(
        SimpleCard(SKILL_NAME, speech_text))
    return response_builder.response


@sb.request_handler(
    can_handle_func=lambda handler_input :
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input) or
        is_intent_name("AMAZON.PauseIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input):
    '''
    Cancel and Stop
    type: (HandlerInput) -> Response
    '''
    logger.debug('location: {}'.format(whoami()))

    response_builder = handler_input.response_builder

    speech_text = GOODBYE

    response_builder.speak(speech_text)
    response_builder.set_card(
        SimpleCard(SKILL_NAME, speech_text))
    response_builder.set_should_end_session(True)

    return response_builder.response


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    '''
    Session end
    type: (HandlerInput) -> Response
    any cleanup logic goes here
    '''
    logger.debug('location: {}'.format(whoami()))


'''
Deal with skill intents
'''
@sb.request_handler(can_handle_func=is_intent_name("AboutUser"))
def aboutuser_intent_handler(handler_input):
    '''
    About user
    type: (HandlerInput) -> Response
    '''
    logger.debug('location: {}'.format(whoami()))

    request_envelope = handler_input.request_envelope
    response_builder = handler_input.response_builder

    # See if we have a location, otherwise we can use the users address
    slots = request_envelope.request.intent.slots
    slot_name = 'location_slot'
    location_list = []
    if slot_name in slots:
        location_list = [slots[slot_name].value]
        logger.debug('slot name: {} value {}'.format(slot_name, location_list))

    if location_list[0] is None:
        # Need to get the location from the address assuming we have permissions
        # TODO Move to a function
        if not (request_envelope.context.system.user.permissions and
                request_envelope.context.system.user.permissions.consent_token):
            logger.error('Insufficient permissions')

            speech_text = NOTIFY_MISSING_PERMISSIONS

            response_builder.speak(speech_text)
            response_builder.set_card(
                AskForPermissionsConsentCard(permissions = PERMISSIONS))

            return response_builder.response

        try:
            device_id = get_device_id(handler_input)
            device_addr_client = handler_input.service_client_factory.get_device_address_service()
            address = device_addr_client.get_full_address(device_id)

            logger.debug('Address: {}'.format(address))

            if address.city is None or address.state_or_region is None:
                speech_text = NOTIFY_ADDRESS_PROBLEM
            else:
                location_list = [address.city, address.state_or_region]

        except ServiceException as e:
            logger.error('Error reported by device location service: {}'.format(e))
            raise e
        except Exception as e:
            logger.error('Error: {}'.format(e))
            speech_text = ERROR_SKILL

    # Example using the progressive Response API -> https://developer.amazon.com/en-US/docs/alexa/alexa-skills-kit-sdk-for-python/call-alexa-service-apis.html#directiveserviceclient
    # Build the initial response back to the user whilst we look for data
    # speech_text = DATA_CHECKING
    # request_id_holder = request_envelope.request.request_id
    # directive_header = Header(request_id = request_id_holder)
    # speech = SpeakDirective(speech_text)
    # directive_request = SendDirectiveRequest(
    #     header = directive_header,
    #     directive = speech
    # )
    # directive_service_client = handler_input.service_client_factory.get_directive_service()
    # directive_service_client.enqueue(directive_request)

    try:
        # TODO fix the capitalisation on non-towns (and probably the user data)
        # TODO need to ensure we scan the data for all items in location_list
        r = dynamodb_table.scan(
            FilterExpression = Attr('location').contains(location_list[0])
        )
        logger.debug('r: {}'.format(r))

    except Exception as e:
        logger.error('Error (dynamodb_table): {}'.format(e))
        speech_text = "It's all gone pete tong"

    news_locations = ' and '.join(location_list)
    if r['Count'] > 0:
        news_item_count = r['Count']
        # news_items = p.plural('new', news_item_count)
        speech_text = f"I've found {news_item_count} news {p.plural('item', news_item_count)} for you in {news_locations}....."
    else:
        speech_text = f"I couldn't find any news items in {news_locations} at this time, sorry."

    response_builder.speak(speech_text).set_card(
        SimpleCard(SKILL_NAME, speech_text)).set_should_end_session(
            True)
    return response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("GetColour"))
def get_colour_intent_handler(handler_input):
    '''
    Get the users preferred colour
    '''
    logger.debug('location: {}'.format(whoami()))

    response_builder = handler_input.response_builder

    speech_text = "I don't know what colour you like, sorry."

    response_builder.speak(speech_text).ask(speech_text).set_card(
        SimpleCard(SKILL_NAME, speech_text))
    return response_builder.response



@sb.request_handler(can_handle_func=is_intent_name("SetColour"))
def set_colour_intent_handler(handler_input):
    '''
    Get the users preferred colour
    '''
    logger.debug('location: {}'.format(whoami()))

    response_builder = handler_input.response_builder

    speech_text = "I don't know what colour you like, sorry."

    response_builder.speak(speech_text).ask(speech_text).set_card(
        SimpleCard(SKILL_NAME, speech_text))
    return response_builder.response

'''
Helpers
'''
@sb.global_request_interceptor()
def request_logger(handler_input):
    logger.debug('Alexa Request: {}'.format(
        handler_input.request_envelope.request))
    logger.debug('Persistence (get): {}'.format(
        adapter.get_attributes(handler_input.request_envelope)))


'''
Exceptions
'''
@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    '''
    type: (HandlerInput, Exception) -> Response
    Log the exception in CloudWatch Logs
    '''
    logger.debug('location: {}'.format(whoami()))
    logger.debug('exception: {}'.format(exception))
    logger.debug('request_envelope: {}'.format(handler_input.request_envelope))

    speech = ERROR

    handler_input.response_builder.speak(speech).ask(speech)
    return handler_input.response_builder.response


def whoami():
    return sys._getframe(1).f_code.co_name


skill = sb.create()
lambda_handler = sb.lambda_handler()
