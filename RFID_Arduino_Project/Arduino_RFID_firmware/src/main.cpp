#include <Arduino.h>
#include <MFRC522.h>
#include <SPI.h>

#include "EasyMifare1K.h"
#include "Timer.h"

// Forward declarations of auxiliary functions
bool detectNewTag(bool alwaysAnswerNotDetected = false);
void showRfidReaderDetails();
bool serialParseHexStr(byte* data, uint size);
int serialParseUint(uint maxDigits);
int serialReadByte();
void serialWriteHexStr(byte* data, int size);

/**
 * Todas as ligações entre o Arduino e o MFRC522:
 *  - Pino SDA ligado na porta 10 do Arduino
 *  - Pino SCK ligado na porta 13 do Arduino
 *  - Pino MOSI ligado na porta 11 do Arduino
 *  - Pino MISO ligado na porta 12 do Arduino
 *  - Pino NC (IRQ) – Não conectado
 *  - Pino GND  ligado no pino GND do Arduino
 *  - Pino RST ligado na porta 9 do Arduino
 *  - Pino 3.3 – ligado ao pino 3.3 V do Arduino
 */

MFRC522 mfrc522(10, 9); //RFID scanner (MFRC522), SDA and RST pins are given as parameters
MFRC522::MIFARE_Key key;

bool rfidStarted;
bool tagSelected;
byte tagUid[4];

byte bufferMagicNum[4];
byte bufferData[1024];

//PollingTimer timerToReleaseTag(5); //0.005s


/**
 * SETUP -- Does some initializations.
 */
void setup() {
  Serial.begin(38400);    //Inicia a serial
  Serial.setTimeout(400); //0.4s

  SPI.begin();        //Inicia barramento SPI
  mfrc522.PCD_Init(); //Inicia o leitor RFID
  
  mfrc522.PCD_AntennaOff();    
  rfidStarted = false;
  
  tagSelected = false;
  for (byte i = 0; i < 4; i++) {
    tagUid[i] = 0;
  }

  //used as key A
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
}

/**
 * LOOP -- Implements the main operation.
 */
