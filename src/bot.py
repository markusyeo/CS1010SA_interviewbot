from telebot import asyncio_filters

import asyncio
from env import TOKEN
from env import FORWARD_CHAT, PRACTICE_LOGS
import emoji
from src.client import aclient
from src.timerAndQueue import timerAndQueue
from src.acknowledgementHelper import AcknowledgementHelper
from src.questionHelper import QuestionHelper

questionTimeLimitMessage = '\n\nYou have 5 minutes in total. Please submit a video of no longer than 2 minutes.'
warningMessage = emoji.emojize('\n\n:spiral_notepad: Ample time has been provided for you to think through your response, record and upload it. It is your responsibility to submit it on time.')

class Bot:
    def __init__(self):
        self.client = self.createClient()
        self.timerAndQueue:timerAndQueue = self.createTimer()
        self.client.addTimer(self.timerAndQueue)
        self.acknowledgementHelper = AcknowledgementHelper(self.client)
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
            await self.forwardMessageToLogs(message, questionNumber)
            return True
        else:
            await self.pleaseSendVideo(message)
            return False
        
    async def deleteState(self, user_id, chat_id):
        await self.client.delete_state(user_id, chat_id)

    async def forwardMessageToLogs(self, message, questionNumber):
        if questionNumber == 'practice':
            name = message.from_user.username
            chat_id = PRACTICE_LOGS
        else:
            name = await self.acknowledgementHelper.getName(message.from_user.id)
            chat_id = FORWARD_CHAT
        msg = f'Recorded a response from {name} for question: {questionNumber}'
        await self.client.send_message(chat_id, msg, parse_mode = "Markdown")
        await self.client.forward_message(chat_id, message.chat.id, message.message_id)

    async def sendQuestionMessage(self, message, questionNumber, name=None):
        msg = await QuestionHelper.getQuestionMessage(self.client, message, questionNumber)
        await self.client.send_message(message.chat.id, msg, parse_mode = "Markdown")
        if questionNumber != 6:
            await self.client.timerAndQueue.mainFunction(message, questionNumber)

    async def sendAcknowledgeMessage(self, message, name):
        msg = emoji.emojize(f'Thank you for your acknowledgement {name}. Your interview will now begin')
        await self.client.reply_to(message, msg, parse_mode = "Markdown")

    async def sendAcknowledgementFailure(self, message):
        msg = emoji.emojize('Your acknowledgement key is invalid. Please try again if your key is suppose to be working, or contact @MarkyYeo if you think there is a mistake.')
        await self.client.reply_to(message, msg, parse_mode = "Markdown")

    async def sendAcknowledgementFormat(self, message):
        msg = emoji.emojize('Please send your acknowledgement key in the following format: /acknowledge <key>')
        await self.client.reply_to(message, msg, parse_mode = "Markdown")