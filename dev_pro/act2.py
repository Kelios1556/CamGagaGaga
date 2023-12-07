#include "mbed.h"
#include "stdint.h" //This allow the use of integers of a known width
#define LM75_REG_TEMP (0x00) // Temperature Register
#define LM75_REG_CONF (0x01) // Configuration Register
#define LM75_ADDR     (0x90) // LM75 address

#define LM75_REG_TOS (0x03) // TOS Register
#define LM75_REG_THYST (0x02) // THYST Register

Ticker cycle_ticker, alarming_ticker;
float cycle_time_interval = 1, alarming_time_interval = 0.1;

I2C i2c(I2C_SDA, I2C_SCL);

DigitalOut green(LED1);
DigitalOut blue(LED2);
DigitalOut red(LED3);

InterruptIn lm75_int(D7); // Make sure you have the OS line connected to D7

Serial pc(SERIAL_TX, SERIAL_RX);

static const int INTERVAL = 60;
int16_t i16[INTERVAL]; // This variable needs to be 16 bits wide for the TOS and THYST conversion to work - can you see why?
// int16_t *index = i16;
char data_write[3];
char data_read[3];

void onCycleTicker(int16_t* &idx)
{
    // Calculate temperature value in Celcius
    *idx = (data_read[0] << 8) | data_read[1];
    idx++;
}

class CycleTickerCallback {
public:
    explicit CycleTickerCallback(int16_t*& index) : index(index) {}

    void operator()() {
        onCycleTicker(index);
    }

private:
    int16_t*& index;
};

void onAlarmTicker(void)
{
    red = true;
    blue = !blue;
    green = !green;
}

void alarm(bool *al)
{
    if (!*al) {
        *al = true;
    }
    // The instruction below may create problems on the latest mbed compilers.
    // Avoid using printf in interrupts anyway as it takes too long to execute.
    // pc.printf("Interrupt triggered!\r\n");
}



void config(void)
{
    data_write[0] = LM75_REG_CONF;
    data_write[1] = 0x02;
    int status = i2c.write(LM75_ADDR, data_write, 2, 0);
    if (status != 0)
    { // Error
        while (1)
        {
            green = !green;
            wait(0.2);
        }
    }

    float tos=22; // TOS temperature
    float thyst=-55; // THYST tempertuare

    // This section of code sets the TOS register
    data_write[0]=LM75_REG_TOS;
    int16_t ii;
    ii = (int16_t)(tos*256) & 0xFF80;
    data_write[1]=(ii >> 8) & 0xff;
    data_write[2]=ii & 0xff;
    i2c.write(LM75_ADDR, data_write, 3, 0);

    //This section of codes set the THYST register
    data_write[0]=LM75_REG_THYST;
    ii = (int16_t)(thyst*256) & 0xFF80;
    data_write[1]=(ii >> 8) & 0xff;
    if (thyst < 0) {
        data_write[1] |= 0x80;
    }
    data_write[2]=ii & 0xff;
    i2c.write(LM75_ADDR, data_write, 3, 0);
}

int main()
{
    bool alarming = false, sending = false, loop = false;
    for (int i = 0; i < INTERVAL; i++) {
        i16[i] = 0;
    }
    /* Configure the Temperature sensor device STLM75:
        - Thermostat mode Interrupt
        - Fault tolerance: 0
        - Interrupt mode means that the line will trigger when you exceed TOS and stay triggered until a register is read - see data sheet
    */
    config();
    green = true;

    // This line attaches the interrupt.
    // The interrupt line is active low so we trigger on a falling edge
    lm75_int.fall(callback(alarm, &alarming));
    int16_t *index = i16;
    CycleTickerCallback cycleTickerCallback(index);
    cycle_ticker.attach(cycleTickerCallback, cycle_time_interval);

    while (1)
    {
        data_write[0] = LM75_REG_TEMP;
        i2c.write(LM75_ADDR, data_write, 1, 1); // no stop
        i2c.read(LM75_ADDR, data_read, 2, 0);
        if (index - i16 == INTERVAL) {
            index = i16;
            // pc.printf("data full!\n");
            loop = true;
        }
        if (alarming && sending == false) {
            // pc.printf("%f\n", ((data_read[0] << 8) | data_read[1]) / 256.0);
            cycle_ticker.detach();
            alarming_ticker.attach(onAlarmTicker, alarming_time_interval);
            sending = true;
            int16_t *temp = NULL;
            if (loop) {
                temp = index;
            } else {
                temp = i16;
            }
            while (temp-i16 < INTERVAL) {
                if (loop) {
                    pc.printf("temperature at %d(%d)s: %f\n", temp-index+1, temp-i16+1, *temp / 256.0);
                } else {
                    pc.printf("temperature at %ds: %f\n", temp-i16+1, *temp / 256.0);
                }
                temp++;
            }
            if (loop) {
                temp = i16;
                while (temp < index) {
                    pc.printf("temperature at %d(%d)s: %f\n", (i16+INTERVAL-index+temp-i16+1), temp - i16+1, *temp / 256.0);
                    temp++;
                }
            }
        }
        wait(0.9);
    }

}
