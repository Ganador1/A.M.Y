#!/usr/bin/env python3
"""Package explicitly anchored native runs and replay a declared frozen toolkit.

Package integrity inspection uses only the standard library and executes no
packaged source. Scientific replay requires an independently supplied package
root and explicit authorization to execute the verified, listed toolkit. It
never executes the retained AMY runtime, calls a model, or regenerates data.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "amy.native_science_package.v1"
TOOLKIT_PATHS = (
    "core/execution_evidence.py", "core/scientific_certificate_checks.py",
    "scripts/verify/verify_native_science_run.py", "scripts/verify/package_native_science.py",
    "scripts/verify/score_scientific_assessments.py", "scripts/verify/summarize_native_benchmark.py",
    "atlas/app/h2_rhf_verifier.py", "atlas/app/population_selection_verifier.py",
    "atlas/app/ssh_spectral_certificate.py", "atlas/app/ssh_certificate_tool.py",
    "atlas/app/ssh_column_witness.py",
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    def reject(value):
        raise ValueError("nonfinite JSON constant")
    value = json.loads(raw, object_pairs_hook=pairs, parse_constant=reject)
    canonical(value)
    return value


def require(condition, message):
    if not condition:
        raise ValueError(message)


def hash_value(value):
    return type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def safe_relative(name):
    require(type(name) is str and name and "\\" not in name, "invalid relative path")
    path = PurePosixPath(name)
    require(not path.is_absolute() and all(part not in (".", "..") for part in path.parts)
            and str(path) == name, "unsafe or noncanonical relative path")
    return path


def regular_file(root, relative):
    relative = safe_relative(relative)
    path = root
    for part in relative.parts:
        path /= part
        require(not path.is_symlink(), "symlink is not a retained regular file")
    require(path.is_file(), "missing regular file: " + str(relative))
    return path


def file_receipt(path):
    sha = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            sha.update(block)
            size += len(block)
    return {"sha256": sha.hexdigest(), "size_bytes": size}


def current_verify_run(source_root):
    # This is trusted local code, never selected from an input archive.
    path = regular_file(source_root, "core/execution_evidence.py")
    spec = importlib.util.spec_from_file_location("amy_packaging_evidence", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.verify_run


def create_package(selections, destination, *, source_root=ROOT, campaign_id="explicit-selection"):
    """Copy only anchored evidence and source bytes; reject changed local code.

    selections is a nonempty list of (run_directory, expected_run_root) pairs.
    Every toolkit source must have been retained by every selected run, including
    this packager. The new destination must not already exist.
    """
    source_root, destination = Path(source_root).resolve(), Path(destination).absolute()
    require(not destination.exists(), "package destination already exists")
    require(type(campaign_id) is str and 0 < len(campaign_id) <= 256, "invalid campaign ID")
    require(isinstance(selections, (list, tuple)) and 0 < len(selections) <= 128,
            "select between 1 and 128 explicit runs")
    verify_run = current_verify_run(source_root)
    toolkit = {name: file_receipt(regular_file(source_root, name)) for name in TOOLKIT_PATHS}
    plans, roots = [], set()
    for directory, expected_root in selections:
        require(hash_value(expected_root), "each run requires an explicit SHA256 root")
        require(expected_root not in roots, "duplicate selected run root")
        roots.add(expected_root)
        path = Path(directory).resolve()
        require(not destination.is_relative_to(path), "package cannot be created inside a selected run")
        integrity = verify_run(path, expected_root=expected_root)
        require(integrity["integrity_verified"], "run integrity failed: " + "; ".join(integrity["errors"]))
        seal = strict_json(regular_file(path, "seal.json").read_bytes())
        events = regular_file(path, "events.jsonl").read_bytes().splitlines()
        first = strict_json(events[0])
        started = strict_json(regular_file(path, first["payload"]["path"]).read_bytes())
        sources = []
        for original, ref in sorted(started["sources"].items()):
            # Paths identify captured local files; they are never used as output
            # paths until mapped and constrained to the explicit source root.
            original_path = Path(original)
            require(original_path.is_absolute() and original_path.is_relative_to(source_root),
                    "retained source outside explicit source root: " + original)
            relative = original_path.relative_to(source_root).as_posix()
            current = regular_file(source_root, relative)
            require(file_receipt(current) == {"sha256": ref["sha256"], "size_bytes": ref["size_bytes"]},
                    "current source incompatible with sealed snapshot: " + relative)
            retained = regular_file(path, ref["path"])
            require(file_receipt(retained) == file_receipt(current), "source receipt mismatch")
            sources.append({"original_path": original, "relative_path": relative,
                            "blob_path": ref["path"], "sha256": ref["sha256"],
                            "size_bytes": ref["size_bytes"],
                            "export_path": "sources/" + expected_root + "/" + relative})
        source_map = {entry["relative_path"]: entry for entry in sources}
        require(set(TOOLKIT_PATHS) <= source_map.keys(),
                "run snapshot lacks required toolkit sources: " + ", ".join(sorted(set(TOOLKIT_PATHS)-source_map.keys())))
        for name in TOOLKIT_PATHS:
            require(toolkit[name] == {key: source_map[name][key] for key in ("sha256", "size_bytes")},
                    "toolkit differs from sealed run source: " + name)
        plans.append((path, seal, sources, integrity, started.get("environment", {})))

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".native-package-", dir=destination.parent))
    files, entries = {}, []
    def copy_file(source, relative):
        safe_relative(relative)
        target = temporary / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        files[relative] = file_receipt(target)
    try:
        for name in TOOLKIT_PATHS:
            copy_file(regular_file(source_root, name), "toolkit/"+name)
            require(files["toolkit/"+name] == toolkit[name], "source changed during packaging: " + name)
        for path, seal, sources, integrity, environment in plans:
            root = seal["root_sha256"]
            relative = "runs/"+root
            for name in ("seal.json", "events.jsonl", *seal["blobs"]):
                copy_file(regular_file(path, name), relative+"/"+name)
            for source in sources:
                copy_file(regular_file(path, source["blob_path"]), source["export_path"])
                require(files[source["export_path"]] == {key: source[key] for key in ("sha256", "size_bytes")},
                        "retained source changed during packaging")
            require(verify_run(temporary / relative, expected_root=root)["integrity_verified"],
                    "copied evidence failed revalidation")
            entries.append({"path": relative, "expected_root": root, "original_run_path": str(path),
                            "sources": sources, "retained_environment": environment,
                            "integrity_at_packaging": integrity,
                            "current_sources_matched_at_packaging": True})
        readme = (
            "AMY native science receipts\n\n"
            "This package retains selected sealed runs, historical source bytes, and a declared offline verification toolkit.\n"
            "It contains no model weights and does not call cloud services or replay the cognitive loop.\n"
            "Hashes prove consistency with an independently retained root, not provider identity, scientific truth, or novelty.\n\n"
            "Inspect integrity without importing packaged code using a trusted copy of package_native_science.py:\n"
            "  python /trusted/package_native_science.py verify PACKAGE --expected-root EXPECTED_ROOT\n"
            "Only after explicitly trusting the listed toolkit and its anchored hashes, replay with Python 3.11+ and NumPy for H2:\n"
            "  python -I -B PACKAGE/toolkit/scripts/verify/package_native_science.py replay PACKAGE --expected-root EXPECTED_ROOT --execute-verified-toolkit --output REPORT_OUTSIDE_PACKAGE.json\n"
            "The replay loads only the listed verifier modules, never retained AMY runtime files or package initializers.\n"
            "Python socket operations are denied by an audit hook; this is not an operating-system security sandbox.\n"
            "No installation or download is performed. Keep reports outside the immutable package.\n"
        ).encode()
        (temporary/"README.txt").write_bytes(readme)
        files["README.txt"] = file_receipt(temporary/"README.txt")
        manifest = {"schema": SCHEMA, "campaign_id": campaign_id, "runs": entries,
                    "toolkit": toolkit, "toolkit_sha256": digest(canonical(toolkit)),
                    "files": dict(sorted(files.items())),
                    "assurance": {"identity_authenticated": False, "scientific_truth_verified": False,
                                  "novelty_verified": False, "source_snapshot_match_checked_at_packaging": True,
                                  "scientific_replay_performed": False}}
        manifest["root_sha256"] = digest(canonical(manifest))
        (temporary/"package.json").write_bytes(canonical(manifest)+b"\n")
        require(verify_package(temporary, expected_root=manifest["root_sha256"])["package_hash_integrity"],
                "new package failed independent inventory verification")
        require(not destination.exists(), "package destination appeared during packaging")
        temporary.rename(destination)
        return {"package_path": str(destination), "root_sha256": manifest["root_sha256"],
                "toolkit_sha256": manifest["toolkit_sha256"], "selected_runs": len(entries),
                "package_hash_integrity": True, "scientific_replay_performed": False,
                "identity_authenticated": False}
    except BaseException:
        shutil.rmtree(temporary)
        raise


def verify_package(directory, *, expected_root=None):
    """Hash/inventory inspection only: never import or execute packaged code."""
    path = Path(directory).resolve()
    result = {"package_hash_integrity": False, "expected_root_supplied": expected_root is not None,
              "root_sha256": None, "errors": [], "identity_authenticated": False,
              "scientific_replay_performed": False, "scientific_truth_verified": False}
    try:
        manifest = strict_json(regular_file(path, "package.json").read_bytes())
        require(isinstance(manifest, dict) and manifest.get("schema") == SCHEMA, "unsupported package schema")
        root = manifest.pop("root_sha256")
        result["root_sha256"] = root
        require(hash_value(root) and digest(canonical(manifest)) == root, "package root digest mismatch")
        if expected_root is not None:
            require(hash_value(expected_root) and root == expected_root, "unexpected package root")
        require(manifest["assurance"]["identity_authenticated"] is False
                and manifest["assurance"]["scientific_truth_verified"] is False
                and manifest["assurance"]["novelty_verified"] is False, "unsupported assurance claims")
        files = manifest["files"]
        require(isinstance(files, dict) and files and "package.json" not in files, "invalid package inventory")
        for name, receipt in files.items():
            require(isinstance(receipt, dict) and set(receipt) == {"sha256", "size_bytes"}
                    and hash_value(receipt["sha256"]) and type(receipt["size_bytes"]) is int
                    and receipt["size_bytes"] >= 0, "invalid file receipt")
            require(file_receipt(regular_file(path, name)) == receipt, "package file mismatch: " + name)
        observed = set()
        for entry in path.rglob("*"):
            require(not entry.is_symlink(), "symlink in package inventory")
            if entry.is_file():
                observed.add(entry.relative_to(path).as_posix())
            else:
                require(entry.is_dir(), "nonregular package inventory entry")
        require(observed == set(files)|{"package.json"}, "unlisted or missing package file")
        toolkit = manifest["toolkit"]
        require(set(toolkit) == set(TOOLKIT_PATHS), "toolkit is not the declared closed set")
        require(digest(canonical(toolkit)) == manifest["toolkit_sha256"], "toolkit manifest mismatch")
        require(all(files.get("toolkit/"+name) == receipt for name, receipt in toolkit.items()),
                "toolkit receipt not bound to package inventory")
        runs = manifest["runs"]
        require(isinstance(runs, list) and 0 < len(runs) <= 128, "invalid selected run list")
        seen = set()
        for run in runs:
            root = run["expected_root"]
            require(hash_value(root) and root not in seen and run["path"] == "runs/"+root, "invalid or duplicate run selection")
            seen.add(root)
            seal_name = run["path"]+"/seal.json"
            require(seal_name in files, "run seal missing from manifest")
            seal = strict_json(regular_file(path, seal_name).read_bytes())
            require(seal.pop("root_sha256") == root and digest(canonical(seal)) == root,
                    "selected run root is not the packaged seal")
            source_map = {}
            for source in run["sources"]:
                name = source["relative_path"]
                safe_relative(name)
                require(name not in source_map and source["export_path"] == "sources/"+root+"/"+name,
                        "duplicate or misplaced source snapshot")
                receipt = {key: source[key] for key in ("sha256", "size_bytes")}
                require(files.get(source["export_path"]) == receipt
                        and files.get(run["path"]+"/"+source["blob_path"]) == receipt,
                        "source export differs from retained source blob")
                source_map[name] = receipt
            require(set(toolkit) <= source_map.keys() and all(source_map[name] == value for name,value in toolkit.items()),
                    "toolkit does not match every selected sealed source snapshot")
        result.update(package_hash_integrity=True, selected_runs=len(runs), toolkit_sha256=manifest["toolkit_sha256"])
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError) as exc:
        result["errors"].append(f"{type(exc).__name__}: {exc}")
    return result


_REPLAY_CODE = r'''
import importlib.metadata, json, pathlib, socket, sys, types
root, run, expected = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
sys.dont_write_bytecode = True
def deny_network(event, args):
    if event.startswith("socket."):
        raise PermissionError("network disabled by declared offline-replay audit hook")
sys.addaudithook(deny_network)
try:
    socket.getaddrinfo("offline-selftest.invalid", 443)
except PermissionError:
    networking_disabled = True
else:
    raise RuntimeError("offline networking guard self-test failed")
# Explicit minimal namespace packages avoid app initializers and their optional
# web/cache dependencies. Only the closed, hashed verifier toolkit is imported.
for name, parts in (("core", ("core",)), ("scripts", ("scripts",)),
                    ("scripts.verify", ("scripts", "verify")),
                    ("atlas", ("atlas",)), ("atlas.app", ("atlas", "app"))):
    module = types.ModuleType(name)
    module.__path__ = [str(root.joinpath(*parts))]
    sys.modules[name] = module
sys.path.insert(0, str(root))
from scripts.verify.verify_native_science_run import verify_native_science_run
from scripts.verify.summarize_native_benchmark import summarize_run
from scripts.verify.score_scientific_assessments import score_run
report = verify_native_science_run(run, expected_root=expected)
first = json.loads((run/"events.jsonl").read_bytes().splitlines()[0])
started = json.loads((run/first["payload"]["path"]).read_bytes())
case_id = started.get("metadata", {}).get("config", {}).get("evidence", {}).get("benchmark", {}).get("case_id")
report["scientific_assessment"] = ({"status": "evaluated", "result": score_run(run, expected_root=expected)}
                                   if case_id is not None else
                                   {"status": "not_applicable", "reason": "retained metadata has no benchmark case_id"})
report["benchmark_metrics"] = summarize_run(run, expected_root=expected, domain_audit={
    "run_root_sha256": expected, "trace_valid": report["trace_valid"], "domain_valid": report["domain_valid"],
    "source": "fresh frozen-toolkit causal/domain replay"})
try:
    numpy_version = importlib.metadata.version("numpy")
except importlib.metadata.PackageNotFoundError:
    numpy_version = None
report["offline_replay_environment"] = {"python": sys.version.split()[0], "numpy": numpy_version,
                                       "isolated_python": bool(sys.flags.isolated),
                                       "networking_disabled": networking_disabled,
                                       "network_guard": "Python audit hook denying socket events; not an OS sandbox"}
print(json.dumps(report, separators=(",", ":"), allow_nan=False))
'''


def replay_package(directory, *, expected_root, execute_verified_toolkit=False, timeout_seconds=60):
    """Execute only the explicitly authorized, root-verified frozen toolkit."""
    require(hash_value(expected_root), "scientific replay requires an independently retained expected package root")
    require(execute_verified_toolkit is True, "scientific replay requires explicit authorization to execute the verified toolkit")
    require(type(timeout_seconds) in (int, float) and 0 < timeout_seconds <= 300,
            "replay timeout must be positive and at most 300 seconds")
    path = Path(directory).resolve()
    integrity = verify_package(path, expected_root=expected_root)
    require(integrity["package_hash_integrity"], "package integrity failed: " + "; ".join(integrity["errors"]))
    manifest = strict_json((path/"package.json").read_bytes())
    reports = []
    with tempfile.TemporaryDirectory(prefix="amy-offline-replay-") as workdir:
        for run in manifest["runs"]:
            item = {"expected_run_root": run["expected_root"], "path": run["path"], "replay_completed": False}
            try:
                process = subprocess.run([sys.executable, "-I", "-B", "-c", _REPLAY_CODE,
                                          str(path/"toolkit"), str(path/run["path"]), run["expected_root"]],
                                         cwd=workdir, stdin=subprocess.DEVNULL, capture_output=True,
                                         text=True, timeout=timeout_seconds, check=False)
                require(process.returncode == 0, "offline replay subprocess failed: " + process.stderr[-4000:])
                item.update(replay_completed=True, audit=strict_json(process.stdout))
            except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
                item["error"] = f"{type(exc).__name__}: {exc}"
            reports.append(item)
    # Also detect mutation during replay; reports are deliberately written outside
    # the immutable package so its inventory remains unchanged.
    after = verify_package(path, expected_root=expected_root)
    complete = after["package_hash_integrity"] and all(item["replay_completed"] for item in reports)
    return {"schema": "amy.native_science_package_replay.v1", "integrity": after,
            "toolkit_sha256": manifest["toolkit_sha256"], "scientific_replay_performed": True,
            "replay_completed": complete, "runs": reports,
            "trace_valid": complete and all(item["audit"]["trace_valid"] for item in reports),
            "domain_valid": complete and all(item["audit"]["domain_valid"] for item in reports),
            "identity_authenticated": False, "scientific_truth_verified": False, "novelty_verified": False,
            "limits": ["No model inference or cognitive loop is replayed.",
                       "Local recorded causal consistency and finite-model certificates do not authenticate execution or identity.",
                       "A valid trace can include operational failures; per-run failures are never removed.",
                       "Verifier and supplied numerical data can share errors; this is not empirical truth or novelty."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    pack = commands.add_parser("pack")
    pack.add_argument("destination", type=Path)
    pack.add_argument("--run", nargs=2, metavar=("DIRECTORY", "EXPECTED_ROOT"), action="append", required=True)
    pack.add_argument("--source-root", type=Path, default=ROOT)
    pack.add_argument("--campaign-id", default="explicit-selection")
    for command in ("verify", "replay"):
        child = commands.add_parser(command)
        child.add_argument("directory", type=Path)
        child.add_argument("--expected-root", required=command == "replay")
        if command == "replay":
            child.add_argument("--execute-verified-toolkit", action="store_true")
            child.add_argument("--timeout-seconds", type=float, default=60)
    for child in (pack, *[commands.choices[name] for name in ("verify", "replay")]):
        child.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "pack":
            result = create_package(args.run, args.destination, source_root=args.source_root, campaign_id=args.campaign_id)
            success = result["package_hash_integrity"]
        elif args.command == "verify":
            result = verify_package(args.directory, expected_root=args.expected_root)
            success = result["package_hash_integrity"]
        else:
            result = replay_package(args.directory, expected_root=args.expected_root,
                                    execute_verified_toolkit=args.execute_verified_toolkit, timeout_seconds=args.timeout_seconds)
            success = result["replay_completed"] and result["trace_valid"]
        if args.output:
            package_path = (args.destination if args.command == "pack" else args.directory).resolve()
            require(not args.output.resolve().is_relative_to(package_path), "write reports outside the immutable package")
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError) as exc:
        result, success = {"error": f"{type(exc).__name__}: {exc}"}, False
    raw = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)+"\n"
    if args.output and "error" not in result:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(raw)
    else:
        print(raw, end="")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
