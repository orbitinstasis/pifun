/**

    Usage: Inject enable I2S commands through i2c safely and quickly 
            with verification within raspivid call 
    
    Copyright c Ben Kazemi 2017 

    Compile:  gcc test.c -std=gnu99 -o test

*/


#include <stdbool.h>

#include <time.h>

#include <getopt.h>
#include <string.h>

#include <signal.h>
#include <unistd.h>

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>

#include <sys/types.h>
#include <netinet/in.h>


#include <linux/i2c.h>
#include <linux/i2c-dev.h>


#define u8  uint8_t
#define u16 uint16_t
#define u32 uint32_t

#define CHECK_TIME 25000 
#define DELAY_TIME 650000 - CHECK_TIME

#define ADDRESS_0 0x0004
#define ADDRESS_1 0x8651

#define WRITE_0 0x0F37
#define WRITE_1 0x04

#define I2C_ADDR 0x0F				

static const char *device = "/dev/i2c-1";	

static int exit_on_error (const char *s)	
{ 	
    perror(s);
    abort();
    return -1;
} 

static void i2c_rd(int fd, uint16_t reg, uint8_t *values, uint32_t n)
{
    int err;
    uint8_t buf[2] = { reg >> 8, reg & 0xff };
    struct i2c_rdwr_ioctl_data msgset;
    struct i2c_msg msgs[2] = {
        {
            .addr = I2C_ADDR,
            .flags = 0,
            .len = 2,
            .buf = buf,
        },
        {
            .addr = I2C_ADDR,
            .flags = I2C_M_RD,
            .len = n,
            .buf = values,
        },
    };

    msgset.msgs = msgs;
    msgset.nmsgs = 2;

    err = ioctl(fd, I2C_RDWR, &msgset);
    if(err != msgset.nmsgs)
        printf("%s: reading register 0x%x from 0x%x failed, err %d\n",
            __func__, reg, I2C_ADDR, err);
}

static void i2c_wr(int fd, uint16_t reg, uint8_t *values, uint32_t n)
{
    uint8_t data[1024];
    int err, i;
    struct i2c_msg msg;
    struct i2c_rdwr_ioctl_data msgset;

    if ((2 + n) > sizeof(data))
        printf("i2c wr reg=%04x: len=%d is too big!\n",
            reg, 2 + n);

    msg.addr = I2C_ADDR;
    msg.buf = data;
    msg.len = 2 + n;
    msg.flags = 0;

    data[0] = reg >> 8;
    data[1] = reg & 0xff;

    for (i = 0; i < n; i++)
        data[2 + i] = values[i];

    msgset.msgs = &msg;
    msgset.nmsgs = 1;

    err = ioctl(fd, I2C_RDWR, &msgset);
    if (err != 1) {
        printf("%s: writing register 0x%x from 0x%x failed\n",
            __func__, reg, I2C_ADDR);
        return;
    }
}

static inline u8 i2c_rd8(int fd, u16 reg)
{
    u8 val;

    i2c_rd(fd, reg, &val, 1);

    return val;
}

static inline void i2c_wr8(int fd, u16 reg, u8 val)
{
    i2c_wr(fd, reg, &val, 1);
}

static inline u16 i2c_rd16(int fd, u16 reg)
{
    u16 val;

    i2c_rd(fd, reg, (u8 *)&val, 2);

    return val;
}

static inline void i2c_wr16(int fd, u16 reg, u16 val)
{
    i2c_wr(fd, reg, (u8 *)&val, 2);
}

static void DelayMicrosecondsNoSleep (int delay_us)
{
    long int start_time;
    long int time_difference;
    struct timespec gettime_now;

    clock_gettime(CLOCK_REALTIME, &gettime_now);
    start_time = gettime_now.tv_nsec;       //Get nS value
    while (1)
    {
        clock_gettime(CLOCK_REALTIME, &gettime_now);
        time_difference = gettime_now.tv_nsec - start_time;
        if (time_difference < 0)
            time_difference += 1000000000;              //(Rolls over every 1 second)
        if (time_difference > (delay_us * 1000))        //Delay for # nS
            break;
    }
}




int main(int argc, char *argv[])
{
    int i2c_fd = open("/dev/i2c-1", O_RDWR);;

    if (!i2c_fd) 
        exit_on_error ("Can't open I2C device");

    if(ioctl(i2c_fd, I2C_SLAVE, I2C_ADDR) < 0)
    {
        exit_on_error("Failed to set I2C address");
        return -1;
    }

    // i2c_wr16(i2c_fd, ADDRESS_0, 0xFFFF); // debug
    // int data = i2c_rd16(i2c_fd, ADDRESS_0);// debug
    // printf("%04x\n", data);// debug

    // i2c_wr8(i2c_fd, ADDRESS_1, 0xFF); // debug
    // data = i2c_rd8(i2c_fd, ADDRESS_1);// debug
    // printf("%04x\n", data);// debug

    DelayMicrosecondsNoSleep(DELAY_TIME);

    // for (u8 i = 0; i < 30; i++) // DEBUG
    // {
    //     i2c_wr8(i2c_fd, 0x0000, 0xFF);
    // }


    u8 loop_counter = 0;
    bool completed_audio_0 = false;
    bool completed_audio_1 = false;

loop: 

    loop_counter++;
    if (loop_counter > 8)
        exit_on_error ("Looped too many times");

    if (!completed_audio_0)
    {
        u16 data_0 = i2c_rd16(i2c_fd, ADDRESS_0);
        if (data_0 != WRITE_0)
        {
            DelayMicrosecondsNoSleep(CHECK_TIME);
            i2c_wr16(i2c_fd, ADDRESS_0, WRITE_0);
            if (i2c_rd16(i2c_fd, ADDRESS_0) == WRITE_0)
            {
                completed_audio_0 = true;
                printf("Audio Data 0 at %04x Re-Written\n", ADDRESS_0);
            } else
                goto loop;
        } else 
        {
            completed_audio_0 = true;
        }
    }

    if (!completed_audio_1)
    {
        u8 data_1 = i2c_rd8(i2c_fd, ADDRESS_1);
        if (data_1 != WRITE_1)
        {
            DelayMicrosecondsNoSleep(CHECK_TIME);
            i2c_wr8(i2c_fd, ADDRESS_1, WRITE_1);
            if (i2c_rd8(i2c_fd, ADDRESS_1) == WRITE_1)
            {
                completed_audio_1 = true;
                printf("Audio Data 1 at %04x Re-Written\n", ADDRESS_1);
            } else
                goto loop;
        } else 
        {
            completed_audio_1 = true;
        }
    }


    // printf("New data at Address: %04x, Data: %04x\n", ADDRESS_0, i2c_rd16(i2c_fd, ADDRESS_0));
    // printf("New data at Address: %04x, Data: %04x\n", ADDRESS_1, i2c_rd8(i2c_fd, ADDRESS_1));

    close(i2c_fd);

    return (0);
}
