
#include <SPI.h>
#include <MFRC522.h>

#include "EasyMifare1K.h"

#define uint unsigned int

static byte blockBuffer[18] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
static byte readWriteTrials = 5;

//#define SHOW_DEBUG_MESSAGES 1 //uncomment this line to enable messages

#ifdef SHOW_DEBUG_MESSAGES
  #define dbgPrintln(str) Serial.println(str)
  #define dbgPrint(str) Serial.print(str)
#else
  #define dbgPrintln(str) (0)
  #define dbgPrint(str) (0)
#endif


/////////////////////////////////////////////////////////////
////////// CONNECT / DISCONNECT / CONFIG FUNCTIONS //////////

bool detectAndSelectMifareTag(MFRC522 *mfrc522) {
  if (! mfrc522->PICC_IsNewCardPresent()) // Look for new cards/tags
    return false;

  if (! mfrc522->PICC_ReadCardSerial())  // Select one of the cards/tags
      return false;

  MFRC522::PICC_Type piccType = mfrc522->PICC_GetType(mfrc522->uid.sak);
  
  if (piccType != MFRC522::PICC_TYPE_MIFARE_1K) {
    return false;
  }

  return true;
}

void unselectMifareTag(MFRC522 *mfrc522, bool allowRedetection) {
  mfrc522->PICC_HaltA();      // Set PICC to HALT status
  mfrc522->PCD_StopCrypto1(); // Stop authentication
  if (allowRedetection) {
    mfrc522->PCD_AntennaOff();
    mfrc522->PCD_AntennaOn();
  }
}

/**
 * Sets/gets the number of times that read or write or authentication operations
 * are repeated when errors occur.
 */
void setNumberOfReadWriteTrials(byte num) {
  if (num == 0) {
    dbgPrintln("Invalid number of read/write trials");
    return;
  }
  readWriteTrials = num;
}

int getNumberOfReadWriteTrials() {
  return readWriteTrials;
}


/////////////////////////////////////
////////// WRITE FUNCTIONS //////////

//auxiliary (not exported by the header)
void prepareInitialBlockInBuffer(const byte magicNum[4], uint datasize);
bool writeBlockAndVerify(byte* data, int startIndex, int bytesToWrite, MFRC522 *mfrc522, int blockAddr);
bool verifyBlock(MFRC522 *mfrc522, byte blockAddr, byte* refData, byte startByte, byte bytesToCheck);

/**
 * Writes the given "data" array (with "dataSize" bytes) in the Mifare 1K tag, starting in "initialBlock" (or in the next one, if it is a 
 * trailer block) and successively writing to the next non-trailer block, until all data is written. 
 * Indeed, in the initial block itself, a identification of this data array is written, followed by the "dataSize". The identification is 
 * given by the fours bytes given in "magicNum". You may choose any 4-byte sequence to identify your data, but the same data must be used
 * to retrieve the data with "readFromMifareTag()".
 * 
 * The tag must have been detected and selected by the MFRC522 sensor (e.g. using "detectAndSelectMifareTag()").
 * There is no need to authenticate in the tag prior to calling this function.
 * This function does not stop authentication (so, in case of success, the tag is still authenticated in the sector of the last block written). 
 * 
 * Returns: negative number -- error
 *          positive number -- last block written
 */
