#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"

// Camera configuration
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

// ------------------- config -------------------
const char* ssid = "Music";
const char* password = "mew654321";
const char* serverUrl = "http://172.20.10.3:8080/upload_image"; // Modify with your server URL

const int FPS = 10;


const unsigned long captureInterval = 1.0/float(FPS) * 1000;
volatile bool captureFlag = false;
hw_timer_t *timer = NULL; // Declare the timer variable

HTTPClient http;

void IRAM_ATTR onTimer() {
  captureFlag = true;
}

void SendJPG() {
  // Capture an image
  camera_fb_t *fb = esp_camera_fb_get();
  
  if (fb) 
  {
    // Send the captured image to the server
    
    http.begin(serverUrl);
    http.addHeader("Content-Type", "image/jpeg");
    http.addHeader("Content-Disposition", "attachment; filename=capture.jpg");
    http.POST(fb->buf, fb->len); // Pass the image data and size
    http.end();

    esp_camera_fb_return(fb);
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

  // Initialize the camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.fb_location = (camera_fb_location_t)CAMERA_FB_IN_PSRAM;

  if(psramFound()){
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 20; // value -> range 3-63 : slow - fast : high - low
    config.fb_count = 5; // buffer : value -> range 1-5 : slow - fast
  } 
  else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
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