/*
 * SPDX-FileCopyrightText: <text>Copyright 2026 Arm Limited and/or its
 * affiliates <open-source-office@arm.com></text>
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <stdint.h>
#include <stdbool.h>

#define DT_DRV_COMPAT arm_pfdi_agent

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/mbox.h>
#include <zephyr/drivers/pfdi/pfdi.h>
#include <zephyr/sys/barrier.h>
#include <zephyr/sys/util.h>
#include <errno.h>
#include <zephyr/logging/log.h>
#include "pfdi_agent.h"

#define LOG_LEVEL CONFIG_PFDI_AGENT_LOG_LEVEL
LOG_MODULE_REGISTER(pfdi_agent);

/* ====== Static Helper Functions ====== */

/**
 * @brief Validate core index and retrieve channel information.
 *
 * Performs validation of the device pointer, readiness, core index bounds,
 * and initialization state. On success, returns the shared memory pointer
 * and channel ID for the specified core.
 *
 * @param dev         Pointer to the PFDI agent device.
 * @param core        Core index (0 to PFDI_AGENT_NUM_CORES-1).
 * @param shmem_out   Output pointer to receive shared memory address.
 * @param chan_id_out Output pointer to receive channel ID.
 *
 * @retval 0        Success.
 * @retval -EINVAL  Invalid device pointer or core index.
 * @retval -ENODEV  Device not ready.
 * @retval -EAGAIN  Device not initialized.
 * @retval -EIO     Channel not configured.
 */
static int pfdi_agent_validate_core(const struct device *dev, uint32_t core,
				    volatile struct scmi_shmem **shmem_out,
				    uint32_t *chan_id_out)
{
	const struct pfdi_agent_config *config;
	struct pfdi_agent_data *data;

	if (dev == NULL) {
		LOG_ERR("PFDI Agent device is NULL");
		return -EINVAL;
	}
	if ((shmem_out == NULL) || (chan_id_out == NULL)) {
		LOG_ERR("Output pointers are NULL");
		return -EINVAL;
	}
	if (!device_is_ready(dev)) {
		LOG_ERR("PFDI Agent device not ready");
		return -ENODEV;
	}
	config = dev->config;
	if (core >= config->num_mboxes) {
		LOG_ERR("Invalid core (core=%u, max=%u)", core, config->num_mboxes - 1);
		return -EINVAL;
	}

	data = dev->data;
	if (data == NULL || !data->initialized) {
		LOG_ERR("PFDI Agent device not initialized");
		return -EAGAIN;
	}
	if (data->channels[core] == NULL) {
		LOG_ERR("PFDI Agent channel not configured for core %u", core);
		return -EIO;
	}

	*shmem_out = data->channels[core];
	*chan_id_out = data->chan_id[core];
	return 0;
}

/**
 * @brief Poll for SCMI response with timeout.
 *
 * Waits for the channel status to transition from busy to free,
 * indicating that the platform has processed the message and
 * written the response.
 *
 * @param shmem      Pointer to shared memory region.
 * @param timeout_ms Maximum time to wait in milliseconds.
 *
 * @retval 0          Response received within timeout.
 * @retval -ETIMEDOUT Timeout expired before response.
 * @retval -EINVAL   Invalid shared memory pointer.
 */
static int pfdi_agent_wait_for_response(volatile struct scmi_shmem *shmem,
					  uint32_t timeout_ms)
{
	uint32_t start = k_uptime_get_32();

	if (shmem == NULL) {
		LOG_ERR("Shared memory pointer is NULL");
		return -EINVAL;
	}

	while (shmem->t_hdr.channel_status != SCMI_CHAN_STATUS_FREE) {
		if ((k_uptime_get_32() - start) > timeout_ms) {
			return -ETIMEDOUT;
		}
		k_busy_wait(10U);
	}

	return 0;
}

/**
 * @brief Verify SCMI response message validity.
 *
 * Validates the transport header, message header, and return status
 * of an SCMI response. Checks channel status, flags, message length,
 * protocol ID, message ID, type, token, and SCMI return code.
 *
 * @param shmem           Pointer to shared memory region with response.
 * @param expected_msg_id Expected message ID in the response header.
 *
 * @retval 0         Response is valid.
 * @retval -EBUSY    Channel still busy (not free).
 * @retval -EBADMSG  Header fields mismatch expected values.
 * @retval -EMSGSIZE Message length incorrect.
 * @retval -EIO      SCMI return code indicates error.
 * @retval -EINVAL   Invalid parameters (NULL pointer).
 */
