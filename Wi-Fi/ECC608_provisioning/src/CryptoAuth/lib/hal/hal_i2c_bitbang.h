/**
 * \file
 * \brief ATCA Hardware abstraction layer for I2C bit banging.
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

#ifndef HAL_I2C_BITBANG_H_
#define HAL_I2C_BITBANG_H_





#if     BOARD == AT88CK9000
#       include "i2c_bitbang_at88ck9000.h"
#endif

#if    (SAMD21 == 1)
#include "i2c_bitbang_samd21.h"
#endif


/**
 * \defgroup hal_ Hardware abstraction layer (hal_)
 *
 * \brief These methods define the hardware abstraction layer for
 *        communicating with a CryptoAuth device using I2C bit banging.
   @{ */

/**
 * \brief This enumeration lists flags for I2C read or write addressing.
 */
enum i2c_read_write_flag
{
    I2C_WRITE = (uint8_t)0x00,  //!< write command flag
    I2C_READ  = (uint8_t)0x01   //!< read command flag
};

/**
 * \brief This is the hal_data for ATCA HAL.
 */
typedef struct atcaI2Cmaster
{
    uint32_t pin_sda;
    uint32_t pin_scl;
    int      ref_ct;
    //! for conveniences during interface release phase
    int bus_index;
} ATCAI2CMaster_t;

/** @} */

#endif /* HAL_AT88CK900X_I2C_H_ */