import logging
import re

# noinspection PyPackageRequirements
from telegram.ext import CommandHandler, CallbackQueryHandler

from bot import qb
from bot import updater
from utils import u
from utils import Permissions
from utils import kb

logger = logging.getLogger(__name__)

PRESETS = [10, 50, 100, 200]


@u.check_permissions(required_permission=Permissions.EDIT)
@u.failwithmessage
def change_alternative_limits(_, update, args):
    logger.info('/altdown or /altup from %s', update.message.from_user.first_name)

    if re.search(r'^[!/]altdown$', update.message.text, re.I):
        logger.info('/altdown: showing alternative download speed limits presets')

        reply_markup = kb.alternative_download_limits(PRESETS)
        update.message.reply_markdown('Select the alternative download speed', reply_markup=reply_markup)

        return

    preferences_to_edit = dict()

    preference_key = 'alt_dl_limit'
    if update.message.text.lower().startswith('/altup'):
        preference_key = 'alt_up_limit'

    kbs: str = args[0]
    if not kbs.isdigit():
        update.message.reply_text('Please pass the alternative speed limit in kb/s, as an integer')
        return

    preferences_to_edit[preference_key] = int(kbs) * 1014
    qb.set_preferences(**preferences_to_edit)

    update.message.reply_markdown('`{}` set to {} kb/s'.format(preference_key, kbs))


@u.check_permissions(required_permission=Permissions.READ)
@u.failwithmessage
def altdown_speed_callback(_, update, groups):
    logger.info('remove buttons inline button')

    speed_kbs = int(groups[0]) * 1024
    preferences_to_edit = dict()
    preference_key = 'alt_dl_limit'

    preferences_to_edit[preference_key] = speed_kbs
    qb.set_preferences(**preferences_to_edit)

    update.callback_query.answer('Alternative dl speed set to {} kb/s'.format(speed_kbs))


updater.add_handler(CommandHandler(['altdown', 'altup'], change_alternative_limits, pass_args=True))
updater.add_handler(CallbackQueryHandler(altdown_speed_callback, pattern=r'^altdown:(\d+)$', pass_groups=True))
