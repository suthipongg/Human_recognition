#include <Arduino.h>
#include "esp32cam.h"
#include <WiFi.h>
#include <HTTPClient.h>

// ------------------- config -------------------
const char* ssid = "Music";
const char* password = "mew654321";
const char* serverUrl = "http://172.20.10.3:8080/upload_image"; // Modify with your server URL

const int FPS = 10;


const unsigned long captureInterval = 1.0/float(FPS) * 1000;
volatile bool captureFlag = false;
hw_timer_t *timer = NULL; // Declare the timer variable

static auto set_res = esp32cam::Resolution::find(800, 600);
HTTPClient http;

void IRAM_ATTR onTimer() {
  captureFlag = true;
}

void SendJPG()
{
  if (!esp32cam::Camera.changeResolution(set_res)) {
    Serial.println("SET-RES FAIL");
  }

  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    return;
  }
  // Send the captured image to the server
  http.begin(serverUrl);
  http.addHeader("Content-Type", "image/jpeg");
  int httpResponseCode = http.POST(frame->data(), frame->size());
  http.end();

  if (httpResponseCode != 200) {
    Serial.print("HTTP error code: ");
    Serial.println(httpResponseCode);
  }
}

void setup() {
  Serial.begin(115200);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Initialize ESP32-CAM
  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(set_res);
    cfg.setBufferCount(2);
    cfg.setJpeg(85);

    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
  }

  // Configure and start the hardware timer for the interrupt
  timer = timerBegin(0, 80, true); // Timer 0, divider 80 (1 MHz), count up
  timerAttachInterrupt(timer, &onTimer, true); // Attach the ISR function
  timerAlarmWrite(timer, captureInterval * 1000, true); // Set the interval in microseconds
  timerAlarmEnable(timer); // Enable the timer
}

void loop() {
  if (captureFlag) 
  {
    captureFlag = false;
    SendJPG();
  }
}