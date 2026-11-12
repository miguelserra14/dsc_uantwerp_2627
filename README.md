# DSC 2026–2027 – Preprocessing decisions

Decisions for the main preprocessing loop, based on the course slides
"Data Preprocessing: Basic" and "Data Preprocessing: Advanced" (Chapter 3.4).
The code is generic and driven by a config; column-to-type assignment is filled in locally.

## General setup
| Topic | Decision |
|---|---|
| Environment | Local Jupyter notebook in VS Code, kernel `C:\Users\migue\miniconda3\python.exe` (numpy, pandas, scikit-learn, openpyxl, xlrd, msoffcrypto-tool) |
| Protected data files | The data files are password-protected Excel files. They are decrypted **in memory only** (msoffcrypto-tool); the password is asked with `getpass` and never stored in the notebook |
| Loading cache | Protected files: **no disk cache** (would be an unprotected copy on OneDrive); kept in memory for the kernel session. Unprotected files: `<file>.<sheet>.cache.pkl` next to the source, rebuilt when the source changes (`use_cache` in CONFIG) |
| Project layout | `data/` (Excel files, git-ignored) · `preprocessing/` (`preprocessing.ipynb`, `col_config.py`, `col_config.example.py`) · `README.md` |
| Column assignment | `preprocessing/col_config.py` (target + column lists), loaded by the CONFIG cell; **git-ignored** because variable names are confidential. Template: `preprocessing/col_config.example.py` |
| Data files | In `data/` at the project root; the notebook uses `"data_dir": "../data"` (relative to `preprocessing/`). A full path in CONFIG also works. Not tracked by git (see `.gitignore`) |
| Notebook outputs | **nbstripout** git filter (`.gitattributes`): outputs are removed from every committed notebook, so printed column names / counts never reach git. Course notebooks in `tutorials/` are excluded. Every team member runs once: `python -m pip install nbstripout` then, in the repo, `python -m nbstripout --install --attributes .gitattributes` |
| Libraries | Preprocessing logic: pandas / numpy / scikit-learn only (no imbalanced-learn / category_encoders); file reading uses openpyxl, xlrd, msoffcrypto-tool |
| Target | Multiclass |
| Models consuming the data | Tree-based / boosting |
| Output | DataFrames with feature names (X/y train, val, test; X scoring) |

## Scope of the first version
Left out for now (may be added later):
- Oversampling (SMOTE / ADASYN)
- External packages (imbalanced-learn, category_encoders)
- Isolation Forest
- Feature interactions / polynomial features

## Splitting
| Topic | Decision |
|---|---|
| Ratios | 70% train / 15% validation / 15% test (from the training file) |
| Stratification | Yes, on the target class |
| Random seed | 42 |
| Scoring file | Only transformed with the pipeline fitted on train, never fitted on |

## Missing values
| Topic | Decision |
|---|---|
| Drop columns | If > 60% missing (measured on train) |
| Numeric imputation | Median |
| Missing indicator | Yes, added for imputed columns |
| Categorical imputation | Separate "Missing" category |

## Outliers and scaling (numeric)
| Topic | Decision |
|---|---|
| Outliers | Clip at 1st / 99th percentile (bounds learned on train) |
| Scaling | Z-score (StandardScaler), configurable: can be switched off or to MinMax |

## Categorical encoding
| Topic | Decision |
|---|---|
| Rare levels | Grouped into "Other" if < 1% of rows (train) |
| Nominal, low cardinality | One-hot encoding, keep all levels, unseen levels ignored |
| High-cardinality threshold | > 40 distinct levels |
| High-cardinality encoding | Hand-written, one-vs-rest per class; both WoE and supervised ratio (Vi) implemented, chosen by a config flag |
| One-vs-rest columns | K columns per variable (one per class) |
| Ordinal | Rank encoding with an explicit order per variable in the config; unknown levels -> -1 |

## Date variables
| Topic | Decision |
|---|---|
| Derived features | Year, month, weekday, is_weekend |
| Cyclical sin/cos | Not used |
| Days since reference date | Not used |
| Raw date column | Dropped after deriving features |

## Implementation details (preprocessing/preprocessing.ipynb)
| Topic | Detail |
|---|---|
| Order of numeric steps | Clip -> median impute (+ indicator) -> scale |
| Date parts | Treated as numeric afterwards (imputed / clipped / scaled like other numerics) |
| "Missing" category | Never grouped into "Other" |
| Unseen categories (val/test/scoring) | Mapped to "Other"; for high-card encoding they get the class prior (ratio) or 0 (WoE) |
| Supervised ratio smoothing | m-estimate toward the class prior, m = 1 (`ratio_smoothing`) |
| WoE adjustment | +0.5 on counts to avoid log(0) (`woe_adjustment`) |
| Columns not listed in CONFIG | Ignored, with a warning listing them |
| Missing indicators | Only for numeric columns that had missing values in train |

