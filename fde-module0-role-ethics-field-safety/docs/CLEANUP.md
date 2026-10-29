# Cleanup

1. Retain only the artefacts required by the evidence and retention plan.
2. Verify the evidence seal before deleting the working directory.
3. Run `uv run python tools/module0.py reset --workspace work/current`.
4. Delete any temporary assessor control file supplied outside the repository, if authorised by the assessor.
5. Confirm that no customer data, credentials or external-system information entered the repository.

The reset command refuses paths outside the repository's `work` directory.
