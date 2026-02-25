#include <SPI.h>
#include <MFRC522.h>
#include <Ethernet2.h>       // W5500
#include <ArduinoJson.h>

// RC522 pins
#define RC522_SS_PIN 7
#define RC522_RST_PIN 6

// W5500 pins
#define ETH_SS_PIN 10
#define ETH_RST_PIN 8

// Network settings
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress localIp(192, 168, 0, 103);     // Arduino static IP
IPAddress serverIp(192, 168, 0, 102);    // Django server
IPAddress gateway(192, 168, 0, 1);
IPAddress subnet(255, 255, 255, 0);

const uint16_t SERVER_PORT = 8000;
const char* PATH = "/api/rfid_log/";     // Django endpoint

EthernetClient client;
MFRC522 mfrc522(RC522_SS_PIN, RC522_RST_PIN);

// Scan timing
unsigned long lastScanTime = 0;           // stores last scan timestamp
const unsigned long scanDelay = 5000;     // 5 seconds delay between scans

void setup() {
  Serial.begin(115200);

  // Initialize SPI
  SPI.begin();

  // Set pin modes for SS pins
  pinMode(RC522_SS_PIN, OUTPUT);
  pinMode(ETH_SS_PIN, OUTPUT);

  // Deselect both devices initially
  digitalWrite(RC522_SS_PIN, HIGH);
  digitalWrite(ETH_SS_PIN, HIGH);

  // Initialize Ethernet (static IP)
  Ethernet.init(ETH_SS_PIN);
  pinMode(ETH_RST_PIN, OUTPUT);
  digitalWrite(ETH_RST_PIN, LOW);
  delay(100);
  digitalWrite(ETH_RST_PIN, HIGH);
  delay(100);

  Ethernet.begin(mac, localIp, gateway, gateway, subnet); // static only
  delay(1000);
  Serial.print("Arduino IP: ");
  Serial.println(Ethernet.localIP());

  // Initialize RC522
  mfrc522.PCD_Init();
  Serial.println("RC522 initialized");
}

void loop() {
  // Check for new RFID card
  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  // Check if enough time has passed since last scan
  unsigned long currentTime = millis();
  if (currentTime - lastScanTime < scanDelay) {
    return;  // skip scanning if less than 5 seconds
  }
  lastScanTime = currentTime;  // update last scan time

  // Read card UID
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();
  Serial.print("Card UID: ");
  Serial.println(uid);

  sendToServer(uid);

  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
}

void sendToServer(const String &rfid_uid) {
  if (!client.connect(serverIp, SERVER_PORT)) {
    Serial.println("Connection to server failed");
    return;
  }
  Serial.println("Connected to server");

  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["uid"] = rfid_uid;
  String payload;
  serializeJson(doc, payload);

  Serial.print("Sending payload: ");
  Serial.println(payload);

  // Send HTTP POST request
  client.print("POST ");
  client.print(PATH);
  client.println(" HTTP/1.1");
  client.println("Host: 192.168.0.102");  // Django server IP
  client.println("Content-Type: application/json");
  client.print("Content-Length: ");
  client.println(payload.length());
  client.println("Connection: close");
  client.println();
  client.println(payload);

  // Read response
  unsigned long timeout = millis() + 4000;
  while (client.connected() && millis() < timeout) {
    while (client.available()) {
      char c = client.read();
      Serial.print(c);
    }
  }

  client.stop();
  Serial.println("\nDisconnected from server");
}