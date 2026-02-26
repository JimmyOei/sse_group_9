import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")

BASE_DIR = "."

# ==========================================
# COLOR PALETTE  (Okabe-Ito inspired — colorblind-safe & visually distinct)
# ==========================================

# Languages
LANG_COLOR_LIST = [
    "#0077BB",   # Python     — strong blue
    "#EE7733",   # JavaScript — warm orange
]

# Algorithms (3 entries)
ALG_COLOR_LIST = [
    "#009988",   # teal
    "#CC3311",   # red
    "#7B2D8B",   # purple
]

# Language × Algorithm combos (6 entries, all clearly distinguishable)
COMBO_PALETTE = [
    "#0077BB",   # Python  + algo0  — blue
    "#33BBEE",   # Python  + algo1  — sky blue
    "#004488",   # Python  + algo2  — dark blue
    "#EE7733",   # JS      + algo0  — orange
    "#EE3377",   # JS      + algo1  — pink-red
    "#AA3377",   # JS      + algo2  — purple-rose
]

def get_combo_color(lang_idx, alg_idx, n_algs=3):
    return COMBO_PALETTE[lang_idx * n_algs + alg_idx]


# ==========================================
# GLOBAL STYLE
# ==========================================
plt.rcParams.update({
    "figure.dpi": 150,
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})

SAVE_DIR = "plots"
os.makedirs(SAVE_DIR, exist_ok=True)


def savefig(name):
    plt.tight_layout()
    plt.savefig(os.path.join(SAVE_DIR, name), bbox_inches="tight")
    plt.close()
    print(f"  Saved: {SAVE_DIR}/{name}")


# ==========================================
# ENERGY + TIME COMPUTATION
# ==========================================

def compute_metrics(csv_file):
    df = pd.read_csv(csv_file)
    df = df.dropna(subset=["Delta", "SYSTEM_POWER (Watts)"])
    energy = np.sum(df["SYSTEM_POWER (Watts)"] * (df["Delta"] / 1000.0))
    total_time = np.sum(df["Delta"] / 1000.0)
    return energy, total_time


# ==========================================
# DIRECTORY TRAVERSAL
# ==========================================

def load_all_results():
    records = []
    for device_folder in os.listdir(BASE_DIR):
        if not device_folder.startswith("results_MacOS_M1"):
            continue
        device = device_folder.replace("results_MacOS_", "")
        device_path = os.path.join(BASE_DIR, device_folder)

        for algorithm in os.listdir(device_path):
            algorithm_path = os.path.join(device_path, algorithm)
            if not os.path.isdir(algorithm_path):
                continue

            for language in os.listdir(algorithm_path):
                language_path = os.path.join(algorithm_path, language)
                if not os.path.isdir(language_path):
                    continue

                for dataset_folder in os.listdir(language_path):
                    if not dataset_folder.startswith("dataset_"):
                        continue
                    size = int(dataset_folder.replace("dataset_", ""))
                    dataset_path = os.path.join(language_path, dataset_folder)

                    for run_file in os.listdir(dataset_path):
                        if not run_file.endswith(".csv"):
                            continue
                        file_path = os.path.join(dataset_path, run_file)
                        energy, time = compute_metrics(file_path)
                        records.append({
                            "device": device,
                            "algorithm": algorithm,
                            "language": language,
                            "size": size,
                            "run": run_file,
                            "energy": energy,
                            "time": time
                        })

    return pd.DataFrame(records)


# ==========================================
# STATISTICS PRINTING
# ==========================================

def print_statistics(df):
    print("\n==============================")
    print("ENERGY PER LANGUAGE-ALGORITHM-DATASET")
    print("==============================\n")
    print(df.groupby(["device", "language", "algorithm", "size"])["energy"]
          .agg(["mean", "std", "min", "max"]))

    print("\n==============================")
    print("ENERGY PER DATASET SIZE")
    print("==============================\n")
    print(df.groupby("size")["energy"].agg(["mean", "std"]))

    print("\n==============================")
    print("ENERGY PER LANGUAGE")
    print("==============================\n")
    print(df.groupby("language")["energy"].agg(["mean", "std"]))

    print("\n==============================")
    print("ENERGY PER ALGORITHM")
    print("==============================\n")
    print(df.groupby("algorithm")["energy"].agg(["mean", "std"]))

    print("\n==============================")
    print("ENERGY PER DEVICE")
    print("==============================\n")
    print(df.groupby("device")["energy"].agg(["mean", "std"]))

    print("\n==============================")
    print("EXECUTION TIME PER LANGUAGE-ALGORITHM-DATASET")
    print("==============================\n")
    print(df.groupby(["device", "language", "algorithm", "size"])["time"]
          .agg(["mean", "std"]))