static int pfdi_agent_verify_response(volatile struct scmi_shmem *shmem,
					 uint32_t expected_msg_id)
{
	uint32_t msg_header;
	uint32_t msg_id;
	uint32_t msg_type;
	uint32_t prot_id;
	uint32_t token;
	int32_t status;

	if (shmem == NULL) {
		LOG_ERR("Shared memory pointer is NULL");
		return -EINVAL;
	}

	/* Verify Transport Header */
	if (shmem->t_hdr.channel_status != SCMI_CHAN_STATUS_FREE) {
		LOG_ERR("PFDI response channel busy (status=%u)",
				shmem->t_hdr.channel_status);
		return -EBUSY;
	}

	if (shmem->t_hdr.flags != SCMI_MSG_FLAGS_POLL) {
		LOG_ERR("PFDI response flags mismatch (flags=%u)",
				shmem->t_hdr.flags);
		return -EBADMSG;
	}

	if (shmem->t_hdr.message_length != SCMI_PFDI_AGENT_MSG_LENGTH) {
		LOG_ERR("PFDI response length mismatch (len=%u, expected=%u)",
				shmem->t_hdr.message_length, SCMI_PFDI_AGENT_MSG_LENGTH);
		return -EMSGSIZE;
	}

	/* Verify SCMI Message Header */
	msg_header = shmem->msg_header;
	msg_id = SCMI_MSG_GET_ID(msg_header);
	msg_type = SCMI_MSG_GET_TYPE(msg_header);
	prot_id = SCMI_MSG_GET_PROT_ID(msg_header);
	token = SCMI_MSG_GET_TOKEN(msg_header);

	if ((prot_id != SCMI_PROTOCOL_ID_PFDI) ||
	    (msg_id != expected_msg_id) ||
	    (msg_type != SCMI_MSG_TYPE_COMMAND) ||
	    (token != PFDI_AGENT_TOKEN_DEFAULT)) {
		LOG_ERR("PFDI response header mismatch (prot=0x%02x msg=0x%02x "
			"type=%u token=%u)",
			prot_id, msg_id, msg_type, token);
		return -EBADMSG;
	}

	/* Check SCMI Return Code */
	status = (int32_t)shmem->payload[0];
	if (status != 0) {
		LOG_ERR("PFDI_AGENT Send Status response error (SCMI Ret Code=0x%X)",
			status);
		return -EIO;
	}

	return 0;
}

/**
 * @brief Query SCMI protocol version for a specific core.
 *
 * Sends the PROTOCOL_VERSION command (message ID 0x00) to verify
 * the PFDI protocol implementation on the platform side.
 *
 * Note: This function accesses data structures directly without calling
 * pfdi_agent_validate_core() to allow use during device initialization
 * when device_is_ready() would return false.
 *
 * @param dev         Pointer to the PFDI agent device.
 * @param core        Core index to query.
 *
 * @retval 0          Success.
 * @retval -EINVAL    Invalid parameters.
 * @retval -EBUSY     Channel busy.
 * @retval -ETIMEDOUT Response timeout.
 * @retval -EMSGSIZE  Response too short.
 * @retval -EIO       Version mismatch or status error.
 */
