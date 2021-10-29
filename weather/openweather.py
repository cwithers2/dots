import requests
import os.path
from datetime import datetime

class BaseForecastObject:
    """An object to give a standard interface to forecast data."""
    def __init__(self, forecast_json):
        """
        Parameters
        ----------
        forecast_json : dict
            A subset of weather data downloaded from openweathermap.org.
        """
        self.json = forecast_json

    def temperature(self):
        raise NotImplementedError

    def feels_like(self):
        raise NotImplementedError

    def humidity(self):
        return self.json["humidity"]

    def wind(self):
        return [self.json["wind_speed"], self.json.get("wind_gust", self.json["wind_speed"])]

    def description(self):
        return self.json["weather"][0]["description"]

    def icon_name(self):
        return self.json["weather"][0]["icon"]

    def datetime(self):
        return datetime.fromtimestamp(self.json["dt"])

class CurrentWeather(BaseForecastObject):
    """An object for the current weather."""
    def __init__(self, forecast_json):
        BaseForecastObject.__init__(self, forecast_json)

    def temperature(self):
        return [self.json["temp"]]

    def feels_like(self):
        return [self.json["feels_like"]]

class DailyForecast(BaseForecastObject):
    """An object for a forecast on a specified date/time."""
    def __init__(self, forecast_json):
        BaseForecastObject.__init__(self, forecast_json)

    def temperature(self):
        temp = self.json["temp"]
        return [temp["min"], temp["max"]]

    def feels_like(self):
            feels_like = self.json["feels_like"]
            max_key = max(feels_like, key=feels_like.get)
            min_key = min(feels_like, key=feels_like.get)
            return [feels_like[min_key], feels_like[max_key]]

class ImageManager:
    """Manges downloading and recalling weather icon files from openweathermap.org."""

    ICON_NAMES = ("01d", "01n", "02d", "02n", "03d", "03n",
                  "04d", "04n", "09d", "09n", "10d", "10n",
                  "11d", "11n", "13d", "13n", "50d", "50n")
    ICON_SIZES = (2, 4)

    def __init__(self, work_directory):
        """
        Parameters
        ----------
        work_directory : str
            Path to a directory to download weather icon files.
        """
        self.dir = work_directory

    def filename(self, name, size=None):
        """Get the file name of an icon by name and optional size.

        Parameters
        ----------
        name : str
            The name of the icon.
        size : int (default=None)
            The scale of the image to download. See ImageManager.ICON_SIZES for valid values.

        Returns
        -------
        str
        """
        #this code is strict so to impede callers from downloading 404 files,
        #do that on your own time... not ours :)
        if name not in self.ICON_NAMES:
            raise ValueError("name is not valid")
        if size in self.ICON_SIZES:
            name = f"{name}@{size}x"
        elif size is not None:
            raise ValueError("size is not valid")
        return f"{name}.png"

    def fullpath(self, name, size=None):
        """Get the full path of an icon file assuming it exists locally.

        Parameters
        ----------
        name : str
            The name of the icon.
        size : int (default=None)
            The scale of the image to download. See ImageManager.ICON_SIZES for valid values.

        Returns
        -------
        str
        """
        return f"{self.dir}/{self.filename(name, size)}"

    def download(self, name, size=None):
        """Try to download an icon by name and optional size

        Parameters
        ----------
        name : str
            The name of the icon.
        size : int (default=None)
            The scale of the image to download. See ImageManager.ICON_SIZES for valid values.

        Returns
        -------
        int
            -1 for connection error, otherwise the status code of the request is returned.
        """
        url = f"http://openweathermap.org/img/wn/{self.filename(name, size)}"
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            return -1
        if response:
            with open(self.fullpath(name, size), "+wb") as fp:
                fp.write(response.content)
        return response.status_code

    def exists(self, name, size=None):
        """Check if an icon file exists locally.

        Parameters
        ----------
        name : str
            The name of the icon.
        size : int (default=None)
            The scale of the image to download. See ImageManager.ICON_SIZES for valid values.

        Returns
        -------
        bool
        """
        return os.path.exists(self.fullpath(name, size))

class OneCallClient:
    """An object to get weather data from OpenWeather's oncall API protocol."""

    API = "http://api.openweathermap.org/data/2.5/onecall"

    def __init__(self, **params):
        """
        Parameters
        ----------
        params : dict
            key-values to pass to the API request.
        """
        self.params  = params
        self.json = {}

    def download(self):
        """Try to download weather data.

        Returns
        -------
        int
            -1 for connection error, otherwise the status code of the request is returned.
        """
        try:
            response = requests.get(self.API, params=self.params)
        except requests.exceptions.ConnectionError:
            return -1
        if response:
            self.json  = response.json()
        return response.status_code

    def current(self):
        """Get the current weather.

        Returns
        -------
        None
            There is no weather data downloaded.
        CurrentWeather
            A weather object."""
        result = None
        if self.json:
            current_data = self.json.get("current", None)
            if current_data:
                result = CurrentWeather(current_data)
        return result

    def daily(self):
        """Get the seven day forecast.

        Returns
        -------
        None
            There is no weather data downloaded.

        Yields
        ------
        DailyForecast
            A weather object for one of the daily forecasts in sequential order.
        """
        if self.json:
            daily_data = self.json.get("daily", None)
            if daily_data:
                for data in daily_data:
                    yield DailyForecast(data)
                return
        return None
