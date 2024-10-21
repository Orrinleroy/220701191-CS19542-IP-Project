#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

// WiFi credentials
const char* ssid = "Your_SSID";
const char* password = "Your_PASSWORD";

// Server URL (Replace with your server IP)
const String serverUrl = "http://<your-server-ip>:5000/api/update_slot";

// Sensor pins
const int trigPin = 5;  // GPIO5 (D1)
const int echoPin = 4;  // GPIO4 (D2)
int slotId = 1;  // Assign each parking slot a unique ID

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // Connect to WiFi
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
}

void loop() {
  long duration, distance;

  // Trigger the ultrasonic sensor
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Measure the pulse duration
  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2;  // Convert to cm

  // Determine if the slot is occupied
  bool isOccupied = (distance < 30);  // Adjust this threshold as necessary

  // Send slot status to the Flask server
  sendSlotStatus(isOccupied);

  delay(5000);  // Update every 5 seconds
}

void sendSlotStatus(bool isOccupied) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);

    // Prepare the JSON payload
    String payload = "{\"id\":" + String(slotId) + ",\"isOccupied\":" + (isOccupied ? "true" : "false") + "}";
    http.addHeader("Content-Type", "application/json");

    // Send the POST request
    int httpResponseCode = http.POST(payload);
    Serial.println("Response Code: " + String(httpResponseCode));
    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }
}
