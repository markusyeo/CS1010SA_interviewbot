import emoji
from env import HEADTA
import asyncio
from src.bot import Bot
from src.questionHelper import QuestionHelper
from src.stateHelper import StateHelper

warningMessage = emoji.emojize('\n\n:spiral_notepad: Ample time has been provided for you to think through your response, record and upload it. It is your responsibility to submit it on time.')

def run_tele_bot(bot: Bot):

    @bot.client.message_handler(commands=['poll'])
    async def poll(message):
        await bot.client.timerHelper.pollQueue()

    @bot.client.message_handler(commands=['start'])
    async def start_message(message):
        start_msg = emoji.emojize(f'''
:robot: Welcome to CS1010S/A New Tutor interview!
Please read the following instructions and acknowledge them before beginning your intereview.
- You might want to have a second device to record your video and upload it to the bot, so you are able to see the questions and the time left.
- You should not use a telebubble, but upload a video from your phone or computer.
- The time for each question will include thinking time as well as answering time and some buffer to upload your attempt.
- When you have only 1 minute more than the video time limit, you will receive a warning message to start recording your video, it is your responsibility to start recording early in order to submit your video on time.
- If you fail to submit a video after the time limit, you will have forefeited that question.\n
- You will be given 5 questions in total, and you should ensure that you have at least 30 minutes free to answer all the questions in 1 sitting.
- Please manage your time wisely, and ensure that you have a suitable internet connection.
If you are unable to complete the interview now, please come back another time and acknowledge the instructions again.\n
You may choose to practice using the bot and get used to the interface by typing `/practice`. You may do this as many times as you like.\n
*By acknowledging the instructions, you begin your interview process.*
Type `/acknowledge <Your unique interview code>` to activate your interview session.\n
- If you have any issues or concerns, please contact @MarkyYeo.
''')                              
        await bot.client.reply_to(message, start_msg, parse_mode = "Markdown")

    @bot.client.message_handler(commands=['help'])
    async def help(message):
        await bot.client.reply_to(message, 
                            emoji.emojize(':information:Help section\n' +
                            '- /start to read the instructions for the interview\n' + 
                            '- /practice to practice answering a question\n' +
                            '- /acknowledge <Your unique interview code> to start your interview\n' +
                            '- /help to see this message again\n' +
                            '- contact @MarkyYeo for any questions or issues you run into'),
                                        parse_mode = "Markdown")
        bot.client.logger.info(
            "\x1b[31mSomeone needs help!\x1b[0m")

    #########################
    ## Interview Questions ##
    #########################
    @bot.client.message_handler(state=StateHelper.questionState_1, content_types=['video', 'document'])
    async def questionReply(message):
        isVideo = await bot.processQuestionResponse(message, 1)
        if isVideo:
            await bot.sendQuestionMessage(message, 2)

    @bot.client.message_handler(state=StateHelper.questionState_2, content_types=['video', 'document'])
    async def questionReply(message):
        isVideo = await bot.processQuestionResponse(message, 2)
        if isVideo:
            await bot.sendQuestionMessage(message, 3)

    @bot.client.message_handler(state=StateHelper.questionState_3, content_types=['video', 'document'])
    async def questionReply(message):
        isVideo = await bot.processQuestionResponse(message, 3)
        if isVideo:
            await bot.sendQuestionMessage(message, 4)

    @bot.client.message_handler(state=StateHelper.questionState_4, content_types=['video', 'document'])
    async def questionReply(message):
        isVideo = await bot.processQuestionResponse(message, 4)
        if isVideo:
            await bot.sendQuestionMessage(message, 5)

    @bot.client.message_handler(state=StateHelper.questionState_5, content_types=['video', 'document'])
    async def questionReply(message):
        isVideo = await bot.processQuestionResponse(message, 5)
        if isVideo:
            await bot.sendQuestionMessage(message, 6)

    ##############################################################
    # Haizz just duplicate for now till i find a better solution #
    ##############################################################
    @bot.client.message_handler(state=StateHelper.questionState_1, func=lambda x: x.content_type not in ['video'])
    async def questionReply(message):
        await bot.processQuestionResponse(message, 1)

    @bot.client.message_handler(state=StateHelper.questionState_2, func=lambda x: x.content_type not in ['video'])
    async def question2Reply(message):
        await bot.processQuestionResponse(message, 2)

    @bot.client.message_handler(state=StateHelper.questionState_3, func=lambda x: x.content_type not in ['video'])
    async def question3Reply(message):
        await bot.processQuestionResponse(message, 3)

    @bot.client.message_handler(state=StateHelper.questionState_4, func=lambda x: x.content_type not in ['video'])
    async def question4Reply(message):
        await bot.processQuestionResponse(message, 4)

    @bot.client.message_handler(state=StateHelper.questionState_5, func=lambda x: x.content_type not in ['video'])
    async def question5Reply(message):
        await bot.processQuestionResponse(message, 5)
    
    #########################
    ## Acknowledge Portion ##
    #########################
    @bot.client.message_handler(commands=['acknowledge'])
    async def acknowledge_command(message):
        # Extract the user input
        try:
            user_input = message.text.split('/acknowledge ')[1]
        except:
            await bot.sendAcknowledgementFormat(message)
            return
        # Process the user input
        # You can perform any logic or actions with the user input here
        # For example, you can send a response to the user
        name, isValid = await bot.acknowledgementHelper.check_key(user_input)
        if isValid:
            await bot.acknowledgementHelper.registerUserId(user_input, message.from_user.id)
            await bot.sendAcknowledgeMessage(message, name)
            await bot.sendQuestionMessage(message, 1)
        else:
            await bot.sendAcknowledgementFailure(message)

    ######################
    ### Handle buttons ###
    ######################

    # TODO add some buttons for easy navigability

    # @bot.client.callback_query_handler(func=lambda call: True)
    # def handle_buttons(call):
    #     if call.data == 'helpbutton': 

    #######################
    ## Practice Question ##
    #######################

    @bot.client.message_handler(commands=['practice'])
    async def start_practice(message):
        msg = await QuestionHelper.getQuestionMessage(bot.client, message, 'practice')
        await bot.client.reply_to(message, msg, parse_mode = "Markdown")
        await bot.client.timerHelper.mainFunction(message, 'practice')

    # Recurring Practice qeustion
    # I would like a feature where the use is able to practice
    # and get used to the bot before starting the actual interview, this way the user would be comfortable
    @bot.client.message_handler(state=StateHelper.questionState_practice, content_types=['video', 'document'])
    async def getQuestionPracticeQuestionReply(message):
        await bot.processQuestionResponse(message, 'practice')

    # Just duplicating it for non video related due to some funky behaviour
    # of the library
    @bot.client.message_handler(state=StateHelper.questionState_practice)
    async def getQuestionPracticeQuestionReply(message):
        await bot.processQuestionResponse(message, 'practice')

    ######################
    #### Admin Stuff #####
    ######################
    @bot.client.message_handler(func=lambda message: message.from_user.id == HEADTA, commands=['add_key'])
    async def add_key(message):
        # Extract the user input
        user_input = message.text.split('/add_key\n')[1]
        listOfKeys = user_input.split('\n')
        for nameAndKey in listOfKeys:
            name, key = nameAndKey.split('/')
            hashedKey = bot.acknowledgementHelper.generate_keys(name, key)
            if not hashedKey:
                msg = emoji.emojize(f'Key already exists for {name}, {key}')
            else:
                msg = emoji.emojize(f'Key added for {name}. Key is {hashedKey}')
            await bot.client.send_message(message.chat.id, msg, parse_mode = "Markdown")

    @bot.client.message_handler(func=lambda message: message.from_user.id == HEADTA, commands=['get_keys'])
    async def get_keys(message):
        # Extract the user input
        msg = await bot.acknowledgementHelper.get_keys()
        await bot.client.reply_to(message, msg, parse_mode = "Markdown")

    @bot.client.message_handler(func=lambda message: message.from_user.id == HEADTA, commands=['delete_key'])
    async def delete_key(message):
        user_input = message.text.split('/delete_key\n')[1]
        listOfKeys = user_input.split('\n')
        for key in listOfKeys:
            isDeleted = await bot.acknowledgementHelper.delete_key(key)
            if isDeleted:
                msg = emoji.emojize(f'Key ({key}) deleted')
            else:
                msg = emoji.emojize(f'Key ({key}) does not exist')
            await bot.client.send_message(message.chat.id, msg, parse_mode = "Markdown")

    asyncio.run(bot.client.infinity_polling(timeout = 0.1))
    # asyncio.run(client.run_webhooks(listen='127.0.0.1'))
