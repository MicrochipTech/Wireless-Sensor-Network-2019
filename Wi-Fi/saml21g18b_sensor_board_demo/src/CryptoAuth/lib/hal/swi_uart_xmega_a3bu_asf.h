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

#ifndef SWI_UART_XMEGA_A3BU_ASF_H_
#define SWI_UART_XMEGA_A3BU_ASF_H_

#include <asf.h>
#include "cryptoauthlib.h"
#include "serial.h"

/** \defgroup hal_ Hardware abstraction layer (hal_)
 *
 * \brief
 * These methods define the hardware abstraction layer for communicating with a CryptoAuth device
 *
   @{ */


/** \brief
    - this HAL implementation assumes you've included the ASF UART libraries in your project, otherwise,
    the HAL layer will not compile because the ASF UART drivers are a dependency *
 */

#define MAX_SWI_BUSES    6  // XMEGA A3BU has up to 6 ports

#define RECEIVE_MODE    0   // UART Receive mode, RX enabled
#define TRANSMIT_MODE   1   // UART Transmit mode, RX disabled
#define RX_DELAY        10  // Delay before responses come
#define TX_DELAY        90  // Delay before new flag is sent

/** \brief this is the hal_data for ATCA HAL for SWI UART
 */
typedef struct atcaSWImaster
{
    // struct usart_module for Atmel SWI interface
    usart_if usart_instance;
    // for conveniences during interface release phase
    int bus_index;
} ATCASWIMaster_t;


ATCA_STATUS swi_uart_init(ATCASWIMaster_t *instance);
ATCA_STATUS swi_uart_deinit(ATCASWIMaster_t *instance);
void swi_uart_setbaud(ATCASWIMaster_t *instance, uint32_t baudrate);
void swi_uart_mode(ATCASWIMaster_t *instance, uint8_t mode);
void swi_uart_discover_buses(int swi_uart_buses[], int max_buses);

ATCA_STATUS swi_uart_send_byte(ATCASWIMaster_t *instance, uint8_t data);
ATCA_STATUS swi_uart_receive_byte(ATCASWIMaster_t *instance, uint8_t *data);

/** @} */

#endif // SWI_UART_XMEGA_A3BU_ASF_H
