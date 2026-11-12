# Column assignment for the preprocessing notebook.
# TEMPLATE: copy to col_config.py and fill in (that file is git-ignored).
COLUMNS = {
    "target": "TARGET_COL",
    "id_cols": [],    # kept aside (returned as ids_score), never used as features
    "numeric": [],    # continuous / count variables
    "nominal": [],    # unordered categories (auto high-card if > threshold levels)
    "high_card": [],    # force-treat these nominal columns as high-cardinality
    "ordinal": {},    # {"col": ["lowest", "middle", "highest"]}  (order matters)
    "datetime": [],    # date columns -> year, month, weekday, is_weekend
    "drop": [],    # columns to remove explicitly
}
