from __future__ import annotations

import argparse
import hashlib
import json
import math
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


POLARIZATION_ANGLE = {
    "linear_y": 0.0,
    "linear_z": math.pi / 2.0,
    "circular_right": math.pi / 4.0,
    "circular_left": -math.pi / 4.0,
}


@dataclass(frozen=True)
class CampaignConfig:
    path: Path
    data: dict[str, Any]

    @property
    def root(self) -> Path:
        return self.path.parent.parent

    @property
    def run_root(self) -> Path:
        return self.root / self.data["run_root"]

    @property
    def database(self) -> Path:
        return self.root / self.data["database"]


def load_config(path: str | Path) -> CampaignConfig:
    config_path = Path(path).resolve()
    return CampaignConfig(config_path, json.loads(config_path.read_text()))


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def stable_run_id(params: dict[str, Any]) -> str:
    blob = json.dumps(params, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha1(blob).hexdigest()[:10]


def flatten_parameters(config: CampaignConfig, params: dict[str, Any]) -> dict[str, Any]:
    target = params["target"]
    epoch = config.data["epoch"]
    grid = epoch["grid"]
    flat = {
        "l": params["l"],
        "p": params["p"],
        "polarization": params["polarization"],
        "pol_angle_rad": POLARIZATION_ANGLE.get(params["polarization"], 0.0),
        "a0": params["a0"],
        "w0_um": params["w0_um"],
        "tau_fs": params["tau_fs"],
        "carbon_thickness_um": target["carbon_thickness_um"],
        "hydrogen_thickness_um": target["hydrogen_thickness_um"],
        "hydrogen_density_nc": target["hydrogen_density_nc"],
        "hydrogen_radius_um": target["hydrogen_radius_um"],
        "final_time_fs": epoch["final_time_fs"],
        "particles_per_cell": epoch["particles_per_cell"],
        "nx": grid["nx"],
        "ny": grid["ny"],
        "nz": grid["nz"],
    }
    return flat


def slurm_values(config: CampaignConfig, run_id: str) -> dict[str, Any]:
    slurm = config.data["slurm"]
    epoch = config.data["epoch"]
    env = slurm["env"]
    return {
        "job_name": f"hpcpic_{run_id[:8]}",
        "nodes": slurm["nodes"],
        "ntasks": slurm["ntasks"],
        "time": slurm["time"],
        "launcher": slurm["launcher"],
        "epoch_binary": epoch["binary"],
        "ompi_root": env["OMPI"],
        "aocc_root": env["AOCC"],
        "hdf5_root": env["HDF5"],
    }


def render_template(template_path: Path, values: dict[str, Any]) -> str:
    text = template_path.read_text()
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as con:
        con.execute(
            """
            create table if not exists runs (
              run_id text primary key,
              campaign text not null,
              status text not null,
              params_json text not null,
              metrics_json text,
              created_at text not null,
              updated_at text not null,
              remote_job_id text
            )
            """
        )


def upsert_run(config: CampaignConfig, run_id: str, status: str, params: dict[str, Any], metrics: dict[str, Any] | None = None) -> None:
    now = utc_now()
    init_db(config.database)
    with sqlite3.connect(config.database) as con:
        con.execute(
            """
            insert into runs(run_id, campaign, status, params_json, metrics_json, created_at, updated_at)
            values (?, ?, ?, ?, ?, ?, ?)
            on conflict(run_id) do update set
              status=excluded.status,
              params_json=excluded.params_json,
              metrics_json=excluded.metrics_json,
              updated_at=excluded.updated_at
            """,
            (
                run_id,
                config.data["campaign"],
                status,
                json.dumps(params, sort_keys=True),
                json.dumps(metrics, sort_keys=True) if metrics else None,
                now,
                now,
            ),
        )


def synthetic_metrics(params: dict[str, Any]) -> dict[str, float]:
    target = params["target"]
    l_bonus = 1.0 + 0.06 * abs(params["l"])
    p_penalty = 1.0 - 0.04 * params["p"]
    density_term = 1.0 - abs(target["hydrogen_density_nc"] - 12.0) / 60.0
    radius_term = 1.0 - abs(target["hydrogen_radius_um"] - 0.15) / 1.0
    peak = params["a0"] * 1.15 * l_bonus * p_penalty * density_term
    charge = 18.0 * radius_term * density_term * (params["tau_fs"] / 45.0)
    fraction = max(0.05, min(0.95, 0.38 + 0.08 * abs(params["l"]) - 0.03 * params["p"]))
    divergence = max(2.0, 14.0 - 1.5 * abs(params["l"]) + 0.8 * params["p"])
    return {
        "proton_peak_mev": round(peak, 3),
        "proton_window_charge_pc": round(charge, 3),
        "proton_window_fraction": round(fraction, 3),
        "proton_divergence_deg": round(divergence, 3),
    }


def write_svg_plot(path: Path, run_id: str, metrics: dict[str, float]) -> None:
    width, height = 720, 420
    margin = 70
    names = list(metrics)
    values = [metrics[n] for n in names]
    max_v = max(values) or 1.0
    bar_w = (width - 2 * margin) / len(values) * 0.62
    gap = (width - 2 * margin) / len(values)
    bars = []
    labels = []
    for i, (name, value) in enumerate(zip(names, values, strict=True)):
        x = margin + i * gap + (gap - bar_w) / 2
        h = (height - 2 * margin) * value / max_v
        y = height - margin - h
        bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" fill="#d94b4b" rx="4" />')
        labels.append(f'<text x="{x + bar_w / 2:.1f}" y="{height - 42}" text-anchor="middle" font-size="11">{name}</text>')
        labels.append(f'<text x="{x + bar_w / 2:.1f}" y="{y - 8:.1f}" text-anchor="middle" font-size="13">{value}</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#f8fafc"/>
  <text x="{margin}" y="38" font-family="Arial" font-size="22" font-weight="700">Dry-run metrics: {run_id}</text>
  <line x1="{margin}" y1="{height-margin}" x2="{width-margin}" y2="{height-margin}" stroke="#334155"/>
  <line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height-margin}" stroke="#334155"/>
  {''.join(bars)}
  {''.join(labels)}
</svg>
"""
    path.write_text(svg)


def run_dry(config: CampaignConfig) -> dict[str, Any]:
    params = config.data["initial_parameters"][0]
    run_id = stable_run_id(params)
    run_dir = config.run_root / run_id
    plots_dir = run_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    upsert_run(config, run_id, "rendered", params)

    flat = flatten_parameters(config, params)
    template = config.root / config.data["epoch"]["template"]
    deck = render_template(template, flat)
    slurm_template = config.root / config.data["slurm"]["template"]
    submit_script = render_template(slurm_template, slurm_values(config, run_id))
    (run_dir / "config.json").write_text(json.dumps(params, indent=2, sort_keys=True))
    (run_dir / "input.deck").write_text(deck)
    (run_dir / "submit.slurm").write_text(submit_script)

    upsert_run(config, run_id, "dry_submitted", params)
    metrics = synthetic_metrics(params)
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True))
    write_svg_plot(plots_dir / "metrics.svg", run_id, metrics)
    upsert_run(config, run_id, "dry_completed", params, metrics)

    return {
        "run_id": run_id,
        "status": "dry_completed",
        "run_dir": str(run_dir),
        "metrics": metrics,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args(argv)
    result = run_dry(load_config(args.config))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
