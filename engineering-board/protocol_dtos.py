class ReaderColorDto(object):
    @classmethod
    def from_json_dict(cls, json_dict):
        return ReaderColorDto(**json_dict)

    def __init__(self, ReaderIndex, R, G, B) -> None:
        self.ReaderIndex = ReaderIndex
        self.R = R
        self.G = G
        self.B = B

class PowerDisplayDto(object):
    @classmethod
    def from_json_dict(cls, json_dict):
        return PowerDisplayDto(**json_dict)

    def __init__(self, DisplayIndex, Value) -> None:
        self.DisplayIndex = DisplayIndex
        self.Value = Value


class PowerGridDto(object):
    @classmethod
    def from_json_dict(cls, json_dict):
        return PowerGridDto(**json_dict)

    def __init__(self, GridIndex: int, MaxLevel: int, CurLevel: int, WarnMode: bool, DeadMode: bool) -> None:
        self.GridIndex = GridIndex
        self.MaxLevel = MaxLevel
        self.CurLevel = CurLevel
        self.WarnMode = WarnMode
        self.DeadMode = DeadMode
