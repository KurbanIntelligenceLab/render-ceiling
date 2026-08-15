# Checkpoint 1.3 — citation verification

Every entry below was checked against a publisher or proceedings record. Venue evidence is
recorded so a reader can confirm without repeating the search. Entries marked DO NOT CITE are
arXiv-only preprints; per the task list they are held back from related-work claims.

## ADD — verified, journal of record

### Tomasi & Kanade 1992
- Title: Shape and motion from image streams under orthography: a factorization method
- Authors: Carlo Tomasi, Takeo Kanade
- Venue: International Journal of Computer Vision, volume 9, issue 2, pages 137-154, November 1992
- Publisher: Kluwer Academic Publishers (now Springer)
- DOI: 10.1007/BF00129684
- Evidence: Springer article record at doi.org/10.1007/BF00129684 gives
  "Int J Comput Vision 9, 137-154 (1992)"; the IJCV volume 9 issue 2 table of contents lists the
  Tomasi/Kanade paper in that issue.
- Position: Section 3.1, as the direct methodological ancestor of the oracle.
- Why it belongs: establishes that under orthographic projection the multi-view measurement matrix
  has rank 3, and recovers shape without computing depth as an intermediate step. Our oracle is the
  known-camera, species-constrained, closed-form specialisation of exactly that setting: we do not
  need to factor for the cameras because the render protocol fixes them, which is what turns the
  reconstruction into a deterministic inversion rather than an estimation problem.

### Daunhawer et al. 2023
- Title: Identifiability Results for Multimodal Contrastive Learning
- Authors: Imant Daunhawer, Alice Bizeul, Emanuele Palumbo, Alexander Marx, Julia E. Vogt
- Venue: International Conference on Learning Representations (ICLR) 2023
- Evidence: OpenReview conference record (forum id U_2kuqoTcB) and the authors' official code
  repository, both labelled ICLR 2023.
- Position: Related Work, multi-view identifiability line.
- Why it belongs: provides identifiability guarantees for recovering shared latent factors from
  multiple views under a learned contrastive objective. The contrast is the point of our framing:
  their guarantee is about what a learned representation recovers, ours is exact geometric
  identifiability of scene content for a known renderer, used to bound task accuracy.

### GaussianCAD
- Title: GaussianCAD: Robust self-supervised CAD reconstruction from three orthographic views using
  3D Gaussian Splatting
- Venue: Computers and Electrical Engineering (Elsevier), 2026
- Evidence: ScienceDirect article PII S0045790626001497. The PII prefix 0045-7906 is the print ISSN
  of Computers and Electrical Engineering, confirming the journal of record; the ScienceDirect
  record is dated 2026.
- Status: journal-published, so citable under the task list's rule.
- Position: Section 3.1 or Related Work, orthographic multi-view reconstruction.
- Why it belongs: nearest neighbour on the input side (three orthographic views), and a clean
  contrast on method: theirs is a learned self-supervised reconstruction objective, ours is a
  closed-form inversion used as a bound.
- Note: the reviewer named this paper; the citation is therefore responsive as well as apt.

## DO NOT CITE — arXiv-only preprint

### TriaGS
- Title: TriaGS: Differentiable Triangulation-Guided Geometric Consistency for 3D Gaussian Splatting
- Identifier: arXiv:2512.06269
- Evidence: arXiv abstract and PDF only; no journal or conference record found.
- Decision: held back from related-work claims per the task list. Available if a reviewer raises it,
  in which case it is cited as a preprint with the arXiv identifier.

## Bibliography entries to add to references.bib

@article{tomasi1992factorization,
  author  = {Carlo Tomasi and Takeo Kanade},
  title   = {Shape and Motion from Image Streams under Orthography: a Factorization Method},
  journal = {International Journal of Computer Vision},
  volume  = {9},
  number  = {2},
  pages   = {137--154},
  year    = {1992},
  doi     = {10.1007/BF00129684}
}

@inproceedings{daunhawer2023identifiability,
  author    = {Imant Daunhawer and Alice Bizeul and Emanuele Palumbo and Alexander Marx and Julia E. Vogt},
  title     = {Identifiability Results for Multimodal Contrastive Learning},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2023}
}

@article{gaussiancad2026,
  title   = {{GaussianCAD}: Robust Self-Supervised {CAD} Reconstruction from Three Orthographic
             Views Using {3D} Gaussian Splatting},
  journal = {Computers and Electrical Engineering},
  year    = {2026},
  note    = {ScienceDirect PII S0045790626001497}
}

Author list for the GaussianCAD entry is incomplete in the search record (the ScienceDirect
abstract page is paywalled). Retrieve the full author list from the publisher record before the
camera-ready; the entry is otherwise verified.
