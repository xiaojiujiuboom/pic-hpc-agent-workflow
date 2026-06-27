#!/usr/bin/env python3

import json
import sys
from datetime import datetime
from pathlib import Path


def now():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def block_summary(obj):
    data = getattr(obj, "data", None)
    dims = getattr(obj, "dims", None)
    shape = None
    if data is not None and hasattr(data, "shape"):
        shape = list(data.shape)
    elif dims is not None:
        try:
            shape = list(dims)
        except TypeError:
            shape = str(dims)
    return {
        "name": getattr(obj, "name", ""),
        "units": getattr(obj, "units", ""),
        "dims": list(dims) if isinstance(dims, tuple) else dims,
        "shape": shape,
    }


def as_2d_slice(array):
    shape = getattr(array, "shape", None)
    if shape is None:
        return None
    if len(shape) == 3:
        return array[:, :, shape[2] // 2]
    if len(shape) == 2:
        return array
    if len(shape) == 1:
        return array.reshape((shape[0], 1))
    return None


def find_density_block(data):
    candidates = []
    for key, value in data.__dict__.items():
        lower = key.lower()
        if key.startswith("_"):
            continue
        if "number_density" in lower or ("density" in lower and "derived" in lower):
            arr = getattr(value, "data", None)
            if arr is not None and hasattr(arr, "shape"):
                candidates.append((key, value, arr))
    if not candidates:
        return None
    for key, value, arr in candidates:
        if "electron" in key.lower():
            return key, value, arr
    return candidates[0]


def write_density_svg(path, array2d, title):
    rows = int(array2d.shape[0])
    cols = int(array2d.shape[1])
    max_cells = 90
    sx = max(1, rows // max_cells)
    sy = max(1, cols // max_cells)
    sampled = array2d[::sx, ::sy]
    rows = int(sampled.shape[0])
    cols = int(sampled.shape[1])
    values = sampled.astype(float)
    vmin = float(values.min())
    vmax = float(values.max())
    span = vmax - vmin if vmax > vmin else 1.0
    cell = 8
    left = 70
    top = 54
    width = left + cols * cell + 24
    height = top + rows * cell + 56
    rects = []
    for i in range(rows):
        for j in range(cols):
            frac = (float(values[i, j]) - vmin) / span
            r = int(20 + 215 * frac)
            g = int(42 + 120 * (1.0 - abs(frac - 0.5) * 2.0))
            b = int(105 + 100 * (1.0 - frac))
            rects.append(
                f'<rect x="{left + j * cell}" y="{top + i * cell}" '
                f'width="{cell}" height="{cell}" fill="rgb({r},{g},{b})" />'
            )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#f8fafc"/>
  <text x="24" y="30" font-family="Arial" font-size="18" font-weight="700">{title}</text>
  <text x="24" y="{height - 22}" font-family="Arial" font-size="12">middle-z slice, min={vmin:.4e}, max={vmax:.4e}</text>
  <text x="24" y="{top + rows * cell / 2:.1f}" font-family="Arial" font-size="12">x</text>
  <text x="{left + cols * cell / 2:.1f}" y="{height - 38}" font-family="Arial" font-size="12">y</text>
  {''.join(rects)}
</svg>
"""
    path.write_text(svg)


def main():
    if len(sys.argv) != 2:
        print("usage: analyze_run.py RUN_DIR", file=sys.stderr)
        return 2

    run_dir = Path(sys.argv[1]).expanduser().resolve()
    data_dir = run_dir / "Data"
    sdf_files = sorted(data_dir.glob("*.sdf"))

    summary = {
        "run_dir": str(run_dir),
        "data_dir": str(data_dir),
        "analyzed_at": now(),
        "sdf_count": len(sdf_files),
        "sdf_files": [p.name for p in sdf_files],
    }

    metrics = {
        "run_dir": str(run_dir),
        "analyzed_at": summary["analyzed_at"],
        "sdf_count": len(sdf_files),
    }

    if not sdf_files:
        summary["error"] = "no SDF files found"
        metrics["analysis_status"] = "no_sdf"
    else:
        from sdf_helper import sdfr

        latest = sdf_files[-1]
        data = sdfr(str(latest))
        keys = [k for k in data.__dict__.keys() if not k.startswith("_")]
        summary["latest_sdf"] = latest.name
        summary["keys"] = keys
        summary["blocks"] = {
            key: block_summary(value)
            for key, value in data.__dict__.items()
            if not key.startswith("_") and hasattr(value, "__dict__")
        }
        metrics["analysis_status"] = "ok"
        metrics["latest_sdf"] = latest.name
        metrics["available_key_count"] = len(keys)
        metrics["has_particles"] = any("Particles" in key or "Particle" in key for key in keys)
        metrics["has_fields"] = any("Electric_Field" in key or "Magnetic_Field" in key for key in keys)
        density = find_density_block(data)
        if density is not None:
            key, _block, arr = density
            slice2d = as_2d_slice(arr)
            metrics["density_key"] = key
            metrics["density_shape"] = list(arr.shape)
            if slice2d is not None:
                plots_dir = run_dir / "plots"
                plots_dir.mkdir(exist_ok=True)
                plot_path = plots_dir / "density_initial.svg"
                write_density_svg(plot_path, slice2d, f"{key} from {latest.name}")
                metrics["density_plot"] = str(plot_path.relative_to(run_dir))

    with open(run_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    with open(run_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