# ==========================================
# HELPER: configure log x-axis for dataset sizes
# ==========================================

def set_log_xaxis(ax, sizes):
    """
    Log-scale x-axis so that small sizes (1k-20k) are not squished
    against large ones (1M-4M). Ticks show the actual size values.
    """
    ax.set_xscale("log")
    ax.set_xticks(sizes)
    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x):,}")
    )
    ax.tick_params(axis="x", which="minor", bottom=False)
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right", fontsize=8)


# ==========================================
# PLOT 1 — Energy vs Dataset Size (log x-axis)
# ==========================================

def plot_energy_vs_size(df):
    sizes = sorted(df["size"].unique())
    for device, ddev in df.groupby("device"):
        fig, ax = plt.subplots(figsize=(10, 5))
        grouped = ddev.groupby(["language", "algorithm", "size"])["energy"]
        mean_s = grouped.mean()

        languages  = sorted(ddev["language"].unique())
        algorithms = sorted(ddev["algorithm"].unique())

        for li, lang in enumerate(languages):
            for ai, alg in enumerate(algorithms):
                color = get_combo_color(li, ai, len(algorithms))
                means = [mean_s.get((lang, alg, s), np.nan) for s in sizes]
                ax.plot(sizes, means,
                        label=f"{lang} — {alg}",
                        color=color, marker="o",
                        linewidth=1.8, markersize=5)

        set_log_xaxis(ax, sizes)
        ax.set_xlabel("Dataset Size (log scale)")
        ax.set_ylabel("Mean Energy (Joules)")
        ax.set_title(f"Mean Energy vs Dataset Size — {device}")
        ax.legend(fontsize=8, ncol=2)
        savefig(f"energy_vs_size_{device}.png")


# ==========================================
# PLOT 2 — Execution Time vs Dataset Size (log x-axis)
# ==========================================

def plot_time_vs_size(df):
    sizes = sorted(df["size"].unique())
    for device, ddev in df.groupby("device"):
        fig, ax = plt.subplots(figsize=(10, 5))
        grouped = ddev.groupby(["language", "algorithm", "size"])["time"]
        mean_s = grouped.mean()

        languages  = sorted(ddev["language"].unique())
        algorithms = sorted(ddev["algorithm"].unique())

        for li, lang in enumerate(languages):
            for ai, alg in enumerate(algorithms):
                color = get_combo_color(li, ai, len(algorithms))
                means = [mean_s.get((lang, alg, s), np.nan) for s in sizes]
                ax.plot(sizes, means,
                        label=f"{lang} — {alg}",
                        color=color, marker="o",
                        linewidth=1.8, markersize=5)

        set_log_xaxis(ax, sizes)
        ax.set_xlabel("Dataset Size (log scale)")
        ax.set_ylabel("Mean Execution Time (s)")
        ax.set_title(f"Mean Execution Time vs Dataset Size — {device}")
        ax.legend(fontsize=8, ncol=2)
        savefig(f"time_vs_size_{device}.png")


# ==========================================
# PLOT 3 — Grouped Bar: Language Comparison per Algorithm (mean only)
# ==========================================

def plot_language_comparison_bar(df):
    for device, ddev in df.groupby("device"):
        fig, ax = plt.subplots(figsize=(9, 5))
        algorithms = sorted(ddev["algorithm"].unique())
        languages  = sorted(ddev["language"].unique())
        x = np.arange(len(algorithms))
        width = 0.35

        for i, lang in enumerate(languages):
            means = []
            for alg in algorithms:
                subset = ddev[(ddev["language"] == lang) & (ddev["algorithm"] == alg)]["energy"]
                means.append(subset.mean())
            color = LANG_COLOR_LIST[i] if i < len(LANG_COLOR_LIST) else f"C{i}"
            ax.bar(x + i * width - width / 2, means, width,
                   label=lang, color=color, alpha=0.85)

        ax.set_xticks(x)
        ax.set_xticklabels(algorithms)
        ax.set_xlabel("Algorithm")
        ax.set_ylabel("Mean Energy (J)")
        ax.set_title(f"Energy: Language Comparison per Algorithm — {device}")
        ax.legend()
        savefig(f"lang_vs_algo_bar_{device}.png")


