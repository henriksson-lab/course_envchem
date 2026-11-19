"""Compare the scaffold and exercise/lecture demo entry points in Chrome.

Run after rendering, using the temporary browser setup documented for
check_demos_browser.py. Pass --live after deployment to verify the Pages site.
"""
from pathlib import Path
import json
import sys
import time
from check_demos_browser import Browser, ROOT

BASE = 'https://henriksson-lab.github.io/course_envchem/'
PAIRS = [('deposition','deposition'), ('carbonate-gases','carbonate'),
         ('metals','metals'), ('organic-contaminants','fate'),
         ('integrated-case','catchment')]


def until(browser, expression):
    deadline=time.monotonic()+20
    while time.monotonic()<deadline:
        if browser.evaluate(expression):
            return
        time.sleep(.1)
    raise AssertionError('Browser condition timed out: '+expression)


def navigate(browser, url):
    browser.call('Page.navigate', {'url': url})
    until(browser,"document.readyState === 'complete' && !!document.querySelector('main')")


def layout(browser):
    return browser.evaluate("""(()=>{
      const rect=s=>{const r=document.querySelector(s).getBoundingClientRect();return {x:r.x,width:r.width};};
      const weeks=Array.from(document.querySelectorAll('.sidebar-menu-container > ul > li')).slice(2,7);
      return {body:document.body.className,sidebar:rect('#quarto-sidebar'),main:rect('main'),
        weekBorders:weeks.map(n=>getComputedStyle(n).borderLeftColor),
        weekLabels:weeks.map(n=>n.querySelector('.sidebar-item-container').textContent.trim()),
        topItems:document.querySelectorAll('.sidebar-menu-container > ul > li').length};
    })()""")


def check(live=False):
    browser=Browser()
    try:
        browser.call('Network.setBlockedURLs', {'urls': []})
        browser.call('Emulation.setDeviceMetricsOverride', {
            'width':1280,'height':1000,'deviceScaleFactor':1,'mobile':False})
        reference=Path('/home/mahogny/github/course/quantbio-3MB00A/docs/index.html')
        baseline=None
        if reference.exists():
            navigate(browser,reference.as_uri())
            baseline=layout(browser)
            browser.screenshot('/tmp/envchem-scaffold-reference.png')
        home=BASE if live else (ROOT/'docs/index.html').as_uri()
        navigate(browser,home)
        current=layout(browser)
        assert current['topItems']==7, current
        assert all(label.startswith(f'Week {i}') for i,label in enumerate(current['weekLabels'],1)),current
        expected=['rgb(42, 127, 143)','rgb(107, 79, 160)','rgb(168, 50, 74)',
                  'rgb(138, 106, 18)','rgb(59, 91, 171)']
        assert current['weekBorders']==expected,current
        if baseline:
            assert current['body']==baseline['body']
            assert current['weekBorders']==baseline['weekBorders']
            for column in ('sidebar','main'):
                for quantity in ('x','width'):
                    assert abs(current[column][quantity]-baseline[column][quantity])<2,(baseline,current)
        browser.screenshot('/tmp/envchem-scaffold-corrected.png')
        for week,(folder,model) in enumerate(PAIRS,1):
            # Follow the actual sidebar target; no standalone demo-page shortcut.
            navigate(browser,home)
            href=browser.evaluate(f"""(()=>{{
              const link=Array.from(document.querySelectorAll('#quarto-sidebar a')).find(a=>(a.getAttribute('href')||'').endsWith('{folder}/exercise.html#explore'));
              if(!link)return null;
              return {{url:link.href,color:getComputedStyle(link).color,text:link.textContent.trim()}};
            }})()""")
            assert href and href['color']=='rgb(179, 89, 0)',href
            browser.open_url(href['url'])
            assert browser.evaluate(f"!!document.querySelector('#explore [data-demo=\"{model}\"][data-demo-mounted]')")
            original=browser.snapshot()
            preset=browser.evaluate("document.querySelectorAll('.chem-demo button')[1].textContent")
            browser.click(preset);browser.click('Reset')
            assert browser.snapshot()==original
            browser.evaluate("document.querySelector('#explore').scrollIntoView()")
            browser.screenshot(f'/tmp/envchem-exercise-week{week}.png')
            browser.call('Emulation.setDeviceMetricsOverride', {
                'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
            assert browser.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1')
            browser.call('Emulation.setDeviceMetricsOverride', {
                'width':1280,'height':1000,'deviceScaleFactor':1,'mobile':False})
            url=(BASE+folder+'/lec.html#/explore') if live else (ROOT/'docs'/folder/'lec.html').as_uri()+'#/explore'
            browser.open_url(url)
            until(browser,"window.Reveal && Reveal.isReady() && Reveal.getCurrentSlide().id==='explore'")
            browser.evaluate("Reveal.slide(Reveal.getIndices(document.getElementById('explore')).h)")
            fit=browser.evaluate("""(()=>{
              const slide=document.getElementById('explore'), demo=slide.querySelector('.chem-demo');
              const state={slideScroll:slide.scrollHeight,slideClient:slide.clientHeight,
                  slideRect:slide.getBoundingClientRect().toJSON(),demoRect:demo.getBoundingClientRect().toJSON()};
              const bounds=slide.getBoundingClientRect();
              state.withinViewport=demo.getBoundingClientRect().bottom<=window.innerHeight-20;
              state.mounts=demo.dataset.demoMounted;return state;
            })()""")
            assert fit['mounts']=='true' and fit['withinViewport'],(week,fit)
            assert not browser.evaluate("!!document.querySelector('[data-demo-error]')")
            browser.click(preset);browser.click('Reset')
            browser.evaluate("document.querySelector('.chem-demo input').focus();document.querySelector('.chem-demo input').dispatchEvent(new Event('pointerup'))")
            assert browser.evaluate("document.activeElement.tagName !== 'INPUT'")
            browser.evaluate("document.querySelector('.chem-demo button').focus()")
            browser.click('Reset')
            assert browser.evaluate("document.activeElement.tagName !== 'BUTTON'")
            browser.screenshot(f'/tmp/envchem-lecture-week{week}.png')
            print(f'Week {week}: orange sidebar demo target, embedded exercise, mobile width, and visible lecture demo passed.')
        print('Scaffold hierarchy, week colours, and article grid match the Quantitative Biology reference.')
    finally:
        browser.ws.close()


if __name__=='__main__':
    check('--live' in sys.argv)
