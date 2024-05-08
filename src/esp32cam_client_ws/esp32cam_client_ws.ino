#include <ArduinoWebsockets.h>
#include <Arduino.h>
#include "ArduinoJson.h"
#include "esp32cam.h"
#include <WiFi.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "base64.h"
// ------------------- config -------------------
const char* ssid = "meen mes mew_2.4G";
const char* password = "meen mes mew";
const char* serverUrl = "http://47.236.74.47:4451/upload_image"; // Modify with your server URL

const int FPS = 10;
const unsigned long captureInterval = 1.0/float(FPS) * 1000;
volatile bool captureFlag = false;
hw_timer_t *timer = NULL; // Declare the timer variable

static auto set_res = esp32cam::Resolution::find(800, 600);

uint8_t state = 0;

using namespace websockets;
WebsocketsClient client;

void IRAM_ATTR onTimer() {
  captureFlag = true;
}

void SendJPG()
{
  if (!esp32cam::Camera.changeResolution(set_res)) {
    Serial.println("SET-RES FAIL");
    return;
  }

  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    return;
  }

  // Send the captured image to the server
  client.sendBinary((const char*) frame->data(), frame->size());
  client.poll();
}

esp_err_t init_camera() {
  // Initialize ESP32-CAM
  using namespace esp32cam;
  Config cfg;
  cfg.setPins(pins::AiThinker);
  cfg.setResolution(set_res);
  cfg.setBufferCount(2);
  cfg.setJpeg(85);

  bool ok = Camera.begin(cfg);
  if (ok) {
    Serial.println("CAMERA OK");
    return ESP_OK;
  }
  else {
    Serial.println("CAMERA FAIL");
    return ESP_FAIL;
  }
}

esp_err_t init_wifi() {
  WiFi.begin(ssid, password);
  Serial.println("Starting Wifi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  return ESP_OK;
}

esp_err_t init_websocket() {
  Serial.println("Connecting to websocket");
  client.onMessage([](WebsocketsMessage message) {
    Serial.print("Got Message: ");
    Serial.println(message.data());
  });

  // Try to connect to WebSocket server
  if (client.connect(serverUrl)) {
    Serial.println("WebSocket Connected!");
    client.send(String(ESP.getEfuseMac(), HEX)); // Send device ID for verification
    return ESP_OK;
  } else {
    Serial.println("WebSocket Connection Failed!");
    return ESP_FAIL;
  }
}


void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); //disable brownout detector
  //  disableCore0WDT();
  Serial.begin(115200);
  Serial.setDebugOutput(true);

  init_camera();
  init_wifi();
  init_websocket();
  
  // Configure and start the hardware timer for the interrupt
  timer = timerBegin(0, 80, true); // Timer 0, divider 80 (1 MHz), count up
  timerAttachInterrupt(timer, &onTimer, true); // Attach the ISR function
  timerAlarmWrite(timer, captureInterval * 1000, true); // Set the interval in microseconds
  timerAlarmEnable(timer); // Enable the timer
}

void loop() {
  if (captureFlag) {
    captureFlag = false;
    SendJPG();
  }

  if (!client.available()) {
    // Reconnect to WebSocket server if disconnected
    init_websocket();
    delay(500);
  }
}