# ==========================================
# PLOT 4 — Grouped Bar: Algorithm Comparison per Language
# ==========================================

def plot_algorithm_comparison_bar(df):
    for device, ddev in df.groupby("device"):
        fig, ax = plt.subplots(figsize=(9, 5))
        languages  = sorted(ddev["language"].unique())
        algorithms = sorted(ddev["algorithm"].unique())
        x = np.arange(len(languages))
        width = 0.25

        for i, alg in enumerate(algorithms):
            means = []
            for lang in languages:
                subset = ddev[(ddev["algorithm"] == alg) & (ddev["language"] == lang)]["energy"]
                means.append(subset.mean())
            color = ALG_COLOR_LIST[i] if i < len(ALG_COLOR_LIST) else f"C{i}"
            offset = (i - len(algorithms) / 2 + 0.5) * width
            ax.bar(x + offset, means, width,
                   label=alg, color=color, alpha=0.85)

        ax.set_xticks(x)
        ax.set_xticklabels(languages)
        ax.set_xlabel("Language")
        ax.set_ylabel("Mean Energy (J)")
        ax.set_title(f"Energy: Algorithm Comparison per Language — {device}")
        ax.legend()
        savefig(f"algo_vs_lang_bar_{device}.png")


# ==========================================
# PLOT 5 — Energy per Dataset Size per Language (log x-axis, per-algo subplots)
# ==========================================

def plot_energy_per_size_per_language(df):
    sizes = sorted(df["size"].unique())
    for device, ddev in df.groupby("device"):
        algorithms = sorted(ddev["algorithm"].unique())
        languages  = sorted(ddev["language"].unique())

        fig, axes = plt.subplots(1, len(algorithms),
                                 figsize=(5 * len(algorithms), 5), sharey=False)
        if len(algorithms) == 1:
            axes = [axes]

        for ax, alg in zip(axes, algorithms):
            for i, lang in enumerate(languages):
                means = []
                for s in sizes:
                    subset = ddev[
                        (ddev["algorithm"] == alg) &
                        (ddev["language"] == lang) &
                        (ddev["size"] == s)
                    ]["energy"]
                    means.append(subset.mean() if len(subset) > 0 else np.nan)
                color = LANG_COLOR_LIST[i] if i < len(LANG_COLOR_LIST) else f"C{i}"
                ax.plot(sizes, means,
                        label=lang, color=color,
                        marker="o", linewidth=1.8, markersize=5)
            set_log_xaxis(ax, sizes)
            ax.set_xlabel("Dataset Size (log scale)")
            ax.set_ylabel("Mean Energy (J)")
            ax.set_title(alg)
            ax.legend(fontsize=9)

        fig.suptitle(f"Energy per Dataset Size per Language — {device}", fontsize=13)
        savefig(f"energy_per_size_per_lang_{device}.png")


# ==========================================
# PLOT 6 — Heatmap: Mean Energy (Algorithm x Language)
# ==========================================

def plot_heatmap_algo_lang(df):
    for device, ddev in df.groupby("device"):
        pivot = ddev.groupby(["algorithm", "language"])["energy"].mean().unstack()
        fig, ax = plt.subplots(figsize=(6, 4))
        im = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns)
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index)
        plt.colorbar(im, ax=ax, label="Mean Energy (J)")

        vmax = pivot.values.max()
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                val = pivot.values[i, j]
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=10,
                        color="white" if val > vmax * 0.65 else "black")

        ax.set_title(f"Mean Energy Heatmap (Algorithm x Language) — {device}")
        savefig(f"heatmap_algo_lang_{device}.png")


# ==========================================
# PLOT 7 — Violin: Energy Distribution per Language
# ==========================================

def plot_violin_language(df):
    for device, ddev in df.groupby("device"):
        languages = sorted(ddev["language"].unique())
        fig, ax = plt.subplots(figsize=(7, 5))
        data = [ddev[ddev["language"] == lang]["energy"].values for lang in languages]
        parts = ax.violinplot(data, positions=range(len(languages)),
                              showmedians=True, showextrema=True)

        for i, pc in enumerate(parts["bodies"]):
            pc.set_facecolor(LANG_COLOR_LIST[i] if i < len(LANG_COLOR_LIST) else f"C{i}")
            pc.set_alpha(0.75)
        for key in ("cbars", "cmins", "cmaxes", "cmedians"):
            if key in parts:
                parts[key].set_color("black")
                parts[key].set_linewidth(1.5)

        ax.set_xticks(range(len(languages)))
        ax.set_xticklabels(languages)
        ax.set_ylabel("Energy (Joules)")
        ax.set_title(f"Energy Distribution per Language — {device}")
        savefig(f"violin_language_{device}.png")


