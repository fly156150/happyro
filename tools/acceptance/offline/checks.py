"""Basic package/container/HTTP checks plus one real browser login, not gameplay coverage."""
import json
from pathlib import Path
import subprocess
import time
import urllib.request

from tools.acceptance.offline.environment import SERVICES, child_options, locked, now
from tools.release.lifecycle import atomic_json


def service_summary(containers):
    result = {}
    for container in containers:
        name = container['Config']['Labels']['com.docker.compose.service']
        if name in result:
            raise ValueError(f'Multiple containers for service {name}')
        state = container['State']
        result[name] = {'status': state['Status'], 'exit_code': state.get('ExitCode'),
                        'health': state.get('Health', {}).get('Status'), 'image_id': container['Image']}
    return result


def healthy(services):
    return (set(services) == set(SERVICES) and all(
        (row['status'] == 'exited' and row['exit_code'] == 0) if name == 'api-init'
        else (row['status'] == 'running' and row['health'] == 'healthy')
        for name, row in services.items()))


def http_checks(state):
    checks = {}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for name, url, content in (
        ('game-health', state['gateway_url'] + '/api/health', 'json'),
        ('game-launcher', state['gateway_url'] + '/applications/pwa/index.html', 'launcher'),
        ('admin-page', state['admin_url'] + '/', 'html'),
        ('api-health', state['admin_url'] + '/api/health', 'json'),
    ):
        with opener.open(url, timeout=15) as response:
            if response.status != 200:
                raise ValueError(f'{name} did not return HTTP 200')
            body = response.read(2 * 1024 * 1024).decode('utf-8')
            if content == 'json':
                value = json.loads(body)
                if not isinstance(value, dict) or value.get('status') != 'ok':
                    raise ValueError(f'{name} did not report healthy status')
            elif '<html' not in body.lower():
                raise ValueError(f'{name} is not an HTML page')
            if content == 'launcher' and '进入游戏' not in body:
                raise ValueError('PWA must provide a launcher, not direct game startup')
            checks[name] = {'url': url, 'status': 200}
    return checks


def check(batch, timeout=300, browser_path=None):
    with locked(batch):
        state = batch.load()
        if state['status'] == 'cleaned':
            raise ValueError('Batch installation has been cleaned')
        attempt = batch.root / 'evidence' / now()
        attempt.mkdir()
        report = {**batch.identity(), 'source_sha256': state['sha256'], 'started_at': now(),
                  'status': 'running', 'checks': {},
                  'not_covered': ['combat', 'skills', 'quests', 'reconnect', 'backup/restore',
                                  'upgrade', 'other CPU architecture', 'mobile devices']}
        atomic_json(batch.root / 'report.json', report)
        try:
            batch.check_config(state)
            # URLs must derive from the protected environment, not arbitrary report input.
            values = dict(line.split('=', 1) for line in (batch.bundle / '.env').read_text().splitlines()
                          if '=' in line and not line.startswith('#'))
            for name, key in [('gateway_url', 'GAME_PUBLIC_URL'), ('admin_url', 'ADMIN_PUBLIC_URL')]:
                if state[name] != values[key] or not state[name].startswith('http://127.0.0.1:'):
                    raise ValueError('Acceptance URL is not the registered loopback address')
            batch.run_tool('verify')
            report['checks']['bundle'] = 'passed'
            deadline = time.monotonic() + timeout
            while True:
                services = service_summary(batch.owned_containers())
                report['services'] = services
                if healthy(services):
                    break
                if time.monotonic() >= deadline:
                    raise ValueError('Services did not become healthy or api-init did not exit successfully')
                time.sleep(2)
            report['checks']['services'] = 'passed'
            info = json.loads(subprocess.check_output(['docker', 'info', '--format', '{{json .}}'], text=True))
            report['runtime'] = {'os': info['OSType'], 'architecture': info['Architecture']}
            report['checks']['http'] = http_checks(state)
            probe = Path(__file__).with_name('browser.mjs')
            command = ['node', str(probe), '--run', '--batch', str(batch.root), '--output', str(attempt)]
            if browser_path:
                command += ['--browser-path', str(browser_path)]
            with (batch.root / 'logs' / f'{attempt.name}-browser.log').open('x') as log:
                subprocess.run(command, env=batch.env(), stdout=log, stderr=subprocess.STDOUT,
                               check=True, timeout=300, **child_options())
            result = json.loads((attempt / 'browser.json').read_text())
            if result.get('status') != 'passed' or result.get('character') != '罗安' or not result.get('moved'):
                raise ValueError('Browser did not prove Luo An entered the game and moved')
            report['checks']['browser'] = result
            report['status'] = 'passed'
        except BaseException as error:
            browser_result = attempt / 'browser.json'
            if browser_result.is_file():
                report['checks']['browser'] = json.loads(browser_result.read_text())
            report.update(status='failed', error_type=type(error).__name__)
            raise
        finally:
            report['finished_at'] = now()
            atomic_json(attempt / 'report.json', report)
            atomic_json(batch.root / 'report.json', report)
            print(f'Basic acceptance {report["status"]}: {batch.root / "report.json"}', flush=True)
    return report
