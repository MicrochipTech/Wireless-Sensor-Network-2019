/** \file
 *  \brief 	Timer Utility Declarations
 *  \author Atmel Crypto Products
 *  \date 	June 20, 2013
 * \copyright Copyright (c) 2014 Atmel Corporation. All rights reserved.
 *
 * \atmel_crypto_device_library_license_start
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
 *    Atmel integrated circuit.
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
* \atmel_crypto_device_library_license_stop
 */

#ifndef TIMER_UTILITIES_H
#define    TIMER_UTILITIES_H

#include <stdint.h>                    // data type definitions
#include "arch/common/atca_types.h"

void atca_delay_10us(uint32_t  delay);
void atca_delay_ms(uint32_t  delay);
void atca_delay_us(uint32_t  delay);

// for ATCA, watchdog timer is used for protocol monitoring or other timer chores.  It doesn't have anything to do 
// with resetting/rebooting the system.

void atca_wdt_init(uint32_t frequencyInHz);
void atca_wdt_start(void);
void atca_wdt_stop(void);
void atca_wdt_tick(void);   // implemented by application/driver, callback for timer ticks

void atca_wdt_clear_counter(void);
bool_t atca_wdt_is_expired( uint32_t compareValue );
uint32_t atca_wdt_counter(void);

extern unsigned long atca_wdt_count;

#endif
