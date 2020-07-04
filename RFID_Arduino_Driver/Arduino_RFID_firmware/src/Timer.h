/**
 * A simple timer, used by polling (not by callback).
 * Pablo A. Sampaio, 2018
 */

#ifndef TIMERS_H
#define TIMERS_H

#include <Arduino.h>

class PollingTimer  {
  private:
    unsigned long lastTickTime;
    unsigned long interval;   // interval in micros
    bool stopped;

  public:
    /**
	   * The first two parameters give the interval either in milliseconds or in microseconds.
     * The interval should be below 50 days, if using millis; or below 70 min, if using micros.
	   */
    PollingTimer(unsigned long interv, bool inMicros = false) {
      if (inMicros) {
        interval = interv;  //interv is already in micro seconds
      } else {
        interval = interv * 1000;  //otherwise, convert it
      }
      lastTickTime = micros();
      stopped = true;
    }

    /**
     * Restarts counting the time interval (given in the constructor),
     * from the current time.
     */
    void restart() {
      lastTickTime = micros();
      stopped = false;
    }

    /**
     * Stops the timer. Then checkTick() will always return false.
     */
    void stop() {
      stopped = true;
    }

    /**
     * Informs whether the interval was reached. Once it is reached, this function returns only
     * true, until reset() or stop() is called.
     *
     * This function should be called repeatedly by the client program. Intervals of a millisecond 
     * or less are recommended, for precision. Big intervals are allowed, with loss of precision,
     * but should not be close to half of the overflow time of the Arduino time function used 
     * (millis() or micros()).
     */
    bool timeoutOccured() {
      return (!stopped && (micros() - lastTickTime >= interval));  //ATENCAO: there is no roll over (overflow) problem --> negative result becomes positive with unsigned data
    }
};

#endif // TIMERS_H
