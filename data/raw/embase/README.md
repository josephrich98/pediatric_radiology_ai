# Embase export drop directory

Put the CSV exports here. See `reports/06_search_strategy.md` section 4.3 for the
query to run and the fields to select.

    embase_unique.csv            line #5:  #4 NOT [medline]/lim   (the new records)
    embase_medline_overlap.csv   line #6:  #4 AND [medline]/lim   (recall audit; PMIDs suffice)

Split exports are fine — any file matching `embase_unique*.csv` or
`embase_medline_overlap*.csv` is picked up and concatenated.

Required columns (Embase's own header names are recognized, in any order):
Title, Abstract, Author Names, Source title, Publication Year, DOI,
Medline PMID, Embase Accession ID, Publication Type, Language.