int writeToMifareTag(const byte magicNumber[4], byte* data, uint dataSize, MFRC522* rfidSensor, MFRC522::MIFARE_Key* key, byte initialBlock) {
  MFRC522::StatusCode status;

  if (initialBlock % 4 == 3) { //it is a trailer block --> better don't write there
    initialBlock ++;
  }

  for (int i = 0; i < readWriteTrials; i ++) {
    status = rfidSensor->PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, initialBlock, key, &(rfidSensor->uid)); //authenticate is not done in the trailer --> ok, it worked
    if (status == MFRC522::STATUS_OK) {
      break;
    }
    dbgPrintln(F("    na"));
  }
  if (status != MFRC522::STATUS_OK) {
    dbgPrintln("Error writeToMifareTag() #1: could not authenticate");
    return -1;
  }

  bool success;

  prepareInitialBlockInBuffer(magicNumber, dataSize);
  for (int i = 0; i < readWriteTrials; i ++) {
    success = writeBlockAndVerify(blockBuffer, 0, 16, rfidSensor, initialBlock); //attention: don't change to write less than 16, because, in writeBlockAndVerify, 
                                                                                 //blockBuffer is used again in such case (i.e., would occur a strange 'name alias' situation)
    if (success) {
      break;
    }
  }
  if (!success) {
    dbgPrintln("Error writeToMifareTag() #2: could not write initial block");
    return -2;
  }

  int bytesWritten = 0;  
  int currBlock = initialBlock + 1;
  int currSector = currBlock / 4;
  bool sectorAuthenticated = true; //authentication in this sector was already done above
  
  while (bytesWritten < dataSize) {
    if (currBlock % 4 == 3) {
      dbgPrint("   - Trailer block (ignored): "); dbgPrintln(currBlock);
      currBlock ++;
      currSector ++;
      sectorAuthenticated = false; //because the sector changed
    }

    if (currBlock > 63) {
      dbgPrint("Error writeToMifareTag() #5: not enough space");
      return -5;
    }

    if (! sectorAuthenticated) {
      dbgPrint("   - Authenticating sector: "); dbgPrintln(currSector); 
      for (int i = 0; i < readWriteTrials; i ++) {
        status = rfidSensor->PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, currBlock, key, &(rfidSensor->uid));
        if (status == MFRC522::STATUS_OK) {
          break;
        }
        dbgPrintln(F("    na"));
      }
      if (status != MFRC522::STATUS_OK) {
        dbgPrint("Error writeToMifareTag() #3: could not authenticate, block "); dbgPrintln(currBlock);
        return -3;
      }
      sectorAuthenticated = true;
    }

    int bytes = dataSize - bytesWritten;
    bytes = (bytes < 16)? bytes : 16;
    for (int i = 0; i < readWriteTrials; i ++) {
      success = writeBlockAndVerify(data, bytesWritten, bytes, rfidSensor, currBlock);
      if (success) {
        bytesWritten += bytes;
        break;
      }
    }
    if (!success) {
      dbgPrint("Error writeToMifareTag() #4: could not write block "); dbgPrintln(currBlock);
      return -4;
    }

    currBlock ++;
  }

  return currBlock - 1;
}

void prepareInitialBlockInBuffer(const byte magicNum[4], uint datasize) {
  blockBuffer[0] = magicNum[0];
  blockBuffer[1] = magicNum[1];
  blockBuffer[2] = magicNum[2];
  blockBuffer[3] = magicNum[3];
  
  blockBuffer[4] = byte(datasize);
  blockBuffer[5] = byte(datasize >> 8);

  for (int i = 6; i < 16; i ++) {
    blockBuffer[i] = 0x00;
  }
}

bool writeBlockAndVerify(byte* data, int startIndex, int bytesToWrite, MFRC522 *mfrc522, int blockAddr) {
  MFRC522::StatusCode status;
  if (bytesToWrite == 16) {
    status = mfrc522->MIFARE_Write(blockAddr, data + startIndex, 16);
    if (status != MFRC522::STATUS_OK) {
      dbgPrintln("Error writeBlockAndVerify() #1a: could not write");
      return false;
    }

    return verifyBlock(mfrc522, blockAddr, data, startIndex, 16); //verifies block written in the tag against the data array (positions 0-16)
    
  } else if (0 < bytesToWrite && bytesToWrite < 16) {
    //copies to the buffer before writing
    for (int i = 0; i < bytesToWrite; i ++) {
      blockBuffer[i] = data[startIndex + i];
    }
    for (int i = bytesToWrite; i < 16; i ++) { //the buffer is completed with 0s
      blockBuffer[i] = 0;
    }
    
    status = mfrc522->MIFARE_Write(blockAddr, blockBuffer, 16);
    if (status != MFRC522::STATUS_OK) {
      dbgPrintln("Error writeBlockAndVerify() #1b: could not write");
      return false;
    }

    return verifyBlock(mfrc522, blockAddr, blockBuffer, 0, bytesToWrite); //verifies block written in the tag against the buffer (positions 0-bytesToWrite)
    
  } else {
    dbgPrintln("Error writeBlockAndVerify() #2: invalid data size");
    return false;
    
  }
}

