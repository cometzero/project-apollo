---
name: update-codebase-indexes
description: Refresh and verify codebase-memory-mcp indexes for one, several, or all Arm Auto Solutions top-level submodules using their canonical project names. Use for requests to index, reindex, incrementally update, list, or check codebase-memory coverage for this workspace, including Linux, firmware, Yocto layers, QBox, QEMU, Buildroot, and tests.
---

# Update Codebase Indexes

Use the repository helper so repeated updates preserve canonical project names
and route healthy indexes through incremental indexing.

## Workflow

1. Work from `/build/arm/arm-auto-solutions` and read the Codebase Memory
   Indexing section in `AGENTS.md`.
2. List the registered mapping when the requested directory is ambiguous:

   ```bash
   scripts/update_codebase_indexes.sh --list
   ```

3. Refresh one directory with its canonical `fast` index:

   ```bash
   scripts/update_codebase_indexes.sh --directory layers/meta-arm
   ```

   Repeat `--directory` to update several selected roots.

4. Refresh all top-level submodules only when the user requests the complete
   set:

   ```bash
   scripts/update_codebase_indexes.sh --all
   ```

5. Read the generated `summary.tsv` and report project, root path, status,
   nodes, edges, DB bytes, elapsed time, maximum RSS, and exit status. Report
   the output directory containing the detailed index, status, and time logs.

## Safety and Scope

- Keep the canonical mapping in the helper aligned with the two index tables in
  `AGENTS.md` and the root `.gitmodules` file.
- Do not call `delete_project` for normal refreshes. Reuse the existing name so
  codebase-memory-mcp can perform incremental indexing.
- Run indexes sequentially. Linux remains last in `--all` because a full Linux
  index can consume approximately 12.5 GiB RSS.
- Do not initialize or independently index recursive ROM, test, or third-party
  submodules unless the user explicitly expands the scope.
- Treat fast-mode exclusions and partial coverage as expected limitations.
  Read excluded or partially parsed source directly when a task depends on it.
- Stop on the first failed command or verification mismatch. Preserve all logs
  and report the exact failing project and output directory.
