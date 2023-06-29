from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.asyncio_storage import StateMemoryStorage

class StateHelper(StatesGroup):
    acknowledgementState = State()
    questionState_practice = State()
    questionState_1 = State()
    questionState_2 = State()
    questionState_3 = State()
    questionState_4 = State()
    questionState_5 = State()
    questionState_over = State()

    def __init__(self):
        self.stateStorage = StateMemoryStorage()

    def getStateStorage(self):
        return self.stateStorage

    @classmethod
    async def getQuestionState(cls, questionNumber):
        match questionNumber:
            case 'practice':
                return cls.questionState_practice
            case 1:
                return cls.questionState_1
            case 2:
                return cls.questionState_2
            case 3:
                return cls.questionState_3
            case 4:
                return cls.questionState_4
            case 5:
                return cls.questionState_5
            case 6:
                return cls.questionState_over