bool verifyBlock(MFRC522 *mfrc522, byte blockAddr, byte* refData, byte startByte, byte bytesToCheck) {
  byte bufferSize = 18;
  MFRC522::StatusCode status = mfrc522->MIFARE_Read(blockAddr, blockBuffer, &bufferSize);
  if (status != MFRC522::STATUS_OK) {
      dbgPrintln("Error verifyBlock() #1: could not read");
      return false;
  }

  for (byte i = 0; i < bytesToCheck; i++) {
      if (blockBuffer[i] != refData[startByte + i]) {
        dbgPrint("Error verifyBlock() #2: verification error in byte: ");
        dbgPrintln(i);
        return false;
      }
  }

  return true;
}


////////////////////////////////////
////////// READ FUNCTIONS //////////

//auxiliary functions (not exported by the header)
bool readBlock(MFRC522* rfidSensor, byte block, byte* destiny, byte firstIndex, byte bytesToRead);

/**
 * Reads the identification block, checking in it is properly identified with the given magic number, then
 * parses and returns the size of the data stored in the remaining blocks.
 * 
 * Returns: negative number -- error
 *          positive number -- the size of the data stored (starting from the next block, not counting trailling blocks)
 */
int readSizeFromMifareTag(MFRC522* rfidSensor, MFRC522::MIFARE_Key* key, byte initialBlock, const byte magicNumber[4]) {
  MFRC522::StatusCode status;

  if (initialBlock % 4 == 3) { //it is a trailer block --> go to the next
    initialBlock ++;
  }

  for (int i = 0; i < readWriteTrials; i ++) {
    status = rfidSensor->PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, initialBlock, key, &(rfidSensor->uid));
    if (status == MFRC522::STATUS_OK) {
      break;
    }
    dbgPrintln(F("    na"));
  }
  if (status != MFRC522::STATUS_OK) {
    dbgPrintln("Error readSizeFromMifareTag() #1: could not authenticate");
    return -1;
  }

  byte bufferSize = 18;
  for (int i = 0; i < readWriteTrials; i ++) {
    status = rfidSensor->MIFARE_Read(initialBlock, blockBuffer, &bufferSize);
    if (status == MFRC522::STATUS_OK) {
      break;
    }
  }
  if (status != MFRC522::STATUS_OK) {
    dbgPrintln("Error readSizeFromMifareTag() #2: could not read");
    return -2;
  }
  
  if (blockBuffer[0] != magicNumber[0] || blockBuffer[1] != magicNumber[1]
      || blockBuffer[2] != magicNumber[2] || blockBuffer[3] != magicNumber[3]) {
    dbgPrintln("Error readSizeFromMifareTag() #3: magic number don't match");
    return -3;
  }

  int dataSize = ((uint)blockBuffer[5] << 8) | (uint)blockBuffer[4];
  return dataSize;
}

/**
 * Reads the data starting in the given initial block, when it also checks if the data is properly identified with the given magic number, 
 * then copies the data stored in the following blocks to "dataOutput". Returns the number of bytes read. 
 * 
 * See more details in the comments to writeToMifareTag().
 * 
 * The "dataOutput" must be previously allocated, with enough room ("dataOutputMaxSize") for the data read from the tag.
 * The tag must have been detected and selected by the MFRC522 sensor (e.g. using "detectAndSelectMifareTag()").
 * There is no need to authenticate in the tag prior to calling this function.
 * This function does not stop authentication (so, in case of success, the tag is still authenticated in the sector of the last block read). 
 * 
 * Returns: negative number -- error
 *          positive number -- number of bytes read (from the tag to the output array)
 */
