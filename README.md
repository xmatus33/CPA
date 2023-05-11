# Python CPA implementation

In `cpa.py` file is python implementation of CPA on DPA Contest v4.2. Implementation uses metrices so that it computes all 256 key guesses at once. It parse traces in groups so that memory isn't limitation. `dpa_parser.py` is used to parse files officialy hosted on DPA Contest websites. At the creation time of this project (May 11th, 2023) index file and traces itselfs was miss matched. Meaning that no CPA was possible. This repo contains striped versions of index file and traces with k00. Striped versions contains only 300 traces.

# Showcase

Repo contains lightweight example consists of `example_traces_300.npy` and `index_file_striped.txt`. Main in `cpa.py` file is composed that it showcases striped example of CPA attack on old version of DPA Contest v4.2 dataset using proposed implementation. To test is just run following command:

```python
python3 cpa.py
```