# Moxion GIF Audit

A small local Python tool for comparing an original GIF with a processed GIF. It reports file-size savings, dimensions, frame count, per-frame timing, loop metadata and exact decoded RGBA frame equality.

This is an original utility prepared for Moxion, not an independent endorsement or an implementation of Moxion’s compressor. You can use it to audit a downloaded result from [Moxion GIF Compressor](https://moxion.ai/gif-compressor) or any other tool. It calls no product API and uploads nothing.

## Quick start

Requires Python 3.10 or newer. The retained run used the Python version in `test-results.json` and Pillow 12.2.0.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python reproduce.py
.venv/bin/python gif_audit.py examples/input.gif examples/local-optimized.gif
```

On Windows, use `.venv\Scripts\python.exe` in place of `.venv/bin/python`.

For an actual compressor result:

```sh
.venv/bin/python gif_audit.py original.gif downloaded-output.gif
```

The command writes JSON to standard output. A mismatch is data in the report, not a failing exit status. Invalid or unreadable input raises an error. Frame mismatch returns `null` for pixel equality rather than a misleading quality score.

## Reproducible demonstration

`reproduce.py` generates an original synthetic animation: an orange square moving across a dark 160 × 90 canvas, with eight 100 ms frames. It saves two encodings of the same frames, then generates deliberately altered files to exercise the checks.

| Measurement | Input | Local optimized encoding |
| --- | --- | --- |
| Bytes | 8,354 | 2,306 |
| Canvas | 160 × 90 | 160 × 90 |
| Frames | 8 | 8 |
| Total duration | 800 ms | 800 ms |
| Loop field | 0 | 0 |
| Decoded RGBA frames | Reference | Equal |

That is a 6,048-byte reduction (72.4%) for this deliberately simple example. **These are local Pillow outputs, not Moxion outputs or a benchmark of any hosted service.** Results may vary with encoder versions. Actual input/output SHA256 hashes and runtime versions are retained in `test-results.json`.

Five assertions check strict equality, positive byte savings, detection of a changed pixel, detection of altered timing, and handling of resized frames. A failed assertion stops reproduction. The pixel comparison examines all four channels independently so an unchanged alpha channel cannot hide an RGB change.

## Files

- `gif_audit.py`: local GIF comparison command and reusable `audit` function.
- `reproduce.py`: original fixture generator and five executable regression assertions.
- `examples/`: generated input, optimized output and three deliberately altered cases.
- `test-results.json`: retained measurements, hashes and environment information.

## Limits

Use small trusted local GIFs. The utility keeps decoded frames in memory and is not an upload service. It compares frames as decoded by Pillow, not every browser’s rendering. Equal-looking animations with different frame segmentation may fail strict alignment. Hidden RGB values under transparency can differ without a visible change. Missing durations are recorded as zero and a missing loop field as null. This is not perceptual scoring, color-managed display validation, or validation of every GIF extension.

## Provenance and AI disclosure

Codex assisted in writing the code, documentation and synthetic fixture generator. The scripts were executed locally and all five assertions passed. No third-party image, downloaded media or product-generated output is included. No claim of human editorial review is made. Moxion’s linked product is affiliated with this project; the utility also works with files from unrelated tools.

## License

The original code, documentation and generated synthetic fixtures in this repository are provided under the MIT license. Pillow is a separate dependency under its own license and is not vendored here.
