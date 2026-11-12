"""Turn an iPhone Mirroring screen recording of the Pokémon GO Pokédex into a swipeable web viewer.
Usage:  python3 process_pokedex.py recording.mov [output_folder]
Needs:  pip3 install opencv-python numpy
"""
import cv2, numpy as np, sys, os, json

def phone_box(frames):  # largest teal region = the iPhone screen
    hsv = cv2.cvtColor(np.median(frames, axis=0).astype(np.uint8), cv2.COLOR_BGR2HSV)
    m = cv2.morphologyEx(cv2.inRange(hsv, (80, 30, 140), (115, 255, 255)), cv2.MORPH_OPEN, np.ones((15, 15), np.uint8))
    n, _, st, _ = cv2.connectedComponentsWithStats(m)
    x, y, w, h = st[1 + np.argmax(st[1:, 4]), :4]
    return x, y, w, h

def rest_frames(path, step_fps=10):
    """Frames where the screen has stopped moving (the script pauses after every swipe)."""
    cap = cv2.VideoCapture(path); fps = cap.get(cv2.CAP_PROP_FPS) or 30; step = max(1, round(fps / step_fps))
    frames, i = [], 0
    while True:
        ok, f = cap.read()
        if not ok: break
        if i % step == 0: frames.append(f)
        i += 1
    if not frames: sys.exit(f'Could not read any video from "{path}". Check the file name, or convert it with: ffmpeg -i "{path}" -c:v libx264 fixed.mp4')
    x, y, w, h = phone_box(frames[::max(1, len(frames) // 30)])
    band = [f[y + int(h * .06):y + int(h * .90), x + int(w * .02):x + w - int(w * .02)] for f in frames]  # skip status bar and bottom bar
    small = [cv2.cvtColor(cv2.resize(b, None, fx=.25, fy=.25), cv2.COLOR_BGR2GRAY).astype(np.float32) for b in band]
    win = cv2.createHanningWindow(small[0].shape[::-1], cv2.CV_32F)
    rests, run, swiped = [], [], False   # each rest: (frame, was there a left/right swipe since the last rest?)
    for k in range(1, len(small) + 1):
        if k < len(small) and (abs(small[k] - small[k - 1]) > 20).mean() < .05: run.append(band[k]); continue
        if len(run) >= 3: rests.append((run[len(run) // 2], swiped)); swiped = False
        run = []
        if k < len(small):
            (dx, dy), _ = cv2.phaseCorrelate(small[k - 1], small[k], win)
            swiped |= abs(dx) > small[k].shape[1] * .04 and abs(dx) > 2 * abs(dy)
    return rests

def offset(a, b):
    """How far the content moved up from frame a to frame b, or None if the frames don't overlap."""
    ga, gb = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), cv2.cvtColor(b, cv2.COLOR_BGR2GRAY); H = ga.shape[0]
    best = max((cv2.minMaxLoc(cv2.matchTemplate(gb, ga[int(H * t):int(H * (t + .15))], cv2.TM_CCOEFF_NORMED))[1:4:2], int(H * t))
               for t in (.1, .42, .75))
    (score, (_, by)), ty = best
    return ty - by if score > .85 else None

def stitch(rests):
    """One tall image per Pokémon. A new Pokémon starts after every left/right swipe."""
    pages, canvas, pos = [], None, 0
    for (prev, _), (cur, swiped) in zip([(None, 0)] + rests, rests):
        if prev is None or swiped:
            if canvas is not None: pages.append(canvas)
            canvas, pos = cur.copy(), 0; continue
        d = offset(prev, cur)
        if d is None:   # scrolled too far to line up the frames: add the whole frame below
            canvas = np.vstack([canvas, cur]); pos = canvas.shape[0] - cur.shape[0]; continue
        pos += d; extra = pos + cur.shape[0] - canvas.shape[0]
        if extra > 0: canvas = np.vstack([canvas, cur[-extra:]])
    return pages + [canvas] if canvas is not None else pages

def edge_tiles(img):  # finds clean, fully visible tiles; used only to measure the grid
    g = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    cs, _ = cv2.findContours(255 - cv2.dilate(cv2.Canny(g, 8, 20), np.ones((3, 3), np.uint8)), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    W = img.shape[1]
    return [r for c in cs for r in [cv2.boundingRect(c)]
            if .17 < r[2] / W < .26 and 1.1 < r[3] / r[2] < 1.5 and cv2.contourArea(c) > .5 * r[2] * r[3]]

def calibrate(pages, fallback=None):
    """Tile width/height and the 4 column positions. Returns fallback if the grid can't be measured here."""
    R = [r for p in pages for r in edge_tiles(p)]
    if len(R) < 2: return fallback
    w, h = int(np.median([r[2] for r in R])), int(np.median([r[3] for r in R]))
    cl = []
    for x in sorted(r[0] for r in R):
        if cl and x - cl[-1][-1] < w * .3: cl[-1].append(x)
        else: cl.append([x])
    cx = [np.median(c) for c in cl]
    steps = [b - a for a, b in zip(cx, cx[1:]) if w < b - a < 1.3 * w]
    if not steps and fallback: return fallback
    pitch = np.median(steps) if steps else w * 1.064          # app's usual gap between boxes
    x0 = cx[0] - int((cx[0] - w * .1) // pitch) * pitch        # step back to the leftmost column
    return w, h, [int(x0 + k * pitch) for k in range(4)]

def tile_rows(img, w, h, cols, T=6):
    """Rows of tiles as (top, count). Tiles are lighter than the background next to the screen edge."""
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    ref = np.median(g[:, cols[0] - 20:cols[0] - 8], axis=1)
    strip = lambda x: np.median(g[:, x + w - 15:x + w - 5], axis=1) - ref
    on, out, y = strip(cols[0]) > T, [], 0
    while y < len(on):
        if not on[y]: y += 1; continue
        e = y
        while e < len(on) and on[e]: e += 1
        full, cut = .85 * h < e - y < 1.15 * h, e == len(on) and e - y > .5 * h   # cut = last tile partly hidden at the bottom
        if full or cut:
            out.append(((y + e - h) // 2 if full else y, int(sum(np.median(strip(x)[y + h // 10:e - h // 10]) > T for x in cols))))
        y = e
    return out

def main(video, out):
    os.makedirs(f'{out}/img', exist_ok=True)
    pages = stitch(rest_frames(video)); print(f'Found {len(pages)} Pokémon')
    glob = calibrate(pages)
    if glob is None: sys.exit('Could not find any Caught boxes in the recording. Make sure the Caught tab is open.')
    data = []
    for i, p in enumerate(pages):
        save = lambda name, im: (cv2.imwrite(f'{out}/img/{name}.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 88]), f'img/{name}.jpg')[1]
        w, h, cols = calibrate([p], glob)   # measured per page if possible, else shared
        rows = tile_rows(p, w, h, cols)
        if not rows: data.append({'head': save(f'p{i}_full', p), 'blocks': []}); continue
        gap = min([b[0] - a[0] - h for a, b in zip(rows, rows[1:])] or [10])
        blocks, tiles = [], []
        for r, (y, n) in enumerate(rows):
            if r and y - rows[r - 1][0] - h > 2 * gap + 10:  # a section heading such as "Costume" sits in a big gap
                blocks += [{'tiles': tiles}, {'strip': save(f'p{i}_s{r}', p[rows[r - 1][0] + h:y])}]; tiles = []
            tiles += [save(f'p{i}_t{r}_{k}', p[y:y + h, x:x + w]) for k, x in enumerate(cols[:n])]
        blocks.append({'tiles': tiles})
        data.append({'head': save(f'p{i}_head', p[:max(0, rows[0][0] - gap)]), 'blocks': blocks})
    page = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'viewer.html')).read()
    w, h, cols = glob; W = pages[0].shape[1]  # tile spacing as a fraction of screen width, so the grid matches the app
    meta = {'pad': cols[0] / W, 'gap': (cols[1] - cols[0] - w) / W, 'pages': data}
    open(f'{out}/index.html', 'w').write(page.replace('/*DATA*/[]', json.dumps(meta)))
    print(f'Open {out}/index.html in your browser')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'pokedex_viewer')