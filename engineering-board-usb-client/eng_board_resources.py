class ClientType:
    NoneType = 0
    EngineeringBoard = 1


class EngBoardResource:
    def __init__(self, name):
        self.name = name


class EnginePower(EngBoardResource):
    @staticmethod
    def from_json(json_blob: dict) -> "EnginePower":
        return EnginePower(
            json_blob["Name"], json_blob["MaxPower"], json_blob["PowerUsage"]
        )

    @staticmethod
    def to_json(engine_power: "EnginePower") -> dict:
        return {
            "Name": engine_power.name,
            "MaxPower": engine_power.max_power,
            "PowerUsage": engine_power.power_usage,
        }

    def __init__(self, name, max_power, power_usage):
        super().__init__(name)
        self.max_power = max_power
        self.power_usage = power_usage


class TransformerPower(EngBoardResource):
    @staticmethod
    def from_json(json_blob: dict) -> "TransformerPower":
        return EnginePower(
            json_blob["Name"], json_blob["MaxPower"], json_blob["PowerUsage"]
        )

    @staticmethod
    def to_json(transformer_power: "TransformerPower") -> dict:
        return {
            "Name": transformer_power.name,
            "MaxPower": transformer_power.max_power,
            "PowerUsage": transformer_power.power_usage,
        }

    def __init__(self, name, max_power, power_usage):
        super().__init__(name)
        self.max_power = max_power
        self.power_usage = power_usage


class SystemPower(EngBoardResource):
    @staticmethod
    def from_json(json_blob: dict) -> "SystemPower":
        return SystemPower(
            json_blob["Name"], json_blob["Power"], json_blob["CardCount"]
        )

    @staticmethod
    def to_json(system_power: "SystemPower") -> dict:
        return {
            "Name": system_power.name,
            "Power": system_power.power,
            "CardCount": system_power.card_count,
        }

    def __init__(self, name, power, card_count):
        super().__init__(name)
        self.power = power
        self.card_count = card_count
