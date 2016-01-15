#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import gtk
import time
import appindicator

import httplib
import re

UPDATE_FREQ_IN_MINUTES = 15

APP_VERSION = "0.1.0"
APP_ID = "yandex-probki-indicator"

USER_AGENT = "{0}/{1} ({2})".format(
    APP_ID, APP_VERSION,
    "{0}/{1}".format("https://github.com/ekalinin", APP_ID))


class YaJamsIndicator:
    def __init__(self):
        self.ind = appindicator.Indicator(
            APP_ID, gtk.STOCK_INFO,
            appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.menu_setup()

    def menu_setup(self):
        self.menu = gtk.Menu()
        self.quit_item = gtk.MenuItem("Выход")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)
        self.ind.set_menu(self.menu)

    def quit(self, widget):
        sys.exit(0)

    def main(self):
        self.update_jams()
        gtk.timeout_add(UPDATE_FREQ_IN_MINUTES * 60 * 1000, self.update_jams)
        gtk.main()

    def get_icon_path(self, icon_filename):
        return os.path.abspath(os.path.join('icons', icon_filename))

    def update_jams(self):
        print ("{}: Updating jams ...".format(time.strftime("%d/%m %H:%M:%S")))
        lvl, lvl_txt = self.get_jam_velel()
        self.ind.set_label(lvl_txt)
        if lvl > 0 and lvl <= 3:
            self.ind.set_icon(self.get_icon_path('green.svg'))
        elif lvl > 3 and lvl < 7:
            self.ind.set_icon(self.get_icon_path('yellow.svg'))
        else:
            self.ind.set_icon(self.get_icon_path('red.svg'))
        return True

    def get_jam_velel(self):
        conn = httplib.HTTPSConnection("www.yandex.ru")
        conn.request("GET", "/", None, {"User-Agent": USER_AGENT})
        resp = conn.getresponse().read()
        conn.close()

        p = re.compile('\d{1,2} бал[\S]*</a')
        res = p.findall(resp)
        if len(res) == 0:
            return (-1, "")
        else:
            txt = res[0].replace('</a', '')
            lvl = int(txt[:2])
            return (lvl, txt)


if __name__ == "__main__":
    indicator = YaJamsIndicator()
    indicator.main()
