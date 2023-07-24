class Period:
    def __init__(self, slot, courseName, code, location, startTime, endTime):
        self.slot = slot
        self.courseName = courseName
        self.code = code
        self.location = location
        self.startTime = startTime
        self.endTime = endTime

    def __eq__(self, other):
        return self.slot == other.slot and self.code == other.code

    def __lt__(self, other):
        return self.startTime < other.startTime

    def to_dict(self):
        return {
            "slot": self.slot,
            "courseName": self.courseName,
            "code": self.code,
            "location": self.location,
            "startTime": self.startTime,
            "endTime": self.endTime
        }

    def __repr__(self) -> str:
        return str(self.to_dict())
