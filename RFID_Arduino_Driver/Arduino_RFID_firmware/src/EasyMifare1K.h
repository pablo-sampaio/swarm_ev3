
#ifndef __EASY_MIFARE_H__
#define __EASY_MIFARE_H__

#include <MFRC522.h>
#define uint unsigned int

/**
 * This library is a wrapper for <MFRC522.h> that provides functions to easily read from and write to Mifare 1KB Classic tags.
 * 
 * It assumes that all sectors and blocks are authenticated with the same keys and that all blocks are in "transport configuration"
 * (therefore, read and write operations can be done using anyone of the keys).
 * 
 * Before any operation, the MFRC522 object must be initialized with "PCD_Init()" member function.
 * 
 * Each chunk of data (that may span for any number of blocks) starts with an user-defined sequence of 4 bytes, called here "magic 
 * number". It is just a data identifier. After the magic number, the library writes the size of the data chunk (in number of bytes).
 * 
 * The data is written and read by giving the magic number and the block where the data starts. The library reads the size of the 
 * data and access all non-trailer blocks in sequence, as necessary.
 * 
 * Pablo A. Sampaio, 2018
 */

bool detectAndSelectMifareTag(MFRC522 *mfrc522);
void unselectMifareTag(MFRC522 *mfrc522, bool allowRedetection = true);

int writeToMifareTag(const byte magicNumber[4], byte* data, uint dataSize, MFRC522* rfidSensor, MFRC522::MIFARE_Key* keyA, byte initialBlock);

int readSizeFromMifareTag(MFRC522* rfidSensor, MFRC522::MIFARE_Key* key, byte initialBlock, const byte magicNumber[4]);
int readFromMifareTag(MFRC522* rfidSensor, MFRC522::MIFARE_Key* key, byte initialBlock, const byte magicNumber[4], byte* dataOutput, uint dataOutputMaxSize);

void setNumberOfReadWriteTrials(byte num);
int getNumberOfReadWriteTrials();


#endif
