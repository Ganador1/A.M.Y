"""Prompt-index projection; no certificate producer/verifier or I/O.

This view only summarizes previously checked receipts. Raw exact certificates remain outside the index.
"""
from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
import json
import re

PRECISION = 14
DEFINITION_ID = 'ssh_gap_squared_outward_decimal_v1'
GAP_DEFINITION = 'E[N/2] - E[N/2-1] = 2*sigma_min(B); ascending eigenvalues, zero-based indices'
SCOPE = 'finite_open_even_positive_hopping_zero_onsite_chain'
DEFINITION = {
    'gap_definition': GAP_DEFINITION,
    'quantity': 'gap squared',
    'units': 'input_hopping_units_squared',
    'scope': SCOPE,
    'enclosure_order': ['lower', 'upper'],
    'encoding': 'scientific decimal strings',
    'rounding': 'outward_enclosure',
    'significant_digits': PRECISION,
    'exact_original': False,
    'physical_truth_verified': False,
    'original_bounds': 'Retained exact certificate addressed by receipt raw_output_sha256; decimals enclose it, not replace it.',
}
_MAX_BITS = 262144
_HEX = re.compile(r'0x[0-9a-f]+\Z')
_SHA = re.compile(r'[0-9a-f]{64}\Z')
_RATIONAL = re.compile(r'[1-9][0-9]{0,38}(?:/[1-9][0-9]{0,38})?\Z')


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def _check_fraction(value):
    if type(value) is not Fraction:
        raise ValueError('expected Fraction; floats, bool, strings and nonfinite data are not accepted')
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > _MAX_BITS:
        raise ValueError('rational exceeds projection bit budget')


def _ge_power(n, d, exponent):
    # Compare n/d >= 10**exponent without logarithms, floats or str(big_int).
    if exponent >= 0:
        return n >= d * 10 ** exponent
    return n * 10 ** (-exponent) >= d


def _floor_log10(n, d):
    estimate = ((n.bit_length() - d.bit_length()) * 30103) // 100000
    while not _ge_power(n, d, estimate):
        estimate -= 1
    while _ge_power(n, d, estimate + 1):
        estimate += 1
    return estimate


def outward_decimal(value: Fraction, direction: str, *, significant_digits: int = PRECISION) -> str:
    """Return a finite decimal <=value (lower) or >=value (upper), exactly.

    For x!=0, e=floor(log10(abs(x))), q=10**(e-p+1). Floor/ceil(x/q)
    are integers, so their multiples of q enclose x. Rendering is exact;
    a carry to 10**p is divisible by ten and changes only the exponent.
    Integer bit bounds limit resources, not the magnitude of representable x.
    """
    _check_fraction(value)
    if direction not in ('lower', 'upper'):
        raise ValueError('direction must be lower or upper')
    if type(significant_digits) is not int or not 1 <= significant_digits <= 64:
        raise ValueError('significant_digits must be an integer in 1..64')
    if value == 0:
        return '0'
    exponent = _floor_log10(abs(value.numerator), value.denominator)
    power = exponent - significant_digits + 1
    n, d = value.numerator, value.denominator
    if power >= 0:
        d *= 10 ** power
    else:
        n *= 10 ** (-power)
    coefficient = n // d if direction == 'lower' else -((-n) // d)
    sign = '-' if coefficient < 0 else ''
    coefficient = abs(coefficient)
    if coefficient == 10 ** significant_digits:
        coefficient //= 10
        exponent += 1
    digits = str(coefficient)  # at most64 digits; never stringify the input integers
    if len(digits) != significant_digits:
        raise ValueError('unexpected significant-digit count')
    mantissa = digits if significant_digits == 1 else digits[0] + '.' + digits[1:]
    return f'{sign}{mantissa}e{exponent}'