int readFromMifareTag(MFRC522* rfidSensor, MFRC522::MIFARE_Key* key, byte initialBlock, const byte magicNumber[4], byte* dataOutput, uint dataOutputMaxSize) {
  MFRC522::StatusCode status;

  if (initialBlock % 4 == 3) { //it is a trailer block --> go to the next (attention: this is done in readSizeFromMifareTag(), but should be kept here too, because of special cases, e.g. initialBlock = 3) and these functions are called successively)
    initialBlock ++;
  }

  int dataSize = readSizeFromMifareTag(rfidSensor, key, initialBlock, magicNumber);
  if (dataSize < 0) {
    dbgPrintln("Error in readFromMifareTag() #1/#2/#3: initial block error");
    return dataSize; //errors -1 to -3
  } else if (dataOutputMaxSize < dataSize) {
    dbgPrintln("Error in readFromMifareTag() #4: not enough room in the given output buffer");
    return -4;
  }

  dbgPrint(" -- data size: "); dbgPrintln(dataSize);
  int bytesRead = 0;
 
  int currBlock = initialBlock + 1;
  int currSector = currBlock / 4;
  bool sectorAuthenticated = true; //authentication in this sector was already done in readSizeFromMifareTag()
  
  while (bytesRead < dataSize) {      
    if (currBlock % 4 == 3) {
      dbgPrint("   - Trailer block (ignored): "); dbgPrintln(currBlock);
      currBlock ++;
      currSector ++;
      sectorAuthenticated = false; //because the sector changed
    }

    if (currBlock > 63) {
      dbgPrint("Error readFromMifareTag() #5: end of tag's memory reached");
      return -5;
    }

    if (! sectorAuthenticated) {
      dbgPrint("   - Authenticating sector: "); dbgPrintln(currSector); 

      for (int i = 0; i < readWriteTrials; i ++) {
        status = rfidSensor->PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, currBlock, key, &(rfidSensor->uid));
        if (status == MFRC522::STATUS_OK) {
          break;
        }
        dbgPrintln(F("    na"));
      }
      if (status != MFRC522::STATUS_OK) {
        dbgPrint("Error readFromMifareTag() #6: could not authenticate block "); dbgPrintln(currBlock);
        return -6;
      }
      sectorAuthenticated = true;
    }

    bool success;
    int bytes = dataSize - bytesRead;
    bytes = (bytes < 16)? bytes : 16;
    
    for (int i = 0; i < readWriteTrials; i ++) {
      success = readBlock(rfidSensor, currBlock, dataOutput, bytesRead, bytes);
      if (success) {
        bytesRead += bytes;
        break;
      }
    }
    if (!success) {
      dbgPrint("Error readFromMifareTag() #7: could not read block "); dbgPrintln(currBlock);
      return -7;
    }

    currBlock ++;
  }

  return dataSize;
}

bool readBlock(MFRC522* rfidSensor, byte block, byte* destiny, byte firstIndex, byte bytesToRead) {
  MFRC522::StatusCode status;
  byte bufferSize = 18;

  status = rfidSensor->MIFARE_Read(block, blockBuffer, &bufferSize);
  if (status != MFRC522::STATUS_OK) {
    dbgPrint("Error readBlock() #1: could not read");
    return false;
  }

  if (bytesToRead < 0 || bytesToRead > 16) {
    dbgPrint("Error readBlock() #2: invalid size");
    return false;
  }

  for (int i = 0; i < bytesToRead; i ++) {
    destiny[firstIndex + i] = blockBuffer[i];
  }

  return true;
}

