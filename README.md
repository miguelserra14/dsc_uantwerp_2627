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
| Libraries | pandas / numpy / scikit-learn only (no external packages) |
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
