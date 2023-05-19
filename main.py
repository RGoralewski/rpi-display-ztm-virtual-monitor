#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import time
from waveshare_OLED import OLED_1in5
from PIL import Image, ImageDraw, ImageFont
import click
from datetime import datetime
from ztm_virtual_monitor_python_api import ZTMVirtualMonitorAPI
import pandas as pd


@click.command()
@click.option('-s', '--stop-code', type=str, required=True, help='Stop code in ZTM Poznan')
@click.option('-v', '--verbose', count=True, help='Logging level')
@click.option('-l', '--log', is_flag=True, default=False, help='Enable logging to file')
def main(stop_code, verbose, log):
    log_handlers = [logging.StreamHandler()]
    log_level = {0: logging.INFO, 1: logging.DEBUG}.get(verbose, logging.INFO)

    if log:
        log_handlers.append(
            logging.FileHandler(datetime.now().strftime(f"%Y-%m-%d-%H-%M-%S.log"))
        )

    logging.basicConfig(
        handlers=log_handlers,
        encoding='utf-8',
        level=log_level,
        format='%(asctime)s|%(levelname)s|%(name)s|%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    vm = ZTMVirtualMonitorAPI(stop_code)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(vm.generate_timetable(6))

    try:
        disp = OLED_1in5.OLED_1in5()

        logging.info("\r 1.5inch OLED ")
        disp.Init()

        logging.info("clear display")
        disp.clear()

        image1 = Image.new('L', (disp.width, disp.height), 0)
        draw = ImageDraw.Draw(image1)
        font = ImageFont.truetype('fonts/Font.ttc', 10)
        luminance = 5

        hour1 = '9:52'
        hour2 = '12:37'

        logging.info("draw text")
        draw.text((0, 0), 'BARANIAKA', font=font, fill=luminance)
        draw.line([(0, 12), (127, 12)], fill=luminance)

        draw.text((0, 24), '6 Junikowo', font=font, fill=luminance)
        hour_text_length = draw.textlength(hour1, font=font)
        draw.text((OLED_1in5.OLED_WIDTH-1-hour_text_length, 24), hour1, font=font, fill=luminance)

        draw.text((0, 36), '6 Junikowo', font=font, fill=luminance)
        hour_text_length = draw.textlength(hour2, font=font)
        draw.text((OLED_1in5.OLED_WIDTH-1-hour_text_length, 36), hour2, font=font, fill=luminance)

        image1 = image1.rotate(0)
        disp.ShowImage(disp.getbuffer(image1))
        time.sleep(60)

        disp.clear()

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt, exiting...")
        OLED_1in5.config.module_exit()


if __name__ == '__main__':
    main()
