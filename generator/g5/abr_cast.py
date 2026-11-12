"""Extra cast for Genesis part 2 (Abraham and Isaac)."""
import cast5
from cast5 import SPECS, ALIAS

def _from(base, **kw):
    d = dict(SPECS[base]); d.update(kw); return d

SPECS.update({
    "Abraham": _from("Abram", hair="gray", beard=("gray", 7, 11), brow="gray", robe="camel", mantle="ivory"),
    "Sarai": dict(robe="rose", w=(11, 15), hem=109, sash="brown", skin="tan", hair="hair", style="veil", veil="cream", inner="linen", beard=None,
                  prop="none", brow="hair", eyes=(50, 32, 26), sleeve="long", trim="cream", kind=True),
    "Lot": dict(robe="crimson", w=(12, 16), hem=106, sash="rope", skin="tan", hair="hair", style="sides", beard=("hair", 5, 7), prop="none",
                brow="hair", eyes=(36, 24, 20), sleeve="long", trim="linen"),
    "LotWife": dict(robe="plum", w=(11, 15), hem=109, sash="brown", skin="tan", hair="brown", style="veil", veil="sand", inner="cream", beard=None,
                    prop="none", brow="brown", eyes=(50, 32, 26), sleeve="long", trim="cream", kind=True),
    "Hagar": dict(robe="terra", w=(11, 15), hem=109, sash="gold", skin="dark", hair="black", style="veil", veil="ochre", inner="cream", beard=None,
                  prop="jar", brow="black", eyes=(30, 20, 16), sleeve="long", trim="gold", kind=True),
    "Ishmael": _from("Boy", skin="dark", hair="black", brow="black", robe="sand"),
    "Isaac": _from("Boy", robe="azure", hair="brown", brow="brown"),
    "IsaacMan": dict(robe="azure", w=(12, 16), hem=106, sash="rope", skin="tan", hair="brown", style="curly", beard=("brown", 4, 6), prop="none",
                     brow="brown", eyes=(36, 24, 20), sleeve="long", trim="linen", kind=True),
    "Rebekah": dict(robe="teal", w=(11, 15), hem=109, sash="gold", skin="tan", hair="auburn", style="veil", veil="rose", inner="cream", beard=None,
                    prop="jar", brow="auburn", eyes=(50, 32, 26), sleeve="long", trim="gold", kind=True),
    "Eliezer": dict(robe="fawn", w=(12, 16), hem=106, sash="brown", skin="tan", hair="gray", style="hat", beard=("gray", 5, 7), prop="staff",
                    brow="gray", eyes=(40, 34, 30), sleeve="long", trim="linen"),
    "Visitor": _from("Angel", wings=False, float=False, aura=False),
})
SPECS["Sarah"] = _from("Sarai", hair="gray", brow="gray", veil="linen", robe="rose")
ALIAS.update({"Pharaoh": "King", "Melchizedek": "Priest", "Angel2": "Angel", "Visitor2": "Visitor", "Visitor3": "Visitor",
              "Sodomite": "Mocker", "Sodomite2": "Mocker2", "Herdsman": "Shepherd", "Herdsman2": "Worker2", "Servant": "Worker"})
for a, b in ALIAS.items():
    if a not in SPECS: SPECS[a] = SPECS[b]
