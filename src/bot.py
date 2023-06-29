from telebot import asyncio_filters

import asyncio
from env import TOKEN
from env import FORWARD_CHAT
from env import question_1, question_2, question_3, question_4, question_5, question_practice
import emoji
from src.client import aclient
from src.timerAndQueue import timerAndQueue
from src.acknowledgementHelper import acknowledgementHelper

questionTimeLimitMessage = '\n\nYou have 5 minutes in total. Please submit a video of no longer than 2 minutes.'
warningMessage = emoji.emojize('\n\n:spiral_notepad: Ample time has been provided for you to think through your response, record and upload it. It is your responsibility to submit it on time.')

class Bot:
    def __init__(self):
        self.client = self.createClient()
        self.timerAndQueue:timerAndQueue = self.createTimer()
        self.client.addTimer(self.timerAndQueue)
        self.acknowledgementHelper = acknowledgementHelper(self.client)
        self.client.add_custom_filter(asyncio_filters.StateFilter(self.client))

    async def check_message_isVideo(self, message):
        messageType = message.content_type
        print('checking messagetype')
        return messageType in ['video', 'video_note']

    def createTimer(self):
        return timerAndQueue(self.client, self)

    @staticmethod
    def createClient():
        return aclient(TOKEN)

    async def pleaseSendVideo(self, message):
        msg = emoji.emojize(':red_exclamation_mark:Please do not send a response other than a video response to this question.')
        await self.client.reply_to(message, msg, parse_mode = "Markdown")

    async def processQuestionResponse(self, message, questionNumber):
        isVideo = await self.check_message_isVideo(message)
        if isVideo:
            await self.timerAndQueue.earlyTerminate(message.from_user.id, questionNumber)
            if questionNumber == 'practice':
                await self.client.delete_state(message.from_user.id, message.chat.id)
            await self.forwardMessageToHeadTA(message, questionNumber)
            return True
        else:
            await self.pleaseSendVideo(message)
            return False

    async def forwardMessageToHeadTA(self, message, questionNumber):
        if questionNumber == 'practice':
            name = message.from_user.username
        else:
            name = await self.acknowledgementHelper.getUserId(message.from_user.id)
        msg = f'Recorded a response from {name} for question: {questionNumber}'
        await self.client.send_message(FORWARD_CHAT, msg, parse_mode = "Markdown")
        await self.client.forward_message(FORWARD_CHAT, message.chat.id, message.message_id)

    async def startInterview(self, message, name):
        await self.sendAcknowledgeMessage(message, name)
        await self.sendQuestion_1(message)

    async def sendQuestionMessage(self, message, questionNumber):
        match questionNumber:
            case 1:
                msg = await self.sendQuestion_1(message)
            case 2:
                msg = await self.sendQuestion_2(message)
            case 3:
                msg = await self.sendQuestion_3(message)
            case 4:
                msg = await self.sendQuestion_4(message)
            case 5:
                msg = await self.sendQuestion_5(message)
            case 6:
                msg = await self.interview_over(message)
        await self.client.send_message(message.chat.id, msg, parse_mode = "Markdown")
        if questionNumber != 6:
            await self.client.timerAndQueue.mainFunction(message, questionNumber+1)

    async def sendQuestion_practice(self, message):
        await self.client.set_state(message.from_user.id, aclient.questionState_practice, message.chat.id)
        msg = emoji.emojize(':robot: Practice question :robot:' +
                            ':target:This is a practice question, you have 3 minutes to answer this question.\n' +
                            f'*{question_practice}*\n\n'+
                            'Your video should be no longer than 1 minute or it will be ignored for evaluation.'
                            + warningMessage)
        return msg

    async def sendQuestion_1(self, message):
        await self.client.set_state(message.from_user.id, aclient.questionState_1, message.chat.id)
        msg = f'The first question is:\n{question_1}{questionTimeLimitMessage}{warningMessage}'
        return msg

    async def sendQuestion_2(self, message):
        await self.client.set_state(message.from_user.id, aclient.questionState_2, message.chat.id)
        msg = f'The second question is:\n{question_2}{questionTimeLimitMessage}{warningMessage}'
        return msg

    async def sendQuestion_3(self, message):
        await self.client.set_state(message.from_user.id, aclient.questionState_3, message.chat.id)
        msg = f'The third question is:\n{question_3}{questionTimeLimitMessage}{warningMessage}'
        return msg

    async def sendQuestion_4(self, message):
        await self.client.set_state(message.from_user.id, aclient.questionState_4, message.chat.id)
        msg = f'The fourth question is:\n{question_4}{questionTimeLimitMessage}{warningMessage}'
        return msg

    async def sendQuestion_5(self, message):
        await self.client.set_state(message.from_user.id, aclient.questionState_5, message.chat.id)
        msg = f'The fifth question is:\n{question_5}{questionTimeLimitMessage}{warningMessage}'
        return msg
        
    async def interview_over(self, message):
        await self.client.set_state(message.from_user.id, aclient.questionState_over, message.chat.id)
        msg = 'Thank you for your time. Your interview is now over.'
        return msg

    async def sendAcknowledgeMessage(self, message, name):
        msg = emoji.emojize(f'Thank you for your acknowledgement {name}. Your interview will now begin')
        await self.client.reply_to(message, msg, parse_mode = "Markdown")

    async def sendAcknowledgementFailure(self, message):
        msg = emoji.emojize('Your acknowledgement key is invalid. Please try again if your key is suppose to be working, or contact @MarkyYeo if you think there is a mistake.')
        await self.client.reply_to(message, msg, parse_mode = "Markdown")