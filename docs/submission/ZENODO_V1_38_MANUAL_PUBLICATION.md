# Zenodo v1.38 - Manual Publication Checklist

Status: completed by Miguel and verified against the public Zenodo API on
2026-08-22. Version DOI: `10.5281/zenodo.22061658`. Record concept DOI:
`10.5281/zenodo.22061657`. The downloaded PDF is byte-identical to the local
candidate.

## 1. Open the correct version chain

1. Sign in to Zenodo.
2. Open the published v1.37 record:
   https://zenodo.org/records/21965090
3. Click **New version**. Do not create an unrelated new upload and do not edit
   the files of v1.37 retroactively.
4. Confirm that the deposit form identifies the draft as a new version.

Zenodo no longer copies files automatically into a new version. If the old
`zuse_preprint.pdf` appears after using **Import files**, remove or replace it
so that the draft contains exactly the v1.38 PDF described below.

## 2. Upload exactly this file

- Local file: `paper/zuse_preprint.pdf`
- Upload name: `zuse_preprint.pdf`
- Pages: `62`
- Size: `1,061,595 bytes`
- MD5: `428f0532c2ff9bbeddc256e5978bd82c`
- SHA-256: `207cff30864d4abd180a5de294628bbe28ac433f1213bad145aa131cbd63b042`

After upload, wait until Zenodo reports the file as fully uploaded. If Zenodo
shows a pending or failed upload, remove that failed entry and upload the file
again. Do not publish with both the v1.37 and v1.38 PDFs attached.

## 3. Basic information

- Resource type: `Publication / Preprint`
- Title: `ZUSE Automat Agent: Empirical Law Discovery in Elementary Cellular Automata`
- Publication date: `2026-08-22`
- Creator: `Miguel Angel Concha Estrada`
- Affiliation: `Independent researcher`
- Version: `v1.38`
- Publisher: `Zenodo`
- Language: `English`
- License: `Creative Commons Attribution 4.0 International (CC BY 4.0)`
- Copyright: `Copyright (C) 2026 The author.`
- Existing DOI for this upload: `No`

Do not type the v1.37 DOI into the field for an existing DOI. This draft is a
new Zenodo version and Zenodo must assign its version-specific DOI. There is no
need to reserve a DOI because the DOI is not embedded in the candidate PDF.

## 4. Description

Copy the complete text under **Descripcion** from
`docs/submission/ZENODO_V1_38_DRAFT.md`, beginning with "La version candidata
v1.38" and ending with the repository URL. Do not add causal, predictive,
external-validation, population-generalization, confirmatory-significance, or
quantum-advantage language.

## 5. Keywords

Enter these eight keywords:

1. `elementary cellular automata`
2. `empirical law discovery`
3. `basin topology`
4. `Hamming geometry`
5. `graph motifs`
6. `mechanism-conditioned analysis`
7. `reproducible computational science`
8. `quantum-ready optimization`

## 6. Related work

Add the repository URL as the related software/repository identifier:

`https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent`

Use the relation **Is supplement to** if Zenodo offers it for the software
record. Do not add an unverified journal, arXiv, funding, or community record.

## 7. Final review before publishing

1. Save the draft and resolve every validation warning.
2. Use **Preview**.
3. Confirm title, creator, version `v1.38`, date, preprint type, English,
   CC-BY-4.0, eight keywords, repository relationship, and public file access.
4. Confirm there is exactly one file named `zuse_preprint.pdf`.
5. Reconfirm the file size is `1,061,595 bytes`.
6. Confirm the description contains the scope `122 rescues in 24 mixed K2
   instances` and the explicit non-causal/non-external-validation limits.
7. Only then click **Publish** and confirm publication.

## 8. Return these values to Codex

Immediately after publication, copy from the public record:

- Version DOI assigned to v1.38.
- Record concept DOI shown under **Cite all versions** or equivalent.
- Public record URL.
- Direct download URL for `zuse_preprint.pdf`.
- Publication date displayed by Zenodo.

Do not create the GitHub tag or release manually. Codex will first download the
public Zenodo PDF, compare it byte-for-byte with the committed local PDF, then
update DOI metadata, create the annotated `v1.38` tag, push it, and create the
GitHub release.
