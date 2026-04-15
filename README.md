# s2p-plots-from-terminal

This script plots S-parameters from an s2p file.

CLI Flags:
```
Flag        Default      Purpose
=======================================================================
--param     s21          Which S-parameter to plot (s11, s12, s21, s22)
--out-dir   .            Where to save the PNG
--title     auto         Override the plot title
--dpi       150          Output resolution
--no-save   off          Show interactively instead of saving
```

Tyipical invocations:
```
# Two files, default S21
python plot_s2p.py pump_line.s2p cryostat.s2p

# S12 specifically, saved to a plots/ folder
python plot_s2p.py pump_line.s2p cryostat.s2p --param s12 --out-dir ./plots

# Three files, interactive display
python plot_s2p.py a.s2p b.s2p c.s2p --no-save
```

The +1e-300 guard from your snippet is kept in extract_db() to avoid -inf from log(0). Each file's legend entry is just its filename, keeping labels clean regardless of how many files are loaded.