# ==========================================
# PLOT 8 — Violin: Energy Distribution per Algorithm
# ==========================================

def plot_violin_algorithm(df):
    for device, ddev in df.groupby("device"):
        algorithms = sorted(ddev["algorithm"].unique())
        fig, ax = plt.subplots(figsize=(8, 5))
        data = [ddev[ddev["algorithm"] == alg]["energy"].values for alg in algorithms]
        parts = ax.violinplot(data, positions=range(len(algorithms)),
                              showmedians=True, showextrema=True)

        for i, pc in enumerate(parts["bodies"]):
            pc.set_facecolor(ALG_COLOR_LIST[i] if i < len(ALG_COLOR_LIST) else f"C{i}")
            pc.set_alpha(0.75)
        for key in ("cbars", "cmins", "cmaxes", "cmedians"):
            if key in parts:
                parts[key].set_color("black")
                parts[key].set_linewidth(1.5)

        ax.set_xticks(range(len(algorithms)))
        ax.set_xticklabels(algorithms)
        ax.set_ylabel("Energy (Joules)")
        ax.set_title(f"Energy Distribution per Algorithm — {device}")
        savefig(f"violin_algorithm_{device}.png")


# ==========================================
# PLOT 9 — Power Draw (Watts) per Algorithm x Language
# ==========================================

def plot_power_draw(df):
    df = df.copy()
    df["power"] = df["energy"] / df["time"]

    for device, ddev in df.groupby("device"):
        fig, ax = plt.subplots(figsize=(9, 5))
        algorithms = sorted(ddev["algorithm"].unique())
        languages  = sorted(ddev["language"].unique())
        x = np.arange(len(algorithms))
        width = 0.35

        for i, lang in enumerate(languages):
            means = []
            for alg in algorithms:
                subset = ddev[(ddev["language"] == lang) & (ddev["algorithm"] == alg)]["power"]
                means.append(subset.mean())
            color = LANG_COLOR_LIST[i] if i < len(LANG_COLOR_LIST) else f"C{i}"
            ax.bar(x + i * width - width / 2, means, width,
                   label=lang, color=color, alpha=0.85)

        ax.set_xticks(x)
        ax.set_xticklabels(algorithms)
        ax.set_xlabel("Algorithm")
        ax.set_ylabel("Mean Power Draw (Watts)")
        ax.set_title(f"Average Power Draw per Algorithm x Language — {device}")
        ax.legend()
        savefig(f"power_draw_{device}.png")


# ==========================================
# PLOT 10 — Energy Ratio Python/JS per Algorithm x Size (log x)
# ==========================================

def plot_energy_ratio(df):
    sizes = sorted(df["size"].unique())
    for device, ddev in df.groupby("device"):
        agg = ddev.groupby(["language", "algorithm", "size"])["energy"].mean().reset_index()
        languages = list(agg["language"].unique())
        if len(languages) < 2:
            continue
        lang_a, lang_b = sorted(languages)[:2]

        pivot = agg.pivot_table(index=["algorithm", "size"],
                                columns="language", values="energy").reset_index()
        if lang_a not in pivot.columns or lang_b not in pivot.columns:
            continue
        pivot["ratio"] = pivot[lang_a] / pivot[lang_b]

        algorithms = sorted(pivot["algorithm"].unique())
        fig, ax = plt.subplots(figsize=(9, 5))

        for i, alg in enumerate(algorithms):
            sub = pivot[pivot["algorithm"] == alg].sort_values("size")
            ax.plot(sub["size"], sub["ratio"],
                    marker="o", label=alg,
                    color=ALG_COLOR_LIST[i] if i < len(ALG_COLOR_LIST) else f"C{i}",
                    linewidth=1.8, markersize=5)

        ax.axhline(1.0, color="#888888", linestyle="--", linewidth=1.2,
                   label="Equal energy")
        set_log_xaxis(ax, sizes)
        ax.set_xlabel("Dataset Size (log scale)")
        ax.set_ylabel(f"Energy Ratio ({lang_a} / {lang_b})")
        ax.set_title(f"Energy Ratio ({lang_a} vs {lang_b}) per Algorithm — {device}")
        ax.legend()
        savefig(f"energy_ratio_{device}.png")


