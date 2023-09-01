import tkinter as tk
import tkintermapview
from PIL import Image, ImageTk
from weather_class import Weather
import requests



class WeatherApp(tk.Tk):
    """
    This class instantiate a weather app instance with tkinter window and all the labels
    it also uses the tkintermapview class to display a map of the world in wich we can choose
    which city we want to see weather  
    """
    def __init__(self):
        super().__init__()
        self.title("Weather App")
        self.geometry("400x400")
        self.weather = Weather()
        self.map_widget = tkintermapview.TkinterMapView(self, width=400, height=300, corner_radius=0)

        self.weather_frame = tk.Frame(self)
        self.weather_frame.pack(padx=10, pady=10)

        self.icon_label = tk.Label(self.weather_frame)
        self.icon_label.pack(fill=tk.BOTH, expand=True)

        self.sunset_label = tk.Label(self.weather_frame)
        self.sunset_label.pack(fill=tk.BOTH, expand=True)
 
        self.sunrise_label = tk.Label(self.weather_frame)
        self.sunrise_label.pack(fill=tk.BOTH, expand=True)
 
        self.temperature_label = tk.Label(self.weather_frame)
        self.temperature_label.pack(fill=tk.BOTH, expand=True)

        self.feels_like_label = tk.Label(self.weather_frame)
        self.feels_like_label.pack(fill=tk.BOTH, expand=True)

        self.description_label = tk.Label(self.weather_frame)
        self.description_label.pack(fill=tk.BOTH, expand=True)
        
        def_lat, def_lon = self.weather.current_location
        self.update_weather((def_lat, def_lon))

        self.map_widget.set_position(def_lat, def_lon, marker=True) # default city at the start
        self.map_widget.set_zoom(5)
        self.map_widget.add_left_click_map_command(self.update_weather) # we add an event of left mouse click on the map
        self.map_widget.pack(fill=tk.BOTH, expand=True)


    def marker_update(self, location):
        """
        this function updates the marker on the map
        """
        lat, lon = location
        city = tkintermapview.convert_coordinates_to_city(lat, lon)
        self.map_widget.delete_all_marker()
        self.map_widget.set_marker(lat, lon, text=city)
    
    def update_weather(self, location):
        """
        this function updates the weather, it will call the open weather api through another function
        for the Weather class
        """
        lat, lon = location
        self.marker_update(location)
        weather_metric_data = self.weather.get_weather((lat, lon), "metric")
        current_weather = self.weather.get_current_weather(weather_metric_data)
        self.display_weather(current_weather)
        

        # Schedule the next update after 10 minutes (600000 milliseconds)
        self.after(600000, self.update_weather)

    def display_weather(self, weather_data):
        """
        this function will display the weather through the tkinter window 
        """
        weather_icon = weather_data.get("icon", "")
        if weather_icon:
            icon_url = f"https://openweathermap.org/img/wn/{weather_icon}.png"
            icon_response = requests.get(icon_url, stream=True)
            if icon_response.status_code == 200:
                icon_image = Image.open(icon_response.raw)
                icon_image = icon_image.resize((50, 50), Image.Resampling.LANCZOS)
                icon_tk = ImageTk.PhotoImage(icon_image)
                self.icon_label.config(image=icon_tk)
                self.icon_label.image = icon_tk # save reference to avoid garbage collecting
        
        sunrise = weather_data.get("sunrise", "")
        if sunrise:
            self.sunrise_label.config(text=f"Sunrise: {sunrise}")
        
        sunset = weather_data.get("sunset", "")
        if sunset:
            self.sunset_label.config(text=f"Sunset: {sunset}")
        
        temperature = weather_data.get("temp", "")
        if temperature:
            self.temperature_label.config(text=f"Temperature: {temperature} °C")

        feels_like = weather_data.get("feels_like", "")
        if feels_like:
            self.feels_like_label.config(text=f"Feels Like: {feels_like} °C")

        wind_speed = weather_data.get("wind_speed", "")
        if wind_speed:
            self.feels_like_label.config(text=f"Wind Speed: {wind_speed} metre/s")

        description = weather_data.get("description", "")
        if description:
            self.description_label.config(text=f"Description: {description}")

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
