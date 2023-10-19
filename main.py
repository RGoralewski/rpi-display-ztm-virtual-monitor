#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import time
from waveshare_OLED import OLED_1in5
from PIL import Image, ImageDraw, ImageFont
import click
from datetime import datetime
from ztm_virtual_monitor_python_api import ZTMVirtualMonitorAPI
import math


@click.command()
@click.option('-s', '--stop-code', type=str, required=True, help='Stop code in ZTM Poznan')
@click.option('-r', '--refresh-time', type=int, required=True, help='Refresh time of the timetable (seconds)')
@click.option('-t', '--timetable-length', type=int, required=True,
              help='A number of rows in result dataframe with trips')
@click.option('-n', '--stop-name', type=str,
              help='Stop name that will be displayed on the top. If not given, the stop code will be displayed.')
@click.option('-v', '--verbose', count=True, help='Logging level')
@click.option('-l', '--log', is_flag=True, default=False, help='Enable logging to file')
def main(stop_code, refresh_time, timetable_length, stop_name, verbose, log):
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

    font = ImageFont.truetype('fonts/Font.ttc', 10)
    luminance = 5

    try:
        disp = OLED_1in5.OLED_1in5()

        logging.info("\r 1.5inch OLED ")
        disp.Init()

        logging.info("clear display")
        disp.clear()

        vm = ZTMVirtualMonitorAPI(stop_code)

        while True:

            current_timetable = vm.generate_timetable(timetable_length)

            current_time_hm = datetime.now().strftime('%H:%M')

            image1 = Image.new('L', (disp.width, disp.height), 0)
            draw = ImageDraw.Draw(image1)

            logging.info("draw text")
            draw.text((0, 0), stop_name if stop_name else stop_code, font=font, fill=luminance)
            hour_text_length = draw.textlength(current_time_hm, font=font)
            draw.text((OLED_1in5.OLED_WIDTH-1-hour_text_length, 0), current_time_hm, font=font, fill=luminance)
            draw.line([(0, 12), (127, 12)], fill=luminance)

            first_trip_offset = 24
            trip_line_height = 12
            trip_info_max_length = 16

            for i in range(0, len(current_timetable)):

                trip = current_timetable.iloc[i]

                arrival_time = trip['arrival_realtime']
                if not arrival_time or arrival_time > 0:
                    arrival_time = ':'.join(trip['arrival_time'].split(":")[:2])
                else:
                    minutes_to_arrive = math.ceil(abs(arrival_time) / 60)
                    arrival_time = f'<{minutes_to_arrive}min'

                t_info = f"{trip['route_id']} {trip['trip_headsign']}"
                t_info = (t_info[:trip_info_max_length-2] + '..') if len(t_info) > trip_info_max_length else t_info

                y_pos = first_trip_offset + trip_line_height * i
                draw.text((0, y_pos), t_info, font=font, fill=luminance)
                hour_text_length = draw.textlength(arrival_time, font=font)
                draw.text((OLED_1in5.OLED_WIDTH-1-hour_text_length, y_pos), arrival_time, font=font, fill=luminance)

            image1 = image1.rotate(180)

            time.sleep(refresh_time)

            disp.clear()
            disp.ShowImage(disp.getbuffer(image1))

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt, exiting...")
        OLED_1in5.config.module_exit()


if __name__ == '__main__':
    main()
