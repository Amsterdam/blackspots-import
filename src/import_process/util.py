from datasets.blackspots.models import Spot


def get_stadsdeel(code: str):
    stadsdeel_code_map = {
        'T': Spot.Stadsdelen.Zuidoost,
        'A': Spot.Stadsdelen.Centrum,
        'N': Spot.Stadsdelen.Noord,
        'B': Spot.Stadsdelen.Westpoort,
        'E': Spot.Stadsdelen.West,
        'F': Spot.Stadsdelen.Nieuw_West,
        'K': Spot.Stadsdelen.Zuid,
        'M': Spot.Stadsdelen.Oost,
        'Geen': Spot.Stadsdelen.Geen,
        'N.v.t.': Spot.Stadsdelen.Geen,
        'n.v.t.': Spot.Stadsdelen.Geen,
        'Nvt': Spot.Stadsdelen.Geen,
        'nvt': Spot.Stadsdelen.Geen,
        '': Spot.Stadsdelen.Geen,
    }
    return stadsdeel_code_map.get(code.strip())
