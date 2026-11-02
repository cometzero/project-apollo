const SYSTEMC_PROCESSES = [
  {
    "id": "sc-emit",
    "title": "SC_METHOD: emit_combined_irq",
    "source": "hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h",
    "line": 3821,
    "detail": "m_irq_update_event에 sensitive한 SystemC method. host OS process나 전용 TID가 아닙니다.",
    "excerpt": "3821          SC_METHOD(emit_combined_irq);\n3822          sensitive << m_irq_update_event;\n3823          dont_initialize();\n3824  \n3825          SC_THREAD(emit_power_on_reset);\n3826  \n3827          SC_METHOD(emit_synthetic_postbox_completions);\n3828          sensitive << m_synthetic_postbox_completion_event;\n3829          dont_initialize();"
  },
  {
    "id": "sc-hold",
    "title": "SC_THREAD: requester_hold_worker",
    "source": "hsoc-stack/tools/qbox-platform/systemc-components/mhu320ae/include/mhu320ae.h",
    "line": 3834,
    "detail": "SystemC kernel이 scheduling하는 process. 현재 실행 중인지는 source만으로 알 수 없습니다.",
    "excerpt": "3834          SC_THREAD(requester_hold_worker);\n3835  \n3836          target_socket.register_b_transport(this, &mhu320ae::b_transport);\n3837          ram_fault_socket.register_b_transport(this, &mhu320ae::ram_fault_transport);\n3838      }\n3839  };\n3840  \n3841  extern \"C\" void module_register();"
  },
  {
    "id": "sc-cpu",
    "title": "sc_spawn: mainloop_thread_coroutine",
    "source": "hsoc-stack/tools/qbox/qemu-components/common/include/cpu.h",
    "line": 1326,
    "detail": "m_coroutines 조건이 참인 구성에서 생성되는 SystemC process. effective runtime policy는 UNKNOWN입니다.",
    "excerpt": "1326  inline void QemuCpu::QuantumKeeperSync::on_after_cpu_created()\n1327  {\n1328      if (m_qemu_cpu.m_coroutines) {\n1329          m_qemu_cpu.m_sc_thread = sc_core::sc_spawn(std::bind(&QemuCpu::mainloop_thread_coroutine, &m_qemu_cpu));\n1330      }\n1331  }\n1332  \n1333  inline void QemuCpu::QuantumKeeperSync::on_before_end_of_elaboration()\n1334  {"
  }
];
