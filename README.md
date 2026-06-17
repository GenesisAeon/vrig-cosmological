# vrig-cosmological

**v_RIG cosmological velocity scale** — `v_RIG = c / (α⁻¹ · Φ) ≈ 1352.12 km/s`,
GenesisAeon Package 31.

[![CI](https://github.com/GenesisAeon/vrig-cosmological/actions/workflows/ci.yml/badge.svg)](https://github.com/GenesisAeon/vrig-cosmological/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A falsifiable cosmological velocity scale derived from the fine-structure
constant α and the golden ratio Φ. Implements the Fisher-Rao
information-geometric interpretation, ERA5-style spike detection, and
cosmological survey comparisons.

## Installation

```bash
pip install vrig-cosmological
```

## Usage

```python
from vrig_cosmological import VRIGCosmological

system = VRIGCosmological()
result = system.run_cycle(duration_years=83.0)

system.v_rig_value()   # 1352.118... (km/s)
system.spike_times()   # years at which Fisher-Rao speed exceeded v_RIG
```

The `VRIGCosmological` class implements the GenesisAeon Diamond Interface:

```python
system.get_crep_state()      # CREP (Gamma, C, R, E, P) tensor state
system.get_utac_state()      # UTAC (r, K, sigma, t) parameter state
system.get_phase_events()    # list of v_RIG spike events
system.to_zenodo_record()    # Zenodo-ready metadata dict
```

## Role in the GenesisAeon Ecosystem

This package is **P31** in the GenesisAeon ecosystem, covering the
*information geometry / cosmological velocity* domain: it derives and
falsifies the `v_RIG` velocity scale via Fisher-Rao information geometry
over UTAC parameter trajectories, and exposes that result through the
standard GenesisAeon Diamond Interface so it can be composed with other
ecosystem packages (orchestration, visualization, governance).

## Citation

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.PLACEHOLDER.svg)](https://doi.org/10.5281/zenodo.PLACEHOLDER)

DOI will be assigned automatically on first GitHub Release once
Zenodo–GitHub integration is enabled for this repo. An existing
ecosystem-level DOI is also referenced in `pyproject.toml`
(`10.5281/zenodo.17472834`).
