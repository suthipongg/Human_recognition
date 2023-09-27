#include <Arduino.h>
#include "esp32cam.h"
#include <WiFi.h>
#include <HTTPClient.h>

#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27

#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

const char* ssid = "Music";
const char* password = "mew654321";
const char* serverUrl = "http://172.20.10.3:8080/upload_image"; // Modify with your server URL

static auto set_res = esp32cam::Resolution::find(800, 600);
HTTPClient http;

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

  if (httpResponseCode == 200) {
    Serial.println("Image uploaded successfully.");
  } else {
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
}

void loop() {
  SendJPG();
}