const int sensorPin = A0;

float sensitivity = 0.185;   // ACS712 5A
float offsetVoltage = 2.534; // your calibrated value

// Simulated vehicle state
float speed = 0.0;
float fuel = 100.0;
float engineTemp = 30.0;
float battery = 12.6;
int ignition = 1;

float lat = 43.6532;
float lon = -79.3832;

bool accelerating = true;

void setup() {
  Serial.begin(9600);
}

// Read current from ACS712
float readCurrent() {
  float sum = 0;

  for (int i = 0; i < 50; i++) {
    int raw = analogRead(sensorPin);
    float voltage = raw * (5.0 / 1023.0);
    sum += voltage;
    delay(2);
  }

  float avgVoltage = sum / 50;
  float current = (avgVoltage - offsetVoltage) / sensitivity;

  return current;
}

// Simulate vehicle behavior
void updateVehicleState() {
  if (ignition == 1) {

    // Speed changes
    if (accelerating) {
      speed += 6.0;
      if (speed >= 110.0) accelerating = false;
    } else {
      speed -= 8.0;
      if (speed <= 20.0) accelerating = true;
    }

    // Fuel consumption
    fuel -= 0.15;
    if (fuel < 0) fuel = 0;

    // Engine temp rises with speed
    engineTemp = 70.0 + (speed * 0.35);
    if (engineTemp > 118.0) engineTemp = 118.0;

    // Battery drops slightly
    battery = 12.4 - (speed / 500.0);
    if (battery < 11.1) battery = 11.1;

    // Simulated movement
    lat += 0.00015;
    lon += 0.00010;

  } else {
    speed = 0.0;

    // Cool down when off
    engineTemp -= 1.0;
    if (engineTemp < 25.0) engineTemp = 25.0;

    battery = 12.5;
  }
}

void loop() {
  updateVehicleState();

  float current = readCurrent();

  // Send structured telemetry string
  Serial.print("speed=");
  Serial.print(speed, 1);
  Serial.print(",fuel=");
  Serial.print(fuel, 1);
  Serial.print(",temp=");
  Serial.print(engineTemp, 1);
  Serial.print(",battery=");
  Serial.print(battery, 2);
  Serial.print(",ignition=");
  Serial.print(ignition);
  Serial.print(",lat=");
  Serial.print(lat, 6);
  Serial.print(",lon=");
  Serial.print(lon, 6);
  Serial.print(",current=");
  Serial.println(current, 3);

  delay(1000);
}