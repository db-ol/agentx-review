"""Check the PAPriv enrollment contract without starting network clients."""

import argparse
from collections import Counter
import contextlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--papriv', type=Path, required=True)
    args = parser.parse_args()
    papriv = args.papriv.resolve()
    product = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(papriv))
    from enrollments.agentx.make_access import build
    from spec.resolve import Spec

    expected = {
        'as-shipped': {'owner': 1, 'team': 7, 'other': 4},
        'all-team': {'owner': 1, 'team': 11},
        'all-other': {'owner': 1, 'other': 11},
    }
    results = []
    with tempfile.TemporaryDirectory(prefix='agentx-enrollment-check-') as temp:
        os.environ['CLAUDE_CONFIG_DIR'] = temp
        os.environ['DISCORD_BOT_TOKEN'] = 'local-test-token'
        os.environ['AGENTX_SANDBOX_RUNTIME'] = 'codex'
        os.environ.pop('PAPRIV_CAST_EXTRA', None)
        config = Path(temp) / 'channels' / 'discord' / 'access.json'
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps(build(Spec.load(), 'as-shipped')))
        spec = importlib.util.spec_from_file_location('review_bridge', product / 'src' / 'discord-bridge.py')
        bridge = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = bridge
        with tempfile.TemporaryFile(mode='w+') as output:
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                spec.loader.exec_module(bridge)
        assert bridge.ACCESS_FILE == config
        for rule, counts in expected.items():
            document = build(Spec.load(), rule)
            config.write_text(json.dumps(document))
            assert bridge.load_allowed() == set(document['allowFrom'])
            assert bridge.load_tier_map() == document['tierMap']
            assert dict(Counter(bridge.load_tier_map().values())) == counts
            books = bridge._tier_rulebooks('"test request"')
            for tier in counts:
                key = bridge.select_rulebook_key(tier, False)
                text = bridge._select_rulebook(books, key, runtime='codex')
                if tier == 'owner':
                    assert text == ''
                else:
                    assert 'codex' in text.lower()
                    assert 'AGENTX SYSTEM INSTRUCTIONS' in text
            results.append({'condition': rule, 'admitted': len(bridge.load_allowed()), 'tiers': counts})
    print(json.dumps({'checks': results, 'model_calls': 0, 'network_clients_started': 0}, indent=2))


if __name__ == '__main__':
    main()