static int pfdi_agent_protocol_version(const struct device *dev, uint32_t core)
{
	const struct pfdi_agent_config *config;
	struct pfdi_agent_data *data;
	volatile struct scmi_shmem *shmem;
	struct mbox_msg msg = {0};
	uint32_t version;
	int32_t status;
	uint32_t chan_id;
	uint32_t expected_len;
	int ret;

	if (dev == NULL) {
		return -EINVAL;
	}

	data = dev->data;
	config = dev->config;

	if (core >= config->num_mboxes) {
		LOG_ERR("Invalid core (core=%u, max=%u)", core, config->num_mboxes - 1);
		return -EINVAL;
	}

	shmem = data->channels[core];
	chan_id = data->chan_id[core];

	if (shmem == NULL) {
		LOG_ERR("Channel not configured for core %u", core);
		return -EIO;
	}

	if (shmem->t_hdr.channel_status != SCMI_CHAN_STATUS_FREE) {
		LOG_ERR("Channel not free (core=%u, status=%u)",
				core, shmem->t_hdr.channel_status);
		return -EBUSY;
	}

	/* Prepare SCMI PROTOCOL_VERSION command (no payload) */
	PFDI_AGENT_PREPARE_TRANSPORT(shmem, SCMI_CHAN_STATUS_BUSY,
				   sizeof(shmem->msg_header));

	shmem->msg_header = SCMI_MSG_CREATE(SCMI_PROTOCOL_ID_PFDI,
			SCMI_PFDI_MSG_ID_PROTOCOL_VERSION,
			PFDI_AGENT_TOKEN_DEFAULT, SCMI_MSG_TYPE_COMMAND);

	LOG_DBG("Sending PROTOCOL_VERSION: core=%u chan_id=%u prot_id=0x%02x",
			core, chan_id, SCMI_PROTOCOL_ID_PFDI);

	/* Signal SCMI PROTOCOL_VERSION command arrival */
	ret = mbox_send(config->mbox[core].dev, chan_id, &msg);
	if (ret < 0) {
		LOG_ERR("Failed to send mailbox message: %d", ret);
		return ret;
	}

	ret = pfdi_agent_wait_for_response(shmem, PFDI_AGENT_RESP_TIMEOUT_MS);
	if (ret < 0) {
		LOG_ERR("PROTOCOL_VERSION timed out (core=%u)", core);
		return ret;
	}

	/* Validate response length */
	expected_len = SCMI_MSG_HEADER_LEN + sizeof(struct scmi_protocol_version_p2a);
	if (shmem->t_hdr.message_length != expected_len) {
		LOG_ERR("PROTOCOL_VERSION response not as expected. (len=%u) expected %u\n",
				shmem->t_hdr.message_length, expected_len);
		return -EMSGSIZE;
	}

	/* Validate response payload */
	struct scmi_protocol_version_p2a *resp =
		(struct scmi_protocol_version_p2a *)&shmem->payload[0];
	status = resp->status;
	version = resp->version;
	LOG_DBG("PROTOCOL_VERSION response: status=%d version=0x%08x len=%u",
			status, version,
			shmem->t_hdr.message_length);
	if (version != SCMI_PROTOCOL_VERSION) {
		LOG_ERR("PROTOCOL_VERSION mismatch (expected 0x%08x, received 0x%08x)",
				SCMI_PROTOCOL_VERSION, version);
		return -EIO;
	}

	if (status != 0) {
		LOG_ERR("PROTOCOL_VERSION status error (core=%u, status=%d)",
				core, status);
		return -EIO;
	}

	return 0;
}

/* ====== Public API Functions ====== */

/**
 * @brief Send PFDI status message for a specific core.
 *
 * Constructs and transmits an SCMI message to report the PFDI status
 * (online or out-of-reset) for the specified core. Waits for an
 * acknowledgment before returning.
 *
 * @param dev    Pointer to the PFDI agent device.
 * @param core   Core index (0 to PFDI_AGENT_NUM_CORES-1).
 * @param mode   PFDI mode (PFDI_MODE_OOR or PFDI_MODE_ONL).
 * @param status Status value to report in the message payload.
 *
 * @retval 0          Success.
 * @retval -EINVAL    Invalid device or core.
 * @retval -EBUSY     Channel busy.
 * @retval -ETIMEDOUT Response timeout.
 * @retval -EBADMSG   Invalid response.
 * @retval -EIO       SCMI error in response.
 */
