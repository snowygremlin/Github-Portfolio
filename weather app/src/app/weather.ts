import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class WeatherService {

  constructor(private http: HttpClient) { }

  getweather() {
    return this.http.get('https://api.open-meteo.com/v1/forecast?latitude=51.5085&longitude=-0.1257&current=temperature_2m,relative_humidity_2m,apparent_temperature,surface_pressure,weather_code&timezone=GMT&forecast_days=1&wind_speed_unit=mph');
  }

}
