import logging
import telebot
from telebot.async_telebot import AsyncTeleBot
from typing import Any, Awaitable, Callable, List, Optional, Union
from telebot import asyncio_helper
import asyncio
import traceback
from src.stateHelper import StateHelper
logger = logging.getLogger('whatever')

class aclient(AsyncTeleBot):

    def __init__(self, TOKEN) -> None:
        self.states = StateHelper()
        super().__init__(TOKEN, state_storage=self.states.getStateStorage())
        self.logger = telebot.logger
        telebot.logger.setLevel(logging.DEBUG)

    def addTimer(self, timer):
        self.timerHelper = timer

    async def infinity_polling(self, timeout: Optional[int]=20, skip_pending: Optional[bool]=False, request_timeout: Optional[int]=None,
            logger_level: Optional[int]=logging.ERROR, allowed_updates: Optional[List[str]]=None,
            restart_on_change: Optional[bool]=False, path_to_watch: Optional[str]=None, *args, **kwargs):
        if skip_pending:
            await self.skip_updates()
        self._polling = True

        if restart_on_change:
            self._setup_change_detector(path_to_watch)

        while self._polling:
            try:
                await self._process_polling(non_stop=True, timeout=timeout, request_timeout=request_timeout,
                             allowed_updates=allowed_updates, *args, **kwargs)  
            except Exception as e:
                if logger_level and logger_level >= logging.ERROR:
                    logger.error("Infinity polling exception: %s", str(e))
                if logger_level and logger_level >= logging.DEBUG:
                    logger.error("Exception traceback:\n%s", traceback.format_exc())
                await asyncio.sleep(3)
                continue
            if logger_level and logger_level >= logging.INFO:
                logger.error("Infinity polling: polling exited")
        if logger_level and logger_level >= logging.INFO:
            logger.error("Break infinity polling")

    async def _process_polling(self, non_stop: bool=False, interval: int=0, timeout: int=20,
            request_timeout: int=None, allowed_updates: Optional[List[str]]=None):

        if not non_stop:
            # show warning
            logger.warning("Setting non_stop to False will stop polling on API and system exceptions.")

        self._user = await self.get_me()
            
        logger.info('Starting your bot with username: [@%s]', self.user.username)

        self._polling = True

        try:
            while self._polling:
                try:
                    await self.timerHelper.pollQueue()
                    updates = await self.get_updates(offset=self.offset, allowed_updates=allowed_updates, timeout=timeout, request_timeout=request_timeout)
                    if updates:
                        self.offset = updates[-1].update_id + 1
                        asyncio.create_task(self.process_new_updates(updates)) # Seperate task for processing updates
                    if interval: await asyncio.sleep(interval)

                except KeyboardInterrupt:
                    return
                except asyncio.CancelledError:
                    return
                except asyncio_helper.RequestTimeout as e:
                    logger.error(str(e))
                    if non_stop:
                        await asyncio.sleep(2)
                        continue
                    else:
                        return
                except asyncio_helper.ApiException as e:
                    handled = False
                    if self.exception_handler:
                        self.exception_handler.handle(e)
                        handled = True

                    if not handled:
                        logger.error('Unhandled exception (full traceback for debug level): %s', str(e))
                        logger.debug(traceback.format_exc())

                    if non_stop or handled:
                        continue
                    else:
                        break
                except Exception as e:
                    handled = False
                    if self.exception_handler:
                        self.exception_handler.handle(e)
                        handled = True

                    if not handled:
                        logger.error('Unhandled exception (full traceback for debug level): %s', str(e))
                        logger.debug(traceback.format_exc())

                    if non_stop or handled:
                        continue
                    else:
                        break
        finally:
            self._polling = False
            await self.close_session()
            logger.warning('Polling is stopped.')