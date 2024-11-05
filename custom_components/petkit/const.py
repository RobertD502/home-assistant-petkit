"""Constants for PetKit"""

import asyncio
import logging

from aiohttp.client_exceptions import ClientConnectionError
from petkitaio.exceptions import AuthError, PetKitError
from petkitaio.constants import W5Command, PurifierCommand

from homeassistant.const import Platform

LOGGER = logging.getLogger(__package__)


DOMAIN = "petkit"
PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.FAN,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT
]

DEFAULT_NAME = "PetKit"
REGION = "region"
PETKIT_COORDINATOR = "petkit_coordinator"
POLLING_INTERVAL = "polling_interval"
TIMEOUT = 20
TIMEZONE = "timezone"
UPDATE_LISTENER = "update_listener"

PETKIT_ERRORS = (
    asyncio.TimeoutError,
    ClientConnectionError,
    AuthError,
    PetKitError,
)

REGIONS_LIST = [
    "Afghanistan",
    "Aland Islands",
    "Albania",
    "Algeria",
    "American Samoa",
    "Andorra",
    "Angola",
    "Anguilla",
    "Antarctica",
    "Antigua and Barbuda",
    "Argentina",
    "Armenia",
    "Aruba",
    "Australia",
    "Austria",
    "Azerbaijan",
    "Bahamas",
    "Bahrain",
    "Bangladesh",
    "Barbados",
    "Belarus",
    "Belgium",
    "Belize",
    "Benin",
    "Bermuda",
    "Bhutan",
    "Bolivia",
    "Bosnia and Herzegovina",
    "Botswana",
    "Bouvet Island",
    "Brazil",
    "British Indian Ocean Territory",
    "Brunei Darussalam",
    "Bulgaria",
    "Burkina Faso",
    "Burundi",
    "Cambodia",
    "Cameroon",
    "Canada",
    "Cape Verde",
    "Cayman Islands",
    "Central African Republic",
    "Chad",
    "Chile",
    "China",
    "Christmas Island",
    "Cocos (Keeling) Islands",
    "Colombia",
    "Comoros",
    "Congo",
    "Congo (the Democratic Republic of the Congo)",
    "Cook Islands",
    "Costa Rica",
    "Côte d'Ivoire",
    "Croatia",
    "Cuba",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Djibouti",
    "Dominica",
    "Dominican Republic",
    "Ecuador",
    "Egypt",
    "El Salvador",
    "Equatorial Guinea",
    "Eritrea",
    "Estonia",
    "Ethiopia",
    "Falkland Islands [Malvinas]",
    "Faroe Islands",
    "Fiji",
    "Finland",
    "France",
    "French Guiana",
    "French Polynesia",
    "French Southern Territories",
    "Gabon",
    "Gambia",
    "Georgia",
    "Germany",
    "Ghana",
    "Gibraltar",
    "Greece",
    "Greenland",
    "Grenada",
    "Guadeloupe",
    "Guam",
    "Guatemala",
    "Guernsey",
    "Guinea",
    "Guinea-Bissau",
    "Guyana",
    "Haiti",
    "Heard Island and McDonald Islands",
    "Holy See [Vatican City State]",
    "Honduras",
    "Hong Kong",
    "Hungary",
    "Iceland",
    "India",
    "Indonesia",
    "Iran (the Islamic Republic of Iran)",
    "Iraq",
    "Ireland",
    "Isle of Man",
    "Israel",
    "Italy",
    "Jamaica",
    "Japan",
    "Jersey",
    "Jordan",
    "Kazakhstan",
    "Kenya",
    "Kiribati",
    "Korea (the Democratic People's Republic of Korea)",
    "Korea (the Republic of Korea)",
    "Kuwait",
    "Kyrgyzstan",
    "Lao People's Democratic Republic",
    "Latvia",
    "Lebanon",
    "Lesotho",
    "Liberia",
    "Libyan Arab Jamahiriya",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Macao",
    "Macedonia (the former Yugoslav Republic of Macedonia)",
    "Madagascar",
    "Malawi",
    "Malaysia",
    "Maldives",
    "Mali",
    "Malta",
    "Marshall Islands",
    "Martinique",
    "Mauritania",
    "Mauritius",
    "Mayotte",
    "Mexico",
    "Micronesia (the Federated States of Micronesia)",
    "Moldova (the Republic of Moldova)",
    "Monaco",
    "Mongolia",
    "Montenegro",
    "Montserrat",
    "Morocco",
    "Mozambique",
    "Myanmar",
    "Namibia",
    "Nauru",
    "Nepal",
    "Netherlands",
    "Netherlands Antilles",
    "New Caledonia",
    "New Zealand",
    "Nicaragua",
    "Niger",
    "Nigeria",
    "Niue",
    "Norfolk Island",
    "Northern Mariana Islands",
    "Norway",
    "Oman",
    "Pakistan",
    "Palau",
    "Palestinian Territory ",
    "Panama",
    "Papua New Guinea",
    "Paraguay",
    "Peru",
    "Philippines",
    "Pitcairn",
    "Poland",
    "Portugal",
    "Puerto Rico",
    "Qatar",
    "Réunion",
    "Romania",
    "Russian Federation",
    "Rwanda",
    "Saint Helena",
    "Saint Kitts and Nevis",
    "Saint Lucia",
    "Saint Pierre and Miquelon",
    "Saint Vincent and the Grenadines",
    "Samoa",
    "San Marino",
    "Sao Tome and Principe",
    "Saudi Arabia",
    "Senegal",
    "Serbia",
    "Seychelles",
    "Sierra Leone",
    "Singapore",
    "Slovakia",
    "Slovenia",
    "Solomon Islands",
    "Somalia",
    "South Africa",
    "South Georgia and the South Sandwich Islands",
    "Spain",
    "Sri Lanka",
    "Sudan",
    "Suriname",
    "Svalbard and Jan Mayen",
    "Swaziland",
    "Sweden",
    "Switzerland",
    "Syrian Arab Republic",
    "Taiwan (Province of China)",
    "Tajikistan",
    "Tanzania,United Republic of",
    "Thailand",
    "Timor-Leste",
    "Togo",
    "Tokelau",
    "Tonga",
    "Trinidad and Tobago",
    "Tunisia",
    "Turkey",
    "Turkmenistan",
    "Turks and Caicos Islands",
    "Tuvalu",
    "Uganda",
    "Ukraine",
    "United Arab Emirates",
    "United Kingdom",
    "United States",
    "United States Minor Outlying Islands",
    "Uruguay",
    "Uzbekistan",
    "Vanuatu",
    "Venezuela",
    "Viet Nam",
    "Virgin Islands (British)",
    "Virgin Islands (U.S.)",
    "Wallis and Futuna",
    "Western Sahara",
    "Yemen",
    "Zambia",
    "Zimbabwe"
]


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

PURIFIERS = {
    'k2': 'Air Magicube'
}

PURIFIER_MODE_TO_COMMAND = {
    'auto': PurifierCommand.AUTO_MODE,
    'silent': PurifierCommand.SILENT_MODE,
    'standard': PurifierCommand.STANDARD_MODE,
    'strong': PurifierCommand.STRONG_MODE
}

PURIFIER_MODES = ['auto', 'silent', 'standard', 'strong']

PURIFIER_MODE_NAMED = {
    0: 'auto',
    1: 'silent',
    2: 'standard',
    3: 'strong'
}


FEEDERS = {
    'd3': 'Fresh Element Infinity',
    'd4': 'Fresh Element Solo',
    'd4s': 'Fresh Element Gemini',
    'd4sh': 'Fresh Element Gemini',
    'feeder': 'Fresh Element',
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
    50: '1/2 Cup (50g)',
}
