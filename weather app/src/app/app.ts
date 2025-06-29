import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { WeatherComponent } from './weather/weather';


@Component({
  selector: 'app-root',
  imports: [WeatherComponent] ,
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected title = 'weather_app';
}
