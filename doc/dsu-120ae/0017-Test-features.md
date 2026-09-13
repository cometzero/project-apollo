# Test features

Source: <https://developer.arm.com/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/Test-features>

### Test features

The DynamIQ Shared Unit-120AE (DSU-120AE) provides test signals that enable the use of Automatic Test Pattern Generation (ATPG) to test the Snoop Control Unit (SCU) and other logic in the DSU-120AE. Additionally, internal Memory Built-In Self Test (MBIST) interfaces are provided to test the L3 cache and other memory arrays of the DSU-120AE.

The DSU-120AE includes an ATPG test interface that provides signals to control the Design for Test (DFT) features of the DSU-120AE, and the cores in the cluster. For example, there are signals to control the resets on the flip-flops during scan shift. Consideration of how you use these signals can help to prevent problems with DFT implementation.

Arm® also provides an MBIST interface that enables you to test the DSU-120AE RAMs at operational frequency. You can add your own MBIST controllers to automatically generate test patterns and perform result comparisons. Optionally, you can use your EDA MBIST interfaces instead of the MBIST interfaces supplied by Arm®.

For a list of external scan control signals and information on their usage, see the Design for Test integration guidelines chapter in the Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual. For information about the test signals related to your core, see your core Configuration and Integration Manual.
