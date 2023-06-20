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
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT
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

LIGHT_BRIGHTNESS_OPTIONS = ['low', 'medium', 'high']

LIGHT_BRIGHTNESS_COMMAND = {
    W5Command.LIGHT_LOW: "low",
    W5Command.LIGHT_MEDIUM: "medium",
    W5Command.LIGHT_HIGH: "high"
}

LIGHT_BRIGHTNESS_NAMED = {
    1: 'low',
    2: 'medium',
    3: 'high'
}

WF_MODE_OPTIONS = ['normal', 'smart']

WF_MODE_NAMED = {
    1: 'normal',
    2: 'smart'
}

WF_MODE_COMMAND = {
    W5Command.NORMAL: "normal",
    W5Command.SMART: "smart"
}

WATER_FOUNTAINS = {
    2: 'Eversweet 5 Mini',
    4: 'Eversweet 3 Pro',
    5: 'Eversweet Solo 2'
}


FEEDERS = {
    'd3': 'Fresh Element Infinity',
    'd4': 'Fresh Element Solo',
    'd4s': 'Fresh Element Gemini',
    'feedermini': 'Fresh Element Mini Pro',
}

LITTER_BOXES = {
    't3': 'PURA X',
    't4': 'PURA MAX',
}

CLEANING_INTERVAL_NAMED = {
    0: 'Disabled',
    300: '5min',
    600: '10min',
    900: '15min',
    1800: '30min',
    2700: '45min',
    3600: '1h',
    4500: '1h15min',
    5400: '1h30min',
    6300: '1h45min',
    7200: '2h'
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

LITTER_TYPE_NAMED = {
    1: 'bentonite',
    2: 'tofu',
    3: 'mixed'
}

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
