/**
 * \file
 * \brief ATXMEGA's ATCA Hardware abstraction layer for SWI interface over XMEGA UART drivers.
 *
 * Prerequisite: add UART Polled support to application in Atmel Studio
 *
 * \copyright Copyright (c) 2017 Microchip Technology Inc. and its subsidiaries (Microchip). All rights reserved.
 *
 * \page License
 *
 * You are permitted to use this software and its derivatives with Microchip
 * products. Redistribution and use in source and binary forms, with or without
 * modification, is permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * 3. The name of Microchip may not be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * 4. This software may only be redistributed and used in connection with a
 *    Microchip integrated circuit.
 *
 * THIS SOFTWARE IS PROVIDED BY MICROCHIP "AS IS" AND ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT ARE
 * EXPRESSLY AND SPECIFICALLY DISCLAIMED. IN NO EVENT SHALL MICROCHIP BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#include <stdlib.h>
#include <stdio.h>
#include "swi_uart_xmega_a3bu_asf.h"
#include "basic/atca_helpers.h"

#define DEBUG_PIN 1

#ifdef DEBUG_PIN
    #define DEBUG_PIN_1 IOPORT_CREATE_PIN(PORTB, 0)
    #define DEBUG_PIN_2 IOPORT_CREATE_PIN(PORTB, 1)
#endif
/** \defgroup hal_ Hardware abstraction layer (hal_)
 *
 * \brief
 * These methods define the hardware abstraction layer for communicating with a CryptoAuth device
 *
   @{ */

/** \brief usart configuration struct */
static usart_serial_options_t config_usart;
/** \brief sysclk_get_per_hz value  */
static uint32_t u32sysclk;

/** \brief Implementation of SWI UART init.
 * \param[in] instance  instance
 * \return ATCA_STATUS
 */
ATCA_STATUS swi_uart_init(ATCASWIMaster_t *instance)
{
#ifdef DEBUG_PIN
    ioport_init();
    ioport_set_pin_dir(DEBUG_PIN_1, IOPORT_DIR_OUTPUT);
    ioport_set_pin_dir(DEBUG_PIN_2, IOPORT_DIR_OUTPUT);
    gpio_set_pin_high(DEBUG_PIN_1);
    gpio_set_pin_high(DEBUG_PIN_2);
#endif
    ATCA_STATUS status = ATCA_SUCCESS;

    //Save sysclk_get_per_hz value
    u32sysclk = sysclk_get_per_hz();
    // Set data size to 7
    config_usart.charlength = USART_CHSIZE_7BIT_gc;
    // Set parity to no parity
    config_usart.paritytype = USART_PMODE_DISABLED_gc;
    // Set data byte to one stopbit
    config_usart.stopbits = false;
    // Set baudrate to 230400
    config_usart.baudrate = 230400;

    switch (instance->bus_index)
    {
    case 0: instance->usart_instance = &USARTC0; break;
    case 1: instance->usart_instance = &USARTC1; break;
    case 2: instance->usart_instance = &USARTD0; break;
    case 3: instance->usart_instance = &USARTD1; break;
    case 4: instance->usart_instance = &USARTE0; break;
    case 5: instance->usart_instance = &USARTF0; break;
    }
    status = usart_serial_init(instance->usart_instance, &config_usart);
    return status;
}

/** \brief Implementation of SWI UART deinit.
 * \param[in] instance  instance
 * \return ATCA_STATUS
 */
ATCA_STATUS swi_uart_deinit(ATCASWIMaster_t *instance)
{
    ATCA_STATUS status = ATCA_SUCCESS;

    instance->usart_instance = NULL;
    return status;
}

/** \brief implementation of SWI UART change baudrate.
 * \param[in] instance  instance
 * \param[in] baudrate  (typically 230400 , 160000 or 115200)
 */
void swi_uart_setbaud(ATCASWIMaster_t *instance, uint32_t baudrate)
{
    // Set baudrate for UART module
    usart_set_baudrate(instance->usart_instance, baudrate, u32sysclk);
}


/** \brief implementation of SWI UART change mode.
 * \param[in] instance  instance
 * \param[in] mode      (TRANSMIT_MODE or RECEIVE_MODE)
 */
