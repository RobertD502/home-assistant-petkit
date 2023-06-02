### Dictionaries describing the events returned by litter box ###


# Event Type --> Result --> Reason --> Optional(Error)
EVENT_DESCRIPTION = {
    5: {
        0: {
            0: 'auto_cleaning_completed',
            1: 'periodic_cleaning_completed',
            2: 'manual_cleaning_completed',
            3: 'manual_cleaning_completed',
        },
        1: {
            0: 'auto_cleaning_terminated',
            1: 'periodic_cleaning_terminated',
            2: 'manual_cleaning_terminated',
            3: 'manual_cleaning_terminated',
        },
        2: {
            0: {
                'full': 'auto_cleaning_failed_full',
                'hallL': 'auto_cleaning_failed_hall_l',
                'hallT': 'auto_cleaning_failed_hall_t',
            },
            1: {
                'full': 'scheduled_cleaning_failed_full',
                'hallL': 'scheduled_cleaning_failed_hall_l',
                'hallT': 'scheduled_cleaning_failed_hall_t',
            },
            2: {
                'full': 'manual_cleaning_failed_full',
                'hallL': 'manual_cleaning_failed_hall_l',
                'hallT': 'manual_cleaning_failed_hall_t',
            },
            3: {
                'full': 'manual_cleaning_failed_full',
                'hallL': 'manual_cleaning_failed_hall_l',
                'hallT': 'manual_cleaning_failed_hall_t',
            },
        },
        3: {
            0: 'auto_cleaning_canceled',
            1: 'periodic_cleaning_canceled',
            2: 'manual_cleaning_canceled',
            3: 'manual_cleaning_canceled',
        },
        4: {
            0: 'auto_cleaning_canceled_kitten',
            1: 'periodic_cleaning_canceled_kitten',
        },
    },
    6: {
        0: 'litter_empty_completed',
        1: 'litter_empty_terminated',
        2: {
            'full': 'litter_empty_failed_full',
            'hallL': 'litter_empty_failed_hall_l',
            'hallT': 'litter_empty_failed_hall_t',
        },
    },
    7: {
        0: 'reset_completed',
        1: 'reset_terminated',
        2: {
            'full': 'reset_failed_full',
            'hallL': 'reset_failed_hall_l',
            'hallT': 'reset_failed_hall_t',
        },
    },
    8: {
        0: {
            0: 'deodorant_finished',
            1: 'periodic_odor_completed',
            2: 'manual_odor_completed',
            3: 'manual_odor_completed',
        },
        1: {
            0: 'deodorant_finished_liquid_lack',
            1: 'periodic_odor_completed_liquid_lack',
            2: 'manual_odor_completed_liquid_lack',
            3: 'manual_odor_completed_liquid_lack',
        },
        2: {
            0: 'auto_odor_failed',
            1: 'periodic_odor_failed',
            2: 'manual_odor_failed',
            3: 'manual_odor_failed',
        },
    },
}

