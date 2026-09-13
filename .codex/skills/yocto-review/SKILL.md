---
name: yocto-review
description: Review Apollo Yocto metadata changes for reachable build, packaging and deployment defects.
---

# Yocto metadata review

Review the affected layer/provider and effective BitBake overrides.
Project metadata lives in hsoc-stack/yocto/meta-hsoc-{bsp,auto-solutions}.
Check affected dependencies, task signatures, licenses, patch ordering,
package ownership, services/permissions and deployment contracts.

Use [review checklist](references/review-checklist.md) or
doc/yocto-layer-recipe-review.md when the review needs those details.
Select parse/task checks that resolve uncertainty; do not fetch, rebuild or
boot every image as an automatic review ritual.

Return actionable findings with file/line and reachable failure path.
Distinguish static inference, parsed values, task results and runtime evidence.
A review request alone does not authorize fixes.
