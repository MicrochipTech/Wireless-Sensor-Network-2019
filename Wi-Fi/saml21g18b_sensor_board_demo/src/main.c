/**
 * \file
 *
 * \brief main file
 *
 * Copyright (c) 2015 Atmel Corporation. All rights reserved.
 *
 * \asf_license_start
 *
 * \page License
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * 3. The name of Atmel may not be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * 4. This software may only be redistributed and used in connection with an
 *    Atmel microcontroller product.
 *
 * THIS SOFTWARE IS PROVIDED BY ATMEL "AS IS" AND ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT ARE
 * EXPRESSLY AND SPECIFICALLY DISCLAIMED. IN NO EVENT SHALL ATMEL BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *
 * \asf_license_stop
 *
 */

/*
 * Support and FAQ: visit <a href="http://www.atmel.com/design-support/">Atmel
 * Support</a>
 */

/*- Includes ---------------------------------------------------------------*/
#include <asf.h>
#include "platform.h"
#include "at_ble_api.h"
#include "console_serial.h"
#include "timer_hw.h"
#include "conf_serialdrv.h"
#include "conf_board.h"
#include "wearable.h"
#include "touch_api_ptc.h"
#include "touch_app.h"
#include "rtc.h"
#include "bme280\bme280_support.h"
#include "conf_sensor.h"
#include "veml60xx\veml60xx.h"
#include "bhi160.h"
#include "bhi160\bhy_uc_driver.h"
#include "i2c.h"
#include "serial_drv.h"
#include "adc_measure.h"
#include "driver/include/m2m_wifi.h"
#include "socket/include/socket.h"
#include "main.h"
#include "led.h"
#include "env_sensor.h"
#include "motion_sensor.h"
#include "button.h"
#include "nvm_handle.h"
#include "winc15x0.h"
#include "cloud_wrapper.h"
#include "iot_message.h"


/* enum variable */
enum status_code veml60xx_sensor_status = STATUS_ERR_NOT_INITIALIZED;

/* variables */
BME280_RETURN_FUNCTION_TYPE bme280_sensor_status = ERROR;
int cloudConnecting =0;
	
/* function prototypes */
void configure_wdt(void);

void enable_gclk1(void);

/** SysTick counter to avoid busy wait delay. */
//volatile uint32_t ms_ticks = 0;



/* Watchdog configuration */
void configure_wdt(void)
{
	/* Create a new configuration structure for the Watchdog settings and fill
	* with the default module settings. */
	struct wdt_conf config_wdt;
	wdt_get_config_defaults(&config_wdt);
	/* Set the Watchdog configuration settings */
	config_wdt.always_on = false;
	//config_wdt.clock_source = GCLK_GENERATOR_4;
	config_wdt.timeout_period = WDT_PERIOD_2048CLK;
	/* Initialize and enable the Watchdog with the user settings */
	wdt_set_config(&config_wdt);
}



void enable_gclk1(void)
{
	struct system_gclk_gen_config gclk_conf;
	
	system_gclk_init();	
	gclk_conf.high_when_disabled = false;
	gclk_conf.source_clock       = GCLK_SOURCE_OSC16M;
	gclk_conf.division_factor = 1;
	gclk_conf.run_in_standby  = true;
	gclk_conf.output_enable   = false;
	system_gclk_gen_set_config(2, &gclk_conf);
	system_gclk_gen_enable(2);
}





/**
 * \brief SysTick handler used to measure precise delay. 
 */
//void SysTick_Handler(void)
//{
//	ms_ticks++;
//	printf("DBG log1\r\n");
//}


void IoTSensorBoardInit()
{	
	/* initialize LED */
	initialise_led();
	led_ctrl_set_color(LED_COLOR_BLUE, LED_MODE_BLINK_NORMAL);
	
	/* initialize RTC for sleep-wakeup operation*/
	rtc_init();
	
	/* SAMD21 system initialization */
	system_init();
	
	/* set sleep mode to backup for deep sleep */
	system_set_sleepmode(SYSTEM_SLEEPMODE_BACKUP);
	
	/*i2c configure, needed for sensor data read*/
	configure_sensor_i2c();
	
	/* Initialize serial console for debugging */
	serial_console_init();

	/* Hardware timer */
	hw_timer_init();
	
	/* delay routine initialization */
	delay_init();

	nvm_init();
	
	//Initialize bme280
	wearable_bme280_init();

	
	/* configure adc for battery measurement */
	configure_adc();
	read_battery_voltage();

	delay_ms(10);
	check_temperature_update();
	/* Initialize the BSP. */
	nm_bsp_init();	
}
bool aws_iot_is_mqtt_connected(void);

/* main function */
int main(void)
{
	Cloud_RC ret = CLOUD_RC_NONE_ERROR;
	
	// IoT sensor board sensors initialization
	IoTSensorBoardInit();

	// Init Wi-Fi (WINC1500) & Crypto Auth (ECC608)
	wifiCryptoInit();

	
	while (1) {
		
		/* Handle pending events from network controller. */
		m2m_wifi_handle_events(NULL);

		/*
			 Step 1: Connect to AWS IoT Core:
		 
				1. Code below establish a secure connection to AWS IoT Core.
				2. WINC1500 will send the device certificate chain to AWS.
				3. Upon reception of the device certificate, AWS will recognize the CA and invoke the lambda function .
				4. The lambda function will create a new thing the first time you try to connect.
				5. First connection will fail while AWS lambda create the thing, second connection will work.
				5. login to your AWS console and observe the lambda invocation and welcome the new thing.
		*/		
#if 1
		if(receivedTime && !cloudConnecting){
			cloudConnecting = 1;
			
			ret = cloud_connect();

			if (ret == CLOUD_RC_SUCCESS)
			{
				led_ctrl_set_mode(LED_MODE_TURN_ON);
				cloudConnecting = 2;
				printf("connected to AWS IoT Cloud ...\r\n");
			}
			else
			{
				printf("\r\nCloud connect fail...\r\n");
				led_ctrl_set_color(LED_COLOR_RED, LED_MODE_BLINK_NORMAL);
				led_ctrl_set_mode(LED_MODE_TURN_ON);
				// Tough luck, try next time
				socketDeinit();
				m2m_wifi_deinit(NULL);
				nm_bsp_deinit();
				rtc_init();
				system_sleep();				
			}

		}
#endif

		/*
			 Step 2: Communicate with AWS IoT Core:
		 
				1. Code below subscribe to a topic in AWS IoT Core.
				2. The topic name is wifiSensorBoard/�your_thing_name�/dataControl
				3. After enabling the code, you can start publishing to the the above topic and receive the data here.
		*/	
#if 0
		if(cloudConnecting == 2){
			cloudConnecting = 3;
			ret = cloud_mqtt_subscribe(gSubscribe_Channel, MQTTSubscribeCBCallbackHandler);
			if (ret == CLOUD_RC_SUCCESS)
			{
				printf("subscribed to : %s\n", gSubscribe_Channel);
			}
			else
				printf("subscribe MQTT channel fail... %s\r\n",gSubscribe_Channel);
		}
#endif

		/*
			 Step 3: Communicate with AWS IoT Core:
		 
				1. Code below publish to a topic in AWS IoT Core.
				2. The topic name is wifiSensorBoard/�your_thing_name�/dataControl
				3. After enabling the code, you can start subscribe to the the above topic and receive the data on AWS IoT.
		*/	
#if 1
		if(cloudConnecting == 2){
			cloudConnecting = 4;
			env_sensor_execute();
		}
#endif

		cloud_mqtt_yield(10);
	}
	
}