## Leakage rules
- Every imputer, clipper, scaler and encoder is fitted on the training set only.
- WoE / supervised ratio mappings are computed from the training target only.
- Validation, test and scoring sets are only transformed.

## Challenge facts that drive the design
Source: course submission instructions (details in `tutorials/PROJECT_INFO.txt`, kept local).
| Fact | Consequence |
|---|---|
| Target = EPC label, 8 **ordered** classes A+ > A > B > C > D > E > F > G | Encode target as rank 0..7; ordinal-aware encodings and decision rule |
| Official metric = **1-notch accuracy** (correct if within one class) | CV harness optimises it; exact accuracy and rank-MAE reported as secondary |
| Grade: report 4/5, 1-notch accuracy 1/5 | Every choice measured and justified (experiment log, ablation table, explainable AI) |
| Code is inspected to verify it **matches the predictions** | Fixed seeds, Run All reproduces the submitted xlsx; final notebook writes the template |
| Predictions for all 76,906 scoring rows, labels "A+".."G", template format | Export cell with checks (row count, valid labels, template columns) |
| "Use of AI" section is mandatory | Keep a log of how AI was used (Claude never saw data or variable descriptions) |
| Peer review adjusts individual grades | Visible, agreed work split within the group |
| Deadline 2026-12-10 23:59 CET, unlimited attempts before | Submit a valid early zip as a safety net; final freeze a few days before |

## Experiment log
Decided 2026-11-12 (analysis in `design_choices/phase0_choices.txt`, kept local). Both files local and git-ignored.
| Topic | Decision |
|---|---|
| Files | **Two files** linked by `run_id`: `experiments.csv` (one row per experiment, summary) and `folds.csv` (one row per fold) |
| `experiments.csv` columns | `run_id`, `timestamp`, `name`, key settings (`model`, `profile`, `high_card_method`, `decision_rule`), `settings_json`, `git_commit`, `git_dirty`, mean and std of each metric |
| `folds.csv` columns | `run_id`, `repeat`, `fold`, one column per metric |
| Settings | All scalar settings (preprocessing + model hyperparameters) in one JSON text column, plus the key columns above. **Column lists are never logged** (confidential) |
| Reproducibility | Git commit hash + dirty flag (uncommitted changes) on every row |
| Labelling | Short experiment name only |
| Metric columns | Follow the metrics decision (still open) |

## Report
Decided 2026-11-12. Skeleton in `report/` (requirements from `tutorials/PROJECT_INFO.txt`, section 4).
| Topic | Decision |
|---|---|
| Tool | LaTeX (Overleaf); `report/main.tex` + one file per section in `report/sections/` (fewer edit conflicts) |
| Structure | Cover · 1 Business Understanding · 2 Data Understanding · 3 Data Preparation · 4 Modeling and Evaluation · 5 Conclusion (counted, max 5 pages, numbered 1–5) · Use of AI (mandatory) · References · Appendices A coverage matrix, B extended results, C reproducibility (not counted, roman numbering) |
| Page budget per section | **Open** – decide later |
| Section owners | **Open** – not assigned yet |
| Placeholders | `\todo{...}` (red; hide with `\showtodosfalse`) and `\figplaceholder{...}` |
| Confidentiality | Tracked `.tex` files contain no variable names or data values; `report/figures/` and the compiled PDF are git-ignored |
| Local build | `pdflatex` → `bibtex` → `pdflatex` ×2 (MiKTeX; `latexmk` needs Perl, which is not installed) |

## Roadmap
Status: **planned, decisions still to be asked** (multiple choice) before each phase.
Items marked *(proposed)* are recommendations, not decisions.

### Phase 0 – Foundation (week of 12–18 Nov)
- Preprocessor made sklearn-compatible (`BaseEstimator`, `TransformerMixin`) so it runs inside
  `Pipeline([("pre", ...), ("model", ...)])` and is refitted in every CV fold (no leakage of target encodings).
- Target mapped to rank 0..7 (A+ = 0 … G = 7) with the inverse mapping for the export.
- Metric functions: 1-notch accuracy (primary), exact accuracy, MAE on rank.
- Scorer `make_scorer(one_notch_accuracy)` used in **all** CV and tuning (GridSearchCV's default
  `accuracy` is exact accuracy, not the official metric).
- **Window decision rule** *(proposed)*: predict the class k maximising p(k-1) + p(k) + p(k+1).
  This is the Bayes-optimal rule for 1-notch accuracy given calibrated probabilities; compared with plain argmax.
