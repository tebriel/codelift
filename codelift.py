#!/usr/bin/env python3

import sys
import json
import coloredlogs
import logging
from building import Building

coloredlogs.install()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PLANS = ['training_1', 'training_2', 'training_3', 'ch_rnd_500_1']

if __name__ == '__main__':
    plan_id = 0
    if sys.argv[1] is not None:
        plan_id = int(sys.argv[1])

    with open('codeliftsettings.json') as settings:
        cl_settings = json.load(settings)

    building = Building(PLANS[plan_id], cl_settings)
    building.connect()
    building.start()
    logger.info("Finished plan: %s", PLANS[plan_id])