void loop() {
  
  /************************************************/
  /*** PARTE 1: detectar e enviar dados de tags ***/
  /************************************************/
  
  if (rfidStarted) {
    
    // known issue: após ler da tag (com r), a tag é dita não detectada
    detectNewTag(false);

  }

  /***************************************/
  /*** PARTE 2: ler/executar comandos  ***/
  /***************************************/

  int option = Serial.read();

  //a start of a command
  if (option != '(') {
    return;
  }

  //TODO: ideia -- retornar 1 (+dados, se tiver) para sucesso (ao inves de OK)
  //                      e 0 (+ mensagem) para erro

  option = serialReadByte(); //wait for a byte (or until a timeout occurs)
  
  //// START RFID ANTENNA ////
  if (option == 's') { //start
    if (rfidStarted) {
      Serial.println(F("(s Warning: already started)"));
      return;
    }
    Serial.print(F("(s "));
    mfrc522.PCD_AntennaOn();
    Serial.println(F("OK)"));
    tagSelected = false;
    rfidStarted = true;
    return;
  
  } 
  //// TEST THE RFID READER ////
  else if (option == 't') {
    if (rfidStarted) {
      Serial.println(F("(t Error: antenna is turned on)"));
      return; 
    }
    Serial.print(F("(t Result: "));
    Serial.print(mfrc522.PCD_PerformSelfTest()? "true, " : "false, ");
    showRfidReaderDetails();
    Serial.println(F(")"));
    mfrc522.PCD_Init();  //without this command, our rfid reader stopped reading tags until it was reseted
    mfrc522.PCD_AntennaOff();
    return;
  }
  
  static char *strRfidTurnedOff = (char*)"(? Error: antenna is turned off)";
  static char *strNoTagSelected = (char*)"(? Error: no tag selected)";

  //// STOP ////
  if (option == 'x') {
    if (!rfidStarted) {
      strRfidTurnedOff[1] = (char)option;
      Serial.println(strRfidTurnedOff);
      return; 
    }
    Serial.print(F("(x "));
    if (tagSelected) {
      unselectMifareTag(&mfrc522, false);
      tagSelected = false;
    }
    mfrc522.PCD_AntennaOff();
    Serial.println(F("OK)"));
    rfidStarted = false;
  
  }
  //// DETECT NEW TAG ////
  else if (option == 'd') {
    if (!rfidStarted) {
      strRfidTurnedOff[1] = (char)option;
      Serial.println(strRfidTurnedOff);
      return; 
    }
    detectNewTag(true);

  }
  //// READ FROM TAG ////  (ex. (r 16 12345678))
  else if (option == 'r') {
    if (!rfidStarted) {
      strRfidTurnedOff[1] = (char)option;
      Serial.println(strRfidTurnedOff);
      return; 
    }
    if (!tagSelected) {
      strNoTagSelected[1] = (char)option;
      Serial.println(strNoTagSelected);
      return;
    }
    Serial.print(F("(r "));
    
    int blockAddr = serialParseUint(2);
    if (blockAddr < 0) { Serial.println(F(")")); return; }
    
    bool parseOk = serialParseHexStr(bufferMagicNum, 4);
    if (!parseOk) { Serial.println(F(")")); return; }

    serialReadByte(); //just to read the final ')', but don't need to check it

    int status = readFromMifareTag(&mfrc522, &key, blockAddr, bufferMagicNum, bufferData, sizeof(bufferData));
    
    if (status < 0) {
      Serial.print(F("Error in tag: "));
      Serial.print(status);
      Serial.println(F(")"));
    } else {
      Serial.print(status);  //size in raw bytes
      Serial.print(F(" "));
      serialWriteHexStr(bufferData, status); // hex string containing the data (size is twice the one given)
      Serial.println(F(")"));
    }

    //detectNewTag(true); //to avoid a strange bug -- the tag disconnects after reading -- didn't work
  }
  //// WRITE TO TAG ////  (ex. para escrever JOSE: (w 16 12345678 4 4A4F5345))
  else if (option == 'w') {
    if (!rfidStarted) {
      strRfidTurnedOff[1] = (char)option;
      Serial.println(strRfidTurnedOff);
      return;
    }
    if (!tagSelected) {
      strNoTagSelected[1] = (char)option;
      Serial.println(strNoTagSelected);
      return;
    }
    
    Serial.print(F("(w "));
    int blockAddr = serialParseUint(2);       //read block
    if (blockAddr < 0) { Serial.println(F(")")); return; }

    bool parseOk = serialParseHexStr(bufferMagicNum, 4);   //read magic number
    if (!parseOk) { Serial.println(F(")")); return; }
    
    int dataSize = serialParseUint(4);        //read number of bytes (to be parsed from a hex string twice as big)
    if (dataSize < 0) { Serial.println(F(")")); return; }

    parseOk = serialParseHexStr(bufferData, dataSize);  //read bytes
    if (!parseOk) { Serial.println(F(")")); return; }

    serialReadByte(); //just to read the final ')', but don't need to check it
    
    int status = writeToMifareTag(bufferMagicNum, bufferData, dataSize, &mfrc522, &key, blockAddr);
    
    if (status < 0) {
      Serial.print(F("Error in tag: "));
      Serial.print(status);
      Serial.println(F(")"));
    } else {
      Serial.println(F("OK)"));
    }
    
  }
  //// INVALID COMMAND ////
  else {
    Serial.print(F("(g Invalid command: "));
    Serial.print((char)option);
    Serial.println(F(")"));

  }

}

bool arrayEquals(byte* array1, byte* array2, int length) {
  for (int i = 0; i < length; i++) {
    if (array1[i] != array2[i]) {
      return false;
    }
  }
  return true;
}

bool detectNewTag(bool forceAnswer) {
  bool newTagDetected = detectAndSelectMifareTag(&mfrc522) || detectAndSelectMifareTag(&mfrc522); //try 2x, at most

  if (newTagDetected) {
    //there was no tag selected before, or a different one was now detected (OR if forced to answer)
    if (!tagSelected || !arrayEquals(mfrc522.uid.uidByte, tagUid, 4)
          || forceAnswer) {
      Serial.print(F("(tag "));
      for (int i = 0; i < 4; i ++) {
        Serial.print(mfrc522.uid.uidByte[i], HEX);
        tagUid[i] = mfrc522.uid.uidByte[i];
      }
      Serial.println(F(")"));  
    }
    tagSelected = true;
    //timerToReleaseTag.restart();
    return true;

  } else if (tagSelected || forceAnswer) {  //no new tag detected now, but there was a selected tag (OR if forced to answer)
    Serial.println(F("(tag not detected)"));
    unselectMifareTag(&mfrc522, true);
    //timerToReleaseTag.stop(); //no timeout occurs anymore
    tagSelected = false;

  }

  return false;
}

