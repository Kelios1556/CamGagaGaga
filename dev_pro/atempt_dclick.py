#include "mbed.h"

DigitalOut led1(LED1);
DigitalOut led2(LED2);
DigitalOut led3(LED3);

Timeout button_debounce_timeout;
float debounce_time_interval = 0.1;

InterruptIn button(USER_BUTTON);

Ticker led_ticker;
float led_time_interval = 1;

Timer click_timer;

static const int N = 5;
int t = 0; // which light is ON
int *colors = (int *)malloc(sizeof(int)*N);
int* c = colors;
bool play_flag = false;

Serial pc(SERIAL_TX, SERIAL_RX);

void select_led(int l)
{
    if (l==1) {
        led1 = true;
        led2 = false;
        led3 = false;
    }
    else if (l==2) {
        led1 = false;
        led2 = true;
        led3 = false;
    }
    else if (l==3) {
        led1 = false;
        led2 = false;
        led3 = true;
    }
}

void onButtonStopDebouncing(void);
void onPlayLED(void)
{
    if (play_flag) {
        play_flag = false;
        button.rise(NULL);
        int *index = colors;
        pc.printf("c - colors: %d\n", c-colors);
        pc.printf("colors size: %d\n", int(sizeof(colors)));
        while (index < c) {
            pc.printf("%d: ", index-c);
            pc.printf("%d ", *index);
            select_led(*index);
            index++;
            wait_us(300000);
        }
        index=NULL;
        pc.printf("\n");
    }
}
void onLEDTicker(void)
{
    t = (t%3) + 1;
    select_led(t);
}
void onButtonPress(void)
{
    if (click_timer.read_ms() < 300) {
        //pc.printf("time: %d\n", click_timer.read_ms());
        click_timer.stop();
        click_timer.reset();
        play_flag=true;
    }
    else {
        //pc.printf("time: %d\n", click_timer.read_ms());
        click_timer.stop();
        click_timer.reset();
        click_timer.start();
        *c = t;
        c++;
        button.rise(NULL);
        button_debounce_timeout.attach(onButtonStopDebouncing, debounce_time_interval);
    }
}

void onButtonStopDebouncing(void)
{
    button.rise(onButtonPress);
}


int main()
{
    button.rise(onButtonPress);
    led_ticker.attach(onLEDTicker, led_time_interval);
    while (true) {
        // if (c - colors == sizeof(colors)) {
        if (play_flag) {
            // button_debounce_timeout.detach();
            led_ticker.detach();
            // play_flag = true;
            onPlayLED();
            free(colors);
            colors = (int *)malloc(sizeof(int)*N);
            c = colors;
            led_ticker.attach(onLEDTicker, led_time_interval);
            // button_debounce_timeout.attach(onButtonStopDebouncing, debounce_time_interval);
        }
        if (c - colors == sizeof(colors)) {
            colors = (int*)realloc(colors, sizeof(colors) + sizeof(int)*N);
            if (colors == NULL) {
                free(colors);
                pc.printf("no enough space!\n");
                exit(0);
            }
        }
    }
    // Even more important code could be placed here

}
