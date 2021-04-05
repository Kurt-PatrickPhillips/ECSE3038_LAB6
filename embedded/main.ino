#include <Arduino.h>
#include <SoftwareSerial.h>

#define DEBUG true

SoftwareSerial esp(10, 11);

String sendData(String command, const int timeout, boolean debug)
{
    String response = "";

    esp.print(command);

    long int time = millis();

    while ((time + timeout) > millis())
    {
        while (esp.available())
        {

            char c = esp.read();
            response += c;
        }
    }

    if (debug)
    {
        Serial.print(response);
    }
    return response;
}

int getWaterLevel()
{
    return (int)random(10, 201);
}
String generatePostRequest(String route, String portNumber, int cLength, String pData)
{
    String requestType = "POST /" + route + " HTTP/1.1\r\n";
    String hostInfo = "Host: 192.168.0.9:" + portNumber + "\r\n";
    String contentType = "Content-Type: application/json\r\n";
    String contentLength = "Content-Length: " + String(cLength) + "\r\n\r\n";
    String postData = pData + "\r\n\r\n";

    return requestType + hostInfo + contentType + contentLength + postData;
}
String generateCIPSend(int requestLength)
{
    String cipSend = "AT+CIPSEND=" + String(requestLength) + "\r\n";
    return cipSend;
}

String generatePost(int tankID, int waterLevel)
{
    String post = "{\"tank_id\":" + String(tankID) + ", \"water_level\":" + String(waterLevel) + "}\r\n\r\n";
    return post;
}
void setup()
{
    // put your setup code here, to run once:
    esp.begin(9600);
    Serial.begin(9600);

    sendData("AT+RST\r\n", 10000, DEBUG);
    // sendData("AT+CWLAP\r\n", 10000, DEBUG);
    sendData("AT+CWJAP=\"CWC-7961954\",\"Zp8jtpkdmdrb\"\r\n", 10000, DEBUG);
    //   sendData("AT+CIFSR\r\n", 10000, DEBUG);
}

void loop()
{
    tank_id++;
    // put your main code here, to run repeatedly:
    sendData("AT+CIPSTART=\"TCP\",\"192.168.0.9\",5000\r\n", 5000, DEBUG);

    String postData = generatePost(tank_id, getWaterLevel());
    String postRequest = generatePostRequest("tank", "5000", postData.length(), postData);
    String cipSend = generateCIPSend(postRequest.length());

    sendData(cipSend, 1000, DEBUG);
    sendData(postRequest, 5000, DEBUG);
}