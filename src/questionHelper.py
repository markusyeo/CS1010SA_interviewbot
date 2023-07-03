from env import question_1, question_2, question_3, question_4, question_5, question_practice
from env import question_1_time, question_2_time, question_3_time, question_4_time, question_5_time, question_practice_time, interview_over_message
from env import question_1_video_time, question_2_video_time, question_3_video_time, question_4_video_time, question_5_video_time, question_practice_video_time
import emoji
from src.stateHelper import StateHelper

warningMessage = emoji.emojize('\n\n:spiral_notepad: Ample time has been provided for you to think through your response, record and upload it. It is your responsibility to submit it on time.')

class QuestionHelper:
    @classmethod
    async def getQuestiontimeLimitMessage(cls, questionNumber):
        totalTime, videoTime = await cls.getQuestionTimes(questionNumber)
        questionTimeLimitMessage = f'\n\nYou have {totalTime} minutes in total. Please submit a video of no longer than {videoTime} minutes.'
        return questionTimeLimitMessage
    
    @staticmethod
    async def getQuestionTimes(questionNumber):
        match questionNumber:
            case 'practice':
                return question_practice_time, question_practice_video_time
            case 1:
                return question_1_time, question_1_video_time
            case 2:
                return question_2_time, question_2_video_time
            case 3:
                return question_3_time, question_3_video_time
            case 4:
                return question_4_time, question_4_video_time
            case 5:
                return question_5_time, question_5_video_time
            
    @classmethod
    async def getQuestionMessage(cls, client, message, questionNumber):
        match questionNumber:
            case 'practice':
                msg = await cls.getQuestion_practice(client, message)
            case 1:
                msg = await cls.getQuestion_1(client, message)
            case 2:
                msg = await cls.getQuestion_2(client, message)
            case 3:
                msg = await cls.getQuestion_3(client, message)
            case 4:
                msg = await cls.getQuestion_4(client, message)
            case 5:
                msg = await cls.getQuestion_5(client, message)
            case 6:
                msg = await cls.interview_over(client, message)
            case _:
                msg = ''
        return msg
    
    @classmethod
    async def getQuestion_practice(cls, client, message):
        await client.set_state(message.from_user.id, StateHelper.questionState_practice, message.chat.id)
        questionTimeLimitMessage = await cls.getQuestiontimeLimitMessage('practice')
        msg = emoji.emojize(':robot::bullseye:Practice question :robot:\n')
        msg += f'{question_practice}{questionTimeLimitMessage}{warningMessage}'
        return msg

    @classmethod
    async def getQuestion_1(cls, client, message):
        await client.set_state(message.from_user.id, StateHelper.questionState_1, message.chat.id)
        questionTimeLimitMessage = await cls.getQuestiontimeLimitMessage(1)
        msg = f'The first question is:\n{question_1}{questionTimeLimitMessage}{warningMessage}'
        return msg

    @classmethod
    async def getQuestion_2(cls, client, message):
        await client.set_state(message.from_user.id, StateHelper.questionState_2, message.chat.id)
        questionTimeLimitMessage = await cls.getQuestiontimeLimitMessage(2)
        msg = f'The second question is:\n{question_2}{questionTimeLimitMessage}{warningMessage}'
        return msg

    @classmethod
    async def getQuestion_3(cls, client, message):
        await client.set_state(message.from_user.id, StateHelper.questionState_3, message.chat.id)
        questionTimeLimitMessage = await cls.getQuestiontimeLimitMessage(3)
        msg = f'The third question is:\n{question_3}{questionTimeLimitMessage}{warningMessage}'
        return msg

    @classmethod
    async def getQuestion_4(cls, client, message):
        await client.set_state(message.from_user.id, StateHelper.questionState_4, message.chat.id)
        questionTimeLimitMessage = await cls.getQuestiontimeLimitMessage(4)
        msg = f'The fourth question is:\n{question_4}{questionTimeLimitMessage}{warningMessage}'
        return msg

    @classmethod
    async def getQuestion_5(cls, client, message):
        await client.set_state(message.from_user.id, StateHelper.questionState_5, message.chat.id)
        questionTimeLimitMessage = await cls.getQuestiontimeLimitMessage(5)
        msg = f'The fifth question is:\n{question_5}{questionTimeLimitMessage}{warningMessage}'
        return msg

    @classmethod
    async def interview_over(cls, client, message):
        await client.set_state(message.from_user.id, StateHelper.questionState_over, message.chat.id)
        msg = interview_over_message
        return msg