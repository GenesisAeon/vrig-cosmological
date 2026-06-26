# vrig-cosmological

**v_RIG cosmological velocity scale** — `v_RIG = c / (α⁻¹ · Φ) ≈ 1352 km/s`

[![CI](https://github.com/GenesisAeon/vrig-cosmological/actions/workflows/ci.yml/badge.svg)](https://github.com/GenesisAeon/vrig-cosmological/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License: GPLv3-or-later](https://img.shields.io/badge/code-GPLv3--or--later-blue.svg)](LICENSE-CODE)
[![Docs License: CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-lightgrey.svg)](LICENSE-DOCS)

A falsifiable cosmological velocity scale derived from the fine-structure
constant α and the golden ratio Φ. Implements the Fisher-Rao information-
geometric interpretation, ERA5-style spike detection, and cosmological
survey comparisons. GenesisAeon Package 31.

## Installation

```bash
pip install vrig-cosmological
```

## Usage

```python
from vrig_cosmological import VRIGCosmological

sys = VRIGCosmological()
result = sys.run_cycle(duration_years=83.0)

print(sys.v_rig_value())   # ≈ 1352.118... km/s
print(sys.spike_times())   # detected v_RIG spike years
print(sys.get_crep_state())
print(sys.to_zenodo_record())
```

Or use the calculator directly:

```python
from vrig_cosmological import compute_vrig

result = compute_vrig()
print(result.v_rig_km_s, result.uncertainty_km_s)
```

A CLI is also available — see [docs/cli.md](docs/cli.md).

## Role in the GenesisAeon Ecosystem

`vrig-cosmological` is **P31** in the GenesisAeon ecosystem, covering the
**information geometry / cosmological velocity** domain. It implements the
standard GenesisAeon Diamond Interface (`run_cycle`, `get_crep_state`,
`get_utac_state`, `get_phase_events`, `to_zenodo_record`) so it can be
orchestrated alongside other ecosystem packages (CREP coupling, UTAC
state tracking, Zenodo-ready records).

## Development

```bash
git clone https://github.com/GenesisAeon/vrig-cosmological.git
cd vrig-cosmological
pip install -e ".[dev]"
pytest --cov=src
ruff check src tests
mypy src
```

## Citation

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.PLACEHOLDER.svg)](https://doi.org/10.5281/zenodo.PLACEHOLDER)

DOI will be assigned automatically on first GitHub Release once
Zenodo–GitHub integration is enabled for this repo.

## License

Dual-licensed:
- **Code**: [GNU GPLv3-or-later](LICENSE-CODE)
- **Documentation** (README, `docs/`): [CC BY 4.0](LICENSE-DOCS)

See [LICENSE](LICENSE) for details.
