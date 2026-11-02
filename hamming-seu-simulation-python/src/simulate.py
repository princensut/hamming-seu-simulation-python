"""Monte Carlo simulation: protected (Hamming) vs unprotected data under bit flips.

Run from the project root:   python src/simulate.py
Outputs:  results/results_table.md  and  results/error_rate_plot.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                      # draw to a file, no window needed
import matplotlib.pyplot as plt
import numpy as np

from hamming import decode, encode, int_to_bits
from fault_injection import flip_each_bit, flip_random_bits

SEED = 42                # fixed seed -> anyone can reproduce your exact numbers
TRIALS = 10_000          # trials for the fixed-flip experiments
SWEEP_TRIALS = 20_000    # trials per probability in the sweep
ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"


def random_word(rng):
    """Return a random 4-bit data word as a list of bits."""
    return int_to_bits(int(rng.integers(0, 16)), 4)


def fixed_flip_experiment(num_flips, trials, rng):
    """Flip exactly `num_flips` bits per trial. Returns (protected_ok, unprotected_ok)."""
    protected_ok = 0
    unprotected_ok = 0
    for _ in range(trials):
        data = random_word(rng)

        # Protected path: encode -> corrupt 7 bits -> decode
        corrupted_code = flip_random_bits(encode(data), num_flips, rng)
        decoded, _ = decode(corrupted_code)
        protected_ok += decoded == data

        # Unprotected path: corrupt the 4 raw bits -> read directly
        corrupted_data = flip_random_bits(data, num_flips, rng)
        unprotected_ok += corrupted_data == data
    return protected_ok, unprotected_ok


def sweep_experiment(probabilities, trials, rng):
    """Flip each bit with probability p. Returns word error rates for both paths."""
    protected_err, unprotected_err = [], []
    for p in probabilities:
        bad_protected = 0
        bad_unprotected = 0
        for _ in range(trials):
            data = random_word(rng)
            decoded, _ = decode(flip_each_bit(encode(data), p, rng))
            bad_protected += decoded != data
            bad_unprotected += flip_each_bit(data, p, rng) != data
        protected_err.append(bad_protected / trials)
        unprotected_err.append(bad_unprotected / trials)
    return protected_err, unprotected_err


def main():
    rng = np.random.default_rng(SEED)
    RESULTS.mkdir(exist_ok=True)

    rows = []
    for flips, label in [(1, "Single-bit flip"), (2, "Double-bit flip")]:
        p_ok, u_ok = fixed_flip_experiment(flips, TRIALS, rng)
        rows.append((label, TRIALS, p_ok, u_ok))
        print(f"{label}: protected {p_ok}/{TRIALS}, unprotected {u_ok}/{TRIALS}")

    lines = [
        "| Experiment | Trials | Protected success | Unprotected success |",
        "|---|---|---|---|",
    ]
    for label, n, p_ok, u_ok in rows:
        lines.append(f"| {label} | {n} | {p_ok} ({100 * p_ok / n:.2f}%) | {u_ok} ({100 * u_ok / n:.2f}%) |")
    (RESULTS / "results_table.md").write_text("\n".join(lines) + "\n")

    # Sweep over the per-bit flip probability
    probs = np.linspace(0.005, 0.2, 14)
    protected_err, unprotected_err = sweep_experiment(probs, SWEEP_TRIALS, rng)

    # Theory: Hamming(7,4) is a perfect code, so a word survives only if there are
    # 0 or 1 bit errors among 7 bits. Unprotected data survives only with 0 errors in 4 bits.
    theory_unprot = 1 - (1 - probs) ** 4
    theory_prot = 1 - ((1 - probs) ** 7 + 7 * probs * (1 - probs) ** 6)

    plt.figure(figsize=(7, 4.5))
    plt.plot(probs, unprotected_err, "o-", label="Unprotected (simulated)")
    plt.plot(probs, protected_err, "s-", label="Hamming(7,4) (simulated)")
    plt.plot(probs, theory_unprot, "--", color="gray", label="Theory")
    plt.plot(probs, theory_prot, "--", color="gray")
    plt.xlabel("Per-bit flip probability")
    plt.ylabel("Word error rate")
    plt.title("Hamming(7,4) vs unprotected data")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTS / "error_rate_plot.png", dpi=150)
    print("Saved results/results_table.md and results/error_rate_plot.png")


if __name__ == "__main__":
    main()