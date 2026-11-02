const QVP_DIAGRAMS = [
  {
    "title": "QBox process / SystemC platform",
    "subtitle": "도메인별 instance 소속 + 최종 mem binding · 점선은 소속/참조 관계이며 C++ 포함 관계가 아님",
    "width": 1600,
    "height": 1440,
    "groups": [
      {
        "label": "AP domain · default 16 CPUs",
        "x": 20,
        "y": 70,
        "w": 380,
        "h": 1040
      },
      {
        "label": "RSE domain",
        "x": 410,
        "y": 70,
        "w": 380,
        "h": 1040
      },
      {
        "label": "Safety Island CL0",
        "x": 800,
        "y": 70,
        "w": 380,
        "h": 1040
      },
      {
        "label": "Safety Island CL1",
        "x": 1190,
        "y": 70,
        "w": 390,
        "h": 1040
      },
      {
        "label": "Global address view / selected AP → System Management path (other windows omitted)",
        "x": 20,
        "y": 1140,
        "w": 1560,
        "h": 260
      }
    ],
    "nodes": [
      {
        "id": "apmgr",
        "x": 55,
        "y": 120,
        "w": 300,
        "h": 96,
        "title": "ap_qemu_inst_mgr",
        "lines": [
          "QemuInstanceManager",
          "libqemu instance lifecycle"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/cpu.lua",
        "line": 89,
        "excerpt": "  89      local options = ctx.options\n  90  \n  91      assert(platform.ap_qemu_inst_mgr == nil, \"duplicate Apollo object\")\n  92      if options.enable_ap_cpus then\n  93          platform.ap_qemu_inst_mgr = {\n  94              moduletype = \"QemuInstanceManager\";\n  95              construction_priority = -300;\n  96          }\n  97      end\n  98  \n  99      assert(platform.ap_qemu_inst == nil, \"duplicate Apollo object\")\n 100      if options.enable_ap_cpus then\n 101          platform.ap_qemu_inst = {\n 102              moduletype = \"QemuInstance\";",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 0
      },
      {
        "id": "apinst",
        "x": 55,
        "y": 275,
        "w": 300,
        "h": 96,
        "title": "ap_qemu_inst",
        "lines": [
          "QemuInstance",
          "domain-local QEMU state"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/cpu.lua",
        "line": 89,
        "excerpt": "  89      local options = ctx.options\n  90  \n  91      assert(platform.ap_qemu_inst_mgr == nil, \"duplicate Apollo object\")\n  92      if options.enable_ap_cpus then\n  93          platform.ap_qemu_inst_mgr = {\n  94              moduletype = \"QemuInstanceManager\";\n  95              construction_priority = -300;\n  96          }\n  97      end\n  98  \n  99      assert(platform.ap_qemu_inst == nil, \"duplicate Apollo object\")\n 100      if options.enable_ap_cpus then\n 101          platform.ap_qemu_inst = {\n 102              moduletype = \"QemuInstance\";",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 1
      },
      {
        "id": "apcpu",
        "x": 55,
        "y": 430,
        "w": 300,
        "h": 96,
        "title": "ap_cpu_0 … 15",
        "lines": [
          "Cortex-A720AE",
          "SystemC wrapper ↔ QEMU CPU object"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/cpu.lua",
        "line": 19,
        "excerpt": "  19              platform[\"ap_cpu_ras_fault_sync_\" .. i] = {\n  20                  moduletype = \"signal_fanout\";\n  21                  signal_out = {\n  22                      bind = \"&ap_gic.ppi_in_cpu_\" .. i .. \"_\" .. AP_RAS_FAULT_INTID;\n  23                  };\n  24              }\n  25              local cpu = {\n  26                  moduletype = \"cpu_arm_cortexA720AE\";\n  27                  args = {ctx.instances.ap};\n  28                  mem = {bind = \"&system_router.target_socket\"};\n  29                  has_el3 = true;\n  30                  has_el2 = true;\n  31                  irq_timer_phys_out = {\n  32                      bind = \"&ap_gic.ppi_in_cpu_\" .. i .. \"_\" .. AP_ARCH_TIMER_NON_SECURE_INTID;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 2
      },
      {
        "id": "aprouter",
        "x": 55,
        "y": 585,
        "w": 300,
        "h": 96,
        "title": "ap_router",
        "lines": [
          "target_socket ← CPU mem",
          "initiator_socket → decoded target"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/interconnect.lua",
        "line": 25,
        "excerpt": "  25  \n  26      local hipc_shared_base, hipc_shared_size =\n  27          ctx.hardware.si_cl1.interconnect.hipc_shared_window()\n  28  \n  29      -- AP logical view\n  30      platform.ap_router = {\n  31          moduletype = \"router\";\n  32          log_level = 0;\n  33      }\n  34  \n  35      platform.ap_hipc_alias = {\n  36          moduletype = \"addrtr\";\n  37          mapped_base_addr = AP_HIPC_ALIAS_BASE;\n  38          target_socket = {",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "apmem",
        "x": 55,
        "y": 760,
        "w": 300,
        "h": 96,
        "title": "host_ap_dram1 / SRAM",
        "lines": [
          "AP router targets",
          "gs_memory / MMIO targets"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/memory.lua",
        "line": 1,
        "excerpt": "   1  local AP_SHARED_SRAM_BASE = 0x00000000\n   2  local AP_MHU_NS_SHARED_SRAM_BASE = 0x00180000\n   3  local AP_PERIPHERAL_NS_SRAM_TAIL_BASE = 0x00181000\n   4  local AP_DRAM1_BASE = 0x80000000\n   5  local AP_CPER_BASE = 0xFFA00000\n   6  local AP_FFA_MM_COMM_BUFFER_BASE = 0xFFBF0000\n   7  local AP_SPMC_BASE = 0xFFC00000\n   8  local AP_DRAM2_BASE = 0x20000000000\n   9  local AP_SHARED_SRAM_SIZE = 0x00100000\n  10  local AP_MHU_NS_SHARED_SRAM_SIZE = 0x00001000\n  11  local AP_PERIPHERAL_NS_SRAM_TAIL_SIZE = 0x0007F000\n  12  local AP_DRAM1_SIZE = 0x7F000000\n  13  local AP_CPER_SIZE = 0x00100000\n  14  local AP_FFA_MM_COMM_BUFFER_SIZE = 0x00002000",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "rsemgr",
        "x": 445,
        "y": 120,
        "w": 300,
        "h": 96,
        "title": "rse_cpu_pass.qemu_inst_mgr",
        "lines": [
          "QemuInstanceManager",
          "libqemu instance lifecycle"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/cpu.lua",
        "line": 115,
        "excerpt": " 115      function block.define_instance(ctx, platform)\n 116          assert(\n 117              platform.qemu_inst_mgr == nil,\n 118              \"duplicate object: platform.qemu_inst_mgr\")\n 119          platform.qemu_inst_mgr = {\n 120              moduletype = \"QemuInstanceManager\";\n 121          }\n 122  \n 123          assert(\n 124              platform.qemu_inst == nil,\n 125              \"duplicate object: platform.qemu_inst\")\n 126          platform.qemu_inst = {\n 127              moduletype = \"QemuInstance\";\n 128              args = {\"&platform.qemu_inst_mgr\", \"AARCH64\"};",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 0
      },
      {
        "id": "rseinst",
        "x": 445,
        "y": 275,
        "w": 300,
        "h": 96,
        "title": "rse_cpu_pass.qemu_inst",
        "lines": [
          "Container-local QemuInstance",
          "CPU args={ctx.instances.rse_local}"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/cpu.lua",
        "line": 115,
        "excerpt": " 115      function block.define_instance(ctx, platform)\n 116          assert(\n 117              platform.qemu_inst_mgr == nil,\n 118              \"duplicate object: platform.qemu_inst_mgr\")\n 119          platform.qemu_inst_mgr = {\n 120              moduletype = \"QemuInstanceManager\";\n 121          }\n 122  \n 123          assert(\n 124              platform.qemu_inst == nil,\n 125              \"duplicate object: platform.qemu_inst\")\n 126          platform.qemu_inst = {\n 127              moduletype = \"QemuInstance\";\n 128              args = {\"&platform.qemu_inst_mgr\", \"AARCH64\"};",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 1
      },
      {
        "id": "rsecpu",
        "x": 445,
        "y": 430,
        "w": 300,
        "h": 96,
        "title": "rse_cpu_pass.cpu_0",
        "lines": [
          "ApolloRseCPU / NVIC",
          "SystemC wrapper ↔ QEMU CPU object"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/cpu.lua",
        "line": 47,
        "excerpt": "  47              \"duplicate object: platform.cpu_0\")\n  48          platform.cpu_0 = {\n  49              moduletype = \"ApolloRseCPU\";\n  50              args = {ctx.instances.rse_local};\n  51              router = {\n  52                  broadcast_invalidation = true;\n  53              };\n  54              cpu = {\n  55                  init_svtor = RSE_ROM_SECURE_BASE;\n  56                  init_nsvtor = RSE_ROM_SECURE_BASE;\n  57                  request_origin_id = ctx.request_context.origin.rse_cpu;\n  58                  request_domain_id = ctx.request_context.domain.rse;\n  59                  requester_id = 0;\n  60                  start_powered_off = false;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 2
      },
      {
        "id": "rserouter",
        "x": 445,
        "y": 585,
        "w": 300,
        "h": 96,
        "title": "rse_router",
        "lines": [
          "target_socket ← CPU mem",
          "initiator_socket → decoded target"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/interconnect.lua",
        "line": 12,
        "excerpt": "  12  local RSE_DOUBLE_REGISTER_WINDOW_SIZE = 0x00002000\n  13  local RSE_NVIC_NUM_IRQ = 160\n  14  \n  15  -- RSE ATU and local pass routing; socket names preserve the existing address views.\n  16  local module = {}\n  17  \n  18  function module.create(ctx, runtime)\n  19      local atu_dmi = ctx.options.atu_dmi\n  20      local atu_trace = ctx.options.atu_trace\n  21      local atu_trace_filter = ctx.options.atu_trace_filter\n  22      local atu_trace_limit = ctx.options.atu_trace_limit\n  23      local rse_local_crypto = ctx.options.rse_local_crypto\n  24      local rse_local_peripherals = ctx.options.rse_local_peripherals\n  25      local RSE_RUNTIME_ADDRESS = runtime.addresses",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "rsemem",
        "x": 445,
        "y": 760,
        "w": 300,
        "h": 96,
        "title": "RSE memory / peripherals",
        "lines": [
          "rse_router address view",
          "gs_memory / MMIO targets"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/memory.lua",
        "line": 1,
        "excerpt": "   1  local RSE_ITCM_SECURE_BASE = 0x10000000\n   2  local RSE_ITCM_SIZE = 0x00008000\n   3  local RSE_ITCM_NON_SECURE_BASE = 0x00000000\n   4  local RSE_ITCM_CPU0_SECURE_BASE = 0x1A000000\n   5  local RSE_ITCM_CPU0_NON_SECURE_BASE = 0x0A000000\n   6  local RSE_DTCM_SECURE_BASE = 0x30000000\n   7  local RSE_DTCM_SIZE = 0x00008000\n   8  local RSE_DTCM_NON_SECURE_BASE = 0x20000000\n   9  local RSE_DTCM_CPU0_SECURE_BASE = 0x34000000\n  10  local RSE_DTCM_CPU0_NON_SECURE_BASE = 0x24000000\n  11  local RSE_VM0_SECURE_BASE = 0x31000000\n  12  local RSE_TRAM_SECURE_BASE = 0x5015D000\n  13  local RSE_REGISTER_WINDOW_SIZE = 0x00001000\n  14  ",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "si_cl0mgr",
        "x": 835,
        "y": 120,
        "w": 300,
        "h": 96,
        "title": "si_cl0_qemu_inst_mgr",
        "lines": [
          "QemuInstanceManager",
          "libqemu instance lifecycle"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/cpu.lua",
        "line": 70,
        "excerpt": "  70      function block.define_qemu_instance(ctx, platform)\n  71          assert(\n  72              platform.si_cl0_qemu_inst_mgr == nil,\n  73              \"duplicate object: platform.si_cl0_qemu_inst_mgr\")\n  74          platform.si_cl0_qemu_inst_mgr = {\n  75              moduletype = \"QemuInstanceManager\";\n  76          }\n  77          assert(\n  78              platform.si_cl0_qemu_inst == nil,\n  79              \"duplicate object: platform.si_cl0_qemu_inst\")\n  80          platform.si_cl0_qemu_inst = {\n  81              moduletype = \"QemuInstance\";\n  82              args = {\"&platform.si_cl0_qemu_inst_mgr\", \"AARCH64\"};\n  83              managed_start_in_reset_release = true;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 0
      },
      {
        "id": "si_cl0inst",
        "x": 835,
        "y": 275,
        "w": 300,
        "h": 96,
        "title": "si_cl0_qemu_inst",
        "lines": [
          "QemuInstance",
          "domain-local QEMU state"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/cpu.lua",
        "line": 70,
        "excerpt": "  70      function block.define_qemu_instance(ctx, platform)\n  71          assert(\n  72              platform.si_cl0_qemu_inst_mgr == nil,\n  73              \"duplicate object: platform.si_cl0_qemu_inst_mgr\")\n  74          platform.si_cl0_qemu_inst_mgr = {\n  75              moduletype = \"QemuInstanceManager\";\n  76          }\n  77          assert(\n  78              platform.si_cl0_qemu_inst == nil,\n  79              \"duplicate object: platform.si_cl0_qemu_inst\")\n  80          platform.si_cl0_qemu_inst = {\n  81              moduletype = \"QemuInstance\";\n  82              args = {\"&platform.si_cl0_qemu_inst_mgr\", \"AARCH64\"};\n  83              managed_start_in_reset_release = true;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 1
      },
      {
        "id": "si_cl0cpu",
        "x": 835,
        "y": 430,
        "w": 300,
        "h": 96,
        "title": "si_cl0_cpu_0",
        "lines": [
          "Cortex-R82",
          "SystemC wrapper ↔ QEMU CPU object"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/cpu.lua",
        "line": 19,
        "excerpt": "  19              moduletype = \"cpu_arm_cortexR82\";\n  20              args = {qemu_instance};\n  21              mem = {bind = \"&si_cl0_ni710ae_primary_nci.protected_target_socket\"};\n  22              has_el2 = true;\n  23              psci_conduit = \"smc\";\n  24              start_powered_off = false;\n  25              start_in_reset = true;\n  26              reset_power_on = true;\n  27              rvbar = runtime.entry;\n  28              cntfrq_hz = 125000000;\n  29              mp_affinity = 0x0;\n  30              request_origin_id = ctx.request_context.origin.si_cl0_cpu_base;\n  31              request_domain_id = ctx.request_context.domain.si_cl0;\n  32              requester_id = 0;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 2
      },
      {
        "id": "si_cl0router",
        "x": 835,
        "y": 585,
        "w": 300,
        "h": 96,
        "title": "si_cl0_ni710ae_primary_nci",
        "lines": [
          "protected_target_socket ← mem",
          "initiator_socket → si_cl0_router"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/interconnect.lua",
        "line": 12,
        "excerpt": "  12  local SYSTEM_AP_SHARED_BRIDGE_SIZE = 0x00200000\n  13  local SYSTEM_AP_GIC_BRIDGE_BASE = 0x20000000\n  14  local SYSTEM_AP_GIC_BRIDGE_SIZE = 0x08000000\n  15  local SI_CL1_SCMI_BRIDGE_BASE = 0x48000000\n  16  local SI_CL1_SCMI_BRIDGE_SIZE = 0x00001000\n  17  local SI_CL0_NI710AE_PRIMARY_NCI_BASE = 0x2A000000\n  18  local SI_CL0_NI710AE_SECONDARY_NCI_BASE = 0x2A200000\n  19  local SI_CL0_NI710AE_MHU_NCI_BASE = 0x2A300000\n  20  local SI_CL0_NI710AE_NCI_SIZE = 0x00010000\n  21  local SI_CL0_ATW0_CMN_SIZE = 0x40000000\n  22  local SI_CL0_ATW2_SMD_EXPANSION_SIZE = 0x00020000\n  23  local SI_CL0_CMN_PHYS_BASE = 0x100000000\n  24  local SI_CL0_CLUSTER_UTILITY_PHYS_SIZE = 0x10000000\n  25  ",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "si_cl0mem",
        "x": 835,
        "y": 760,
        "w": 300,
        "h": 96,
        "title": "si_cl0_router → local targets",
        "lines": [
          "decode after NI-710AE protection",
          "gs_memory / MMIO targets"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/memory.lua",
        "line": 1,
        "excerpt": "   1  local SI_CL0_SRAM_BASE = 0x120000000\n   2  local HOST_SI_CL0_CL_UTIL_BASE = 0x4000028000000\n   3  \n   4  local SI_CL0_SRAM_SIZE = 0x00800000\n   5  local HOST_SI_CL_UTIL_SIZE = 0x00800000\n   6  local HOST_SI_CL0_SRAM_PHYS_BASE = 0x4000120000000\n   7  local HOST_SI_SRAM_WINDOW_SIZE = 0x01000000\n   8  \n   9  local module = {}\n  10  \n  11  function module.create(ctx, _runtime)\n  12      local host_si_sram_dmi = ctx.options.host_si_sram_dmi\n  13  \n  14      local block = {}",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "si_cl1mgr",
        "x": 1225,
        "y": 120,
        "w": 300,
        "h": 96,
        "title": "si_cl1_qemu_inst_mgr",
        "lines": [
          "QemuInstanceManager",
          "libqemu instance lifecycle"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/cpu.lua",
        "line": 83,
        "excerpt": "  83      function block.define_qemu_instance(ctx, platform)\n  84          assert(\n  85              platform.si_cl1_qemu_inst_mgr == nil,\n  86              \"duplicate object: platform.si_cl1_qemu_inst_mgr\")\n  87          platform.si_cl1_qemu_inst_mgr = {\n  88              moduletype = \"QemuInstanceManager\";\n  89          }\n  90          assert(\n  91              platform.si_cl1_qemu_inst == nil,\n  92              \"duplicate object: platform.si_cl1_qemu_inst\")\n  93          platform.si_cl1_qemu_inst = {\n  94              moduletype = \"QemuInstance\";\n  95              args = {\"&platform.si_cl1_qemu_inst_mgr\", \"AARCH64\"};\n  96              managed_start_in_reset_release = true;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 0
      },
      {
        "id": "si_cl1inst",
        "x": 1225,
        "y": 275,
        "w": 300,
        "h": 96,
        "title": "si_cl1_qemu_inst",
        "lines": [
          "QemuInstance",
          "domain-local QEMU state"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/cpu.lua",
        "line": 83,
        "excerpt": "  83      function block.define_qemu_instance(ctx, platform)\n  84          assert(\n  85              platform.si_cl1_qemu_inst_mgr == nil,\n  86              \"duplicate object: platform.si_cl1_qemu_inst_mgr\")\n  87          platform.si_cl1_qemu_inst_mgr = {\n  88              moduletype = \"QemuInstanceManager\";\n  89          }\n  90          assert(\n  91              platform.si_cl1_qemu_inst == nil,\n  92              \"duplicate object: platform.si_cl1_qemu_inst\")\n  93          platform.si_cl1_qemu_inst = {\n  94              moduletype = \"QemuInstance\";\n  95              args = {\"&platform.si_cl1_qemu_inst_mgr\", \"AARCH64\"};\n  96              managed_start_in_reset_release = true;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 1
      },
      {
        "id": "si_cl1cpu",
        "x": 1225,
        "y": 430,
        "w": 300,
        "h": 96,
        "title": "si_cl1_cpu_0 … 3",
        "lines": [
          "Cortex-R82",
          "SystemC wrapper ↔ QEMU CPU object"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/cpu.lua",
        "line": 19,
        "excerpt": "  19      function block.define(ctx, platform, qemu_instance)\n  20          local gic_name = \"si_cl1_gic\"\n  21          local gic = platform[gic_name]\n  22  \n  23          for i = 0,(SI_CL1_CPU_COUNT-1) do\n  24              local gic_cpu = i\n  25              assert(\n  26                  platform[\"si_cl1_cpu_\" .. i] == nil,\n  27                  \"duplicate object: platform.\" .. (\"si_cl1_cpu_\" .. i))\n  28              platform[\"si_cl1_cpu_\" .. i] = {\n  29                  moduletype = \"cpu_arm_cortexR82\";\n  30                  args = {qemu_instance};\n  31                  mem = {bind = \"&si_cl1_router.target_socket\"};\n  32                  has_el2 = true;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 2
      },
      {
        "id": "si_cl1router",
        "x": 1225,
        "y": 585,
        "w": 300,
        "h": 96,
        "title": "si_cl1_router",
        "lines": [
          "target_socket ← CPU mem",
          "initiator_socket → decoded target"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/interconnect.lua",
        "line": 12,
        "excerpt": "  12      function block.define(ctx, platform)\n  13          assert(\n  14              platform.si_cl1_router == nil,\n  15              \"duplicate object: platform.si_cl1_router\")\n  16          platform.si_cl1_router = {\n  17              moduletype = \"router\";\n  18              log_level = 0;\n  19          }\n  20  \n  21          assert(\n  22              platform.si_cl1_hipc_bridge == nil,\n  23              \"duplicate object: platform.si_cl1_hipc_bridge\")\n  24          platform.si_cl1_hipc_bridge = {\n  25              moduletype = \"addrtr\";",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "si_cl1mem",
        "x": 1225,
        "y": 760,
        "w": 300,
        "h": 96,
        "title": "si_cl1_sram / scmi_shmem",
        "lines": [
          "local SRAM ≠ host_si_cl1_sram",
          "gs_memory / MMIO targets"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/memory.lua",
        "line": 1,
        "excerpt": "   1  local SI_CL1_SRAM_BASE = 0x140000000\n   2  local HOST_SI_CL1_CL_UTIL_BASE = 0x4000028800000\n   3  local SI_CL1_SCMI_SHMEM_BASE = 0x48000000\n   4  \n   5  local HOST_SI_CL1_SRAM_PHYS_BASE = 0x4000140000000\n   6  local HOST_SI_SRAM_WINDOW_SIZE = 0x01000000\n   7  local HOST_SI_CL_UTIL_SIZE = 0x00800000\n   8  local SI_CL1_SRAM_SIZE = 0x00800000\n   9  local SI_CL1_SCMI_SHMEM_SIZE = 0x00001000\n  10  \n  11  local module = {}\n  12  \n  13  function module.create(ctx, _runtime)\n  14      local host_si_sram_dmi = ctx.options.host_si_sram_dmi",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "rseouter",
        "x": 445,
        "y": 950,
        "w": 300,
        "h": 96,
        "title": "platform.qemu_inst",
        "lines": [
          "Separate outer QEMU instance",
          "peripheral-side instance ≠ CPU local"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/rse/cpu.lua",
        "line": 115,
        "excerpt": " 115      function block.define_instance(ctx, platform)\n 116          assert(\n 117              platform.qemu_inst_mgr == nil,\n 118              \"duplicate object: platform.qemu_inst_mgr\")\n 119          platform.qemu_inst_mgr = {\n 120              moduletype = \"QemuInstanceManager\";\n 121          }\n 122  \n 123          assert(\n 124              platform.qemu_inst == nil,\n 125              \"duplicate object: platform.qemu_inst\")\n 126          platform.qemu_inst = {\n 127              moduletype = \"QemuInstance\";\n 128              args = {\"&platform.qemu_inst_mgr\", \"AARCH64\"};",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 1
      },
      {
        "id": "apgic",
        "x": 55,
        "y": 950,
        "w": 300,
        "h": 96,
        "title": "ap_gic → ap_cpu_i.irq_in",
        "lines": [
          "irq_out_i / fiq_out_i",
          "GIC and CPU share AP instance"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/cpu.lua",
        "line": 77,
        "excerpt": "  77              platform[\"ap_gic\"][\"irq_out_\" .. i] = {bind = \"&ap_cpu_\" .. i .. \".irq_in\"}\n  78              assert(platform[\"ap_gic\"][\"fiq_out_\" .. i] == nil, \"duplicate Apollo object\")\n  79              platform[\"ap_gic\"][\"fiq_out_\" .. i] = {bind = \"&ap_cpu_\" .. i .. \".fiq_in\"}\n  80              assert(platform[\"ap_gic\"][\"virq_out_\" .. i] == nil, \"duplicate Apollo object\")\n  81              platform[\"ap_gic\"][\"virq_out_\" .. i] = {bind = \"&ap_cpu_\" .. i .. \".virq_in\"}\n  82              assert(platform[\"ap_gic\"][\"vfiq_out_\" .. i] == nil, \"duplicate Apollo object\")\n  83              platform[\"ap_gic\"][\"vfiq_out_\" .. i] = {bind = \"&ap_cpu_\" .. i .. \".vfiq_in\"}\n  84          end\n  85      end\n  86  end\n  87  \n  88  function cpu.define_instance(ctx, platform, policy)\n  89      local options = ctx.options\n  90  ",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "si0gic",
        "x": 835,
        "y": 950,
        "w": 300,
        "h": 96,
        "title": "si_cl0_gic",
        "lines": [
          "GIC output → CPU irq_in",
          "per-core timer PPI signals"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl0/cpu.lua",
        "line": 35,
        "excerpt": "  35              irq_timer_sec_out = {\n  36                  bind = \"&si_cl0_gic.ppi_in_cpu_0_\" ..\n  37                      SI_SECURE_TIMER_INTID;\n  38              };\n  39              irq_timer_phys_out = {\n  40                  bind = \"&si_cl0_gic.ppi_in_cpu_0_\" ..\n  41                      SI_PHYSICAL_TIMER_INTID;\n  42              };\n  43              irq_timer_virt_out = {\n  44                  bind = \"&si_cl0_gic.ppi_in_cpu_0_\" ..\n  45                      SI_VIRTUAL_TIMER_INTID;\n  46              };\n  47              irq_timer_hyp_out = {\n  48                  bind = \"&si_cl0_gic.ppi_in_cpu_0_\" ..",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "si1gic",
        "x": 1225,
        "y": 950,
        "w": 300,
        "h": 96,
        "title": "si_cl1_gic",
        "lines": [
          "GIC output → CPU irq_in",
          "per-core timer PPI signals"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/cpu.lua",
        "line": 74,
        "excerpt": "  74              }\n  75              for _, signal in ipairs({\"irq\", \"fiq\", \"virq\", \"vfiq\"}) do\n  76                  gic[signal .. \"_out_\" .. gic_cpu] = {\n  77                      bind = \"&si_cl1_cpu_\" .. i .. \".\" .. signal .. \"_in\";\n  78                  }\n  79              end\n  80          end\n  81      end\n  82  \n  83      function block.define_qemu_instance(ctx, platform)\n  84          assert(\n  85              platform.si_cl1_qemu_inst_mgr == nil,\n  86              \"duplicate object: platform.si_cl1_qemu_inst_mgr\")\n  87          platform.si_cl1_qemu_inst_mgr = {",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "atu",
        "x": 55,
        "y": 1210,
        "w": 300,
        "h": 96,
        "title": "host_ap_atu",
        "lines": [
          "AP translation window",
          "configured regions → system PA"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/interconnect.lua",
        "line": 35,
        "excerpt": "  35      local options = ctx.options\n  36      local atu_trace_address_min = options.atu_trace_address_min\n  37      local atu_trace_address_max = options.atu_trace_address_max\n  38      assert(platform.host_ap_atu == nil, \"duplicate Apollo object: host_ap_atu\")\n  39      platform.host_ap_atu = {\n  40          moduletype = \"rse_atu\";\n  41          trace = options.atu_trace;\n  42          trace_limit = options.atu_trace_limit;\n  43          trace_filter = options.atu_trace_filter;\n  44          trace_address_min = atu_trace_address_min;\n  45          trace_address_max = atu_trace_address_max;\n  46          enable_dmi = options.enable_ap_cpus and options.atu_dmi;\n  47          build_config = SYSTEM_ATU_BUILD_CONFIG;\n  48          target_socket = {",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "sys",
        "x": 445,
        "y": 1210,
        "w": 300,
        "h": 96,
        "title": "system_router",
        "lines": [
          "global address decode",
          "includes high-address MHU targets"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/fabric/fabric.lua",
        "line": 7,
        "excerpt": "   7      -- Root fabric\n   8      assert(platform.system_router == nil, \"duplicate Apollo object: system_router\")\n   9      platform.system_router = {\n  10          moduletype = \"router\";\n  11          log_level = 0;\n  12      }\n  13  \n  14      -- The 0x2 high-nibble is the architected System Management Domain.\n  15      -- Keep its internal decode separate so an unmapped SMD address ends\n  16      -- at the SMD boundary instead of falling through the system fabric.\n  17      assert(platform.smd_router == nil, \"duplicate Apollo object: smd_router\")\n  18      platform.smd_router = {\n  19          moduletype = \"router\";\n  20          log_level = 0;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "smdbridge",
        "x": 835,
        "y": 1210,
        "w": 300,
        "h": 96,
        "title": "system_to_smd_nci",
        "lines": [
          "addrtr / SMD global window",
          "base 0x2000000000000"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/fabric/fabric.lua",
        "line": 24,
        "excerpt": "  24      platform.system_to_smd_nci = {\n  25          moduletype = \"addrtr\";\n  26          mapped_base_addr = SMD_PHYS_BASE;\n  27          target_socket = {\n  28              address = SMD_PHYS_BASE;\n  29              size = SMD_PHYS_SIZE;\n  30              bind = \"&system_router.initiator_socket\";\n  31              relative_addresses = false;\n  32          };\n  33          initiator_socket = {bind = \"&smd_router.target_socket\"};\n  34          log_level = 0;\n  35      }\n  36  \n  37  end",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "smd",
        "x": 1225,
        "y": 1210,
        "w": 300,
        "h": 96,
        "title": "smd_router",
        "lines": [
          "System Management address view",
          "decode ends at SMD boundary"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/fabric/fabric.lua",
        "line": 17,
        "excerpt": "  17      assert(platform.smd_router == nil, \"duplicate Apollo object: smd_router\")\n  18      platform.smd_router = {\n  19          moduletype = \"router\";\n  20          log_level = 0;\n  21      }\n  22  \n  23      assert(platform.system_to_smd_nci == nil, \"duplicate Apollo object: system_to_smd_nci\")\n  24      platform.system_to_smd_nci = {\n  25          moduletype = \"addrtr\";\n  26          mapped_base_addr = SMD_PHYS_BASE;\n  27          target_socket = {\n  28              address = SMD_PHYS_BASE;\n  29              size = SMD_PHYS_SIZE;\n  30              bind = \"&system_router.initiator_socket\";",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      }
    ],
    "edges": [
      {
        "a": "apmgr",
        "b": "apinst",
        "label": "args: manager",
        "kind": "own",
        "stage": 1,
        "route": null
      },
      {
        "a": "apinst",
        "b": "apcpu",
        "label": "args: QemuInstance",
        "kind": "own",
        "stage": 2,
        "route": null
      },
      {
        "a": "apcpu",
        "b": "aprouter",
        "label": "mem binding",
        "kind": "tlm",
        "stage": 3,
        "route": null
      },
      {
        "a": "aprouter",
        "b": "apmem",
        "label": "address decode",
        "kind": "tlm",
        "stage": 3,
        "route": null
      },
      {
        "a": "rsemgr",
        "b": "rseinst",
        "label": "args: manager",
        "kind": "own",
        "stage": 1,
        "route": null
      },
      {
        "a": "rseinst",
        "b": "rsecpu",
        "label": "args: QemuInstance",
        "kind": "own",
        "stage": 2,
        "route": null
      },
      {
        "a": "rsecpu",
        "b": "rserouter",
        "label": "Container initiator_socket_0/1",
        "kind": "tlm",
        "stage": 3,
        "route": null
      },
      {
        "a": "rserouter",
        "b": "rsemem",
        "label": "address decode",
        "kind": "tlm",
        "stage": 3,
        "route": null
      },
      {
        "a": "si_cl0mgr",
        "b": "si_cl0inst",
        "label": "args: manager",
        "kind": "own",
        "stage": 1,
        "route": null
      },
      {
        "a": "si_cl0inst",
        "b": "si_cl0cpu",
        "label": "args: QemuInstance",
        "kind": "own",
        "stage": 2,
        "route": null
      },
      {
        "a": "si_cl0cpu",
        "b": "si_cl0router",
        "label": "mem binding",
        "kind": "tlm",
        "stage": 3,
        "route": null
      },
      {
        "a": "si_cl0router",
        "b": "si_cl0mem",
        "label": "address decode",
        "kind": "tlm",
        "stage": 3,
        "route": null
      },
      {
        "a": "si_cl1mgr",
        "b": "si_cl1inst",
        "label": "args: manager",
        "kind": "own",
        "stage": 1,
        "route": null
      },
      {
        "a": "si_cl1inst",
        "b": "si_cl1cpu",
        "label": "args: QemuInstance",
        "kind": "own",
        "stage": 2,
        "route": null
      },
      {
        "a": "si_cl1cpu",
        "b": "si_cl1router",
        "label": "mem binding",
        "kind": "tlm",
        "stage": 3,
        "route": null
      },
      {
        "a": "si_cl1router",
        "b": "si_cl1mem",
        "label": "address decode",
        "kind": "tlm",
        "stage": 3,
        "route": null
      },
      {
        "a": "aprouter",
        "b": "atu",
        "label": "translation_socket",
        "kind": "tlm",
        "stage": 3,
        "route": [
          [
            55,
            633
          ],
          [
            30,
            633
          ],
          [
            30,
            1258
          ],
          [
            55,
            1258
          ]
        ]
      },
      {
        "a": "atu",
        "b": "sys",
        "label": "initiator_socket",
        "kind": "tlm",
        "stage": 3,
        "route": null
      },
      {
        "a": "sys",
        "b": "smdbridge",
        "label": "SMD window",
        "kind": "tlm",
        "stage": 3,
        "route": null
      },
      {
        "a": "smdbridge",
        "b": "smd",
        "label": "initiator_socket",
        "kind": "tlm",
        "stage": 3,
        "route": null
      },
      {
        "a": "apgic",
        "b": "apcpu",
        "label": "irq_out → irq_in",
        "kind": "irq",
        "stage": 3,
        "route": [
          [
            355,
            998
          ],
          [
            380,
            998
          ],
          [
            380,
            478
          ],
          [
            355,
            478
          ]
        ]
      },
      {
        "a": "si0gic",
        "b": "si_cl0cpu",
        "label": "irq_out → irq_in",
        "kind": "irq",
        "stage": 3,
        "route": [
          [
            1135,
            998
          ],
          [
            1160,
            998
          ],
          [
            1160,
            478
          ],
          [
            1135,
            478
          ]
        ]
      },
      {
        "a": "si1gic",
        "b": "si_cl1cpu",
        "label": "irq_out → irq_in",
        "kind": "irq",
        "stage": 3,
        "route": [
          [
            1525,
            998
          ],
          [
            1550,
            998
          ],
          [
            1550,
            478
          ],
          [
            1525,
            478
          ]
        ]
      }
    ]
  },
  {
    "title": "Memory access / CPU bridge and SystemC initiators",
    "subtitle": "실선: TLM transaction · 각 target는 자신의 host backing 사용 · 노드 선택으로 source excerpt 확인",
    "width": 1600,
    "height": 960,
    "groups": [
      {
        "label": "QEMU + QBox bridge",
        "x": 20,
        "y": 70,
        "w": 370,
        "h": 840
      },
      {
        "label": "SystemC transport / fabric",
        "x": 410,
        "y": 70,
        "w": 370,
        "h": 840
      },
      {
        "label": "Target components",
        "x": 800,
        "y": 70,
        "w": 370,
        "h": 840
      },
      {
        "label": "Host storage / policy",
        "x": 1190,
        "y": 70,
        "w": 390,
        "h": 840
      }
    ],
    "nodes": [
      {
        "id": "cpu",
        "x": 55,
        "y": 130,
        "w": 300,
        "h": 96,
        "title": "ap_cpu_i / QEMU vCPU",
        "lines": [
          "guest load / store",
          "RequestContext + data_length"
        ],
        "source": "hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h",
        "line": 125,
        "excerpt": " 125  \n 126              if (masked_addr == it->first) {\n 127                  return it;\n 128              }\n 129          }\n 130          return table.end();\n 131      }\n 132  \n 133      void init_payload(TlmPayload& trans, tlm::tlm_command command, uint64_t addr, uint64_t* val, unsigned int size)\n 134      {\n 135          trans.set_command(command);\n 136          trans.set_address(addr);\n 137          trans.set_data_ptr(reinterpret_cast<unsigned char*>(val));\n 138          trans.set_data_length(size);",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 0
      },
      {
        "id": "bridge",
        "x": 55,
        "y": 350,
        "w": 300,
        "h": 96,
        "title": "Qemu initiator socket",
        "lines": [
          "do_regular_access()",
          "unlock_iothread → run_on_sysc"
        ],
        "source": "hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h",
        "line": 658,
        "excerpt": " 658      }\n 659  \n 660      void do_regular_access(TlmPayload& trans)\n 661      {\n 662          using sc_core::sc_time;\n 663  \n 664          uint64_t addr = trans.get_address();\n 665          sc_time now = m_initiator.initiator_get_local_time();\n 666  \n 667          m_inst.get().unlock_iothread();\n 668          m_on_sysc.run_on_sysc([this, &trans, &now] { (*this)->b_transport(trans, now); });\n 669          m_inst.get().lock_iothread();\n 670          /*\n 671           * Reset transaction address before dmi check (could be altered by",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 1
      },
      {
        "id": "router",
        "x": 445,
        "y": 350,
        "w": 300,
        "h": 96,
        "title": "ap_router",
        "lines": [
          "target_socket → decode",
          "initiator_socket → target"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/interconnect.lua",
        "line": 25,
        "excerpt": "  25  \n  26      local hipc_shared_base, hipc_shared_size =\n  27          ctx.hardware.si_cl1.interconnect.hipc_shared_window()\n  28  \n  29      -- AP logical view\n  30      platform.ap_router = {\n  31          moduletype = \"router\";\n  32          log_level = 0;\n  33      }\n  34  \n  35      platform.ap_hipc_alias = {\n  36          moduletype = \"addrtr\";\n  37          mapped_base_addr = AP_HIPC_ALIAS_BASE;\n  38          target_socket = {",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 2
      },
      {
        "id": "dram",
        "x": 835,
        "y": 350,
        "w": 300,
        "h": 96,
        "title": "host_ap_dram1",
        "lines": [
          "gs_memory · target_socket",
          "base 0x80000000 / size 0x7f000000"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/memory.lua",
        "line": 61,
        "excerpt": "  61      assert(platform.host_ap_dram1 == nil, \"duplicate Apollo object\")\n  62      if options.enable_ap_cpus then\n  63          platform.host_ap_dram1 = {\n  64              moduletype = \"gs_memory\";\n  65              dmi_allow = options.host_memory_dmi;\n  66              target_socket = {\n  67                  address = AP_DRAM1_BASE;\n  68                  size = AP_DRAM1_SIZE;\n  69                  bind = \"&system_router.initiator_socket\";\n  70                  priority = 10;\n  71              };\n  72              log_level = 0;\n  73          }\n  74      end",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "back",
        "x": 1225,
        "y": 350,
        "w": 300,
        "h": 96,
        "title": "gs_memory host backing",
        "lines": [
          "read/write through sub-block",
          "response_status / delay / DMI hint"
        ],
        "source": "hsoc-stack/tools/qbox/systemc-components/gs_memory/include/gs_memory.h",
        "line": 301,
        "excerpt": " 301      virtual void b_transport(int id, tlm::tlm_generic_payload& txn, sc_core::sc_time& delay)\n 302      {\n 303          unsigned int len = txn.get_data_length();\n 304          unsigned char* ptr = txn.get_data_ptr();\n 305          sc_dt::uint64 addr = txn.get_address();\n 306          unsigned char* byt = txn.get_byte_enable_ptr();\n 307          unsigned int bel = txn.get_byte_enable_length();\n 308  \n 309          if (txn.get_streaming_width() < len) {\n 310              SCP_FATAL(()) << \"using streaming width: 0x\" << std::hex << txn.get_streaming_width()\n 311                            << \" less than data length: 0x\" << std::hex << len << \" is not supported.\";\n 312          }\n 313          SCP_INFO(()) << \"Start b_transport :\" << get_txn_command_str(txn) << \" to address: 0x\" << std::hex << addr\n 314                       << \" len: 0x\" << std::hex << len;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "epc",
        "x": 445,
        "y": 130,
        "w": 300,
        "h": 96,
        "title": "ap_pcie_epc.local_master",
        "lines": [
          "SystemC bus master example",
          "initiator → ap_router.target_socket"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/interconnect.lua",
        "line": 150,
        "excerpt": " 150      end\n 151      if platform.ap_pcie_epc ~= nil then\n 152          bind_ap_target(platform.ap_pcie_epc.regs)\n 153          bind_ap_target(platform.ap_pcie_epc.outbound)\n 154          platform.ap_pcie_epc.local_master = {bind = \"&ap_router.target_socket\"}\n 155      end\n 156  \n 157      -- Memory and interrupt controller windows\n 158      bind_ap_socket(platform.host_ap_shared_sram, \"target_socket\")\n 159      bind_ap_socket(platform.host_ap_mhu_ns_shared_sram, \"target_socket\")\n 160      bind_ap_socket(platform.host_ap_peripheral_ns_sram_tail, \"target_socket\")\n 161      bind_ap_socket(platform.host_ap_bl2_header_sram, \"target_socket\")\n 162      bind_ap_socket(platform.host_ap_flash, \"target_socket\")\n 163      bind_ap_socket(platform.host_ap_trusted_nvctr, \"target_socket\")",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 2
      },
      {
        "id": "sram",
        "x": 835,
        "y": 570,
        "w": 300,
        "h": 96,
        "title": "host_ap_shared_sram",
        "lines": [
          "gs_memory · 0x00000000",
          "size 0x00100000 (1 MiB)"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/memory.lua",
        "line": 23,
        "excerpt": "  23      assert(platform.host_ap_shared_sram == nil, \"duplicate Apollo object\")\n  24      platform.host_ap_shared_sram = {\n  25          moduletype = \"gs_memory\";\n  26          dmi_allow = options.host_memory_dmi;\n  27          target_socket = {\n  28              address = AP_SHARED_SRAM_BASE;\n  29              size = AP_SHARED_SRAM_SIZE;\n  30              bind = \"&system_router.initiator_socket\";\n  31          };\n  32          log_level = 0;\n  33      }\n  34  \n  35      assert(platform.host_ap_mhu_ns_shared_sram == nil, \"duplicate Apollo object\")\n  36      platform.host_ap_mhu_ns_shared_sram = {",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "boot",
        "x": 835,
        "y": 760,
        "w": 300,
        "h": 96,
        "title": "host_ap_bl2_header_sram",
        "lines": [
          "gs_memory · 0x00100000",
          "size 0x00080000 / HIPC backing"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/boot.lua",
        "line": 1,
        "excerpt": "   1  local AP_FLASH_SIZE = 0x08000000\n   2  local AP_FLASH_BASE = 0x38000000\n   3  local AP_BL2_HEADER_SRAM_BASE = 0x00100000\n   4  local AP_TRUSTED_NVCTR_BASE = 0x32030000\n   5  local AP_BL2_HEADER_SRAM_SIZE = 0x00080000\n   6  local AP_FLASH_SECTOR_SIZE = 0x00001000\n   7  local AP_TRUSTED_NVCTR_SIZE = 0x00010000\n   8  \n   9  local boot = {}\n  10  \n  11  function boot.define(ctx, platform)\n  12      local options = ctx.options\n  13      assert(platform.host_ap_bl2_header_sram == nil, \"duplicate Apollo object\")\n  14      platform.host_ap_bl2_header_sram = {",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "dram2",
        "x": 1225,
        "y": 130,
        "w": 300,
        "h": 96,
        "title": "host_ap_dram2",
        "lines": [
          "base 0x20000000000",
          "size 0x80000000 (2 GiB)"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/memory.lua",
        "line": 105,
        "excerpt": " 105      assert(platform.host_ap_dram2 == nil, \"duplicate Apollo object\")\n 106      if options.enable_ap_cpus then\n 107          platform.host_ap_dram2 = {\n 108              moduletype = \"gs_memory\";\n 109              dmi_allow = options.host_memory_dmi;\n 110              target_socket = {\n 111                  address = AP_DRAM2_BASE;\n 112                  size = AP_DRAM2_SIZE;\n 113                  bind = \"&system_router.initiator_socket\";\n 114              };\n 115              log_level = 0;\n 116          }\n 117      end\n 118  ",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "policy",
        "x": 1225,
        "y": 570,
        "w": 300,
        "h": 96,
        "title": "DMI policy",
        "lines": [
          "host_memory_dmi = false",
          "SoC default; runtime may override"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/config.lua",
        "line": 35,
        "excerpt": "  35              ap_power_domain_reset_delay_ns = 1;\n  36              si_cl0_ppu_on_delay_ns = 0;\n  37              si_cl0_ppu_access_latency_ns = 100;\n  38              host_memory_dmi = false;\n  39              host_si_sram_dmi = false;\n  40              atu_dmi = false;\n  41              boot_flash_dmi = false;\n  42              boot_flash_dmi_ranges = \"\";\n  43              rse_itcm_dmi = false;\n  44              rse_dtcm_dmi = false;\n  45              rse_vm_dmi = false;\n  46              reset_trace = false;\n  47              ap_gic_multiview_trace = false;\n  48              ap_gic_multiview_trace_limit = 256;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "return",
        "x": 55,
        "y": 570,
        "w": 300,
        "h": 96,
        "title": "Return to initiator",
        "lines": [
          "restore original address",
          "check DMI hint / update local time"
        ],
        "source": "hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h",
        "line": 670,
        "excerpt": " 670          /*\n 671           * Reset transaction address before dmi check (could be altered by\n 672           * b_transport).\n 673           */\n 674          trans.set_address(addr);\n 675          if (!m_requester_id_from_qemu) {\n 676              check_qemu_mr_hint(trans);\n 677              if (trans.is_dmi_allowed()) {\n 678                  RequestContextTlmExtension* context_ext = nullptr;\n 679                  trans.get_extension(context_ext);\n 680                  RequestAccessPath previous_path = RequestAccessPath::UNKNOWN;\n 681                  if (context_ext != nullptr) {\n 682                      previous_path = context_ext->get_context().access_path;\n 683                      context_ext->set_access_path(RequestAccessPath::DMI);",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "payload",
        "x": 55,
        "y": 760,
        "w": 300,
        "h": 96,
        "title": "TLM generic payload",
        "lines": [
          "address / command / data_length",
          "response_status + context extension"
        ],
        "source": "hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h",
        "line": 125,
        "excerpt": " 125  \n 126              if (masked_addr == it->first) {\n 127                  return it;\n 128              }\n 129          }\n 130          return table.end();\n 131      }\n 132  \n 133      void init_payload(TlmPayload& trans, tlm::tlm_command command, uint64_t addr, uint64_t* val, unsigned int size)\n 134      {\n 135          trans.set_command(command);\n 136          trans.set_address(addr);\n 137          trans.set_data_ptr(reinterpret_cast<unsigned char*>(val));\n 138          trans.set_data_length(size);",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 0
      }
    ],
    "edges": [
      {
        "a": "cpu",
        "b": "bridge",
        "label": "QEMU memory callback",
        "kind": "tlm",
        "stage": 1,
        "route": null
      },
      {
        "a": "bridge",
        "b": "router",
        "label": "b_transport(trans, delay)",
        "kind": "tlm",
        "stage": 2,
        "route": null
      },
      {
        "a": "epc",
        "b": "router",
        "label": "local_master",
        "kind": "tlm",
        "stage": 2,
        "route": null
      },
      {
        "a": "router",
        "b": "dram",
        "label": "target_socket",
        "kind": "tlm",
        "stage": 3,
        "route": null
      },
      {
        "a": "dram",
        "b": "back",
        "label": "backing read / write",
        "kind": "call",
        "stage": 3,
        "route": null
      },
      {
        "a": "router",
        "b": "sram",
        "label": "SRAM decode",
        "kind": "tlm",
        "stage": 3,
        "route": [
          [
            765,
            398
          ],
          [
            790,
            398
          ],
          [
            790,
            618
          ],
          [
            835,
            618
          ]
        ]
      },
      {
        "a": "router",
        "b": "boot",
        "label": "0x00100000 decode",
        "kind": "tlm",
        "stage": 3,
        "route": [
          [
            765,
            398
          ],
          [
            782,
            398
          ],
          [
            782,
            808
          ],
          [
            835,
            808
          ]
        ]
      },
      {
        "a": "bridge",
        "b": "return",
        "label": "response / local time",
        "kind": "return",
        "stage": 3,
        "route": null
      },
      {
        "a": "router",
        "b": "dram2",
        "label": "DRAM2 decode",
        "kind": "tlm",
        "stage": 3,
        "route": [
          [
            595,
            350
          ],
          [
            595,
            260
          ],
          [
            1180,
            260
          ],
          [
            1180,
            178
          ],
          [
            1225,
            178
          ]
        ]
      }
    ]
  },
  {
    "title": "DMI / negotiation, alias and invalidation",
    "subtitle": "허용된 경우의 설명 · 기본 host_memory_dmi=false · 보라색 점선은 DMI, 일반 MMIO와 구분",
    "width": 1600,
    "height": 960,
    "groups": [
      {
        "label": "QEMU instance / initiator",
        "x": 20,
        "y": 70,
        "w": 500,
        "h": 840
      },
      {
        "label": "SystemC route / policy",
        "x": 550,
        "y": 70,
        "w": 480,
        "h": 840
      },
      {
        "label": "gs_memory / host backing",
        "x": 1060,
        "y": 70,
        "w": 520,
        "h": 840
      }
    ],
    "nodes": [
      {
        "id": "access",
        "x": 65,
        "y": 135,
        "w": 390,
        "h": 96,
        "title": "do_regular_access()",
        "lines": [
          "b_transport first",
          "trans.is_dmi_allowed()"
        ],
        "source": "hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h",
        "line": 658,
        "excerpt": " 658      }\n 659  \n 660      void do_regular_access(TlmPayload& trans)\n 661      {\n 662          using sc_core::sc_time;\n 663  \n 664          uint64_t addr = trans.get_address();\n 665          sc_time now = m_initiator.initiator_get_local_time();\n 666  \n 667          m_inst.get().unlock_iothread();\n 668          m_on_sysc.run_on_sysc([this, &trans, &now] { (*this)->b_transport(trans, now); });\n 669          m_inst.get().lock_iothread();\n 670          /*\n 671           * Reset transaction address before dmi check (could be altered by",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 0
      },
      {
        "id": "hint",
        "x": 65,
        "y": 350,
        "w": 390,
        "h": 96,
        "title": "check_dmi_hint_locked()",
        "lines": [
          "get_direct_mem_ptr(trans, dmi)",
          "range / access permissions"
        ],
        "source": "hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h",
        "line": 448,
        "excerpt": " 448      tlm::tlm_dmi check_dmi_hint_locked(TlmPayload& trans)\n 449      {\n 450          assert(trans.is_dmi_allowed());\n 451          tlm::tlm_dmi dmi_data;\n 452          int shm_fd = -1;\n 453          uint64_t shm_offset = 0;\n 454          auto addr = trans.get_address();\n 455          {\n 456              std::lock_guard<std::mutex> lock(m_mutex);\n 457              clear_retired_aliases_locked();\n 458          }\n 459          /* We got a DMI hint, lets just make sure this isn't in an existing m_mmio_mrs region\n 460           * Because if it is, what probably happened is that we took the MMIO path\n 461           * rather than getting a translation done. We should invalidate any mmio 1-1 mapping",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 1
      },
      {
        "id": "route",
        "x": 590,
        "y": 350,
        "w": 390,
        "h": 96,
        "title": "router / translation policy",
        "lines": [
          "forward DMI request",
          "constrain translated address range"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/interconnect.lua",
        "line": 25,
        "excerpt": "  25  \n  26      local hipc_shared_base, hipc_shared_size =\n  27          ctx.hardware.si_cl1.interconnect.hipc_shared_window()\n  28  \n  29      -- AP logical view\n  30      platform.ap_router = {\n  31          moduletype = \"router\";\n  32          log_level = 0;\n  33      }\n  34  \n  35      platform.ap_hipc_alias = {\n  36          moduletype = \"addrtr\";\n  37          mapped_base_addr = AP_HIPC_ALIAS_BASE;\n  38          target_socket = {",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 1
      },
      {
        "id": "grant",
        "x": 1110,
        "y": 350,
        "w": 390,
        "h": 96,
        "title": "gs_memory::get_direct_mem_ptr",
        "lines": [
          "dmi_allow + address range + ROM",
          "host pointer / start / end / access"
        ],
        "source": "hsoc-stack/tools/qbox/systemc-components/gs_memory/include/gs_memory.h",
        "line": 247,
        "excerpt": " 247      virtual bool get_direct_mem_ptr(int id, tlm::tlm_generic_payload& txn, tlm::tlm_dmi& dmi_data)\n 248      {\n 249          if (!p_dmi) return false;\n 250          sc_dt::uint64 addr = txn.get_address();\n 251  \n 252          if (!m_relative_addresses) {\n 253              if (addr < m_address) {\n 254                  txn.set_response_status(tlm::TLM_ADDRESS_ERROR_RESPONSE);\n 255                  return false;\n 256              }\n 257              addr -= m_address;\n 258          }\n 259          if (addr >= m_size) {\n 260              txn.set_response_status(tlm::TLM_ADDRESS_ERROR_RESPONSE);",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 1
      },
      {
        "id": "reject",
        "x": 590,
        "y": 135,
        "w": 390,
        "h": 96,
        "title": "Grant denied",
        "lines": [
          "no usable DMI mapping",
          "continue regular b_transport"
        ],
        "source": "hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h",
        "line": 488,
        "excerpt": " 488          bool dmi_valid = (*this)->get_direct_mem_ptr(trans, dmi_data);\n 489          trans.clear_extension(&u_dmi);\n 490          if (!dmi_valid) {\n 491              SCP_INFO(())(\"No DMI available for {:x}\", trans.get_address());\n 492              /* this is used by the map function below\n 493               * - a better plan may be to tag memories to be mapped so we dont need this\n 494               */\n 495              if (u_dmi.has_dmi(gs::tlm_dmi_ex::dmi_mapped)) {\n 496                  tlm::tlm_dmi first_map = u_dmi.get_first(gs::tlm_dmi_ex::dmi_mapped);\n 497                  return first_map;\n 498              }\n 499              if (u_dmi.has_dmi(gs::tlm_dmi_ex::dmi_nomap)) {\n 500                  tlm::tlm_dmi first_nomap = u_dmi.get_first(gs::tlm_dmi_ex::dmi_nomap);\n 501                  return first_nomap;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 1
      },
      {
        "id": "alias",
        "x": 65,
        "y": 570,
        "w": 390,
        "h": 96,
        "title": "QemuInstanceDmiManager",
        "lines": [
          "get_new_region_alias()",
          "add_dmi_mr_alias()"
        ],
        "source": "hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h",
        "line": 620,
        "excerpt": " 620                      return result;\n 621                  };\n 622              }\n 623  \n 624              DmiRegionAlias::Ptr alias =\n 625                  m_inst.get_dmi_manager().get_new_region_alias(dmi_data, shm_fd, shm_offset, write_cb);\n 626  \n 627              m_dmi_aliases[start] = alias;\n 628              add_dmi_mr_alias(m_dmi_aliases[start]);\n 629          } else {\n 630              SCP_INFO(())(\"Already have DMI for 0x{:x}\", start);\n 631          }\n 632          return dmi_data;\n 633      }",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 2
      },
      {
        "id": "mapping",
        "x": 590,
        "y": 570,
        "w": 390,
        "h": 96,
        "title": "QEMU MemoryRegion alias",
        "lines": [
          "mapping of granted host region",
          "not a second memory copy"
        ],
        "source": "hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h",
        "line": 620,
        "excerpt": " 620                      return result;\n 621                  };\n 622              }\n 623  \n 624              DmiRegionAlias::Ptr alias =\n 625                  m_inst.get_dmi_manager().get_new_region_alias(dmi_data, shm_fd, shm_offset, write_cb);\n 626  \n 627              m_dmi_aliases[start] = alias;\n 628              add_dmi_mr_alias(m_dmi_aliases[start]);\n 629          } else {\n 630              SCP_INFO(())(\"Already have DMI for 0x{:x}\", start);\n 631          }\n 632          return dmi_data;\n 633      }",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 2
      },
      {
        "id": "backing",
        "x": 1110,
        "y": 570,
        "w": 390,
        "h": 96,
        "title": "Same gs_memory backing",
        "lines": [
          "mapped host pointer",
          "subsequent eligible direct access"
        ],
        "source": "hsoc-stack/tools/qbox/systemc-components/gs_memory/include/gs_memory.h",
        "line": 269,
        "excerpt": " 269          else\n 270              dmi_data.allow_read_write();\n 271  \n 272          SubBlock<>& blk = m_sub_block->access(addr);\n 273  \n 274          uint8_t* ptr = blk.get_ptr();\n 275          uint64_t size = blk.get_len();\n 276          uint64_t block_address = blk.get_address();\n 277  \n 278          dmi_data.set_dmi_ptr(reinterpret_cast<unsigned char*>(ptr));\n 279          if (!m_relative_addresses) {\n 280              dmi_data.set_start_address(block_address + m_address);\n 281              dmi_data.set_end_address((block_address + m_address + size) - 1);\n 282          } else {",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 2
      },
      {
        "id": "invalidate",
        "x": 590,
        "y": 775,
        "w": 390,
        "h": 96,
        "title": "invalidate_direct_mem_ptr",
        "lines": [
          "invalidate affected alias range",
          "reacquire or return to transport"
        ],
        "source": "hsoc-stack/tools/qbox/qemu-components/common/include/ports/initiator.h",
        "line": 560,
        "excerpt": " 560                  // the TE is looked up, we'll get the lock and re-establish the translation. In any case we should do\n 561                  // nothing and simply return\n 562                  // Moving to a cached TE will improve speed and prevent this from happening?\n 563                  SCP_DEBUG(())\n 564                  (\"Memory request should be directed via MMIO interface {:x} {:x}\", start, trans.get_address());\n 565  \n 566                  //                std::lock_guard<std::mutex> lock(m_mutex);\n 567  \n 568                  uint64_t start_range = itr->first;\n 569                  uint64_t end_range = itr->first + itr->second->get_size() - 1;\n 570  \n 571                  invalidate_direct_mem_ptr(start_range, end_range);\n 572              }\n 573              return dmi_data;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      }
    ],
    "edges": [
      {
        "a": "access",
        "b": "hint",
        "label": "DMI hint",
        "kind": "dmi",
        "stage": 1,
        "route": null
      },
      {
        "a": "hint",
        "b": "route",
        "label": "request",
        "kind": "dmi",
        "stage": 1,
        "route": null
      },
      {
        "a": "route",
        "b": "grant",
        "label": "get_direct_mem_ptr",
        "kind": "dmi",
        "stage": 1,
        "route": null
      },
      {
        "a": "route",
        "b": "reject",
        "label": "false / blocked",
        "kind": "return",
        "stage": 1,
        "route": null
      },
      {
        "a": "hint",
        "b": "alias",
        "label": "granted region",
        "kind": "dmi",
        "stage": 2,
        "route": null
      },
      {
        "a": "alias",
        "b": "mapping",
        "label": "install alias",
        "kind": "call",
        "stage": 2,
        "route": null
      },
      {
        "a": "mapping",
        "b": "backing",
        "label": "direct backing access",
        "kind": "dmi",
        "stage": 2,
        "route": null
      },
      {
        "a": "backing",
        "b": "invalidate",
        "label": "backward invalidation",
        "kind": "return",
        "stage": 3,
        "route": [
          [
            1305,
            666
          ],
          [
            1305,
            823
          ],
          [
            980,
            823
          ]
        ]
      },
      {
        "a": "invalidate",
        "b": "alias",
        "label": "remove stale mapping",
        "kind": "return",
        "stage": 3,
        "route": [
          [
            590,
            823
          ],
          [
            260,
            823
          ],
          [
            260,
            666
          ]
        ]
      }
    ]
  },
  {
    "title": "Interrupt / SI CL1 MHU → GIC → vCPU",
    "subtitle": "IRQ assert / mask / clear는 device 상태와 연결 · handler 실행은 guest 설정에 따른 조건부 단계",
    "width": 1600,
    "height": 960,
    "groups": [
      {
        "label": "SystemC mhu320ae model",
        "x": 20,
        "y": 70,
        "w": 500,
        "h": 840
      },
      {
        "label": "QBox signal / QEMU GIC",
        "x": 550,
        "y": 70,
        "w": 480,
        "h": 840
      },
      {
        "label": "CPU wrapper / guest software",
        "x": 1060,
        "y": 70,
        "w": 520,
        "h": 840
      }
    ],
    "nodes": [
      {
        "id": "status",
        "x": 65,
        "y": 140,
        "w": 390,
        "h": 96,
        "title": "signal_doorbell_channel()",
        "lines": [
          "m_frame.set_status_bits()",
          "mask / status / channel"
        ],
        "source": "hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h",
        "line": 1770,
        "excerpt": "1770      void signal_doorbell_channel(unsigned int channel, uint32_t value)\n1771      {\n1772          if (channel >= channel_count()) {\n1773              return;\n1774          }\n1775  \n1776          m_frame.set_status_bits(channel, value);\n1777          detect_ram_error(false, channel);\n1778          if (!p_doorbell_commit_on_notify.get_value() ||\n1779              p_protocol.get_value() != \"doorbell-bridge\" ||\n1780              channel == notify_channel()) {\n1781              update_combined_irq();\n1782          }\n1783  ",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 0
      },
      {
        "id": "update",
        "x": 65,
        "y": 350,
        "w": 390,
        "h": 96,
        "title": "update_combined_irq()",
        "lines": [
          "pending level + mutex",
          "m_irq_update_event.notify(0)"
        ],
        "source": "hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h",
        "line": 1059,
        "excerpt": "1059      void update_combined_irq()\n1060      {\n1061          {\n1062              std::lock_guard<std::mutex> lock(m_ras_irq_lock);\n1063              for (unsigned group = 0; group < m_group_irq_level.size(); ++group) {\n1064                  const bool level = is_mbx() && group < fast_groups() &&\n1065                      (m_fast_control & 4) && m_fast_pending[group];\n1066                  if (!level && m_group_irq_level[group] && fch_irq[group].size()) {\n1067                      fch_irq[group]->write(false);\n1068                  }\n1069                  m_group_irq_level[group] = level;\n1070              }\n1071              m_ras_irq_event.notify(sc_core::SC_ZERO_TIME);\n1072          }",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 1
      },
      {
        "id": "emit",
        "x": 590,
        "y": 350,
        "w": 390,
        "h": 96,
        "title": "emit_combined_irq()",
        "lines": [
          "irq->write(level)",
          "SI1 MBX → spi_in_41"
        ],
        "source": "hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h",
        "line": 1101,
        "excerpt": "1101      void emit_combined_irq()\n1102      {\n1103          std::lock_guard<std::mutex> lock(m_irq_update_lock);\n1104          if (!m_pending_irq_update) {\n1105              return;\n1106          }\n1107          const bool level = m_pending_irq_level;\n1108          m_pending_irq_update = false;\n1109  \n1110          if (p_trace.get_value()) {\n1111              std::ostringstream detail;\n1112              detail << \"level=\" << std::boolalpha << level\n1113                     << \" bound=\" << (irq.size() != 0);\n1114              trace_event(\"combined-irq\", detail.str());",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 1
      },
      {
        "id": "gic",
        "x": 1110,
        "y": 350,
        "w": 390,
        "h": 96,
        "title": "si_cl1_gic",
        "lines": [
          "SPI index 41 / INTID 73",
          "enable / pending / route / priority"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/mailbox.lua",
        "line": 54,
        "excerpt": "  54              platform.si_cl1_hipc_mhu_mbx == nil,\n  55              \"duplicate object: platform.si_cl1_hipc_mhu_mbx\")\n  56          platform.si_cl1_hipc_mhu_mbx = {\n  57              moduletype = \"mhu320ae\";\n  58              fast_channel_count = 64;\n  59              fast_channels_per_group = 32;\n  60              fast_channel_word_bits = 32;\n  61              frame = \"mbx\";\n  62              pair = \"apollo_ap_to_si_cl1\";\n  63              protocol = \"doorbell-bridge\";\n  64              channel_count = SI_CL1_MHU_CHANNELS;\n  65              trace = mhu_trace;\n  66              trace_limit = mhu_trace_limit;\n  67              target_socket = {",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 2
      },
      {
        "id": "cpu",
        "x": 1110,
        "y": 570,
        "w": 390,
        "h": 96,
        "title": "si_cl1_cpu_i.irq_in",
        "lines": [
          "GIC irq_out_i → irq_in",
          "QEMU CPU exception condition"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/cpu.lua",
        "line": 74,
        "excerpt": "  74              }\n  75              for _, signal in ipairs({\"irq\", \"fiq\", \"virq\", \"vfiq\"}) do\n  76                  gic[signal .. \"_out_\" .. gic_cpu] = {\n  77                      bind = \"&si_cl1_cpu_\" .. i .. \".\" .. signal .. \"_in\";\n  78                  }\n  79              end\n  80          end\n  81      end\n  82  \n  83      function block.define_qemu_instance(ctx, platform)\n  84          assert(\n  85              platform.si_cl1_qemu_inst_mgr == nil,\n  86              \"duplicate object: platform.si_cl1_qemu_inst_mgr\")\n  87          platform.si_cl1_qemu_inst_mgr = {",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "isr",
        "x": 590,
        "y": 570,
        "w": 390,
        "h": 96,
        "title": "Guest ISR / conditional",
        "lines": [
          "read status + process payload",
          "device clear is separate from EOI"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/cpu.lua",
        "line": 74,
        "excerpt": "  74              }\n  75              for _, signal in ipairs({\"irq\", \"fiq\", \"virq\", \"vfiq\"}) do\n  76                  gic[signal .. \"_out_\" .. gic_cpu] = {\n  77                      bind = \"&si_cl1_cpu_\" .. i .. \".\" .. signal .. \"_in\";\n  78                  }\n  79              end\n  80          end\n  81      end\n  82  \n  83      function block.define_qemu_instance(ctx, platform)\n  84          assert(\n  85              platform.si_cl1_qemu_inst_mgr == nil,\n  86              \"duplicate object: platform.si_cl1_qemu_inst_mgr\")\n  87          platform.si_cl1_qemu_inst_mgr = {",
        "detail": "일반적인 guest 처리 흐름을 설명하는 조건부 노드입니다. 연결 소스는 CPU IRQ binding이며 firmware ISR 구현 자체는 아직 추적하지 않았습니다.",
        "stage": 3
      },
      {
        "id": "clear",
        "x": 65,
        "y": 570,
        "w": 390,
        "h": 96,
        "title": "clear_mbx_doorbell_channel()",
        "lines": [
          "clear status / recompute level",
          "paired_pbx() acknowledgement"
        ],
        "source": "hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h",
        "line": 1807,
        "excerpt": "1807      void clear_mbx_doorbell_channel(unsigned int channel, uint32_t mask)\n1808      {\n1809          if (channel >= channel_count()) {\n1810              return;\n1811          }\n1812  \n1813          m_frame.clear_status_bits(channel, mask);\n1814          update_combined_irq();\n1815  \n1816          std::ostringstream detail;\n1817          detail << \"channel=\" << channel\n1818                 << \" mask=0x\" << std::hex << mask\n1819                 << \" status=0x\" << m_frame.status(channel);\n1820          if (p_trace.get_value() &&",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "deassert",
        "x": 65,
        "y": 775,
        "w": 390,
        "h": 96,
        "title": "IRQ deassert",
        "lines": [
          "update_combined_irq()",
          "falling level special handling"
        ],
        "source": "hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h",
        "line": 1074,
        "excerpt": "1074          const bool level = m_frame.any_combined_irq() || fast_group_status() != 0;\n1075          {\n1076              std::lock_guard<std::mutex> lock(m_irq_update_lock);\n1077              m_pending_irq_level = level;\n1078              m_pending_irq_update = true;\n1079              /*\n1080               * Serialize the socket write with an in-flight asynchronous\n1081               * assertion. A mailbox clear can run inside a guest ISR, so the\n1082               * deassertion must be visible before its MMIO write returns.\n1083               */\n1084              if (!level && m_emitted_irq_valid && m_emitted_irq_level) {\n1085                  m_pending_irq_update = false;\n1086                  if (p_trace.get_value()) {\n1087                      trace_event(\"combined-irq\", \"level=false bound=\" +",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "eoi",
        "x": 1110,
        "y": 775,
        "w": 390,
        "h": 96,
        "title": "GIC EOI / deactivate",
        "lines": [
          "guest interrupt completion",
          "not mailbox status clear"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/cpu.lua",
        "line": 74,
        "excerpt": "  74              }\n  75              for _, signal in ipairs({\"irq\", \"fiq\", \"virq\", \"vfiq\"}) do\n  76                  gic[signal .. \"_out_\" .. gic_cpu] = {\n  77                      bind = \"&si_cl1_cpu_\" .. i .. \".\" .. signal .. \"_in\";\n  78                  }\n  79              end\n  80          end\n  81      end\n  82  \n  83      function block.define_qemu_instance(ctx, platform)\n  84          assert(\n  85              platform.si_cl1_qemu_inst_mgr == nil,\n  86              \"duplicate object: platform.si_cl1_qemu_inst_mgr\")\n  87          platform.si_cl1_qemu_inst_mgr = {",
        "detail": "아키텍처 설명 노드이며 현재 단계에서 guest handler와 GIC register trace는 NOT_RUN입니다.",
        "stage": 3
      }
    ],
    "edges": [
      {
        "a": "status",
        "b": "update",
        "label": "status changed",
        "kind": "call",
        "stage": 1,
        "route": null
      },
      {
        "a": "update",
        "b": "emit",
        "label": "async event / delta cycle",
        "kind": "irq",
        "stage": 1,
        "route": null
      },
      {
        "a": "emit",
        "b": "gic",
        "label": "irq signal → spi_in_41",
        "kind": "irq",
        "stage": 2,
        "route": null
      },
      {
        "a": "gic",
        "b": "cpu",
        "label": "irq_out_i",
        "kind": "irq",
        "stage": 3,
        "route": null
      },
      {
        "a": "cpu",
        "b": "isr",
        "label": "exception, if enabled",
        "kind": "irq",
        "stage": 3,
        "route": null
      },
      {
        "a": "isr",
        "b": "clear",
        "label": "MMIO clear via router",
        "kind": "tlm",
        "stage": 3,
        "route": null
      },
      {
        "a": "clear",
        "b": "deassert",
        "label": "status recomputation",
        "kind": "call",
        "stage": 3,
        "route": null
      },
      {
        "a": "isr",
        "b": "eoi",
        "label": "architectural completion",
        "kind": "irq",
        "stage": 3,
        "route": [
          [
            785,
            666
          ],
          [
            785,
            823
          ],
          [
            1110,
            823
          ]
        ]
      }
    ]
  },
  {
    "title": "Mailbox / AP ↔ SI CL1 HIPC",
    "subtitle": "Data lane은 동일 backing 접근 · control lane은 pair 기반 내부 호출 · ATU 설정과 firmware 순서는 조건부",
    "width": 1600,
    "height": 960,
    "groups": [
      {
        "label": "DATA / shared-memory access (address view)",
        "x": 20,
        "y": 70,
        "w": 1560,
        "h": 260
      },
      {
        "label": "CONTROL / AP → SI CL1 notification",
        "x": 20,
        "y": 350,
        "w": 1560,
        "h": 270
      },
      {
        "label": "ACK / receiver clear and sender status",
        "x": 20,
        "y": 640,
        "w": 1560,
        "h": 280
      }
    ],
    "nodes": [
      {
        "id": "apdata",
        "x": 55,
        "y": 140,
        "w": 300,
        "h": 96,
        "title": "AP CPU → ap_router",
        "lines": [
          "AP alias 0xE0130000",
          "ap_hipc_alias → 0x00100000"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/interconnect.lua",
        "line": 34,
        "excerpt": "  34  \n  35      platform.ap_hipc_alias = {\n  36          moduletype = \"addrtr\";\n  37          mapped_base_addr = AP_HIPC_ALIAS_BASE;\n  38          target_socket = {\n  39              address = hipc_shared_base;\n  40              size = hipc_shared_size;\n  41              bind = \"&ap_router.initiator_socket\";\n  42              relative_addresses = false;\n  43              priority = 0;\n  44          };\n  45          initiator_socket = {bind = \"&ap_router.target_socket\"};\n  46          log_level = 0;\n  47      }",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 0
      },
      {
        "id": "shared",
        "x": 445,
        "y": 140,
        "w": 300,
        "h": 96,
        "title": "host_ap_bl2_header_sram",
        "lines": [
          "gs_memory backing",
          "0x00100000 / size 0x80000"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/boot.lua",
        "line": 1,
        "excerpt": "   1  local AP_FLASH_SIZE = 0x08000000\n   2  local AP_FLASH_BASE = 0x38000000\n   3  local AP_BL2_HEADER_SRAM_BASE = 0x00100000\n   4  local AP_TRUSTED_NVCTR_BASE = 0x32030000\n   5  local AP_BL2_HEADER_SRAM_SIZE = 0x00080000\n   6  local AP_FLASH_SECTOR_SIZE = 0x00001000\n   7  local AP_TRUSTED_NVCTR_SIZE = 0x00010000\n   8  \n   9  local boot = {}\n  10  \n  11  function boot.define(ctx, platform)\n  12      local options = ctx.options\n  13      assert(platform.host_ap_bl2_header_sram == nil, \"duplicate Apollo object\")\n  14      platform.host_ap_bl2_header_sram = {",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 0
      },
      {
        "id": "sib",
        "x": 835,
        "y": 140,
        "w": 300,
        "h": 96,
        "title": "si_cl1_hipc_bridge",
        "lines": [
          "addrtr: 0xE0130000",
          "→ AP address 0x00100000"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/interconnect.lua",
        "line": 21,
        "excerpt": "  21          assert(\n  22              platform.si_cl1_hipc_bridge == nil,\n  23              \"duplicate object: platform.si_cl1_hipc_bridge\")\n  24          platform.si_cl1_hipc_bridge = {\n  25              moduletype = \"addrtr\";\n  26              mapped_base_addr = SI_CL1_HIPC_ALIAS_BASE;\n  27              target_socket = {\n  28                  address = SI_CL1_HIPC_SHARED_BASE;\n  29                  size = SI_CL1_HIPC_SHARED_SIZE;\n  30                  bind = \"&si_cl1_router.initiator_socket\";\n  31                  relative_addresses = false;\n  32              };\n  33              initiator_socket = {bind = \"&ap_router.target_socket\"};\n  34              log_level = 0;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 0
      },
      {
        "id": "sidata",
        "x": 1225,
        "y": 140,
        "w": 300,
        "h": 96,
        "title": "SI CL1 CPU → router",
        "lines": [
          "mem → si_cl1_router",
          "HIPC window 0xE0130000"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/cpu.lua",
        "line": 28,
        "excerpt": "  28              platform[\"si_cl1_cpu_\" .. i] = {\n  29                  moduletype = \"cpu_arm_cortexR82\";\n  30                  args = {qemu_instance};\n  31                  mem = {bind = \"&si_cl1_router.target_socket\"};\n  32                  has_el2 = true;\n  33                  psci_conduit = \"smc\";\n  34                  start_powered_off = false;\n  35                  start_in_reset = true;\n  36                  reset_power_on = true;\n  37                  rvbar = runtime.entry;\n  38                  mp_affinity = SI_CL1_AFFINITY_BASE +\n  39                      (i * SI_CL1_AFFINITY_STRIDE);\n  40                  cntfrq_hz = ARCH_TIMER_FREQUENCY_HZ;\n  41                  request_origin_id = ctx.request_context.origin.si_cl1_cpu_base + i;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 0
      },
      {
        "id": "atu",
        "x": 55,
        "y": 420,
        "w": 300,
        "h": 96,
        "title": "AP → host_ap_atu",
        "lines": [
          "translation_socket @ 0x40000000",
          "initiator → system_router"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/interconnect.lua",
        "line": 35,
        "excerpt": "  35      local options = ctx.options\n  36      local atu_trace_address_min = options.atu_trace_address_min\n  37      local atu_trace_address_max = options.atu_trace_address_max\n  38      assert(platform.host_ap_atu == nil, \"duplicate Apollo object: host_ap_atu\")\n  39      platform.host_ap_atu = {\n  40          moduletype = \"rse_atu\";\n  41          trace = options.atu_trace;\n  42          trace_limit = options.atu_trace_limit;\n  43          trace_filter = options.atu_trace_filter;\n  44          trace_address_min = atu_trace_address_min;\n  45          trace_address_max = atu_trace_address_max;\n  46          enable_dmi = options.enable_ap_cpus and options.atu_dmi;\n  47          build_config = SYSTEM_ATU_BUILD_CONFIG;\n  48          target_socket = {",
        "detail": "AP router의 ATU translation window를 통해 system address로 접근합니다. 도달 주소는 firmware가 설정한 ATU region에 의존합니다.",
        "stage": 0
      },
      {
        "id": "pbx",
        "x": 445,
        "y": 420,
        "w": 300,
        "h": 96,
        "title": "host_ap_si_cl1_mhu_pbx",
        "lines": [
          "mhu320ae / frame=pbx",
          "pair=apollo_ap_to_si_cl1"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/system_mgmt/ap_si_mailbox.lua",
        "line": 145,
        "excerpt": " 145      assert(platform.host_ap_si_cl1_mhu_pbx == nil, \"duplicate Apollo object: host_ap_si_cl1_mhu_pbx\")\n 146      platform.host_ap_si_cl1_mhu_pbx = options.enable_ap_cpus and {\n 147          moduletype = \"mhu320ae\";\n 148          fast_channel_count = 64;\n 149          fast_channels_per_group = 32;\n 150          fast_channel_word_bits = 32;\n 151          frame = \"pbx\";\n 152          pair = \"apollo_ap_to_si_cl1\";\n 153          protocol = \"doorbell-bridge\";\n 154          channel_count = AP_SI_CL1_MHU_CHANNEL_COUNT;\n 155          trace = options.mhu_trace;\n 156          trace_limit = options.mhu_trace_limit;\n 157          target_socket = {\n 158              address = HOST_AP_SI_CL1_MHU_PBX_PHYS_BASE;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 1
      },
      {
        "id": "mbx",
        "x": 835,
        "y": 420,
        "w": 300,
        "h": 96,
        "title": "si_cl1_hipc_mhu_mbx",
        "lines": [
          "frame=mbx / same pair",
          "signal_doorbell_channel()"
        ],
        "source": "hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h",
        "line": 2230,
        "excerpt": "2230                                m_runtime_doorbell_fault.channel == channel;\n2231              if (drop) {\n2232                  m_runtime_doorbell_fault.armed = false;\n2233                  ++m_runtime_doorbell_fault.match_count;\n2234  \n2235                  std::ostringstream fault_detail;\n2236                  fault_detail << \"channel=\" << channel\n2237                               << \" match_count=\"\n2238                               << m_runtime_doorbell_fault.match_count;\n2239                  trace_event(\"runtime-doorbell-dropped\", fault_detail.str());\n2240              } else if (auto mbx = paired_mbx()) {\n2241                  mbx->signal_doorbell_channel(channel, value);\n2242              }\n2243              schedule_requester_hold(channel, requester);",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 2
      },
      {
        "id": "irq",
        "x": 1225,
        "y": 420,
        "w": 300,
        "h": 96,
        "title": "SI CL1 GIC → CPU",
        "lines": [
          "MBX irq → spi_in_41",
          "INTID 73 → irq_out_i"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/mailbox.lua",
        "line": 54,
        "excerpt": "  54              platform.si_cl1_hipc_mhu_mbx == nil,\n  55              \"duplicate object: platform.si_cl1_hipc_mhu_mbx\")\n  56          platform.si_cl1_hipc_mhu_mbx = {\n  57              moduletype = \"mhu320ae\";\n  58              fast_channel_count = 64;\n  59              fast_channels_per_group = 32;\n  60              fast_channel_word_bits = 32;\n  61              frame = \"mbx\";\n  62              pair = \"apollo_ap_to_si_cl1\";\n  63              protocol = \"doorbell-bridge\";\n  64              channel_count = SI_CL1_MHU_CHANNELS;\n  65              trace = mhu_trace;\n  66              trace_limit = mhu_trace_limit;\n  67              target_socket = {",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 2
      },
      {
        "id": "ack",
        "x": 445,
        "y": 725,
        "w": 300,
        "h": 96,
        "title": "clear_postbox_doorbell_channel",
        "lines": [
          "clear sender status bits",
          "set interrupt status / update IRQ"
        ],
        "source": "hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h",
        "line": 1791,
        "excerpt": "1791      void clear_postbox_doorbell_channel(unsigned int channel, uint32_t mask)\n1792      {\n1793          if (channel >= channel_count()) {\n1794              return;\n1795          }\n1796  \n1797          const bool had_pending_transfer = (m_frame.status(channel) & mask) != 0;\n1798          const bool ack_empty_transfer = p_pair.get_value() != \"ap_si_cl1\" ||\n1799                                          p_protocol.get_value() != \"doorbell\";\n1800          m_frame.clear_status_bits(channel, mask);\n1801          if (had_pending_transfer || ack_empty_transfer) {\n1802              m_frame.set_int_status_bits(channel, 1);\n1803          }\n1804          update_combined_irq();",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "clear",
        "x": 835,
        "y": 725,
        "w": 300,
        "h": 96,
        "title": "clear_mbx_doorbell_channel",
        "lines": [
          "receiver MMIO clear",
          "paired_pbx() → sender clear"
        ],
        "source": "hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h",
        "line": 1807,
        "excerpt": "1807      void clear_mbx_doorbell_channel(unsigned int channel, uint32_t mask)\n1808      {\n1809          if (channel >= channel_count()) {\n1810              return;\n1811          }\n1812  \n1813          m_frame.clear_status_bits(channel, mask);\n1814          update_combined_irq();\n1815  \n1816          std::ostringstream detail;\n1817          detail << \"channel=\" << channel\n1818                 << \" mask=0x\" << std::hex << mask\n1819                 << \" status=0x\" << m_frame.status(channel);\n1820          if (p_trace.get_value() &&",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "reverse",
        "x": 1225,
        "y": 725,
        "w": 300,
        "h": 96,
        "title": "Reply: separate reverse pair",
        "lines": [
          "si_cl1_hipc_mhu_pbx → AP MBX",
          "pair=apollo_si_cl1_to_ap"
        ],
        "source": "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/si_cl1/mailbox.lua",
        "line": 29,
        "excerpt": "  29          assert(\n  30              platform.si_cl1_hipc_mhu_pbx == nil,\n  31              \"duplicate object: platform.si_cl1_hipc_mhu_pbx\")\n  32          platform.si_cl1_hipc_mhu_pbx = {\n  33              moduletype = \"mhu320ae\";\n  34              fast_channel_count = 64;\n  35              fast_channels_per_group = 32;\n  36              fast_channel_word_bits = 32;\n  37              frame = \"pbx\";\n  38              pair = \"apollo_si_cl1_to_ap\";\n  39              protocol = \"doorbell-bridge\";\n  40              channel_count = SI_CL1_MHU_CHANNELS;\n  41              trace = mhu_trace;\n  42              trace_limit = mhu_trace_limit;",
        "detail": "현재 소스의 선언 및 연결을 표시합니다. 아래 발췌와 socket 방향을 함께 확인하세요.",
        "stage": 3
      },
      {
        "id": "helper",
        "x": 55,
        "y": 725,
        "w": 300,
        "h": 96,
        "title": "Optional memory helper",
        "lines": [
          "MHU initiator_socket",
          "mem_read32 → b_transport"
        ],
        "source": "hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h",
        "line": 674,
        "excerpt": " 674      template <typename T>\n 675      T load(uint64_t offset) const\n 676      {\n 677          return m_frame.load<T>(offset);\n 678      }\n 679  \n 680      bool mem_access(tlm::tlm_command command, uint64_t address, void* data, unsigned int len)\n 681      {\n 682          tlm::tlm_generic_payload trans;\n 683          sc_core::sc_time delay = sc_core::SC_ZERO_TIME;\n 684  \n 685          trans.set_command(command);\n 686          trans.set_address(address);\n 687          trans.set_data_ptr(static_cast<unsigned char*>(data));",
        "detail": "이 socket은 memory helper용입니다. doorbell peer 호출 자체가 이 socket을 통한 payload 복사라는 뜻은 아닙니다.",
        "stage": 3
      }
    ],
    "edges": [
      {
        "a": "apdata",
        "b": "shared",
        "label": "addrtr + AP decode",
        "kind": "tlm",
        "stage": 0,
        "route": null
      },
      {
        "a": "sidata",
        "b": "sib",
        "label": "router initiator",
        "kind": "tlm",
        "stage": 0,
        "route": null
      },
      {
        "a": "sib",
        "b": "shared",
        "label": "ap_router.target_socket",
        "kind": "tlm",
        "stage": 0,
        "route": null
      },
      {
        "a": "atu",
        "b": "pbx",
        "label": "system_router decode",
        "kind": "tlm",
        "stage": 1,
        "route": null
      },
      {
        "a": "pbx",
        "b": "mbx",
        "label": "paired_mbx() → signal",
        "kind": "call",
        "stage": 2,
        "route": null
      },
      {
        "a": "mbx",
        "b": "irq",
        "label": "event → irq signal",
        "kind": "irq",
        "stage": 2,
        "route": null
      },
      {
        "a": "mbx",
        "b": "clear",
        "label": "receiver clears status",
        "kind": "tlm",
        "stage": 3,
        "route": null
      },
      {
        "a": "clear",
        "b": "ack",
        "label": "paired_pbx()",
        "kind": "call",
        "stage": 3,
        "route": null
      }
    ]
  }
];