- Evaluation harness: `RepeatedStratifiedKFold`, results (mean ± std, per fold) appended to a local,
  git-ignored `experiments.csv`; test set used once at the end.
- Probe model *(proposed)*: `HistGradientBoostingClassifier` (sklearn, native NaN / categoricals).
- Export cell for the submission template.

### Phase 1 – Biggest expected gains (19–25 Nov)
- Out-of-fold target encoding for high-cardinality columns (backlog 3): `fit_transform` encodes train
  out-of-fold, `transform` uses the full-train mapping; checked against `sklearn.preprocessing.TargetEncoder`.
- Ordinal target encoding (backlog 2) *(proposed default)*: mean rank per category (1 column) or
  cumulative P(rank ≤ k) (7 columns), instead of 8 one-vs-rest columns.
- Separate thresholds: `rare_min_frac` for one-hot, lower `te_min_count` for target encoding; smoothing `m` tuned in CV.
- "tree" profile: no scaling / clipping, low-cardinality nominals as native categoricals.
- Class weights (backlog 8): *(proposed)* **off by default** – 1-notch accuracy is an overall accuracy and rewards
  frequent classes; tested once in the ablation.
- Classification vs regression on the rank + rounding, compared under the same CV.
- Missing-value ablation (course slides Prep 1–2): median + indicator · native NaN in HGB ("keep") ·
  `IterativeImputer` · `KNNImputer` (on a subsample if too slow).
- Model comparison table under the same harness and metric: the course models (KNN, decision tree,
  logistic regression, random forest, SVM) + HGB. KNN / SVM / logistic use the scaled profile;
  SVM-RBF is O(n²) → subsample or `LinearSVC`.
- Tuning with the preprocessor inside the Pipeline; `HalvingRandomSearchCV` for large grids.
- Oversampling (SMOTE / ADASYN) *(proposed)*: not used – argued from the metric (changes class priors,
  invalid synthetic values in encoded columns); if tested, only inside training folds.

### Phase 2 – Data understanding checks (19–25 Nov, run locally by the team)
- Duplicates / same property in several rows (backlog 5) → `GroupKFold` if needed.
- Sentinel / capped values → NaN + indicator or `is_capped` flag.
- Near-constant, duplicated, highly correlated columns.
- Drift train vs scoring (backlog 4): adversarial validation + PSI per variable.
- Missingness mechanism (MCAR / MAR / MNAR – selection bias): is being missing related to the EPC label
  or to other variables? Justifies indicators vs imputation in the report.
- Isolation Forest *(proposed)*: anomaly score as a **feature** and as a diagnostic (inspect the most
  anomalous rows for data errors). **Never remove scoring rows** (all 76,906 need a prediction);
  removing training rows is only one ablation line.
- Time features: test cyclical sin/cos for month and whether weekday / weekend add anything.

### Phase 3 – New information and selection (26 Nov – 2 Dec)
- Domain features from a spec sheet filled in by the team (backlog 6): ratios, age instead of year,
  group aggregates, count encoding, missing count per row.
- Grouped permutation importance on held-out folds (backlog 7): per original variable **and per feature group**
  (groups from the business presentation – mapping filled in locally) → answers the business
  question and drives feature removal.
- Hyperparameter tuning of the final model(s).

### Phase 4 – Freeze and submit (3–10 Dec)
- Final ablation table (baseline → + each step), test set evaluated once.
- Explainability for the report: grouped permutation importance, partial dependence, confusion matrix by notch distance.
- Optional: interpretable linear profile (WoE / ordinal logistic) as comparison or ensemble member.
- **Course coverage matrix** (appendix): every technique from the course slides → considered / tested
  (Δ 1-notch accuracy in CV) / used or rejected, with the reason.
- Pipeline freeze ~6 Dec; predictions xlsx from Run All; zip submitted by 9 Dec (one day buffer).

### Open decisions (to ask before implementing)
CV scheme (folds × repeats) · data used for CV (train+val, or keep a separate val split / switch to 85/15) ·
probe model(s) · default high-card encoding (mean rank / cumulative / one-vs-rest) · window rule vs argmax ·
classification vs regression.

### Course calendar to use
- 17/19 Nov – Modelling + evaluation (2): have Phase 0 ready to apply it directly.
- 24/26 Nov – Q&A: ask (1) whether variable names may be in code on a private GitHub repo
  (`col_config.py` is git-ignored for now), (2) whether a CV harness with 1-notch accuracy is accepted as validation.
- 03 Dec – Additional topic (ML4B): after the feature freeze; mainly for the report.

## Backlog mapping
The 8 original backlog ideas are all scheduled above: 1 → Phase 4 (and the harness in Phase 0),
2 → Phases 0–1, 3 → Phase 1, 4–5 → Phase 2, 6–7 → Phase 3, 8 → Phase 1.
