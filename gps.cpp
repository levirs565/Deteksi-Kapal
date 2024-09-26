#include <TinyGPS++.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

TinyGPSPlus gps;
Adafruit_SSD1306 display(128, 64, &Wire, -1);

void setup() {
  Serial.begin(9600);
  Wire.begin();
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
}

void loop() {
  while (Serial.available() > 0) {
    gps.encode(Serial.read());
  }

  if (gps.location.isUpdated()) {
    display.clearDisplay();
    display.setCursor(0, 0);
    display.print("Lat: "); display.println(gps.location.lat());
    display.print("Lng: "); display.println(gps.location.lng());
    display.display();

    // Send data to Raspberry Pi
    Serial.print(gps.location.lat());
    Serial.print(",");
    Serial.println(gps.location.lng());
  }
}