static int pfdi_agent_send_status(const struct device *dev, uint32_t core,
				   pfdi_mode_t mode, pfdi_status_t status)
{
	const struct pfdi_agent_config *config;
	struct pfdi_agent_data *data;
	volatile struct scmi_shmem *shmem;
	struct mbox_msg msg = {0};
	uint32_t msg_type = 0u;
	uint32_t chan_id;
	bool use_mutex = false;
	int ret;

	ret = pfdi_agent_validate_core(dev, core, &shmem, &chan_id);
	if (ret < 0) {
		return ret;
	}

	/* Check mode validity */
	if (mode != PFDI_MODE_OLT &&
		mode != PFDI_MODE_OLE &&
		mode != PFDI_MODE_OOR) {
		LOG_ERR("Invalid PFDI mode: %u", (uint32_t)mode);
		return -EINVAL;
	}

	data = dev->data;
	config = dev->config;

	/* Mutex is not enabled for OOR */
	use_mutex = (mode != PFDI_MODE_OOR);
	if (use_mutex) {
		ret = k_mutex_lock(&data->channel_lock[core], K_NO_WAIT);
		if (ret < 0) {
			LOG_ERR("Mutex lock failed (core=%u mode=%u ret=%d)",
				core, mode, ret);
			return ret;
		}
	}

	/* Check if channel is free (status=1) before writing */
	if (shmem->t_hdr.channel_status != SCMI_CHAN_STATUS_FREE) {
		LOG_ERR("Channel not free (core=%u, status=%u)",
				core, shmem->t_hdr.channel_status);
		if (use_mutex) {
			k_mutex_unlock(&data->channel_lock[core]);
		}
		return -EBUSY;
	}

	/* Prepare SCMI message in shared memory */
	PFDI_AGENT_PREPARE_TRANSPORT(shmem, SCMI_CHAN_STATUS_BUSY,
				   SCMI_PFDI_AGENT_MSG_LENGTH);

	msg_type = (mode == PFDI_MODE_OOR) ?
			SCMI_PFDI_MSG_ID_OOR : SCMI_PFDI_MSG_ID_ONLINE;

	shmem->msg_header = SCMI_MSG_CREATE(SCMI_PROTOCOL_ID_PFDI, msg_type,
			PFDI_AGENT_TOKEN_DEFAULT, SCMI_MSG_TYPE_COMMAND);

	shmem->payload[0] = status;

	/* Ensure shared memory writes are globally visible before doorbell. */
	barrier_dmem_fence_full();

	LOG_DBG("Sending PFDI status: core=%u mode=%u status=0x%08x "
		"chan_id=%u prot_id=0x%02x",
		core, mode, status, chan_id, SCMI_PROTOCOL_ID_PFDI);

	/* Send doorbell via MHUv3 */
	ret = mbox_send(config->mbox[core].dev, chan_id, &msg);
	if (ret < 0) {
		LOG_ERR("Failed to send mailbox message: %d", ret);
		if (use_mutex) {
			k_mutex_unlock(&data->channel_lock[core]);
		}
		return ret;
	}

	/* Wait for valid response */
	ret = pfdi_agent_wait_for_response(shmem, PFDI_AGENT_RESP_TIMEOUT_MS);
	if (ret < 0) {
		LOG_ERR("PFDI status timed out (core=%u)", core);
		if (use_mutex) {
			k_mutex_unlock(&data->channel_lock[core]);
		}
		return ret;
	}

	ret = pfdi_agent_verify_response(shmem, msg_type);
	if (ret < 0) {
		LOG_ERR("PFDI status response invalid (core=%u, ret=%d)",
				core, ret);
		if (use_mutex) {
			k_mutex_unlock(&data->channel_lock[core]);
		}
		return ret;
	}

	if (use_mutex) {
		k_mutex_unlock(&data->channel_lock[core]);
	}

	return 0;
}

/* ====== Device Initialization ====== */

/**
 * @brief Initialize PFDI agent device.
 *
 * Device initialization callback invoked by the Zephyr device subsystem.
 * Validates configuration, checks mailbox device readiness, initializes
 * per-core mutexes, and sets up shared memory channel pointers.
 *
 * @param dev Pointer to the PFDI agent device.
 *
 * @retval 0       Success.
 * @retval -EINVAL Mailbox count mismatch.
 * @retval -ENODEV Mailbox device not ready.
 */
static int pfdi_agent_init(const struct device *dev)
{
	const struct pfdi_agent_config *config;
	struct pfdi_agent_data *data;
	int ret;
	int core;

	if (dev == NULL) {
		LOG_ERR("PFDI Agent device is NULL");
		return -EINVAL;
	}
	data = dev->data;
	config = dev->config;

	/* Validate mailbox count */
	if (config->num_mboxes == 0U ||
		config->num_mboxes > PFDI_AGENT_NUM_CORES) {
		LOG_ERR("Invalid mboxes count (num=%u, max=%u)",
			config->num_mboxes, PFDI_AGENT_NUM_CORES);
		return -EINVAL;
	}

	/* Check if mailbox devices are ready and initialize channels */
	for (core = 0; core < config->num_mboxes; core++) {
		if (!device_is_ready(config->mbox[core].dev)) {
			LOG_ERR("MHUv3 device not ready (mbox=%u)", core);
			return -ENODEV;
		}

		/* Extract shared memory base address for each core */
		data->channels[core] = (volatile struct scmi_shmem *)
			(config->shmem_addr + (core * SCMI_MSG_SIZE_PER_CORE));
		/* Store mailbox channel ID for each core */
			data->chan_id[core] = config->mbox[core].channel_id;

		/* Initialize mutex for each core */
		ret = k_mutex_init(&data->channel_lock[core]);
		if (ret < 0) {
			LOG_ERR("Mutex init failed for core %u: %d", core, ret);
			return ret;
		}

		/* Query PROTOCOL_VERSION */
		ret = pfdi_agent_protocol_version(dev, core);
		if (ret < 0) {
			LOG_ERR("PROTOCOL_VERSION failed (core=%u, ret=%d)", core, ret);
			return ret;
		}
	}

	data->initialized = true;

	LOG_INF("PFDI Agent setup complete");

	return 0;
}

