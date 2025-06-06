#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_sleep.h"

// WiFi
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// Webhook.site URL
const char* serverUrl = "https://webhook.site/767080bf-7888-4b6b-a52a-bc964f85f8ab";

// Pinos
#define BUZZER 23

// Parâmetros
const int PORCENTAGEM_ALERTA = 40;
const int PORCENTAGEM_CRITICO = 20;

const unsigned long TEMPO_ATIVO = 30000;
const uint64_t TEMPO_DEEP_SLEEP_US = 300 * 1000000;

int falhasWiFiConsecutivas = 0;

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
    Serial.print("\nConectado! Endereço IP: ");
    Serial.println(WiFi.localIP());
  } else {
    falhasWiFiConsecutivas++;
    Serial.println("\nFalha na conexão WiFi");
    if (falhasWiFiConsecutivas > 3) ESP.restart();
  }
}

void verificarBateriaCritica(int nivelBateria) {
  if (nivelBateria < 10) {
    for (int i = 0; i < 3; i++) {
      digitalWrite(BUZZER, HIGH); delay(300);
      digitalWrite(BUZZER, LOW); delay(300);
    }
    Serial.println("ALERTA: Bateria crítica!");
  }
}

void ativarAlarme() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(BUZZER, HIGH); delay(100);
    digitalWrite(BUZZER, LOW); delay(100);
  }
}

void enviarDadosParaServidor(int porcentagem, String nivel, int bateria, int rssi, String mac) {
  if (WiFi.status() != WL_CONNECTED) iniciarWiFi();
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");

  String postData = String("{") +
    "\"dispositivo\":\"" + mac + "\"," +
    "\"espaco_livre_percent\":" + String(porcentagem) + "," +
    "\"status_reportado\":\"" + nivel + "\"," +
    "\"bateria\":" + String(bateria) + "," +
    "\"rssi\":" + String(rssi) + "}";

  Serial.println("Enviando dados para o servidor...");
  Serial.println(postData);

  int httpCode = http.POST(postData);
  Serial.printf("Código de resposta HTTP: %d\n", httpCode);
  http.end();
}

void prepararDeepSleep() {
  Serial.println("Entrando em deep sleep...");
  WiFi.disconnect(true);
  esp_sleep_enable_timer_wakeup(TEMPO_DEEP_SLEEP_US);
  esp_deep_sleep_start();
}

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER, OUTPUT);
  iniciarWiFi();
  Serial.println("Sistema iniciado. Começando o primeiro ciclo.");
}

void loop() {
  int distancia_cm = random(10, 90);
  int porcentagem = 100 - distancia_cm;
  int nivelBateria = 85;

  verificarBateriaCritica(nivelBateria);

  Serial.print("Espaço livre: ");
  Serial.print(porcentagem);
  Serial.print("% | Bateria: ");
  Serial.print(nivelBateria);
  Serial.println("%");

  if (porcentagem >= 0) {
    String statusReportado = "NORMAL";
    if (porcentagem <= PORCENTAGEM_CRITICO) {
      statusReportado = "CRITICO";
      ativarAlarme();
    } else if (porcentagem <= PORCENTAGEM_ALERTA) {
      statusReportado = "ALERTA";
    }

    enviarDadosParaServidor(porcentagem, statusReportado, nivelBateria, WiFi.RSSI(), WiFi.macAddress());
  } else {
    Serial.println("Leitura do sensor inválida. Não enviando dados.");
  }

  Serial.printf("Fim do ciclo. Entrando em deep sleep após %d segundos.\n", TEMPO_ATIVO / 1000);
  delay(TEMPO_ATIVO);
  prepararDeepSleep();
}
