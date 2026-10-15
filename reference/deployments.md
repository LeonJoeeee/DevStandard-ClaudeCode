# Deploying a self-hosted service

Deploying follows the existing release authorization: the human's words or standing delegation;
the agent executes the deploy. This page grants no authority. **Merge ≠ deploy:** deploying is a
separate act with its own record.

Run the deploy on the service's own host, from a local checkout of the merged commit. Cut the
release archive from that commit (for example, `git archive`), never from a working tree. The repo
remains the source of truth; the host holds the instance.

Keep four roles separate: **development checkout** (editable source), **release archive** (commit
snapshot), **running instance** (activated release), and **project data** (service state). Never
develop in the running directory.

The default is **immutable release directories** and an atomically switched **`current` pointer**.
Stop the service, switch the pointer, start the service, then probe its health. If the probe fails,
roll back by switching to the previous release with the same stop / switch / start / probe sequence;
rollback changes the pointer, not the code.

Write a per-deploy receipt recording the authorization, merged commit, previous and new release
identities, time, health result, and any rollback.

A deploy never migrates or resets state implicitly. For destinations, including data, secrets and
configuration, use the [placement rule](where-it-goes.md#the-placement-rule). For deploy-root
requirements, including retention of previous releases for rollback, follow
[kind 2 of out-of-repo writes](out-of-repo-writes.md#three-kinds-of-write-one-rule-each).

Containers or orchestration earn their cost when multiple hosts or many services need coordination.
A trivial stateless tool may instead run from a checkout whose deployed contents match the merged
commit exactly; never develop there. Otherwise use the immutable-release default above.
Service-specific commands and health probes belong in the project's own docs.