/* Helper macro to construct mbox spec from phandle-array entry */
#define PFDI_MBOX_ENTRY(idx, inst) \
	{ \
		.dev = DEVICE_DT_GET(DT_INST_PHANDLE_BY_IDX(inst, mboxes, idx)), \
		.channel_id = DT_INST_PHA_BY_IDX(inst, mboxes, idx, channel), \
	},

#define PFDI_AGENT_INIT(inst)							\
	BUILD_ASSERT(DT_INST_PROP_LEN(inst, mboxes) <= PFDI_AGENT_NUM_CORES,	\
		"mboxes exceeds PFDI_AGENT_NUM_CORES");			\
										\
	static struct pfdi_agent_data pfdi_agent_data_##inst;		\
										\
	static const struct mbox_dt_spec pfdi_agent_mbox_##inst[] = {		\
		LISTIFY(DT_INST_PROP_LEN(inst, mboxes), PFDI_MBOX_ENTRY, (), inst)\
	};									\
										\
	static const struct pfdi_agent_config pfdi_agent_config_##inst = {	\
		.mbox = pfdi_agent_mbox_##inst,				\
		.num_mboxes = ARRAY_SIZE(pfdi_agent_mbox_##inst),		\
		.shmem_addr = DT_REG_ADDR(DT_INST_PHANDLE(inst, shmem)),	\
	};									\
										\
	DEVICE_DT_INST_DEFINE(inst,						\
			      pfdi_agent_init,				\
			      NULL,						\
			      &pfdi_agent_data_##inst,			\
			      &pfdi_agent_config_##inst,			\
			      POST_KERNEL,					\
			      CONFIG_PFDI_AGENT_INIT_PRIORITY,		\
			      NULL);

DT_INST_FOREACH_STATUS_OKAY(PFDI_AGENT_INIT)
BUILD_ASSERT(DT_NUM_INST_STATUS_OKAY(DT_DRV_COMPAT) == 1,
	     "pfdi_agent_get_device() assumes a single instance");

/* ====== PFDI Agent Hooks Implementation ====== */

/**
 * @brief Get the PFDI agent device instance.
 *
 * @return Pointer to the PFDI agent device, or NULL if not available.
 */
static const struct device *pfdi_agent_get_device(void)
{
	const static struct device *dev = DEVICE_DT_INST_GET(0);

	if (!device_is_ready(dev)) {
		return NULL;
	}
	return dev;
}

#ifdef CONFIG_PLAT_PFDI_POST_RUN_HOOK
/**
 * @brief Hook implementation for sending status.
 *
 * Sends OOR or online status to the agent system via SCMI.
 *
 * @param cpu    CPU/core index.
 * @param mode   PFDI mode (PFDI_MODE_OOR, PFDI_MODE_OLE or PFDI_MODE_ONL).
 * @param status Test result status code.
 *
 */
void pfdi_post_run_hook(uint32_t cpu, uint64_t mode,
			   int32_t status)
{
	int ret;
	const struct device *dev = pfdi_agent_get_device();

	if (dev == NULL) {
		LOG_ERR("PFDI Agent device not ready");
		return;
	}

	ret = pfdi_agent_send_status(dev, cpu, (pfdi_mode_t)mode, (pfdi_status_t)status);
	if (ret < 0) {
		LOG_ERR("Failed to send PFDI status (cpu=%u, mode=%llu, status=%d, ret=%d)",
			cpu, mode, status, ret);
	}
}
#endif /* CONFIG_PLAT_PFDI_POST_RUN_HOOK */