PURA_X_EVENT_FULL_DESCRIPTION = {
    'auto_cleaning_completed': 'Auto cleaning completed',
    'periodic_cleaning_completed': 'Periodic cleaning completed',
    'manual_cleaning_completed': 'Manual cleaning completed',
    'auto_cleaning_terminated': 'Automatic cleaning terminated',
    'periodic_cleaning_terminated': 'Periodic cleaning terminated',
    'manual_cleaning_terminated': 'Manual cleaning terminated',
    'auto_cleaning_failed_full': 'Automatic cleaning failed, waste collection bin is full, please empty promptly',
    'auto_cleaning_failed_hall_l': 'Automatic cleaning failure, the cylinder is not properly locked in place, please check',
    'auto_cleaning_failed_hall_t': 'Automatic cleaning failure, the litter box\'s upper cupper cover is not placed properly, please check',
    'scheduled_cleaning_failed_full': 'Scheduled cleaning failed, waste collection bin is full, please empty promptly',
    'scheduled_cleaning_failed_hall_l': 'Scheduled cleaning failure, the cylinder is not properly locked in place, please check',
    'scheduled_cleaning_failed_hall_t': 'Scheduled cleaning failure, the litter box\'s upper cupper cover is not placed properly, please check',
    'manual_cleaning_failed_full': 'Manual cleaning failed, waste collection bin is full, please empty promptly',
    'manual_cleaning_failed_hall_l': 'Manual cleaning failure, the cylinder is not properly locked in place, please check',
    'manual_cleaning_failed_hall_t': 'Manual cleaning failure, the litter box\'s upper cupper cover is not placed properly, please check',
    'auto_cleaning_canceled': 'Automatic cleaning canceled, device in operation',
    'periodic_cleaning_canceled': 'Periodic cleaning canceled, device in operation',
    'manual_cleaning_canceled': 'Manual cleaning canceled, device in operation',
    'auto_cleaning_canceled_kitten': 'Kitten mode is enabled, auto cleaning is canceled',
    'periodic_cleaning_canceled_kitten': 'Kitten mode is enabled, periodically cleaning is canceled',
    'litter_empty_completed': 'Cat litter empty completed',
    'litter_empty_terminated': 'Cat litter empty terminated',
    'litter_empty_failed_full': 'Cat litter empty failed, waste collection bin is full, please empty promptly',
    'litter_empty_failed_hall_l': 'Cat litter empty failure, the cylinder is not properly locked in place, please check',
    'litter_empty_failed_hall_t': 'Cat litter empty failure, the litter box\'s cupper cover is not placed properly, please check',
    'reset_completed': 'Device reset completed',
    'reset_terminated': 'Device reset terminated',
    'reset_failed_full': 'Device reset failed, waste collection bin is full, please empty promptly',
    'reset_failed_hall_l': 'Device reset failure, the cylinder is not properly locked in place, please check',
    'reset_failed_hall_t': 'Device reset failure, the litter box\'s cupper cover is not placed properly, please check',
    'deodorant_finished': 'Deodorant finished',
    'periodic_odor_completed': 'Periodic odor removal completed',
    'manual_odor_completed': 'Manual odor removal completed',
    'deodorant_finished_liquid_lack': 'Deodorant finished, not enough purifying liquid, please refill in time',
    'periodic_odor_completed_liquid_lack': 'Periodic odor removal completed, not enough purifying liquid, please refill in time',
    'manual_odor_completed_liquid_lack': 'Manual odor removal completed, not enough purifying liquid, please refill in time',
    'auto_odor_failed': 'Automatic odor removal failed, odor eliminator error',
    'periodic_odor_failed': 'Periodic odor removal failure, odor eliminator malfunction',
    'manual_odor_failed': 'Manual odor removal failure, odor eliminator malfunction'
}

EVENT_TYPE_NAMED = {
    5: 'cleaning_completed',
    6: 'dumping_over',
    7: 'reset_over',
    8: 'spray_over',
    10: 'pet_out',
}
VALID_EVENT_TYPES = [5, 6, 7, 8, 10]
MAX_EVENT_TYPES = [5, 6, 7, 8, 10, 17]

MAX_EVENT_TYPE_NAMED = {
    5: 'cleaning_completed',
    6: 'dumping_over',
    7: 'reset_over',
    8: 'spray_over',
    10: 'pet_out',
    17: 'light_over'
}

