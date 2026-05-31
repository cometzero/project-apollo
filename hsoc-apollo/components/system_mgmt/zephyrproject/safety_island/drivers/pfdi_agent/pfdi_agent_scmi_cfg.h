/*
 * SPDX-FileCopyrightText: <text>Copyright 2026 Arm Limited and/or its
 * affiliates <open-source-office@arm.com></text>
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef PFDI_AGENT_SCMI_CFG_H_
#define PFDI_AGENT_SCMI_CFG_H_

/* ====== SCMI Protocol Definitions ====== */

/* SCMI protocol version configured */
#define SCMI_PROTOCOL_VERSION			0x00020000U

/* SCMI Message header length */
#define SCMI_MSG_HEADER_LEN			4U

/* PFDI Protocol ID (vendor-defined) */
#define SCMI_PROTOCOL_ID_PFDI			0x90U

/* Message payload length for PFDI status messages */
#define SCMI_PFDI_AGENT_MSG_LENGTH		0x08U

/* SCMI standard message ID for protocol version query */
#define SCMI_PFDI_MSG_ID_PROTOCOL_VERSION	0x00U

/* Size of per-core shared memory region in bytes */
#define SCMI_MSG_SIZE_PER_CORE			40U

/* Default token value for SCMI messages */
#define PFDI_AGENT_TOKEN_DEFAULT		0U

/* Number of cores configured */
#if defined(CONFIG_MP_MAX_NUM_CPUS)
#define PFDI_AGENT_NUM_CORES			CONFIG_MP_MAX_NUM_CPUS
#else
#define PFDI_AGENT_NUM_CORES			1U
#endif

/* Timeout for waiting on SCMI response (milliseconds) */
#define PFDI_AGENT_RESP_TIMEOUT_MS		30U

/* ====== SCMI PFDI Message IDs ====== */

/* Message ID for reporting online status */
#define SCMI_PFDI_MSG_ID_ONLINE			0x04U

/* Message ID for reporting out-of-reset status */
#define SCMI_PFDI_MSG_ID_OOR			0x03U

/* ====== SCMI Channel Status ====== */

/* Channel is free and ready for new commands */
#define SCMI_CHAN_STATUS_FREE			1U

/* Channel is busy processing a command */
#define SCMI_CHAN_STATUS_BUSY			0U

/* Polling-based message flag (no interrupt) */
#define SCMI_MSG_FLAGS_POLL			0U

/* ====== SCMI Message Header Encoding ====== */

#define SCMI_MSG_ID_SHIFT			0U
#define SCMI_MSG_TYPE_SHIFT			8U
#define SCMI_MSG_PROT_ID_SHIFT			10U
#define SCMI_MSG_TOKEN_SHIFT			18U

#define SCMI_MSG_ID_MASK			0xFFU
#define SCMI_MSG_TYPE_MASK			0x3U
#define SCMI_MSG_PROT_ID_MASK			0xFFU
#define SCMI_MSG_TOKEN_MASK			0x3FFU

#define SCMI_MSG_TYPE_COMMAND			0U

#endif /* PFDI_AGENT_SCMI_CFG_H_ */
