# Release Checklist — A.M.Y v0.9.0

## Pre-Release Validation

### Core Functionality
- [x] Heartbeat runs without errors
- [x] Memory systems (episodic, semantic, procedural) functional
- [x] Global workspace competition and broadcast works
- [x] Reasoning engine generates valid JSON
- [x] Experiment sandbox executes code safely
- [x] Syntax validation catches errors before execution

### Scientific Rigor
- [x] Reproducibility test passes (3 identical runs)
- [x] Syntax validation test passes
- [x] Atlas tools validated across 8 domains
- [x] No invented numbers in generated papers
- [x] Real citations required for claims
- [x] Falsification attempted before confirmation

### Code Quality
- [x] All modules have implementations (no empty placeholders)
- [x] Tests pass: `python test_amy_quick.py`
- [x] Tests pass: `python test_reproducibility.py`
- [x] Tests pass: `python test_atlas_tools.py`
- [x] No broken imports in core modules
- [x] JSON parsing robust with multiple fallbacks

### Documentation
- [x] README.md updated with status table
- [x] README_PUBLIC.md created for public audience
- [x] SCIENCE_MANIFESTO.md with rigor principles
- [x] CHANGELOG.md with version history
- [x] CONTRIBUTING.md exists
- [x] CODE_OF_CONDUCT.md exists
- [x] LICENSE exists

### Integration
- [x] Atlas subproject accessible
- [x] 84+ tools registered in DynamicToolRegistry
- [x] Literature search functional (with known async issue)
- [x] Peer review pipeline documented
- [x] Tool validation results recorded

### Security
- [x] Sandbox blocks dangerous commands
- [x] No `rm -rf /`, `sudo`, or `eval` allowed
- [x] Execution timeout configured (300s default)
- [x] Memory limit configured (2048MB default)
- [x] Ethics gate documented

### Performance
- [x] Heartbeat interval configurable
- [x] Focused mode: 5s intervals
- [x] Idle mode: 120s intervals
- [x] Max cycles before reflection: 20
- [x] Experiment timeout prevents infinite loops

## Known Issues for v0.9.0

| Issue | Severity | Workaround | Target Fix |
|-------|----------|------------|------------|
| Literature search async handling | Medium | Use sync wrapper | v0.9.1 |
| Redis cache optional | Low | In-memory fallback | v0.9.1 |
| Brian2 not available | Low | Optional dependency | v0.10.0 |
| yt not available | Low | Optional dependency | v0.10.0 |

## Post-Release Monitoring

- [ ] Monitor experiment success rate
- [ ] Track paper generation quality
- [ ] Collect user feedback on scientific rigor
- [ ] Measure reproducibility across different machines
- [ ] Validate citations in generated papers

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Lead Developer | Giovanni Arangio | 2026-04-23 | ✓ |
| Scientific Advisor | [Pending] | | |
| QA Engineer | [Pending] | | |

---

**Release Date Target:** 2026-05-01  
**Current Version:** v0.9.0-pre  
**Next Milestone:** v1.0.0 (Production Release)
