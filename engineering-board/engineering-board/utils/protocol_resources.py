import json

# Resource Names
LEFT_WING = "LeftWing"
RIGHT_WING = "RightWing"
TRANS1 = "Transformer1"
TRANS2 = "Transformer2"
TRANS3 = "Transformer3"
TRANS4 = "Transformer4"
MAX_DISPLAY = "_Max"
CUR_DISPLAY = "_Cur"


def json_string(data):
    if isinstance(data, list):
        return "[ " + ", ".join([json_string(json_el) for json_el in data]) + " ]"
    return json.dumps(data.__dict__)


class EngBoardResource(object):
    def __init__(self, Name) -> None:
        self.Name = Name


class EnginePower(EngBoardResource):
    @classmethod
    def from_json_dict(cls, json_dict):
        return EnginePower(**json_dict)

    def __init__(self, Name, MaxPower, PowerUsage) -> None:
        EngBoardResource.__init__(self, Name)
        self.MaxPower = MaxPower
        self.PowerUsage = PowerUsage

    def __str__(self):
        return f"{self.Name}, Max:{self.MaxPower}, Usage:{self.PowerUsage}"


class TransformerPower(EngBoardResource):
    @classmethod
    def from_json_dict(cls, json_dict):
        return TransformerPower(**json_dict)

    def __init__(self, Name, MaxPower, PowerUsage) -> None:
        EngBoardResource.__init__(self, Name)
        self.MaxPower = MaxPower
        self.PowerUsage = PowerUsage

    def __str__(self):
        return f"{self.Name}, Max:{self.MaxPower}, Usage:{self.PowerUsage}"


class SystemPower(EngBoardResource):
    @classmethod
    def from_json_dict(cls, json_dict):
        return SystemPower(**json_dict)

    def __init__(self, Name, Power, CardCount) -> None:
        EngBoardResource.__init__(self, Name)
        self.Power = Power
        self.CardCount = CardCount

    def __str__(self):
        return f"{self.Name}, Power:{self.Power}, CardCount:{self.CardCount}"
