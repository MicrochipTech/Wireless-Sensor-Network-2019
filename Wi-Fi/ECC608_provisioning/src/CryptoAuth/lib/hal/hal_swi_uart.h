/**
 * \file
 * \brief ATCA Hardware abstraction layer for SWI over UART drivers.
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

#ifndef HAL_SWI_UART_H_
#define HAL_SWI_UART_H_

#ifdef SAMD21_START
    #include "swi_uart_samd21_start.h"
#elif defined (SAMD21_ASF)
    #include "swi_uart_samd21_asf.h"
#elif defined (XMEGA_ASF)
    #include "swi_uart_xmega_a3bu_asf.h"
#elif defined (AT90USB_ASF)
    #include "swi_uart_at90usb1287_asf.h"
#endif


/** \defgroup hal_ Hardware abstraction layer (hal_)
 *
 * \brief
 * These methods define the hardware abstraction layer for communicating with a CryptoAuth device
 * using SWI interface.
 *
   @{ */
#define SWI_WAKE_TOKEN   ((uint8_t)0x00)    //!< flag preceding a command
#define SWI_FLAG_CMD     ((uint8_t)0x77)    //!< flag preceding a command
#define SWI_FLAG_TX      ((uint8_t)0x88)    //!< flag requesting a response
#define SWI_FLAG_IDLE    ((uint8_t)0xBB)    //!< flag requesting to go into Idle mode
#define SWI_FLAG_SLEEP   ((uint8_t)0xCC)    //!< flag requesting to go into Sleep mode

ATCA_STATUS hal_swi_send_flag(ATCAIface iface, uint8_t flag);

/** @} */
#endif /* HAL_SWI_UART_H_ */