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
    'd3': 'Fresh Element Infinity',
    'd4': 'Fresh Element Solo',
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
    1: 'Bentonite',
    2: 'Tofu',
    3: 'Mixed'
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

VALID_EVENT_TYPES = [5, 6, 7, 8, 10]
EVENT_TYPE_NAMED = {
    5: 'Cleaning Completed',
    6: 'Dumping Over',
    7: 'Reset Over',
    8: 'Spray Over',
    10: 'Pet Out',
}

# Event Type --> Result --> Reason --> Optional(Error)
EVENT_DESCRIPTION = {
    5: {
        0: {
            0: 'Auto cleaning completed',
            1: 'Periodic cleaning completed',
            2: 'Manual cleaning completed',
            3: 'Manual cleaning completed',
        },
        1: {
            0: 'Automatic cleaning terminated',
            1: 'Periodic cleaning terminated',
            2: 'Manual cleaning terminated',
            3: 'Manual cleaning terminated',
        },
        2: {
            0: {
                'full': 'Automatic cleaning failed, waste collection bin is full, please empty promptly',
                'hallL': 'Automatic cleaning failure, the cylinder is not properly locked in place, please check',
                'hallT': 'Automatic cleaning failure, the litter box\'s upper cupper cover is not placed properly, please check',
            },
            1: {
                'full': 'Scheduled cleaning failed, waste collection bin is full, please empty promptly',
                'hallL': 'Scheduled cleaning failure, the cylinder is not properly locked in place, please check',
                'hallT': 'Scheduled cleaning failure, the litter box\'s upper cupper cover is not placed properly, please check',
            },
            2: {
                'full': 'Manual cleaning failed, waste collection bin is full, please empty promptly',
                'hallL': 'Manual cleaning failure, the cylinder is not properly locked in place, please check',
                'hallT': 'Manual cleaning failure, the litter box\'s upper cupper cover is not placed properly, please check',
            },
            3: {
                'full': 'Manual cleaning failed, waste collection bin is full, please empty promptly',
                'hallL': 'Manual cleaning failure, the cylinder is not properly locked in place, please check',
                'hallT': 'Manual cleaning failure, the litter box\'s upper cupper cover is not placed properly, please check',
            },
        },
        3: {
            0: 'Automatic cleaning cancelled, device in operation',
            1: 'Periodic cleaning cancelled, device in operation',
            2: 'Manual cleaning cancelled, device in operation',
            3: 'Manual cleaning cancelled, device in operation',
        },
        4: {
            0: 'Kitten mode is enabled, auto cleaning is canceled',
            1: 'Kitten mode is enabled, periodically cleaning is canceled',
        },
    },
    6: {
        0: 'Cat litter empty completed',
        1: 'Cat litter empty terminated',
        2: {
            'full': 'Cat litter empty failed, waste collection bin is full, please empty promptly',
            'hallL': 'Cat litter empty failure, the cylinder is not properly locked in place, please check',
            'hallT': 'Cat litter empty failure, the litter box\'s cupper cover is not placed properly, please check',
        },
    },
    7: {
        0: 'Device reset completed',
        1: 'Device reset terminated',
        2: {
            'full': 'Device reset failed, waste collection bin is full, please empty promptly',
            'hallL': 'Device reset failure, the cylinder is not properly locked in place, please check',
            'hallT': 'Device reset failure, the litter box\'s cupper cover is not placed properly, please check',
        },
    },
    8: {
        0: {
            0: 'Deodorant finished',
            1: 'Periodic odor removal completed',
            2: 'Manual odor removal completed',
            3: 'Manual odor removal completed',
        },
        1: {
            0: 'Deodorant finished, not enough purifying liquid, please refill in time',
            1: 'Periodic odor removal completed, not enough purifying liquid, please refill in time',
            2: 'Manual odor removal completed, not enough purifying liquid, please refill in time',
            3: 'Manual odor removal completed, not enough purifying liquid, please refill in time',
        },
        2: {
            0: 'Automatic odor removal failed, odor eliminator error',
            1: 'Periodic odor removal failure, odor eliminator malfunction',
            2: 'Manual odor removal failure, odor eliminator malfunction',
            3: 'Manual odor removal failure, odor eliminator malfunction',
        },
    },
}    
    
    
    
    
