"""Plot 7-day weather forecast from Yr CSV data."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from matplotlib.patches import Ellipse
from scipy.interpolate import CubicSpline


def _data_dir() -> Path:
    """Return the data directory (same folder as this script)."""
    return Path(__file__).resolve().parents[0] / "data"


def _load_forecast(location: str, days: int = 7) -> pd.DataFrame:
    """Load forecast CSV and return the next N days of data.

    Args:
        location: Location name, e.g. ``"oslo"``.
        days: Number of forecast days to include.

    Returns:
        DataFrame with forecast data sorted by time.
    """
    csv_path = _data_dir() / location / "yr.csv"
    if not csv_path.exists():
        print(f"No data found for {location!r} at {csv_path}", file=sys.stderr)
        sys.exit(1)

    df: pd.DataFrame = pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"], utc=True)

    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=days)
    df = df[(df["time"] >= now) & (df["time"] <= cutoff)]
    df = df.sort_values("time").reset_index(drop=True)

    for col in (
        "air_temperature",
        "cloud_area_fraction",
        "precipitation_1h",
        "precipitation_amount_min",
        "precipitation_amount_max",
    ):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def _plot_temp_line(
    ax: Any,
    t_fine: np.ndarray,
    temp_fine: np.ndarray,
) -> None:
    """Plot temperature as a cubic-spline curve, red >=0\u00b0C and blue <0\u00b0C.

    Args:
        ax: Matplotlib axes object.
        t_fine: Array of x-positions (matplotlib date numbers) on the fine grid.
        temp_fine: Interpolated temperature values at ``t_fine``.
    """
    n = len(t_fine)
    for i in range(n - 1):
        t0, t1 = float(t_fine[i]), float(t_fine[i + 1])
        v0, v1 = float(temp_fine[i]), float(temp_fine[i + 1])

        if (v0 >= 0) == (v1 >= 0):
            color = "tomato" if v0 >= 0 else "cornflowerblue"
            ax.plot(
                [t0, t1], [v0, v1], color=color, linewidth=1.8, solid_capstyle="round", zorder=5
            )
        else:
            # Zero crossing: split the segment
            frac = v0 / (v0 - v1)
            t_cross = t0 + frac * (t1 - t0)
            c0 = "tomato" if v0 >= 0 else "cornflowerblue"
            c1 = "cornflowerblue" if v0 >= 0 else "tomato"
            ax.plot(
                [t0, t_cross], [v0, 0.0], color=c0, linewidth=1.8, solid_capstyle="round", zorder=5
            )
            ax.plot(
                [t_cross, t1], [0.0, v1], color=c1, linewidth=1.8, solid_capstyle="round", zorder=5
            )


def _draw_cloud(ax: Any, cx: float, cy: float, r: float, ar: float, color: str) -> None:
    """Draw a cloud shape using overlapping ellipses in axes-fraction coordinates.

    Args:
        ax: Matplotlib axes.
        cx: Centre x in axes fraction.
        cy: Centre y in axes fraction.
        r: Base half-width in axes x-fraction.
        ar: Axes height/width ratio (inches) to keep shapes visually round.
        color: Fill colour.
    """
    for dx_r, dy_r, sz_r in ((0.0, 0.38, 0.60), (0.52, 0.05, 0.47), (-0.48, 0.05, 0.42)):
        ax.add_patch(
            Ellipse(
                (cx + dx_r * r, cy + dy_r * r / ar),
                width=2 * sz_r * r,
                height=2 * sz_r * r / ar,
                facecolor=color,
                edgecolor="none",
                transform=ax.transAxes,
                zorder=6,
                clip_on=True,
            )
        )


def _draw_weather_symbol(
    ax: Any,
    x_ax: float,
    y_ax: float,
    ar: float,
    cloud_pct: float,
    precip: float,
) -> None:
    """Draw a weather symbol at axes-fraction coordinates using patches.

    Args:
        ax: Matplotlib axes.
        x_ax: x position in axes fraction.
        y_ax: y position in axes fraction (symbol centre).
        ar: Axes height/width ratio in inches (for visually round shapes).
        cloud_pct: Cloud area fraction 0-100.
        precip: Precipitation amount in mm.
    """
    r = 0.0043  # base half-width in axes x-fraction (1/3 of original)

    if precip > 0:
        _draw_cloud(ax, x_ax, y_ax + r / ar * 0.35, r, ar, "lightsteelblue")
        for ddx in (-0.6, 0.0, 0.6):
            ax.plot(
                [x_ax + ddx * r, x_ax + ddx * r - 0.15 * r],
                [y_ax - r / ar * 0.05, y_ax - r / ar * 1.0],
                color="deepskyblue",
                linewidth=1.2,
                transform=ax.transAxes,
                zorder=6,
                clip_on=True,
            )
    elif cloud_pct <= 20:
        ax.add_patch(
            Ellipse(
                (x_ax, y_ax),
                width=2 * r,
                height=2 * r / ar,
                facecolor="gold",
                edgecolor="none",
                transform=ax.transAxes,
                zorder=6,
                clip_on=True,
            )
        )
    elif cloud_pct <= 80:
        # Partly cloudy: small sun (upper-left) + cloud in front
        sx, sy = x_ax - r * 0.35, y_ax + r / ar * 0.38
        sr = r * 0.65
        ax.add_patch(
            Ellipse(
                (sx, sy),
                width=2 * sr,
                height=2 * sr / ar,
                facecolor="gold",
                edgecolor="none",
                transform=ax.transAxes,
                zorder=6,
                clip_on=True,
            )
        )
        _draw_cloud(ax, x_ax + r * 0.12, y_ax - r / ar * 0.12, r * 0.9, ar, "white")
    else:
        _draw_cloud(ax, x_ax, y_ax, r, ar, "lightgray")


def _aligned_precip_ylim(
    precip_max_arr: np.ndarray,
    temp_ylim: tuple[float, float],
) -> tuple[float, float]:
    """Compute precipitation y-limits so tick lines align with the temperature axis.

    Args:
        precip_max_arr: Array of maximum-precipitation values.
        temp_ylim: ``(ymin, ymax)`` of the temperature axis (unused; kept for
            caller clarity ? aligning is implicit via LinearLocator).

    Returns:
        ``(0, p_top)`` where ``p_top`` is chosen so that each tick interval
        on the precipitation axis lands at the same physical position as the
        corresponding temperature tick.
    """
    p_raw = float(np.nanmax(precip_max_arr)) if np.any(precip_max_arr > 0) else 1.0
    # Round up to one decimal place and add 10 % headroom
    p_top = np.ceil(p_raw * 10) / 10 * 1.1
    # We want n_ticks - 1 equal intervals.  The bottom is always 0, and the
    # top just needs to be positive ? LinearLocator will produce n_ticks ticks
    # from 0 to p_top regardless of the temperature range, so gridlines align
    # automatically when both axes use the same LinearLocator numticks.
    _ = temp_ylim
    return (0.0, float(p_top))


def plot_forecast(location: str) -> None:
    """Create and display a 7-day weather forecast plot.

    Args:
        location: Location name to load CSV data for.
    """
    df = _load_forecast(location)

    if df.empty:
        print("No forecast data in range.", file=sys.stderr)
        sys.exit(1)

    # ------------------------------------------------------------------ figure
    bg = "#16213e"
    fig, ax_t = plt.subplots(figsize=(21, 4.5))
    fig.patch.set_facecolor(bg)
    ax_t.set_facecolor(bg)

    ax_p: Any = ax_t.twinx()

    # --------------------------------------------------------- temperature data
    times_dt: pd.Series = df["time"]
    temps: np.ndarray = df["air_temperature"].to_numpy(dtype=float, na_value=np.nan)

    valid = ~np.isnan(temps)
    t_valid_dt = times_dt[valid]
    t_valid_num: np.ndarray = np.array(mdates.date2num(t_valid_dt.dt.to_pydatetime()))
    temp_valid: np.ndarray = temps[valid]

    if len(t_valid_num) >= 2:
        cs = CubicSpline(t_valid_num, temp_valid)
        # Fine grid: one point every 15 minutes
        t_fine: np.ndarray = np.arange(
            float(t_valid_num[0]), float(t_valid_num[-1]), 15 / (24 * 60)
        )
        temp_fine: np.ndarray = cs(t_fine)
        _plot_temp_line(ax_t, t_fine, temp_fine)

    # ------------------------------------------------------ precipitation bars
    bar_times: np.ndarray = np.array(mdates.date2num(times_dt.dt.to_pydatetime()))
    bar_width = 0.8 / 24  # 80 % of one hour in matplotlib date units

    precip: np.ndarray = np.nan_to_num(df["precipitation_1h"].to_numpy(dtype=float))
    precip_max: np.ndarray = np.nan_to_num(df["precipitation_amount_max"].to_numpy(dtype=float))

    # Striped bar for max-precipitation range (drawn first, behind solid bar)
    ax_p.bar(
        bar_times,
        precip_max,
        width=bar_width,
        align="edge",
        facecolor="steelblue",
        alpha=0.25,
        edgecolor="cornflowerblue",
        hatch="///",
        linewidth=0.5,
        zorder=2,
    )
    # Solid light-blue bar for actual precipitation
    ax_p.bar(
        bar_times,
        precip,
        width=bar_width,
        align="edge",
        color="lightblue",
        alpha=0.65,
        zorder=3,
    )

    # ---------------------------------------- temperature axis limits / ticks
    t_min_raw = float(np.nanmin(temp_valid))
    t_max_raw = float(np.nanmax(temp_valid))
    t_lo = float(np.floor(t_min_raw / 2) * 2)
    t_hi = float(np.ceil(t_max_raw / 2) * 2)
    if t_hi <= t_lo:
        t_hi = t_lo + 2.0
    n_ticks = max(5, round((t_hi - t_lo) / 2) + 1)

    ax_t.set_ylim(t_lo, t_hi)
    ax_t.yaxis.set_major_locator(ticker.LinearLocator(numticks=n_ticks))
    ax_t.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:.0f}\u00b0C"))

    # ----------------------------------------- precipitation axis limits / ticks
    p_lo, p_hi = _aligned_precip_ylim(precip_max, (t_lo, t_hi))
    ax_p.set_ylim(p_lo, p_hi)
    ax_p.yaxis.set_major_locator(ticker.LinearLocator(numticks=n_ticks))
    ax_p.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:.1f} mm"))

    # --------------------------------------------------------- y-axis grid
    ax_t.yaxis.grid(linestyle=":", color="gray", alpha=0.35, zorder=1)
    ax_t.set_axisbelow(True)

    # --------------------------------------------------------- x-axis range
    t_start = (
        float(t_valid_num[0])
        if len(t_valid_num)
        else mdates.date2num(df["time"].iloc[0].to_pydatetime())
    )
    t_end = float(t_valid_num[-1]) if len(t_valid_num) else t_start + 7
    ax_t.set_xlim(t_start, t_end)

    # ------------------------------------------- day-boundary dashed vlines
    first_dt: datetime = mdates.num2date(t_start).replace(hour=0, minute=0, second=0, microsecond=0)
    day = first_dt + timedelta(days=1)
    while mdates.date2num(day) <= t_end:
        ax_t.axvline(
            mdates.date2num(day),
            linestyle="--",
            color="gray",
            alpha=0.55,
            linewidth=0.8,
            zorder=4,
        )
        day += timedelta(days=1)

    # ---------------------------------- 2-hour dotted vertical minor gridlines
    ax_t.xaxis.set_minor_locator(mdates.HourLocator(byhour=range(2, 24, 2)))
    ax_t.grid(which="minor", axis="x", linestyle=":", color="gray", alpha=0.3, zorder=1)

    # ------------------------------------- x-axis tick labels (major = midnight)
    ax_t.xaxis.set_major_locator(mdates.DayLocator(tz=timezone.utc))

    def _x_label(_num: float, _pos: Any) -> str:
        return "00"

    ax_t.xaxis.set_major_formatter(ticker.FuncFormatter(_x_label))
    ax_t.tick_params(which="major", axis="x", labelsize=7, length=5, pad=2)
    ax_t.tick_params(which="minor", axis="x", labelsize=0, length=2)

    # Place hour labels at every 4 hours (04, 08, 12, 16, 20); 00 is the major tick
    start_day = first_dt
    anno_y = ax_t.get_ylim()[0] - (t_hi - t_lo) * 0.07
    for h in range(4, 24, 4):
        d = start_day
        while True:
            candidate = d.replace(hour=h, minute=0, second=0, microsecond=0)
            cnum = mdates.date2num(candidate)
            if cnum < t_start:
                d += timedelta(days=1)
                continue
            if cnum > t_end:
                break
            ax_t.annotate(
                f"{h:02d}",
                xy=(cnum, anno_y),
                xycoords=("data", "axes fraction"),
                ha="center",
                va="top",
                fontsize=6,
                color="lightgray",
                annotation_clip=False,
                xytext=(0, -4),
                textcoords="offset points",
            )
            d += timedelta(days=1)

    # Day name annotations centred at noon of each day
    d = first_dt
    while True:
        noon = d.replace(hour=12, minute=0, second=0, microsecond=0)
        noon_num = mdates.date2num(noon)
        if noon_num > t_end:
            break
        if noon_num >= t_start:
            ax_t.annotate(
                noon.strftime("%a"),
                xy=(noon_num, anno_y),
                xycoords=("data", "axes fraction"),
                ha="center",
                va="top",
                fontsize=7,
                color="lightgray",
                annotation_clip=False,
                xytext=(0, -14),
                textcoords="offset points",
            )
        d += timedelta(days=1)

    # --------------------------------------------------- spine / tick styling
    label_color = "lightgray"
    precip_color = "cornflowerblue"

    for spine in ax_t.spines.values():
        spine.set_color(label_color)
    ax_t.tick_params(colors=label_color)
    ax_t.yaxis.label.set_color(label_color)
    ax_t.xaxis.label.set_color(label_color)

    for spine_name, spine in ax_p.spines.items():
        if spine_name == "right":
            spine.set_color(precip_color)
        else:
            spine.set_visible(False)
    ax_p.tick_params(axis="y", colors=precip_color, labelsize=7)

    ax_t.tick_params(axis="y", colors=label_color, labelsize=7)

    # --------------------------------------------------------------- title
    ax_t.set_title(
        f"7-day forecast \u2013 {location.capitalize()}",
        color="white",
        fontsize=9,
        pad=4,
    )

    fig.tight_layout(rect=(0, 0.08, 1, 1))

    # ------------------------------------------------- cloud / weather symbols
    # Compute aspect ratio AFTER layout so Ellipse patches appear visually round.
    fig_w, fig_h = fig.get_size_inches()
    ax_pos = ax_t.get_position()
    ar = (fig_h * ax_pos.height) / (fig_w * ax_pos.width)
    # Build CubicSpline interpolator for cloud cover
    cloud_src = df[["time", "cloud_area_fraction", "precipitation_1h"]].dropna(
        subset=["cloud_area_fraction"]
    )
    cloud_nums = np.array(mdates.date2num(cloud_src["time"].dt.to_pydatetime()))
    cloud_vals = cloud_src["cloud_area_fraction"].to_numpy(dtype=float)
    cs_cloud = (
        CubicSpline(cloud_nums, np.clip(cloud_vals, 0.0, 100.0)) if len(cloud_nums) >= 2 else None
    )

    # Precompute bar-time array for nearest-precip lookup
    bar_nums_all = np.array(mdates.date2num(df["time"].dt.to_pydatetime()))

    # Draw symbols at every 2-hour mark
    sym_h_start = (mdates.num2date(t_start).hour + 1) // 2 * 2  # round up to even hour
    sym_day = first_dt.replace(hour=sym_h_start)
    while mdates.date2num(sym_day) < t_start:
        sym_day += timedelta(hours=2)
    while True:
        tx = mdates.date2num(sym_day)
        if tx > t_end:
            break
        x_ax = (tx - t_start) / (t_end - t_start)
        cloud = float(np.clip(cs_cloud(tx), 0.0, 100.0)) if cs_cloud is not None else 50.0
        nearest_idx = int(np.argmin(np.abs(bar_nums_all - tx)))
        precip_val = (
            float(df["precipitation_1h"].iloc[nearest_idx])
            if pd.notna(df["precipitation_1h"].iloc[nearest_idx])
            else 0.0
        )
        _draw_weather_symbol(ax_t, x_ax, 0.93, ar, cloud, precip_val)
        sym_day += timedelta(hours=2)

    plt.show()


def main() -> None:
    """Entry point for yr-plot."""
    parser = argparse.ArgumentParser(description="Plot Yr weather forecast.")
    parser.add_argument(
        "location",
        nargs="?",
        default="oslo",
        help="Location name (default: oslo)",
    )
    args = parser.parse_args()
    plot_forecast(args.location)


if __name__ == "__main__":
    main()
