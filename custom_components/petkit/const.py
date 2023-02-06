"""Constants for PetKit"""

import asyncio
import logging

from aiohttp.client_exceptions import ClientConnectionError
from petkitaio.exceptions import AuthError, PetKitError
from petkitaio.constants import W5Command

from homeassistant.const import Platform

LOGGER = logging.getLogger(__package__)


DEFAULT_SCAN_INTERVAL = 120
DOMAIN = "petkit"
PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]

DEFAULT_NAME = "PetKit"
TIMEOUT = 20

PETKIT_ERRORS = (
    asyncio.TimeoutError,
    ClientConnectionError,
    AuthError,
    PetKitError,
)

# Dictionaries and lists.

LIGHT_BRIGHTNESS_OPTIONS = ['Low', 'Medium', 'High']

LIGHT_BRIGHTNESS_COMMAND = {
    W5Command.LIGHTLOW: "Low",
    W5Command.LIGHTMEDIUM: "Medium",
    W5Command.LIGHTHIGH: "High"
}

LIGHT_BRIGHTNESS_NAMED = {
    1: 'Low',
    2: 'Medium',
    3: 'High'
}

WF_MODE_OPTIONS = ['Normal', 'Smart']

WF_MODE_NAMED = {
    1: 'Normal',
    2: 'Smart'
}

WF_MODE_COMMAND = {
    W5Command.NORMAL: "Normal",
    W5Command.SMART: "Smart"
}

WATER_FOUNTAINS = {
    'w5': 'Eversweet 3 Pro',
}

FEEDERS = {
    'd4': 'Fresh Element Solo',
    'feedermini': 'Fresh Element Mini Pro',
}

FEEDER_MANUAL_FEED_OPTIONS = ['', '1/10th Cup (10g)', '1/5th Cup (20g)', '3/10th Cup (30g)', '2/5th Cup (40g)', '1/2 Cup (50g)']
MINI_FEEDER_MANUAL_FEED_OPTIONS = [
    '',
    '1/20th Cup (5g)',
    '1/10th Cup (10g)',
    '3/20th Cup (15g)',
    '1/5th Cup (20g)',
    '1/4th Cup (25g)',
    '3/10th Cup (30g)',
    '7/20th Cup (35g)',
    '2/5th Cup (40g)',
    '9/20th Cup (45g)',
    '1/2 Cup (50g)'
]

MANUAL_FEED_NAMED = {
    0: '',
    5: '1/20th Cup (5g)',
    10: '1/10th Cup (10g)',
    15: '3/20th Cup (15g)',
    20: '1/5th Cup (20g)',
    25: '1/4th Cup (25g)',
    30: '3/10th Cup (30g)',
    35: '7/20th Cup (35g)',
    40: '2/5th Cup (40g)',
    45: '9/20th Cup (45g)',
    50: '1/2 Cup (50g)'
}
