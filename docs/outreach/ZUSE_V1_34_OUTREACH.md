# ZUSE v1.34 Outreach Pack

## Short release post

ZUSE v1.34 is out.

This release audits a methodological limit in the historical
periodic-background oscillator detector. A checkpointed replay of 5,783,040
configurations recovers and independently confirms 3,296 stationary
oscillators omitted by the former `T<=16` period cap.

All recovered cases belong to `rule_73` or `rule_109`. Previously detected
oscillators and the T=12 cohort used by the causal audits remain unchanged.
The result corrects catalog completeness without turning the finite replay into
an arbitrary-time theorem.

Preprint: https://doi.org/10.5281/zenodo.21826401

Release: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.34