void swi_uart_mode(ATCASWIMaster_t *instance, uint8_t mode)
{
    switch (mode)
    {
    case TRANSMIT_MODE:
        usart_set_baudrate(instance->usart_instance, 230400, u32sysclk);
        break;
    case RECEIVE_MODE:
        //Reset UART RX buffer.
        usart_rx_disable(instance->usart_instance);
        usart_rx_enable(instance->usart_instance);
        break;
    default:
        break;
    }

}

/** \brief discover UART buses available for this hardware
 * this maintains a list of logical to physical bus mappings freeing the application
 * of the a-priori knowledge
 * \param[in] swi_uart_buses - an array of logical bus numbers
 * \param[in] max_buses - maximum number of buses the app wants to attempt to discover
 */
void swi_uart_discover_buses(int swi_uart_buses[], int max_buses)
{
    /* if every PORT was a likely candidate bus, then would need to initialize the entire array to all PORT n numbers.
     * As an optimization and making discovery safer, make assumptions about bus-num / PORT map based on XMEGA-A3BU Xplained board
     * If you were using a raw XMEGA on your own board, you would supply your own bus numbers based on your particular hardware configuration.
     */
    swi_uart_buses[0] = 4;   // default xmega-a3bu for xplained dev board
}

/** \brief HAL implementation of SWI UART send byte over ASF.  This function send one byte over UART
 * \param[in] instance  instance
 * \param[in] data      byte to send
 * \return ATCA_STATUS
 */
ATCA_STATUS swi_uart_send_byte(ATCASWIMaster_t *instance, uint8_t data)
{
    int8_t timeout = 0x7F;
    bool data_reg_empty = false;
    ATCA_STATUS status = ATCA_COMM_FAIL;

    // Send one byte over UART module
#ifdef DEBUG_PIN
    gpio_toggle_pin(DEBUG_PIN_1);
#endif
    // Send one byte over UART module
    timeout = 0x7F;
    while ((timeout > 0) && (data_reg_empty == false))
    {
        data_reg_empty = usart_data_register_is_empty(instance->usart_instance);
        timeout--;
    }
    if (data_reg_empty)
    {
        usart_put(instance->usart_instance, data);
        while (!usart_tx_is_complete(instance->usart_instance))
            ;
        usart_clear_tx_complete(instance->usart_instance);
        status = ATCA_SUCCESS;
    }
#ifdef DEBUG_PIN
    gpio_toggle_pin(DEBUG_PIN_1);
#endif
    if (timeout > 0)
        return status;
    else
        return ATCA_TIMEOUT;
}

/** \brief HAL implementation of SWI UART receive bytes over ASF.  This function receive one byte over UART
 * \param[in]    instance  instance
 * \param[inout] data      pointer to space to receive the data
 * \return ATCA_STATUS
 */
ATCA_STATUS swi_uart_receive_byte(ATCASWIMaster_t *instance, uint8_t *data)
{
    int8_t timeout, retries = 0x2; // This retry is used to compensate the baudrate that do not match when receiving response

    *data = 0xFF;
    bool rx_complete = false;
    ATCA_STATUS status = ATCA_COMM_FAIL;
#ifdef DEBUG_PIN
    gpio_toggle_pin(DEBUG_PIN_2);
#endif
    // Receive one byte over UART module
    while ((retries > 0) && (status != ATCA_SUCCESS))
    {
        timeout = 0x7F; retries--;
        while ((timeout > 0) && (rx_complete == false))
        {
            rx_complete = usart_rx_is_complete(instance->usart_instance);
            timeout--;
        }

        if (rx_complete)
        {
            *data = usart_get(instance->usart_instance);
            if ((*data >= 0x70) && (*data <= 0x7F))
                status = ATCA_SUCCESS;
            else
                status = ATCA_COMM_FAIL;
        }
    }
#ifdef DEBUG_PIN
    gpio_toggle_pin(DEBUG_PIN_2);
#endif
    if (timeout > 0)
        return status;
    else
        return ATCA_TIMEOUT;
}

/** @} */
