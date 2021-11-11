#!/usr/bin/env python3

from configparser import ConfigParser
from xdg import xdg_config_home, xdg_cache_home
from tkinter import *
from openweather import OneCallClient, ImageManager
from time import sleep
from threading import Thread

class WeatherPanel(Tk):
    """The main application."""
    ICON_SCALE_LARGE = 4
    ICON_SCALE_NORMAL = 2

    BACKGROUND = "#002b36"

    TEXT_PRIMARY_KWARGS = { "font" : ("ProFontIIx Nerd Font Mono", 13, "bold"), "fill" : "#839496" }
    TEXT_SECONDARY_KWARGS = { "font" : ("ProFontIIx Nerd Font Mono", 10), "fill" : "#586e75" }

    def __init__(self, client, image_manager):
        Tk.__init__(self)
        self.title("Weather TK")
        
        #create canvas
        self.canvas = Canvas(self, background=self.BACKGROUND)
        self.canvas.config(highlightthickness=0) # this removes the widgets border
        self.canvas.pack(side="left", expand="yes", fill="both")

        self.client = client
        self.image_manager = image_manager

        self.current_cache = None
        self.daily_cache = None

    def mainloop(self):
        Thread(target=self.worker).start()
        Tk.mainloop(self)

    def worker(self):
        """This method is meant to be ran as its own thread.

        Weather data is downloaded and the display is updated on an aproximately 30 minute loop."""
        while True:
            self.download(self.client.download)
            self.current_cache = self.client.current()
            self.daily_cache = [ f for f in self.client.daily()]

            self.download_icons()

            self.clear()
            self.update_current()
            self.update_daily()
            self.update_timestamp()

            sleep(1800)

    def clear(self):
        self.canvas.delete("all")

    def download(self, downloader, *args, **kwargs):
        """A download helper.

        This method loops until the downloader returns a status code of 200.
        Parameters
        ----------
        downloader : callable
            An object that returns a status code on exit.
        args : *
            arguments to pass to the downloader.
        kwargs : **
            keyword arguments to pass to the downloader.
        """
        while downloader(*args, **kwargs) != 200:
            sleep(3)

    def download_icons(self):
        """Download the missing icons for the current weather data."""
        name = self.current_cache.icon_name()
        size = self.ICON_SCALE_LARGE
        downloader = self.image_manager.download
        if not self.image_manager.exists(name, size):
            self.download(downloader, name, size)
        size = self.ICON_SCALE_NORMAL
        for f in self.daily_cache:
            name = f.icon_name()
            if not self.image_manager.exists(name, size):
                self.download(downloader, name, size)

    def load_icon(self, forecast, size=None):
        """Load the icon for the forecast.

        Parameters
        ----------
        forecast : openweather.BaseForecastObject
            some forecast.
        size : int (default=None)
            The size of the icon to download.
        """
        name = forecast.icon_name()
        path = self.image_manager.fullpath(name, size)
        forecast.icon = PhotoImage(file=path) #this object needs to avoid GC, so here is its new owner

    def update_current(self):
        """Update the current weather display."""
        xoffset = 150
        yoffset =  70
        self.load_icon(self.current_cache, self.ICON_SCALE_LARGE)
        self.canvas.create_image(xoffset, yoffset, anchor="center", image=self.current_cache.icon)
        desc = self.current_cache.description().capitalize()
        temp = f"{round(self.current_cache.temperature()[0], 2)}°F"
        feel = f"feels like {round(self.current_cache.feels_like()[0], 2)}°F"
        hum  = f"humidity at {self.current_cache.humidity()}%"
        wind = f"winds at {self.current_cache.wind()[0]} MpH"
        gust = f"gusts at {self.current_cache.wind()[1]} MpH"
        self.canvas.create_text(xoffset, yoffset+70, text=desc, anchor="center", **self.TEXT_PRIMARY_KWARGS)
        self.canvas.create_text(xoffset, yoffset+90, text=temp, anchor="center", **self.TEXT_PRIMARY_KWARGS)
        self.canvas.create_text(xoffset, yoffset+110, text=feel, anchor="center", **self.TEXT_SECONDARY_KWARGS)
        self.canvas.create_text(xoffset, yoffset+122, text=hum, anchor="center", **self.TEXT_SECONDARY_KWARGS)
        self.canvas.create_text(xoffset, yoffset+134, text=wind, anchor="center", **self.TEXT_SECONDARY_KWARGS)
        self.canvas.create_text(xoffset, yoffset+146, text=gust, anchor="center", **self.TEXT_SECONDARY_KWARGS)

    def update_daily(self):
        """Update the daily forecasts."""
        xoffset = 300
        yoffset = 240
        ystep   = 100
        for i, f in enumerate(self.daily_cache):
            self.load_icon(f, self.ICON_SCALE_NORMAL)
            self.canvas.create_image(xoffset, yoffset, anchor="ne", image=f.icon)
            if i == 0:
                title = "Today"
            elif i == 1:
                title = "Tomorrow"
            else:
                title = f.datetime().strftime("%A")
            self.canvas.create_text(15, yoffset+15, text=title, anchor="nw", **self.TEXT_PRIMARY_KWARGS)
            desc = f.description().capitalize()
            temp_list = f.temperature()
            feel_list = f.feels_like()
            temp = f"{round(temp_list[0])}°F - {round(temp_list[1])}°F"
            feel = f"feels like {round(feel_list[0])}°F - {round(feel_list[1])}°F"
            info = f"{desc}\n{temp}\n{feel}"
            self.canvas.create_text(15, yoffset+32, text=info, anchor="nw", **self.TEXT_SECONDARY_KWARGS)
            yoffset += ystep

    def update_timestamp(self):
        """Update the 'last updated' timestamp."""
        text = self.current_cache.datetime().strftime("Last updated at %T on %D")
        self.canvas.create_text(5, 1055, text=text, anchor="nw", **self.TEXT_SECONDARY_KWARGS)

if __name__ == "__main__":
    cache_dir  = "/".join([str(xdg_cache_home()), "wpanel"])
    config_filename = "/".join([str(xdg_config_home()), "wpanel", "config.ini"])

    config = ConfigParser()
    config.read(config_filename)

    client = OneCallClient(**config["open weather"])
    image_manager = ImageManager(cache_dir)

    app = WeatherPanel(client, image_manager)
    app.mainloop()
