"""Exercise built demos in an isolated Chrome DevTools session.

Start a temporary-profile headless Chrome with --remote-debugging-port=9223.
Requires the optional websocket-client Python package; the normal site build
and Node model checks do not require this browser QA helper.
"""
from pathlib import Path
import base64
import json
import time
import urllib.request
import websocket

ROOT = Path(__file__).resolve().parents[1]


class Browser:
    def __init__(self):
        with urllib.request.urlopen('http://127.0.0.1:9223/json/list') as response:
            targets = json.load(response)
        target = next(t for t in targets if t['type'] == 'page')
        self.ws = websocket.create_connection(target['webSocketDebuggerUrl'],
                                               timeout=15, suppress_origin=True)
        self.seq = 0
        self.exceptions = []
        self.call('Page.enable')
        self.call('Runtime.enable')
        self.call('Network.enable')
        # Demonstrate that the interactive models use no remote dependencies.
        self.call('Network.setBlockedURLs', {'urls': ['http://*', 'https://*']})

    def call(self, method, params=None):
        self.seq += 1
        request_id = self.seq
        self.ws.send(json.dumps({'id': request_id, 'method': method,
                                 'params': params or {}}))
        while True:
            message = json.loads(self.ws.recv())
            if message.get('method') == 'Runtime.exceptionThrown':
                self.exceptions.append(message['params']['exceptionDetails'])
            if message.get('id') == request_id:
                if 'error' in message:
                    raise AssertionError(message['error'])
                return message.get('result', {})

    def evaluate(self, expression):
        result = self.call('Runtime.evaluate', {'expression': expression,
                           'returnByValue': True, 'awaitPromise': True})
        assert 'exceptionDetails' not in result, result
        return result['result'].get('value')

    def open(self, name):
        self.exceptions.clear()
        self.call('Page.navigate', {'url': (ROOT/'docs'/'interactives'/name).as_uri()})
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if self.evaluate("document.readyState === 'complete' && !!document.querySelector('[data-demo-mounted]')"):
                break
            time.sleep(.1)
        else:
            raise AssertionError(f'{name}: demo did not mount')
        assert not self.evaluate("!!document.querySelector('[data-demo-error]')"), name

    def snapshot(self):
        return self.evaluate("""({
            controls:Array.from(document.querySelectorAll('.chem-demo input')).map(i=>i.value),
            values:Array.from(document.querySelectorAll('.chem-demo output')).map(i=>i.textContent),
            results:document.querySelector('.chem-demo-results').textContent,
            explanation:document.querySelector('.chem-demo-explanation').textContent
        })""")

    def click(self, label):
        assert self.evaluate(f"""(()=>{{
            const b=Array.from(document.querySelectorAll('.chem-demo button')).find(b=>b.textContent==={json.dumps(label)});
            if(!b) return false; b.click(); return true;
        }})()"""), label
        assert not self.evaluate("!!document.querySelector('[data-demo-error]')")

    def set_input(self, index, value):
        self.evaluate(f"""(()=>{{const i=document.querySelectorAll('.chem-demo input')[{index}];
            i.value={json.dumps(value)};i.dispatchEvent(new Event('input',{{bubbles:true}}));}})()""")
        assert not self.evaluate("!!document.querySelector('[data-demo-error]')")

    def screenshot(self, path):
        image = self.call('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': False})
        Path(path).write_bytes(base64.b64decode(image['data']))


