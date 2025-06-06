#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include "esp_sleep.h"
#include "esp_task_wdt.h"

// Configurações do WiFi
const char* ssid = "Wokwi-GUEST";
const char* password = "";
// url servidor
const char* serverUrl = "https://webhook.site/767080bf-7888-4b6b-a52a-bc964f85f8ab";

// Pinos
#define TRIG_PIN 5
#define ECHO_PIN 18
#define BUZZER 23
#define BATTERY_PIN 34

// Parâmetros do sistema
const int PROFUNDIDADE_TOTAL = 100;
const int PORCENTAGEM_VAZIO = 70;
const int PORCENTAGEM_ALERTA = 40;
const int PORCENTAGEM_CRITICO = 20;

// Parâmetros da bateria
#define BATERIA_MIN_V 3.2  // Tensão mínima (0%)
#define BATERIA_MAX_V 4.2  // Tensão máxima (100%)

// Intervalos
const unsigned long INTERVALO_ALERTA_CRITICO = 300000;
const unsigned long INTERVALO_ALERTA_MEDIO = 1800000;
const unsigned long TEMPO_ATIVO = 30000;
const unsigned long TEMPO_DEEP_SLEEP = 300000000;

// Variáveis globais
unsigned long ultimoAlertaCritico = 0;
unsigned long ultimoAlertaMedio = 0;
int porcentagemAnterior = -1;
int falhasWiFiConsecutivas = 0;

// Certificado SSL
const char* rootCACertificate = "-----BEGIN CERTIFICATE-----\n...";

void iniciarWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  Serial.println("Conectando ao WiFi...");
  WiFi.begin(ssid, password);
  
  unsigned long inicioConexao = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - inicioConexao < 20000) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    falhasWiFiConsecutivas = 0;
    Serial.println("\nConectado!");
  } else {
    falhasWiFiConsecutivas++;
    Serial.println("\nFalha na conexão WiFi");
    if (falhasWiFiConsecutivas > 3) ESP.restart();
  }
}

long medirDistancia() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duracao = pulseIn(ECHO_PIN, HIGH);
  long distancia = duracao * 0.0343 / 2;
  return (distancia > PROFUNDIDADE_TOTAL || distancia < 2) ? -1 : distancia;
}

int calcularPorcentagem(long distancia) {
  return (distancia <= 0 || distancia > PROFUNDIDADE_TOTAL) ? -1 : (distancia * 100) / PROFUNDIDADE_TOTAL;
}

int lerNivelBateria() {
  int leitura = analogRead(BATTERY_PIN);
  float tensao = leitura * (3.3 / 4095.0) * 1.1; // Fator 1.1 para compensação
  int nivel = map(tensao * 1000, BATERIA_MIN_V * 1000, BATERIA_MAX_V * 1000, 0, 100);
  return constrain(nivel, 0, 100);
}

void verificarBateriaCritica() {
  int nivel = lerNivelBateria();
  if (nivel < 10) {
    for (int i = 0; i < 3; i++) {
      digitalWrite(BUZZER, HIGH);
      delay(300);
      digitalWrite(BUZZER, LOW);
      delay(300);
    }
    Serial.println("ALERTA: Bateria crítica!");
  }
}

void ativarAlarme() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(BUZZER, HIGH);
    delay(100);
    digitalWrite(BUZZER, LOW);
    delay(100);
  }
}

void enviarAlertaSeguro(int porcentagem, String nivel, int bateria, int rssi, String mac) {
  if (WiFi.status() != WL_CONNECTED) iniciarWiFi();
  if (WiFi.status() != WL_CONNECTED) return;

  WiFiClientSecure client;
  client.setCACert(rootCACertificate);
  HTTPClient https;

String postData = String("{") +
  "\"dispositivo\":\"" + mac + "\"," +
  "\"espaco_livre_percent\":" + porcentagem + "," +
  "\"status_reportado\":\"" + nivel + "\"," +
  "\"bateria\":" + bateria + "," +
  "\"rssi\":" + WiFi.RSSI() + "}";


  if (https.begin(client, serverUrl)) {
    https.addHeader("Content-Type", "application/json");
    https.POST(postData);
    https.end();
  }
}

void prepararDeepSleep() {
  Serial.println("Entrando em deep sleep...");
  WiFi.disconnect(true);
  esp_sleep_enable_timer_wakeup(TEMPO_DEEP_SLEEP);
  esp_deep_sleep_start();
}

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER, OUTPUT);
  pinMode(BATTERY_PIN, INPUT);

  // Configuração do Watchdog
  esp_task_wdt_config_t twdt_config = {
    .timeout_ms = 30000,
    .idle_core_mask = 0,
    .trigger_panic = true
  };
  esp_task_wdt_init(&twdt_config);
  esp_task_wdt_add(NULL);

  iniciarWiFi();
  Serial.println("Sistema iniciado");
}

void loop() {
  long distancia = medirDistancia();
  int porcentagem = calcularPorcentagem(distancia);
  int nivelBateria = lerNivelBateria();
  verificarBateriaCritica();

  Serial.print("Espaço livre: ");
  Serial.print(porcentagem);
  Serial.print("% | Bateria: ");
  Serial.print(nivelBateria);
  Serial.println("%");

  if (porcentagem <= PORCENTAGEM_CRITICO) {
    ativarAlarme();
    enviarAlertaSeguro(porcentagem, "CRITICO", nivelBateria, WiFi.RSSI(), WiFi.macAddress());
  }

  if (millis() > TEMPO_ATIVO) prepararDeepSleep();
  delay(2000);
}