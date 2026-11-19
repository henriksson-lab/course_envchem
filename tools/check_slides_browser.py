"""Screenshot every slide of rendered reveal.js decks and flag overflow.

Usage (after `make render`):
  google-chrome --headless=new --remote-debugging-port=9223 \
      --user-data-dir="$(mktemp -d)" --window-size=1280,720 about:blank &
  [CHECK_SLIDES_PORT=9223] python3 tools/check_slides_browser.py OUTDIR docs/carbonate-gases/lec.html [...]

Writes OUTDIR/<deck>/sNN.png and prints, per deck, the slide count, the share of
slides containing a picture (img/svg/demo), and slides whose content is taller
than the 720 px slide. Requires the optional websocket-client package.
"""
from pathlib import Path
import base64
import os
import json
import sys
import time
import urllib.request

import websocket


class Browser:
    def __init__(self, port=9223):
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/json/list') as response:
            target = next(t for t in json.load(response) if t['type'] == 'page')
        self.ws = websocket.create_connection(target['webSocketDebuggerUrl'],
                                               timeout=30, suppress_origin=True)
        self.seq = 0
        self.call('Page.enable')
        self.call('Emulation.setDeviceMetricsOverride',
                  {'width': 1280, 'height': 720, 'deviceScaleFactor': 1, 'mobile': False})

    def call(self, method, params=None):
        self.seq += 1
        self.ws.send(json.dumps({'id': self.seq, 'method': method, 'params': params or {}}))
        while True:
            message = json.loads(self.ws.recv())
            if message.get('id') == self.seq:
                if 'error' in message:
                    raise RuntimeError(message['error'])
                return message.get('result', {})

    def evaluate(self, expression):
        result = self.call('Runtime.evaluate', {'expression': expression,
                           'returnByValue': True, 'awaitPromise': True})
        return result['result'].get('value')

    def wait(self, expression, timeout=20):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.evaluate(expression):
                return
            time.sleep(0.2)
        raise TimeoutError(expression)


def check_deck(browser, html, outdir):
    browser.call('Page.navigate', {'url': Path(html).resolve().as_uri()})
    browser.wait("typeof Reveal !== 'undefined' && Reveal.isReady && Reveal.isReady()")
    browser.evaluate("document.fonts.ready.then(() => true)")
    slides = browser.evaluate("Reveal.getSlides().length")
    pictured, overflow = 0, []
    outdir.mkdir(parents=True, exist_ok=True)
    for i in range(slides):
        browser.evaluate(f"Reveal.slide({i})")
        time.sleep(0.4)
        info = browser.evaluate("""(() => {
            const s = Reveal.getCurrentSlide();
            const pic = !!s.querySelector('img, svg, [data-demo]');
            const title = (s.querySelector('h1,h2') || {}).textContent || '';
            return {pic, title, height: s.scrollHeight};
        })()""")
        pictured += info['pic']
        if info['height'] > 722:
            overflow.append(f"{i}: {info['title']!r} ({info['height']} px)")
        shot = browser.call('Page.captureScreenshot', {'format': 'png'})
        (outdir / f's{i:02d}.png').write_bytes(base64.b64decode(shot['data']))
    print(f"{html}: {slides} slides, {pictured} with a picture "
          f"({100 * pictured / slides:.0f}%), title slide included")
    for item in overflow:
        print("  OVERFLOW", item)
    return not overflow


def main():
    out = Path(sys.argv[1])
    browser = Browser(int(os.environ.get('CHECK_SLIDES_PORT', '9223')))
    ok = all([check_deck(browser, html, out / Path(html).parent.name / Path(html).stem)
              for html in sys.argv[2:]])
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
