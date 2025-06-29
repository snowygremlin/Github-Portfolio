import { Component, OnInit } from '@angular/core';
import { WeatherService } from '../weather';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-weather',
  templateUrl: './weather.html',
  styleUrls: ['./weather.css'],
  standalone:true
})
export class WeatherComponent implements OnInit {

  myWeather: any;
  temperature_2m: number = 0;
  apparent_temperature: number = 0;
  relative_humidity: number = 0;
  surface_pressure: number = 0;
  summary: string = '';
  iconURL: string = '';
  city: string = 'London';


  constructor(private weatherService: WeatherService) { }

  ngOnInit(): void {
    this.getWeather();
  }

  getWeather() {
    this.weatherService.getweather().subscribe({

      next: (res) => {
        console.log(res)

        this.myWeather = res;
        this.temperature_2m = this.myWeather.current.temperature_2m;
        this.apparent_temperature = this.myWeather.current.apparent_temperature;
        this.relative_humidity = this.myWeather.current.relative_humidity_2m;
        this.surface_pressure = this.myWeather.current.surface_pressure;
        this.summary = this.weatherSummary(this.myWeather.current.weather_code);
      },

      error: (error) => console.log(error.message),

      complete: () => console.info('API call completed')
    })
  }

  weatherSummary(weatherCode: number){
    if(weatherCode === 0 ){
      return "Clear Sky"
    }
    if(weatherCode === 1 ){
      return "Mainly Clear"
    }
    if(weatherCode === 2 ){
      return "Partly Cloudy"
    }
    if(weatherCode === 3 ){
      return "Overcast"
    }
    else{
      return "Unknwon"
    }
  }



}
