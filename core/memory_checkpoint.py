"""Lossless state deltas with hash-bound reconstruction and periodic checkpoints."""
from __future__ import annotations
import copy
from core.execution_evidence import canonical, digest


def reconstruct(previous, payload):
    if payload['encoding'] == 'full_v1':
        state = copy.deepcopy(payload['state'])
    elif payload['encoding'] == 'delta_v1':
        if previous is None or digest(canonical(previous)) != payload['base_sha256']:
            raise ValueError('memory delta base mismatch')
        state = copy.deepcopy(previous)
        for key in payload['deleted']:
            if key not in state:
                raise ValueError('memory delta deletes absent field')
            del state[key]
        for key, value in payload['replaced'].items():
            state[key] = copy.deepcopy(value)
        for key, delta in payload['maps'].items():
            if not isinstance(state.get(key), dict):
                raise ValueError('memory map delta base mismatch')
            for deleted in delta['deleted']:
                if deleted not in state[key]:
                    raise ValueError('memory delta deletes absent entry')
                del state[key][deleted]
            state[key].update(copy.deepcopy(delta['upsert']))
    else:
        raise ValueError('unknown memory checkpoint encoding')
    if digest(canonical(state)) != payload['state_sha256']:
        raise ValueError('memory checkpoint state hash mismatch')
    return state


class MemoryCheckpoints:
    def __init__(self, interval=20):
        if type(interval) is not int or interval < 1:
            raise ValueError('memory checkpoint interval must be positive integer')
        self.interval, self.count, self.previous = interval, 0, None

    def encode(self, state):
        state = copy.deepcopy(state)
        sha = digest(canonical(state))
        if self.previous is None or self.count % self.interval == 0:
            payload = {'encoding': 'full_v1', 'state': state, 'state_sha256': sha}
        else:
            old = self.previous
            maps, replaced = {}, {}
            for key, value in state.items():
                if key in old and value == old[key]:
                    continue
                if isinstance(value, dict) and isinstance(old.get(key), dict):
                    maps[key] = {'deleted': sorted(set(old[key]) - set(value)),
                                 'upsert': {k:v for k,v in value.items() if k not in old[key] or old[key][k] != v}}
                else:
                    replaced[key] = value
            payload = {'encoding': 'delta_v1', 'base_sha256': digest(canonical(old)),
                       'state_sha256': sha, 'maps': maps, 'replaced': replaced,
                       'deleted': sorted(set(old)-set(state))}
        # Reject an encoder bug before recording a purportedly reconstructable state.
        if reconstruct(self.previous, payload) != state:
            raise ValueError('memory delta reconstruction mismatch')
        self.previous = state
        self.count += 1
        return payload
