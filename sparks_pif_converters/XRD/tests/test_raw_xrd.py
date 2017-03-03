from sparks_pif_converters.XRD import raw_to_pif
from pypif.util.read_view import ReadView

def test_raw_xrd():
    pif = raw_to_pif("./examples/XX001_TaPO5.raw")
    rv = ReadView(pif)
    assert("TaPO5" in pif.ids)
    assert(rv["2$\\theta$ (I$_{max}$)"].scalars[0].value == 21.530142749115)
