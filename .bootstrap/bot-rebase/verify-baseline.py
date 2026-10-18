from pathlib import Path
import subprocess,json,sys,os
source=Path(sys.argv[1]).resolve(); evidence=Path(sys.argv[2]).resolve();evidence.mkdir(exist_ok=True)
base='d69e626899c83e8a996afed09e8b51ad111bc34a'
validator='cloudflare-worker/src/validators.js'
(source/'cloudflare-worker/src/validators.baseline.js').write_bytes(subprocess.check_output(['git','-C',source,'show',base+':'+validator]))
test=source/'cloudflare-worker/test/validators/uci.test.js';baseline=test.with_name('uci.baseline.mjs')
baseline.write_text(test.read_text().replace("from '../../src/validators.js'","from '../../src/validators.baseline.js'"))
r=subprocess.run(['node','--test','--test-reporter=tap',str(baseline)],capture_output=True,text=True,env=dict(os.environ,NODE_ENV="test"))
(evidence/'baseline-uci.log').write_text(r.stdout+r.stderr)
assert r.returncode==1 and '# tests 23' in r.stdout and '# pass 18' in r.stdout and '# fail 5' in r.stdout
expected=['rpcd plugin with the same basename as its UCI sibling','bare relative source path','double-quoted source path','single-quoted source path','brace-form package root destination']
failures=[line.strip().split(' - ',1)[1] for line in r.stdout.splitlines() if line.startswith('    not ok')]
assert failures==expected,failures
(evidence/'baseline-proof.json').write_text(json.dumps({'passed':True,'base':base,'cases':23,'expected_original_failures':expected,'preserved_upstream_rename_regression':True},indent=2)+'\n')
print('Exact five upstream source-identity failures reproduced; upstream rename regression retained')
