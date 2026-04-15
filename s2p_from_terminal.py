"""
plot_s2p.py — Plot S-parameter magnitude (dB) from one or more .s2p files.

Usage:
    python plot_s2p.py file1.s2p file2.s2p [file3.s2p ...]  [OPTIONS]

Options:
    --param     S-parameter to plot: s11, s12, s21, s22  (default: s21)
    --out-dir   Directory to save the plot PNG            (default: current dir)
    --title     Plot title                                (default: auto)
    --dpi       PNG resolution                            (default: 150)
    --no-save   Show the plot interactively instead of saving

Examples:
    python plot_s2p.py pump_line.s2p cryostat.s2p
    python plot_s2p.py pump_line.s2p cryostat.s2p --param s11 --out-dir ./plots
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

try:
    import skrf as rf
except ImportError:
    sys.exit(
        "scikit-rf is required.  Install it with:\n"
        "    pip install scikit-rf"
    )

# ---------------------------------------------------------------------------
# S-parameter index mapping
# ---------------------------------------------------------------------------
PARAM_MAP = {
    "s11": (0, 0),
    "s12": (0, 1),
    "s21": (1, 0),
    "s22": (1, 1),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot S-parameter magnitude from one or more .s2p files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "s2p_files",
        nargs="+",
        metavar="FILE",
        help="Paths to .s2p files (one or more).",
    )
    parser.add_argument(
        "--param",
        default="s21",
        choices=list(PARAM_MAP.keys()),
        help="S-parameter to plot (default: s21).",
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        metavar="DIR",
        help="Directory to save the output PNG (default: current directory).",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Custom plot title.",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="PNG resolution in DPI (default: 150).",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Display the plot interactively instead of saving to disk.",
    )
    return parser.parse_args()


def load_network(path: Path) -> rf.Network:
    """Load an s2p file and return a scikit-rf Network."""
    if not path.exists():
        sys.exit(f"File not found: {path}")
    if not path.suffix.lower().startswith(".s"):
        print(f"Warning: '{path.name}' may not be an s2p file.", file=sys.stderr)
    return rf.Network(str(path))


def extract_db(network: rf.Network, row: int, col: int) -> np.ndarray:
    """Return the dB magnitude of S[row, col], guarded against log(0)."""
    return 20.0 * np.log10(np.abs(network.s[:, row, col]) + 1e-300)


def build_param_label(param: str) -> str:
    """e.g. 's21'  →  'S21'"""
    return param.upper()


def plot_networks(
    paths: list[Path],
    param: str,
    title: str | None,
    dpi: int,
    no_save: bool,
    out_dir: Path,
) -> None:
    row, col = PARAM_MAP[param]
    param_label = build_param_label(param)

    fig, ax = plt.subplots(figsize=(9, 5))

    for path in paths:
        ntwk = load_network(path)
        s_db = extract_db(ntwk, row, col)
        ax.plot(ntwk.f / 1e9, s_db, label=path.name, linewidth=1.5)
        print(f"Loaded: {path.name}  ({len(ntwk.f)} points, "
              f"{ntwk.f[0]/1e9:.3f}–{ntwk.f[-1]/1e9:.3f} GHz)")

    ax.set_xlabel("Frequency [GHz]", fontsize=12)
    ax.set_ylabel(f"{param_label} Magnitude [dB]", fontsize=12)
    ax.set_title(
        title if title else f"{param_label} Magnitude vs Frequency",
        fontsize=13,
    )
    ax.legend(fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()

    if no_save:
        plt.show()
    else:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"s2p_{param_label}.png"
        fig.savefig(out_file, dpi=dpi)
        print(f"Saved: {out_file}")

    plt.close(fig)


def main() -> None:
    args = parse_args()
    paths = [Path(p) for p in args.s2p_files]
    out_dir = Path(args.out_dir)

    plot_networks(
        paths=paths,
        param=args.param,
        title=args.title,
        dpi=args.dpi,
        no_save=args.no_save,
        out_dir=out_dir,
    )


if __name__ == "__main__":
    main()