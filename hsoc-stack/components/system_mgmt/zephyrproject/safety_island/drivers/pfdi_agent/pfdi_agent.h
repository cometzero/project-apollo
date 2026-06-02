/*
 * SPDX-FileCopyrightText: <text>Copyright 2026 Arm Limited and/or its
 * affiliates <open-source-office@arm.com></text>
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef PFDI_AGENT_PFDI_AGENT_H_
#define PFDI_AGENT_PFDI_AGENT_H_

#include <stdint.h>
#include <stdbool.h>

#include <zephyr/kernel.h>
#include <zephyr/drivers/mbox.h>

#include "pfdi_agent_scmi_cfg.h"

/* Extract message ID from SCMI header */
#define SCMI_MSG_GET_ID(header) \
	(((header) >> SCMI_MSG_ID_SHIFT) & SCMI_MSG_ID_MASK)

/* Extract message type from SCMI header */
#define SCMI_MSG_GET_TYPE(header) \
	(((header) >> SCMI_MSG_TYPE_SHIFT) & SCMI_MSG_TYPE_MASK)

/* Extract protocol ID from SCMI header */
#define SCMI_MSG_GET_PROT_ID(header) \
	(((header) >> SCMI_MSG_PROT_ID_SHIFT) & SCMI_MSG_PROT_ID_MASK)

/* Extract token from SCMI header */
#define SCMI_MSG_GET_TOKEN(header) \
	(((header) >> SCMI_MSG_TOKEN_SHIFT) & SCMI_MSG_TOKEN_MASK)

#define PFDI_AGENT_PREPARE_TRANSPORT(shmem, chan_status, msg_len) \
	do { \
		(shmem)->t_hdr.reserved = 0U; \
		(shmem)->t_hdr.channel_status = (chan_status); \
		(shmem)->t_hdr.reserved2[0] = 0U; \
		(shmem)->t_hdr.reserved2[1] = 0U; \
		(shmem)->t_hdr.flags = SCMI_MSG_FLAGS_POLL; \
		(shmem)->t_hdr.message_length = (msg_len); \
	} while (0)

#define SCMI_MSG_CREATE(prot_id, msg_id, token, msg_type) \
	((((uint32_t)(msg_id) & SCMI_MSG_ID_MASK) << SCMI_MSG_ID_SHIFT) | \
	(((uint32_t)(msg_type) & SCMI_MSG_TYPE_MASK) << SCMI_MSG_TYPE_SHIFT) | \
	(((uint32_t)(prot_id) & SCMI_MSG_PROT_ID_MASK) << SCMI_MSG_PROT_ID_SHIFT) | \
	(((uint32_t)(token) & SCMI_MSG_TOKEN_MASK) << SCMI_MSG_TOKEN_SHIFT))

struct transport_header {
	uint32_t reserved;
	uint32_t channel_status;
	uint32_t reserved2[2];
	uint32_t flags;
	uint32_t message_length;
};

struct scmi_shmem {
	struct transport_header t_hdr;
	uint32_t msg_header;
	uint32_t payload[];
};

struct scmi_protocol_version_p2a {
	int32_t status;
	uint32_t version;
};

struct pfdi_agent_config {
	const struct mbox_dt_spec *mbox;
	uint32_t num_mboxes;
	uintptr_t shmem_addr;
};

struct pfdi_agent_data {
	volatile struct scmi_shmem *channels[PFDI_AGENT_NUM_CORES];
	uint32_t chan_id[PFDI_AGENT_NUM_CORES];
	struct k_mutex channel_lock[PFDI_AGENT_NUM_CORES];
	bool initialized;
};

#endif /* PFDI_AGENT_PFDI_AGENT_H_ */
