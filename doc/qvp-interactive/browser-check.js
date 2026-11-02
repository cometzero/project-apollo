async page => {
 const assert=(v,m)=>{if(!v)throw Error(m);};
 await page.goto('http://192.168.0.13:8765/?test=process-view');
 for(let c=0;c<5;c++){
  await page.locator('#chapters button').nth(c).click();
  await page.locator('#path button').nth(2).click();
  for(const mode of ['map','detail','component']){
   await page.locator('#viewMode').selectOption(mode);
   assert((await page.locator('#count').textContent())==='03 / 4','step lost on view switch');
   assert(await page.locator('.diagram-group.process').count()>0,'missing process boundary');
  }
 }
 await page.locator('#viewMode').selectOption('map');
 await page.locator('#showSupport').check();
 const qbox=page.locator('[data-id="proc-qbox"]');await qbox.focus();await page.keyboard.press('Enter');
 assert(await page.locator('#viewMode').inputValue()==='detail','keyboard process navigation');
 const fixture={schema_version:1,collected_at:'2026-11-01T00:00:00Z',processes:[
  {id:'qbox',host:'TEST_HOST',executable:'TEST_QBOX',pid:101,ppid:1,start_time:'TEST_BOOT:900',status:'OBSERVED',evidence:'TEST_ONLY',binary_revision:'UNKNOWN',tcg_mode:'UNKNOWN',threads:[{tid:102,name:'test-vcpu',start_time:'TEST_BOOT:901',role:'QMP fixture',cpus:[{instance:'platform.ap_qemu_inst',index:0,evidence:'QMP query-cpus-fast'}]}]},
  {id:'helper',host:'TEST_HOST',executable:'TEST_HELPER',pid:201,ppid:1,start_time:'TEST_BOOT:902',status:'OBSERVED',evidence:'TEST_ONLY',binary_revision:'UNKNOWN',tcg_mode:'UNKNOWN',threads:[]}],links:[{from:'qbox',to:'helper',transport:'Unix socket',endpoint:'TEST_ONLY /tmp/fixture.sock',evidence:'TEST_ONLY'}]};
 const upload=async data=>{await page.locator('#snapshotFile').setInputFiles({name:'test-only.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(data))});};
 await upload(fixture);await page.waitForFunction(()=>document.querySelector('#snapshotStatus').textContent.includes('NOT LIVE'));
 assert((await page.locator('#snapshotStatus').textContent()).includes('2026-11-01'),'snapshot timestamp');
 await page.locator('#viewMode').selectOption('map');
 assert(await page.locator('[data-kind="ipc"]').count()===1,'IPC path');
 await page.locator('#processSelect').selectOption('helper');
 await page.locator('[data-id="endpoint-1"]').click();
 assert(await page.locator('#processSelect').inputValue()==='qbox','boundary navigation');
 assert((await page.locator('#diagram').textContent()).includes('TID 102'),'thread visibility');
 await upload({schema_version:999});await page.waitForFunction(()=>document.querySelector('#snapshotError').textContent.includes('rejected'));
 assert((await page.locator('#snapshotStatus').textContent()).includes('NOT LIVE'),'invalid import replaced valid snapshot');
 const xml=await page.evaluate(()=>currentViewDrawio());assert(xml.includes('OS PROCESS'),'export boundary');
 await page.locator('#snapshotMode').selectOption('static');
 await page.locator('#viewMode').selectOption('component');
 assert(!(await page.locator('#diagram').textContent()).includes('PID 101'),'static leaked PID');
 await page.locator('#reset').click();await page.locator('#play').click();await page.waitForTimeout(2500);await page.locator('#play').click();
 assert((await page.locator('#count').textContent())==='02 / 4','play');await page.waitForTimeout(2500);assert((await page.locator('#count').textContent())==='02 / 4','pause');
 for(const width of [1440,1280,768]){await page.setViewportSize({width,height:1000});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'page overflow '+width);}
 await page.emulateMedia({reducedMotion:'reduce'});
 assert(await page.evaluate(()=>getComputedStyle(document.querySelector('.diagram-edge.active path')).animationName==='none'),'reduced motion');
 await page.locator('#chapters button').nth(0).click();
 return 'PASS: 5 chapters / 3 views / step preservation / keyboard / snapshot validation / IPC / boundary navigation / thread list / export / player / responsive';
}
