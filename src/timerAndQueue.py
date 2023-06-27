import copy
import emoji
import logging
import time
from datetime import timedelta as td

class timerAndQueue:
    def __init__(self, client, bot, timeLimit=300):
        self.client = client
        self.bot = bot
        self.timerQueue = {}
        self.timeLimit = timeLimit 

    async def mainFunction(self, message, nextQuestionNumber):
        start_time = time.time()
        logging.info(f"{message.from_user.full_name} started question 1 at {start_time}")
        await self.addToTimerQueue(message, start_time, nextQuestionNumber)

    async def addToTimerQueue(self, message, startTime, nextQuestionNumber):
        chat_id = message.chat.id
        timerMessage = await self.sendTimerMessage(chat_id)
        self.timerQueue[(message.from_user.id, message.chat.id)] = {'time': startTime,
                                   'remindOneMinute': False,
                                   'chat_id': chat_id,
                                   'message_id': timerMessage.id,
                                   'nextQuestionNumber': nextQuestionNumber,
                                   'message': message}

    async def sendTimerMessage(self, chat_id):
        message = await self.client.send_message(chat_id, self.formatTime(self.timeLimit))
        return message
    
    async def pollQueue(self):
        print(self.timerQueue)
        timerQueue = copy.deepcopy(self.timerQueue)
        for k,v in timerQueue.items():
            await self.checkTime(k, v)

    async def checkTime(self, user_id, value):
        currentTime = time.time()
        questionStartTime = value['time']
        chat_id = value['chat_id']
        message_id = value['message_id']
        isOneMinuteLeft = value['remindOneMinute']

        if questionStartTime + self.timeLimit < currentTime + 60 and isOneMinuteLeft == False:
            await self.remindOneMinuteLeft(user_id)
        if questionStartTime + self.timeLimit < currentTime:
            await self.deleteTimer(user_id, value)
        else:
            newTimeLeft = questionStartTime + self.timeLimit - currentTime
            await self.updateTimer(newTimeLeft, chat_id, message_id, isOneMinuteLeft)
        
    async def timesUpGoToNextState(self, user_id, value):
        nextQuestionNumber = value['nextQuestionNumber']
        nextState = await self.client.getQuestionState(nextQuestionNumber)
        await self.client.set_state(user_id[0], nextState, value['chat_id'])
        await self.bot.sendQuestionMessage(value['message'], value['nextQuestionNumber'])

    async def deleteTimer(self, user_id, value):
        del self.timerQueue[user_id]
        msg = emoji.emojize(f':timer_clock::red_exclamation_mark: Time\'s up for question {value["nextQuestionNumber"]-1}! :red_exclamation_mark::timer_clock:')
        await self.client.edit_message_text(msg, value['chat_id'], value['message_id'])
        await self.timesUpGoToNextState(user_id, value)

    async def remindOneMinuteLeft(self, user_id):
        self.timerQueue[user_id]['remindOneMinute'] = True
        # await self.client.send_message(value['chat_id'], msg)
        
    async def updateTimer(self, newTimeLeft, chat_id, message_id, isOneMinuteLeft):
        formattedTime = self.formatTime(newTimeLeft)
        if isOneMinuteLeft:
            msg = emoji.emojize(':timer_clock::red_exclamation_mark: You less than 1 minute left :red_exclamation_mark::timer_clock:\n'+
                                formattedTime)
        else:
            msg = formattedTime
        await self.client.edit_message_text(msg, chat_id, message_id)

    async def earlyTerminate(self, user_id, questionNumber):
        chats = list(filter(lambda x: x[0] == user_id, self.timerQueue.keys()))
        chat_id = self.timerQueue[chats[0]]['chat_id']
        message_id = self.timerQueue[chats[0]]['message_id']
        if questionNumber == 'practice':
            msg = 'You have submitted a practice response. To try again, use `/practice`'
        else:
            msg = f'We have received your response for question {questionNumber}.'
        await self.client.send_message(chat_id, msg, parse_mode='Markdown')
        await self.client.edit_message_text(emoji.emojize(f':check_mark_button: Submitted question {questionNumber}!'), chat_id, message_id)
        del self.timerQueue[chats[0]]

    @staticmethod
    def formatTime(time):
        if type(time) == str:
            time = float(time)
        formattedTime = str(td(seconds=time))[2:7]
        return formattedTime