void showRfidReaderDetails() {
  byte v = mfrc522.PCD_ReadRegister(mfrc522.VersionReg); //get the MFRC522 software version
  Serial.print(F("MFRC522 sw version: "));
  if (v == 0x91) {
    Serial.print(F("v1.0"));
  } else if (v == 0x92) {
    Serial.print(F("v2.0"));
  } else if ((v == 0x00) || (v == 0xFF)) {
    Serial.print(F("communication failure")); //check physical connections and initialization parameters
  } else {
    Serial.print(F("unknown ")); //a chinese clone?
    Serial.print(v, HEX);
  }
}

PollingTimer readByteTimer(400); // waits 0.4 secs

inline int serialReadByte() {
  readByteTimer.restart();
  while (Serial.available() == 0) { 
    if (readByteTimer.timeoutOccured()) {
      return -1;
    }
  }
  return Serial.read();
}

inline int serialPeekByte() {
  readByteTimer.restart();
  while (Serial.available() == 0) { 
    if (readByteTimer.timeoutOccured()) {
      return -1;
    }
  }
  return Serial.peek();
}

/**
 * Parses from input a string representing an integer with up to 'maxDigits'.
 * Must start with a space.
 * No byte is consumed from input if it is in incorrect format.
 */
int serialParseUint(uint maxDigits) {
  if (serialReadByte() != ' ') {
    Serial.print(F("Error: no space char before int string"));
    return -1;
  }

  int c;
  int num = 0;
  
  for (uint i = 0; i < maxDigits; i ++) {
    c = serialPeekByte(); //char not consumed yet
    
    if (c >= '0' && c <= '9') {
      num = (num * 10) + (c - '0');
      Serial.read(); //consumes c from buffer
    } else if (c == ' ') {
      break;
    } else {
      Serial.print(F("Error: unexpected byte in int string"));
      return -1; //error
    }
  }
  
  c = serialPeekByte(); //char not consumed
  if (c >= '0' && c <= '9') {
    Serial.print(F("Error: too long integer"));
    return -1;
  }

  return num;
}

inline int hexToByte(char c) {
  if (c >= '0' && c <= '9') {
    return c - '0';
  } else if (c >= 'A' && c <= 'F') {
    return 10 + (c - 'A');
  } else if (c >= 'a' && c <= 'f') {
    return 10 + (c - 'a');
  } else {
    return -1;
  }
}


/* For each byte to be written to "data", two hexadecimal characters (two bytes)
 * are read from Serial. Input "dataSize" is given in bytes to be written (half the
 * number of hexa characters).
 * Must start with a space.
 * No byte is consumed from input if it is in incorrect format.
 */
bool serialParseHexStr(byte* data, uint dataSize) {
  int ibyte[2];

  if (serialReadByte() != ' ') {
    Serial.print(F("Error: no space char before hex string"));
    return false;
  }

  int c;
  for (uint i = 0; i < dataSize; i++) {
    for (uint k = 0; k < 2; k++) {
      if ((c = serialPeekByte()) == -1) {
        Serial.print(F("Missing byte (timeout)"));  //data not received for too long
        return false;
      }
      ibyte[k] = hexToByte(c); //attention: char not consumed yet
      if (ibyte[k] == -1) { 
        Serial.print(F("Error in hex string"));  //data in wrong format
        return false;
      } else {
        Serial.read(); //consumes the parsed char
      }
    }
    data[i] = byte( (ibyte[0] << 4) | ibyte[1] );
  }

  if (hexToByte(serialPeekByte()) > 0) {
    Serial.print(F("Error: too long hex string"));
    return false;
  }
  
  return true;
}


#define HEX_STR_BUFFER 128   // in number of raw bytes (not in hex digits)

inline char byteToHex(byte b) {
  if (b >= 0 && b <= 9) {
    return '0' + b;
  } else if (b >= 10 && b <= 15) {
    return 'A' + (b - 10);
  } else {
    return -1;
  }
}

/**
 * Outuputs to Serial the given data as a hexadecimal ASCII string.
 */
void serialWriteHexStr(byte* data, int dataSize) {  
  static byte serialHexBuffer[2 * HEX_STR_BUFFER];

  int remainingBytes = dataSize;
  while (remainingBytes > 0) {
    int bytesToSend = min(HEX_STR_BUFFER, remainingBytes);
    for (int i = 0; i < bytesToSend; i++) {
      serialHexBuffer[2*i] = byteToHex(data[i] >> 4);
      serialHexBuffer[2*i+1] = byteToHex(data[i] & 0x0F);
    }
    Serial.write(serialHexBuffer, 2*bytesToSend);
    remainingBytes -= bytesToSend;
  }
}
