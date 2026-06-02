#
# SPDX-FileCopyrightText: <text>Copyright 2026 Arm Limited and/or its
# affiliates <open-source-office@arm.com></text>
#
# SPDX-License-Identifier: Apache-2.0

# MHUv3 mailbox driver
add_subdirectory_ifdef(CONFIG_MBOX_MHUV3 mbox)
add_subdirectory(ethernet)
add_subdirectory(pfdi)
add_subdirectory_ifdef(CONFIG_PFDI_AGENT pfdi_agent)
