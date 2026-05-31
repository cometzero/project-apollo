<a id="product-and-document-information"></a>
# Product and document information

<!-- Source PDF page: 683 -->

Read the information in these sections to understand the release status of the product and
documentation, and the conventions used in Arm documents.

<a id="product-status"></a>
## Product status

All products and services provided by Arm require deliverables to be prepared and made available
at different levels of completeness. The information in this document indicates the appropriate
level of completeness for the associated deliverables.

Product completeness status
The information in this document is Final, that is for a developed product.

Product revision status
The r0p1 identifier indicates the revision status of the product described in this manual, where:

rx                   Identifies the major revision of the product.
py                   Identifies the minor revision or modification status of the product.

<a id="revision-history"></a>
## Revision history

These sections can help you understand how the document has changed over time.

Document release information
The Document history table gives the issue number and the released date for each released issue
of this document.

Document history

Issue           Date                        Confidentiality              Change

0001-01         27 January 2026             Non-Confidential             First early access release for r0p1

Change history
The Change history tables describe the technical changes between released issues of this
document in reverse order. Issue numbers match the revision history in Document release
information on page 683.

<!-- Source PDF page: 684 -->

Table 2: Issue 01-01
Change                              Location
First early access release for r0p0 -

<a id="conventions"></a>
## Conventions

The following subsections describe conventions used in Arm documents.

Glossary
The Arm Glossary is a list of terms used in Arm documentation, together with definitions for
those terms. The Arm Glossary does not contain terms that are industry standard unless the Arm
meaning differs from the generally accepted meaning.

See the Arm Glossary for more information: developer.arm.com/glossary.

Typographic conventions
Arm documentation uses typographical conventions to convey specific meaning.

Convention                   Use
italic                       Citations.
bold                         Terms in descriptive lists, where appropriate.
monospace                    Text that you can enter at the keyboard, such as commands, file and program names, and
source code.
monospace underline A permitted abbreviation for a command or option. You can enter the underlined text
instead of the full command or option name.
<and>                        Encloses replaceable terms for assembler syntax where they appear in code or code
fragments.

For example:

MRC p15, 0, <Rd>, <CRn>, <CRm>, <Opcode_2>

SMALL CAPITALS               Terms that have specific technical meanings as defined in the Arm® Glossary. For example,
IMPLEMENTATION DEFINED, IMPLEMENTATION SPECIFIC, UNKNOWN, and UNPREDICTABLE.

We recommend the following. If you do not follow these recommendations your
system might not work.

Your system requires the following. If you do not follow these requirements your
system will not work.

<!-- Source PDF page: 685 -->

You are at risk of causing permanent damage to your system or your equipment, or
of harming yourself.

This information is important and needs your attention.

This information might help you perform a task in an easier, better, or faster way.

This information reminds you of something important relating to the current
content.

Timing diagrams
The following figure explains the components used in timing diagrams. Variations, when they occur,
have clear labels. You must not assume any timing information that is not explicit in the diagrams.

Shaded bus and signal areas are undefined, so the bus or signal can assume any value within the
shaded area at that time. The actual level is unimportant and does not affect normal operation.

Figure 1: Key to timing diagram conventions

Signals
The signal conventions are:

<!-- Source PDF page: 686 -->

Signal level
The level of an asserted signal depends on whether the signal is active-HIGH or active-LOW.
Asserted means:
•   HIGH for active-HIGH signals.
•   LOW for active-LOW signals.

Lowercase n
At the start or end of a signal name, n denotes an active-LOW signal.