# Event Type --> Result --> Reason --> Optional(Error)
MAX_EVENT_DESCRIPTION = {
    5: {
        0: {
            0: 'auto_cleaning_completed',
            1: 'periodic_cleaning_completed',
            2: 'manual_cleaning_completed',
            3: 'manual_cleaning_completed',
        },
        1: {
            0: 'auto_cleaning_terminated',
            1: 'periodic_cleaning_terminated',
            2: 'manual_cleaning_terminated',
            3: 'manual_cleaning_terminated',
        },
        2: {
            0: {
                'full': 'auto_cleaning_failed_full',
                'hallT': 'auto_cleaning_failed_hall_t',
                'falldown': 'auto_cleaning_failed_falldown'
            },
            1: {
                'full': 'scheduled_cleaning_failed_full',
                'hallT': 'scheduled_cleaning_failed_hall_t',
                'falldown': 'scheduled_cleaning_failed_falldown'
            },
            2: {
                'full': 'manual_cleaning_failed_full',
                'hallT': 'manual_cleaning_failed_hall_t',
                'falldown': 'manual_cleaning_failed_falldown'
            },
            3: {
                'full': 'manual_cleaning_failed_full',
                'hallT': 'manual_cleaning_failed_hall_t',
                'falldown': 'manual_cleaning_failed_falldown'
            },
        },
        3: {
            0: 'auto_cleaning_canceled',
            1: 'periodic_cleaning_canceled',
            2: 'manual_cleaning_canceled',
            3: 'manual_cleaning_canceled',
        },
        4: {
            0: 'auto_cleaning_failed_full',
            1: 'scheduled_cleaning_failed_full',
            2: 'manual_cleaning_failed_full',
            3: 'manual_cleaning_failed_full',
        },
        5: {
            0: 'auto_cleaning_failed_maintenance',
            1: 'periodic_cleaning_failed_maintenance',
        },
        7: {
            0: 'auto_cleaning_canceled_kitten',
            1: 'periodic_cleaning_canceled_kitten',
        }
    },
    6: {
        0: 'litter_empty_completed',
        1: 'litter_empty_terminated',
        2: {
            'full': 'litter_empty_failed_full',
            'hallT': 'litter_empty_failed_hall_t',
            'falldown': 'litter_empty_failed_falldown',
        },
    },
    7: {
        0: 'reset_completed',
        1: 'reset_terminated',
        2: {
            'full': 'reset_failed_full',
            'hallT': 'reset_failed_hall_t',
            'falldown': 'reset_failed_falldown'
        },
        5: 'maintenance_mode'
    },
    8: {
        0: {
            0: 'deodorant_finished',
            1: 'periodic_odor_completed',
            2: 'manual_odor_completed',
            3: 'manual_odor_completed',
        },
        1: {
            0: 'auto_odor_terminated',
            1: 'periodic_odor_terminated',
            2: 'manual_odor_terminated',
            3: 'manual_odor_terminated',
        },
        2: {
            0: 'auto_odor_failed',
            1: 'periodic_odor_failed',
            2: 'manual_odor_failed',
            3: 'manual_odor_failed',
        },
        4: {
            0: 'auto_odor_canceled',
            1: 'periodic_odor_canceled',
            2: 'manual_odor_canceled',
            3: 'manual_odor_canceled'
        },
        5: {
            0: 'auto_odor_failed_device',
            1: 'periodic_odor_failed_device',
            2: 'manual_odor_failed_device',
            3: 'manual_odor_failed_device'
        },
        6: {
            0: 'auto_odor_failed_batt',
            1: 'periodic_odor_failed_batt',
            2: 'manual_odor_failed_batt',
            3: 'manual_odor_failed_batt'
        },
        7: {
            0: 'auto_odor_failed_low_batt',
            1: 'periodic_odor_failed_low_batt',
            2: 'manual_odor_failed_low_batt',
            3: 'manual_odor_failed_low_batt'
        },
        8: {
            0: 'deodorant_finished',
            1: 'periodic_odor_completed',
            2: 'manual_odor_completed'
        },
        9: 'cat_stopped_odor'
    },
    17: {
        0: 'light_on',
        1: 'light_already_on',
        2: 'light_malfunc',
        5: 'light_no_device',
        6: 'light_batt_cap',
        7: 'light_low_batt'
    }
}

