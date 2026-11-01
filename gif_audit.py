"""Compare trusted local GIFs. No upload, product API, or compression service."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops


def read_gif(path):
    path = Path(path)
    frames, durations = [], []
    with Image.open(path) as im:
        if im.format != 'GIF':
            raise ValueError(f'{path}: expected GIF')
        loop = im.info.get('loop')
        size = list(im.size)
        for i in range(im.n_frames):
            im.seek(i)
            frames.append(im.convert('RGBA').copy())
            durations.append(im.info.get('duration', 0))
    return {'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'size': size, 'frames': len(frames), 'durations_ms': durations,
            'total_duration_ms': sum(durations), 'loop': loop}, frames


def audit(before, after):
    a, af = read_gif(before)
    b, bf = read_gif(after)
    aligned = a['size'] == b['size'] and a['frames'] == b['frames']
    # Extrema across EVERY channel: RGBA getbbox alone can miss RGB-only changes.
    pixels_equal = (all(all(lo == hi == 0 for lo, hi in
                          ImageChops.difference(x, y).getextrema())
                        for x, y in zip(af, bf)) if aligned else None)
    timing_equal = a['durations_ms'] == b['durations_ms']
    return {'before': a, 'after': b,
            'bytes_saved': a['bytes'] - b['bytes'],
            'percent_saved': round(100 * (1 - b['bytes'] / a['bytes']), 2),
            'frame_alignment_comparable': aligned,
            'decoded_rgba_frames_equal': pixels_equal,
            'frame_timing_equal': timing_equal, 'loop_equal': a['loop'] == b['loop'],
            'strict_decoded_match': bool(aligned and pixels_equal and timing_equal and a['loop'] == b['loop'])}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before')
    parser.add_argument('after')
    args = parser.parse_args()
    print(json.dumps(audit(args.before, args.after), indent=2))
