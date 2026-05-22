from app.mathlab.topology.topology_builder import VietorisRipsBuilder


def test_vietoris_rips_builder_basic():
    pts = [(0.0, 0.0), (0.1, 0.0), (1.0, 1.0)]
    b = VietorisRipsBuilder(epsilon=0.2)
    res = b.build(pts)
    assert res["n_points"] == 3
    assert res["components_est"] >= 1
    assert res["cycles_est"] >= 0