# ==========================================
# PLOT 11 — Box Plot: Energy per Algorithm per Language
# ==========================================

def plot_boxplot_algo_per_lang(df):
    for device, ddev in df.groupby("device"):
        languages  = sorted(ddev["language"].unique())
        algorithms = sorted(ddev["algorithm"].unique())

        fig, axes = plt.subplots(1, len(languages),
                                 figsize=(6 * len(languages), 5), sharey=False)
        if len(languages) == 1:
            axes = [axes]

        for ax, lang in zip(axes, languages):
            data = [ddev[(ddev["language"] == lang) & (ddev["algorithm"] == alg)]["energy"].values
                    for alg in algorithms]
            bp = ax.boxplot(data, patch_artist=True, notch=False)
            for patch, color in zip(bp["boxes"], ALG_COLOR_LIST):
                patch.set_facecolor(color)
                patch.set_alpha(0.75)
            for median in bp["medians"]:
                median.set_color("black")
                median.set_linewidth(2)
            ax.set_xticks(range(1, len(algorithms) + 1))
            ax.set_xticklabels(algorithms, rotation=0)
            ax.set_ylabel("Energy (J)")
            ax.set_title(lang)

        fig.suptitle(f"Energy Distribution by Algorithm per Language — {device}", fontsize=13)
        savefig(f"boxplot_algo_per_lang_{device}.png")


# ==========================================
# PLOT 12 — Grouped Bar: Energy Breakdown per Language per Algorithm
# ==========================================

def plot_total_energy_stacked(df):
    for device, ddev in df.groupby("device"):
        agg = ddev.groupby(["language", "algorithm"])["energy"].mean().unstack(level=0)
        fig, ax = plt.subplots(figsize=(8, 5))
        agg.plot(kind="bar", ax=ax,
                 color=LANG_COLOR_LIST[:len(agg.columns)],
                 alpha=0.85, edgecolor="white", width=0.55)
        ax.set_xlabel("Algorithm")
        ax.set_ylabel("Mean Energy (J)")
        ax.set_title(f"Mean Energy per Algorithm — {device}")
        ax.set_xticklabels(agg.index, rotation=0)
        ax.legend(title="Language")
        savefig(f"energy_breakdown_{device}.png")


# ==========================================
# PLOT 13 — Device Comparison
# ==========================================

def plot_device_comparison(df):
    if df["device"].nunique() < 2:
        return

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, metric in zip(axes, ["energy", "time"]):
        pivot = df.groupby(["device", "language"])[metric].mean().unstack()
        pivot.plot(kind="bar", ax=ax,
                   color=LANG_COLOR_LIST[:pivot.shape[1]],
                   alpha=0.85, edgecolor="white")
        ax.set_xlabel("Device")
        ax.set_ylabel(f"Mean {'Energy (J)' if metric == 'energy' else 'Time (s)'}")
        ax.set_title(f"Device Comparison — Mean {metric.capitalize()} per Language")
        ax.set_xticklabels(pivot.index, rotation=0)
        ax.legend(title="Language")

    savefig("device_comparison.png")


# ==========================================
# MAIN
# ==========================================

def main():
    print("Loading data ...")
    df = load_all_results()

    if df.empty:
        print("No data found. Check BASE_DIR and folder structure.")
        return

    print(f"Loaded {len(df)} run records across "
          f"{df['device'].nunique()} device(s), "
          f"{df['language'].nunique()} language(s), "
          f"{df['algorithm'].nunique()} algorithm(s), "
          f"{df['size'].nunique()} dataset size(s).")

    print_statistics(df)

    print("\nGenerating plots ...")
    plot_energy_vs_size(df)
    plot_time_vs_size(df)
    plot_language_comparison_bar(df)
    plot_algorithm_comparison_bar(df)
    plot_energy_per_size_per_language(df)
    plot_heatmap_algo_lang(df)
    plot_violin_language(df)
    plot_violin_algorithm(df)
    plot_power_draw(df)
    plot_energy_ratio(df)
    plot_boxplot_algo_per_lang(df)
    plot_total_energy_stacked(df)
    plot_device_comparison(df)

    print(f"\nAll plots saved to '{SAVE_DIR}/'")


if __name__ == "__main__":
    main()