PURA_MAX_EVENT_FULL_DESCRIPTION = {
    'auto_cleaning_completed': 'Auto cleaning completed',
    'periodic_cleaning_completed': 'Periodic cleaning completed',
    'manual_cleaning_completed': 'Manual cleaning completed',
    'auto_cleaning_terminated': 'Automatic cleaning terminated',
    'periodic_cleaning_terminated': 'Periodic cleaning terminated',
    'manual_cleaning_terminated': 'Manual cleaning terminated',
    'auto_cleaning_failed_full': 'Automatic cleaning failed, waste collection bin is full, please empty promptly',
    'auto_cleaning_failed_hall_t': 'Automatic cleaning failure, the litter box\'s upper cupper cover is not placed properly, please check',
    'auto_cleaning_failed_falldown': 'Automatic cleaning failure, the litter box has been knocked down, please check.',
    'auto_cleaning_failed_other': 'Automatic cleaning failure, device malfunction, please check.',
    'scheduled_cleaning_failed_full': 'Scheduled cleaning failed, waste collection bin is full, please empty promptly',
    'scheduled_cleaning_failed_hall_t': 'Scheduled cleaning failure, the litter box\'s upper cupper cover is not placed properly, please check',
    'scheduled_cleaning_failed_falldown': 'Scheduled cleaning failure, the litter box has been knocked down, please check.',
    'scheduled_cleaning_failed_other': 'Scheduled cleaning failure, device malfunction, please check.',
    'manual_cleaning_failed_full': 'Manual cleaning failed, waste collection bin is full, please empty promptly',
    'manual_cleaning_failed_hall_t': 'Manual cleaning failure, the litter box\'s upper cupper cover is not placed properly, please check',
    'manual_cleaning_failed_falldown': 'Manual cleaning failure, the litter box has been knocked down, please check.',
    'manual_cleaning_failed_other': 'Manual cleaning failure, device malfunction, please check.',
    'auto_cleaning_canceled': 'Automatic cleaning canceled, device in operation',
    'periodic_cleaning_canceled': 'Periodic cleaning canceled, device in operation',
    'manual_cleaning_canceled': 'Manual cleaning canceled, device in operation',
    'auto_cleaning_failed_maintenance': 'Automatic cleaning failed, the device is in maintenance mode',
    'periodic_cleaning_failed_maintenance': 'Periodically cleaning failed, the device is in maintenance mode',
    'auto_cleaning_canceled_kitten': 'Kitten mode is enabled, auto cleaning is canceled',
    'periodic_cleaning_canceled_kitten': 'Kitten mode is enabled, periodically cleaning is canceled',
    'litter_empty_completed': 'Cat litter empty completed',
    'litter_empty_terminated': 'Cat litter empty terminated',
    'litter_empty_failed_full': 'Cat litter empty failed, waste collection bin is full, please empty promptly',
    'litter_empty_failed_hall_t': 'Cat litter empty failure, the litter box\'s cupper cover is not placed properly, please check',
    'litter_empty_failed_falldown': 'Cat litter empty failure, the litter box has been knocked down, please check',
    'litter_empty_failed_other': 'Cat litter empty failure, device malfunction, please check.',
    'reset_completed': 'Device reset completed',
    'reset_terminated': 'Device reset terminated',
    'reset_failed_full': 'Device reset failed, waste collection bin is full, please empty promptly',
    'reset_failed_hall_t': 'Device reset failure, the litter box\'s cupper cover is not placed properly, please check',
    'reset_failed_falldown': 'Device reset failure, the litter box has been knocked down, please check.',
    'reset_failed_other': 'Device reset failure, device malfunction, please check.',
    'maintenance_mode': 'Maintenance mode',
    'deodorant_finished': 'Deodorant finished',
    'periodic_odor_completed': 'Periodic odor removal completed',
    'manual_odor_completed': 'Manual odor removal completed',
    'auto_odor_terminated': 'Automatic odor removal has been terminated.',
    'periodic_odor_terminated': 'Periodic odor removal terminated.',
    'manual_odor_terminated': 'Manual odor removal terminated.',
    'auto_odor_failed': 'Automatic odor removal failed, odor eliminator error',
    'periodic_odor_failed': 'Periodic odor removal failure, odor eliminator malfunction',
    'manual_odor_failed': 'Manual odor removal failure, odor eliminator malfunction',
    'auto_odor_canceled': 'Automatic odor removal has been canceled, the device is running.',
    'periodic_odor_canceled': 'Periodic odor removal canceled. Litter Box is working.',
    'manual_odor_canceled': 'Manual odor removal canceled. Litter Box is working.',
    'auto_odor_failed_device': 'Automatic odor removal failed, no smart spray is connected.',
    'periodic_odor_failed_device': 'Periodic odor removal failed. Odor Removal Device disconnected.',
    'manual_odor_failed_device': 'Manual odor removal failed. Odor Removal Device disconnected.',
    'auto_odor_failed_batt': 'Automatic odor removal failed, please confirm that the battery of smart spray is sufficient.',
    'periodic_odor_failed_batt': 'Periodic odor removal failed. Please make sure the Odor Removal Device has sufficient battery.',
    'manual_odor_failed_batt': 'Manual odor removal failed. Please make sure the Odor Removal Device has sufficient battery.',
    'auto_odor_failed_low_batt': 'Automatic odor removal failed, battery is low.',
    'periodic_odor_failed_low_batt': 'Periodic odor removal failed. Odor Removal Device battery low.',
    'manual_odor_failed_low_batt': 'Manual odor removal failed. Odor Removal Device battery low.',
    'cat_stopped_odor': 'Your cat is using the litter box, deodorization has been canceled',
    'light_on': 'The light is ON',
    'light_already_on': 'The light is on. There is no need to turn on again.',
    'light_malfunc': 'Failing to turn on the light. Device malfunction, please check.',
    'light_no_device': 'Failing to turn on the light. Please bind the odor removal device first.',
    'light_batt_cap': 'Failing to turn on the light. Please check the battery capacity of the odor removal device.',
    'light_low_batt': 'Failing to turn on the light. Low battery capacity of odor removal device.'
}
