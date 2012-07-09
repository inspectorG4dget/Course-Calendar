# Scrapy settings for regcal project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'regcal'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['regcal.spiders']
NEWSPIDER_MODULE = 'regcal.spiders'
DEFAULT_ITEM_CLASS = 'regcal.items.RegcalItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

