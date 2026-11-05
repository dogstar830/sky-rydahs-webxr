import asyncio,json,sys
from playwright.async_api import async_playwright
U=f"http://localhost:{sys.argv[1]}/"
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
    ctx=await b.new_context(viewport={"width":1280,"height":720}); pg=await ctx.new_page()
    errs=[];fails=[]
    pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.on("pageerror",lambda e: errs.append("PAGEERROR "+str(e)))
    pg.on("requestfailed",lambda r: fails.append(r.url))
    pg.on("response",lambda r: fails.append(f"{r.status} {r.url}") if r.status>=400 else None)
    await pg.goto(U,wait_until="load"); await pg.wait_for_timeout(15000)
    r={}
    r["manifest"]=await pg.evaluate("fetch('manifest.webmanifest').then(r=>r.json()).then(j=>({name:j.name,display:j.display,icons:j.icons.length}))")
    r["sw"]=await pg.evaluate("navigator.serviceWorker.ready.then(g=>({scope:g.scope,state:g.active&&g.active.state,ctrl:!!navigator.serviceWorker.controller}))")
    r["caches"]=await pg.evaluate("caches.keys().then(async ks=>{const o={};for(const k of ks){o[k]=(await (await caches.open(k)).keys()).length};return o})")
    cdp=await ctx.new_cdp_session(pg)
    r["installabilityErrors"]=(await cdp.send("Page.getInstallabilityErrors"))["installabilityErrors"]
    m=await cdp.send("Page.getAppManifest"); r["manifestParseErrors"]=m.get("errors")
    r["canvas"]=await pg.evaluate("!!document.querySelector('canvas')")
    r["installBtnDisplay"]=await pg.evaluate("getComputedStyle(document.getElementById('pwaInstall')).display")
    await pg.screenshot(path="/workspace/sky-rydahs-pwa/test-shot.png")
    r["onlineErrors"]=list(errs); r["onlineFails"]=list(fails)
    # offline reload
    await ctx.set_offline(True); await pg.reload(); await pg.wait_for_timeout(8000)
    r["offlineReloadTitle"]=await pg.title(); r["offlineCanvas"]=await pg.evaluate("!!document.querySelector('canvas')")
    r["consoleErrors"]=errs; r["failedRequests"]=fails
    print(json.dumps(r,indent=1)); await b.close()
asyncio.run(main())
