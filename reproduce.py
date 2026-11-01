"""Generate original synthetic fixtures, run comparisons and regression checks."""
import json
import platform
from pathlib import Path
import PIL
from PIL import Image, ImageDraw
from gif_audit import audit

root = Path(__file__).resolve().parent
out = root / 'examples'
out.mkdir(exist_ok=True)
palette = [20, 30, 50, 255, 150, 40, 60, 180, 210] + [0] * (768 - 9)
frames = []
for i in range(8):
    im = Image.new('P', (160, 90), 0)
    im.putpalette(palette)
    ImageDraw.Draw(im).rectangle((10+i*12, 25, 29+i*12, 44), fill=1)
    frames.append(im)

def save(name, ims, optimize, duration=100):
    ims[0].save(out/name, save_all=True, append_images=ims[1:],
                optimize=optimize, duration=duration, loop=0, disposal=2)

save('input.gif', frames, False)
save('local-optimized.gif', frames, True)
changed = [im.copy() for im in frames]
changed[3].putpixel((0,0), 2)
save('changed-pixel.gif', changed, True)
save('changed-timing.gif', frames, True, 200)
save('resized.gif', [im.resize((80,45), Image.Resampling.NEAREST) for im in frames], True)
results = {n:audit(out/'input.gif', out/n) for n in
           ['local-optimized.gif','changed-pixel.gif','changed-timing.gif','resized.gif']}
assert results['local-optimized.gif']['strict_decoded_match']
assert results['local-optimized.gif']['bytes_saved'] > 0
assert results['changed-pixel.gif']['decoded_rgba_frames_equal'] is False
assert results['changed-timing.gif']['frame_timing_equal'] is False
assert results['resized.gif']['decoded_rgba_frames_equal'] is None
report = {'provenance':'Original synthetic animation generated locally with Pillow. No Moxion output used.',
          'python':platform.python_version(),'pillow':PIL.__version__,
          'checks_passed':5,'results':results}
(root/'test-results.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({'checks_passed':5,'pillow':PIL.__version__,'example':results['local-optimized.gif']}, indent=2))
