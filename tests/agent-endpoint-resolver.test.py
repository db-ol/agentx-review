#!/usr/bin/env python3
"""resolve(endpoint, mode) contract: same address, different lanes, different
transports — and the known remote-realtime gap stays loud, never silent."""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from agent_endpoint import (  # noqa: E402
    MODES, Route, UnsupportedLane, parse_endpoint, resolve,
)

DESCRIPTOR = {
    "workspace": "/ws",
    "runtimeSocket": "/run/agentx-runtime.sock",
    "call_tiers": [
        {"tier": "direct-tailnet", "url": "https://mac.tail.ts.net", "reachable": False},
        {"tier": "direct-lan", "url": "http://10.0.0.2:8080", "reachable": True},
    ],
}


class TestParse(unittest.TestCase):
    def test_scheme_and_bare_forms_normalize_identically(self):
        self.assertEqual(parse_endpoint("agentx://maintainer-001"), "maintainer-001")
        self.assertEqual(parse_endpoint("maintainer-001"), "maintainer-001")

    def test_junk_is_rejected(self):
        for bad in ("agentx://", "agentx://../x", "a b", "", "agentx://UPPER"):
            with self.assertRaises(ValueError):
                parse_endpoint(bad)


class TestSelfRoutes(unittest.TestCase):
    def test_durable_routes_to_the_task_filesystem(self):
        r = resolve("agentx://maintainer-001", "durable", DESCRIPTOR, self_id="maintainer-001")
        self.assertEqual(r, Route("filesystem", "/ws/tasks", "maintainer-001", "durable"))

    def test_local_control_and_realtime_route_to_the_uds(self):
        for mode in ("local-control", "realtime"):
            r = resolve("self", mode, DESCRIPTOR)
            self.assertEqual((r.transport, r.address), ("uds", "/run/agentx-runtime.sock"))

    def test_missing_descriptor_fields_fail_loud(self):
        with self.assertRaises(ValueError):
            resolve("self", "durable", {"runtimeSocket": "/s"})
        with self.assertRaises(ValueError):
            resolve("self", "local-control", {"workspace": "/ws"})


class TestRemoteRoutes(unittest.TestCase):
    def test_reachable_call_tier_is_not_a_durable_route(self):
        # The review pin: call_tiers advertise voice/Web endpoints — a
        # reachable tier must NEVER be returned as a durable task gateway.
        # DESCRIPTOR has a reachable tier, and remote durable still raises.
        self.assertTrue(any(t["reachable"] for t in DESCRIPTOR["call_tiers"]))
        with self.assertRaises(UnsupportedLane):
            resolve("agentx://wu-air", "durable", DESCRIPTOR, self_id="maintainer-001")

    def test_remote_durable_names_the_missing_coordinate(self):
        with self.assertRaises(UnsupportedLane) as ctx:
            resolve("agentx://wu-air", "durable", DESCRIPTOR, self_id="maintainer-001")
        self.assertIn("task-gateway", str(ctx.exception))

    def test_remote_realtime_is_a_loud_gap_not_a_silent_fallback(self):
        # The named gap from the model: no session gateway exists. This must
        # raise UnsupportedLane — if it ever returns a Route, the gateway got
        # built and this pin should be updated alongside it.
        for mode in ("realtime", "local-control"):
            with self.assertRaises(UnsupportedLane):
                resolve("agentx://wu-air", mode, DESCRIPTOR, self_id="maintainer-001")


class TestModeVocabulary(unittest.TestCase):
    def test_unknown_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            resolve("self", "batch", DESCRIPTOR)

    def test_modes_are_the_models_lanes(self):
        self.assertEqual(MODES, ("durable", "realtime", "local-control"))


class TestLoadDescriptor(unittest.TestCase):
    def test_parses_the_subprocess_descriptor(self):
        import agent_endpoint

        class FakeCompleted:
            stdout = '{"workspace": "/ws", "runtimeSocket": "/s"}'

        real_run = agent_endpoint.subprocess.run
        agent_endpoint.subprocess.run = lambda *a, **k: FakeCompleted()
        try:
            d = agent_endpoint.load_descriptor()
        finally:
            agent_endpoint.subprocess.run = real_run
        self.assertEqual(d["runtimeSocket"], "/s")

    def test_missing_repo_root_fails_loud(self):
        import agent_endpoint
        import agentx_config

        real = agentx_config._find_repo_root
        agentx_config._find_repo_root = lambda *a, **k: None
        try:
            with self.assertRaises(ValueError):
                agent_endpoint.load_descriptor()
        finally:
            agentx_config._find_repo_root = real


if __name__ == "__main__":
    unittest.main(verbosity=2)
