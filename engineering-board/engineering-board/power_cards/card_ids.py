class PowerCardIds:
    FUSION_ENGINES_ID = "fusion_engines"
    WARP_FIELD_ID = "warp_field"
    MAIN_COMPUTER_ID = "main_computer"
    FORE_SHIELDS_ID = "fore_shields"
    AFT_SHIELDS_ID = "aft_shields"
    PORT_SHIELDS_ID = "port_shields"
    STARBOARD_SHIELDS_ID = "starboard_shields"
    DORSAL_SHIELDS_ID = "dorsal_shields"
    VENTRAL_SHIELDS_ID = "ventral_shields"
    LASER_CANNON_ID = "laser_cannon"
    TRACTOR_BEAM_ID = "tractor_beam"
    STEALTH_FIELDS_ID = "stealth_fields"
    TARGETING_ID = "targeting"
    SIGNAL_JAMMER_ID = "signal_jammer"
    ALCUBIERRE_WARP_DRIVE_ID = "alcubierre_warp_drive"
    THRUSTERS_ID = "thrusters"
    NAVIGATION_ID = "navigation"
    EXTERNAL_SENSORS_ID = "external_sensors"
    INTERNAL_SENSORS_ID = "internal_sensors"
    LONG_RANGE_COMMS_ID = "long_range_comms"
    RADIO_COMMUNICATIONS_ID = "radio_communications"
    TRANSPORTERS_ID = "transporters"
    CO2_SCRUBBERS_ID = "co2_scrubbers"
    OXYGEN_GENERATORS_ID = "oxygen_generators"
    GRAVITY_FIELD_ID = "gravity_field"

    ALL_CARD_IDS = [
        FUSION_ENGINES_ID,
        WARP_FIELD_ID,
        MAIN_COMPUTER_ID,
        FORE_SHIELDS_ID,
        AFT_SHIELDS_ID,
        PORT_SHIELDS_ID,
        STARBOARD_SHIELDS_ID,
        DORSAL_SHIELDS_ID,
        VENTRAL_SHIELDS_ID,
        LASER_CANNON_ID,
        TRACTOR_BEAM_ID,
        STEALTH_FIELDS_ID,
        TARGETING_ID,
        SIGNAL_JAMMER_ID,
        ALCUBIERRE_WARP_DRIVE_ID,
        THRUSTERS_ID,
        NAVIGATION_ID,
        EXTERNAL_SENSORS_ID,
        INTERNAL_SENSORS_ID,
        LONG_RANGE_COMMS_ID,
        RADIO_COMMUNICATIONS_ID,
        TRANSPORTERS_ID,
        CO2_SCRUBBERS_ID,
        OXYGEN_GENERATORS_ID,
        GRAVITY_FIELD_ID,
    ]

    @classmethod
    def validate_id(cls, cardId):
        return cardId in PowerCardIds.ALL_CARD_IDS

    @classmethod
    def get_name(cls, cardId:str):
        if not PowerCardIds.validate_id(cardId):
            return None
        return cardId.replace("_", " ").title()