def check():
    browser = Browser()
    try:
        for week in range(1, 6):
            browser.call('Emulation.setDeviceMetricsOverride', {
                'width': 1280, 'height': 1000, 'deviceScaleFactor': 1, 'mobile': False})
            browser.open(f'week{week}.html')
            original = browser.snapshot()
            assert browser.evaluate("Array.from(document.querySelectorAll('.chem-demo input')).every(i => !!document.querySelector('label[for=\"'+i.id+'\"]'))")
            assert browser.evaluate("Array.from(document.querySelectorAll('.chem-demo input')).every(i => i.getAttribute('aria-valuetext'))")
            assert browser.evaluate("document.querySelector('.chem-demo svg').getAttribute('role')==='img'")
            # Every reference preset must redraw without an exception.
            presets = browser.evaluate("Array.from(document.querySelectorAll('.chem-demo button')).map(b=>b.textContent)")
            for label in presets:
                browser.click(label)
            browser.click('Reset')
            assert browser.snapshot() == original, f'week {week}: reset mismatch'
            # Focused sliders retain native keyboard behaviour.
            browser.evaluate("document.querySelector('.chem-demo input').focus()")
            browser.call('Input.dispatchKeyEvent', {'type': 'rawKeyDown', 'key': 'ArrowRight',
                          'code': 'ArrowRight', 'windowsVirtualKeyCode': 39, 'nativeVirtualKeyCode': 39})
            browser.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'ArrowRight', 'code': 'ArrowRight'})
            assert browser.snapshot()['controls'][0] != original['controls'][0]
            browser.click('Reset')
            if week == 1:
                browser.click('Double water export')
                state = browser.snapshot()
                assert '40,000' in state['results'] and '0.0400' in state['results']
            elif week == 2:
                browser.click('Water B: less carbon')
                assert '6.252' in browser.snapshot()['results']
            elif week == 3:
                browser.click('Exactly saturated')
                assert '1 saturated' in browser.snapshot()['results']
            elif week == 4:
                browser.click('U at day 30')
                assert '0.0625' in browser.snapshot()['results']
                browser.click('V at day 30')
                assert '0.4545' in browser.snapshot()['results']
            else:
                browser.click('Exceed reference alkalinity')
                assert '-0.0600' in browser.snapshot()['results']
            browser.click('Reset')
            # All UI endpoint combinations must remain finite and mounted.
            ends = browser.evaluate("Array.from(document.querySelectorAll('.chem-demo input')).map(i=>[i.min,i.max])")
            for mask in range(1 << len(ends)):
                for index, limits in enumerate(ends):
                    browser.set_input(index, limits[(mask >> index) & 1])
                state = browser.snapshot()
                assert 'NaN' not in state['results'] and 'Infinity' not in state['results']
                assert browser.evaluate("!document.querySelector('.chem-demo svg path[d*=\"NaN\"]')")
            browser.click('Reset')
            assert browser.snapshot() == original
            # Narrow viewports may scroll a chart, but not the entire document.
            browser.call('Emulation.setDeviceMetricsOverride', {
                'width': 390, 'height': 844, 'deviceScaleFactor': 1, 'mobile': True})
            assert browser.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'), f'week {week}: mobile overflow'
            browser.evaluate("document.querySelector('.chem-demo').scrollIntoView()")
            if week == 2:
                browser.screenshot('/tmp/envchem-demo-mobile.png')
            browser.call('Emulation.setDeviceMetricsOverride', {
                'width': 1280, 'height': 1000, 'deviceScaleFactor': 1, 'mobile': False})
            browser.evaluate("document.querySelector('.chem-demo').scrollIntoView()")
            if week in (1, 2, 3, 4, 5):
                browser.screenshot(f'/tmp/envchem-demo-week{week}.png')
            assert not browser.exceptions, (week, browser.exceptions)
            browser.call('Emulation.setEmulatedMedia', {'media': 'print'})
            assert browser.evaluate("getComputedStyle(document.querySelector('.chem-demo')).display === 'none'")
            assert browser.evaluate("document.getElementById('hand-check-and-static-reference').textContent.includes('Hand check')")
            browser.call('Emulation.setEmulatedMedia', {'media': ''})
            print(f'Week {week}: offline mount, presets, reset, keyboard, endpoint redraws, mobile width, and print fallback passed.')
        browser.call('Emulation.setScriptExecutionDisabled', {'value': True})
        browser.call('Page.navigate', {'url': (ROOT/'docs/interactives/week2.html').as_uri()})
        deadline = time.monotonic()+15
        while time.monotonic()<deadline:
            if browser.evaluate("document.readyState === 'complete' && !!document.getElementById('hand-check-and-static-reference')"):
                break
            time.sleep(.1)
        assert browser.evaluate("!document.querySelector('[data-demo-mounted]') && document.body.textContent.includes('7.235') && document.body.textContent.includes('6.252')")
        browser.call('Emulation.setScriptExecutionDisabled', {'value': False})
        print('JavaScript-disabled reference calculations remain available.')
    finally:
        browser.ws.close()


if __name__ == '__main__':
    check()