def decode_positive_pair(pair):
    if (not isinstance(pair, list) or len(pair) != 2
            or any(type(v) is not str or len(v) > _MAX_BITS // 4 + 2 or not _HEX.fullmatch(v) for v in pair)):
        raise ValueError('expected bounded canonical positive hexadecimal rational pair')
    n, d = (int(v, 16) for v in pair)
    if n <= 0 or d <= 0:
        raise ValueError('SSH squared bounds must be positive')
    value = Fraction(n, d)
    _check_fraction(value)
    if pair != [hex(value.numerator), hex(value.denominator)]:
        raise ValueError('noncanonical rational pair')
    return value


def _validate_checked_summary(receipt):
    s = receipt.get('verified_summary')
    if not isinstance(s, dict) or receipt.get('interpretation_verified') is not False:
        raise ValueError('checked data must not imply verified interpretation')
    for key, owner in (('raw_output_sha256', receipt), ('certificate_sha256', s),
                       ('hoppings_sha256', s), ('raw_output_sha256', s)):
        if type(owner.get(key)) is not str or not _SHA.fullmatch(owner[key]):
            raise ValueError('missing or malformed retained evidence hash')
    if s['raw_output_sha256'] != receipt['raw_output_sha256']:
        raise ValueError('contradictory original output hashes')
    if not isinstance(receipt.get('experiment_id'), str) or not receipt['experiment_id']:
        raise ValueError('missing experiment ID')
    if (s.get('encoding') != 'hex_numerator_denominator_pairs'
            or s.get('bounds_kind') != 'exact_rational_squared_gap'
            or s.get('scope') != SCOPE or s.get('gap_definition') != GAP_DEFINITION
            or s.get('gap_squared_units') != 'input_hopping_units_squared'):
        raise ValueError('unsupported or absent original SSH scope/units/definition')
    lower = decode_positive_pair(s.get('gap_squared_lower'))
    upper = decode_positive_pair(s.get('gap_squared_upper'))
    if lower > upper:
        raise ValueError('reversed exact bounds')
    h = s.get('hoppings_rational')
    if (not isinstance(h, list) or not 3 <= len(h) <= 511 or len(h) % 2 != 1
            or type(s.get('site_count')) is not int or s['site_count'] != len(h) + 1):
        raise ValueError('hopping dimension mismatch')
    values = []
    for token in h:
        if type(token) is not str or len(token) > 79 or not _RATIONAL.fullmatch(token):
            raise ValueError('invalid hopping token')
        try:
            rational = Fraction(token)
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError('invalid hopping rational') from exc
        if (rational <= 0 or max(rational.numerator.bit_length(), rational.denominator.bit_length()) > 128
                or token != str(rational)):
            raise ValueError('hoppings must be canonical positive rational strings')
        values.append(rational)
    encoded_h = [[hex(v.numerator), hex(v.denominator)] for v in values]
    if canonical_sha(encoded_h) != s['hoppings_sha256']:
        raise ValueError('parameters disagree with retained hopping hash')
    return s, lower, upper


def project_receipt(receipt, *, shared_definition=True):
    """Keep all input parameters and evidence hashes; project only checked SSH data.

    Existing certificate_verified is carried, never computed or upgraded here.
    Non-SSH/unverified entries are copied unchanged. Bad allegedly checked
    entries fail closed rather than exposing a fabricated projection.
    """
    if not isinstance(receipt, dict) or type(shared_definition) is not bool:
        raise ValueError('expected receipt object and boolean mode')
    if receipt.get('tool_name') != 'ssh_gap_certificate' or receipt.get('certificate_verified') is not True:
        return copy.deepcopy(receipt)
    original, lower, upper = _validate_checked_summary(receipt)
    result = copy.deepcopy(receipt)
    summary = result['verified_summary']
    # Each removed datum has a replacement or an identical retained reference.
    # No optional threshold or other source field is silently discarded.
    for key in ('gap_squared_lower', 'gap_squared_upper', 'encoding', 'bounds_kind',
                'display', 'scope', 'gap_definition', 'gap_squared_units', 'raw_output_sha256'):
        summary.pop(key, None)
    summary['gap_squared_enclosure'] = [outward_decimal(lower, 'lower'), outward_decimal(upper, 'upper')]
    if shared_definition:
        summary['projection_definition'] = DEFINITION_ID
    else:
        summary['projection_definition'] = copy.deepcopy(DEFINITION)
    return result



def _context_size(value):
    return len(json.dumps(value, ensure_ascii=False, allow_nan=False))


def _minimal_overhead_view(context, character_budget):
    # Returning legacy empty metadata for a tiny budget is intentional. Once
    # metadata itself cannot fit, report the exception rather than claiming
    # that a nonempty JSON object fits in zero/one characters.
    context['context_budget'] = {
        'requested_characters': character_budget,
        'reason': 'fixed_metadata_overhead',
        'limit_exceeded': True,
        'measured_complete_context_characters': 0,
    }
    for _ in range(8):
        measured = _context_size(context)
        if measured == context['context_budget']['measured_complete_context_characters']:
            return context
        context['context_budget']['measured_complete_context_characters'] = measured
    raise ValueError('unable to stabilize context metadata size')


def _project_or_original(receipt):
    """Keep renderable legacy/invalid receipts, explicitly marking failed projection.

    This does not reclassify the original certificate: its existing status is
    preserved. The caller-owned original remains detached and unchanged.
    """
    try:
        projected = project_receipt(receipt)
        used_definition = (receipt.get('tool_name') == 'ssh_gap_certificate'
                           and receipt.get('certificate_verified') is True)
        return projected, used_definition
    except (ValueError, TypeError, KeyError, OverflowError, ZeroDivisionError) as exc:
        fallback = copy.deepcopy(receipt)
        fallback['projection_status'] = {
            'status': 'fallback_original',
            'requested_definition': DEFINITION_ID,
            'reason': str(exc)[:240],
            'certificate_status_changed': False,
        }
        return fallback, False


def projected_receipt_context(index, *, limit=64, character_budget=48000):
    """V2: contextual projection with compatible counts, row fallback and bounds.

    The normal budget covers the ENTIRE returned JSON object. When even empty
    metadata cannot fit, return no rows plus an honest measured-overhead flag.
    Non-SSH/unverified rows are unchanged; a definition is added only when a
    projected SSH row is visible. Limits0/>64 are allowed as by the old API;
    a negative integer limit selects none. Parameters must be integers, not bool.
    Input receipts originate from compact_receipt and must be JSON-serializable.
    """
    if (not isinstance(index, dict) or type(limit) is not int
            or type(character_budget) is not int):
        raise ValueError('expected index and integer context size/count budgets')
    context = {'total_receipts': len(index), 'visible_receipts': [], 'omitted_receipts': len(index),
               'scope': 'current runtime; model interpretations are not certified'}
    if _context_size(context) > character_budget:
        return _minimal_overhead_view(context, character_budget)
    selected = []  # (row, uses_common_definition), newest first
    for receipt in reversed(list(index.values())):
        # Stop before interpreting entries that will be omitted by count.
        if len(selected) >= max(0, limit):
            break
        if not isinstance(receipt, dict):
            raise ValueError('expected receipt objects from compact_receipt')
        projected, uses_definition = _project_or_original(receipt)
        trial_selected = selected + [(projected, uses_definition)]
        trial = {'total_receipts': len(index),
                 'visible_receipts': [row for row, _ in reversed(trial_selected)],
                 'omitted_receipts': len(index) - len(trial_selected),
                 'scope': 'current runtime; model interpretations are not certified'}
        if any(uses for _, uses in trial_selected):
            trial['projection_definitions'] = {DEFINITION_ID: copy.deepcopy(DEFINITION)}
        if _context_size(trial) <= character_budget:
            selected = trial_selected
            context = trial
    return context
