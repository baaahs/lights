import json
import math

HALF_PI = math.pi / 2.0

class SectorMapper(object):

    def __init__(self, filename, fov):
        with open(filename) as f:
            self.sectors = json.load(f)

        self.fov = fov

    def sector_at(self, pan, tilt):
        m, panIx = math.modf(pan / self.fov)
        panIx = int(panIx)

        tilt = tilt + HALF_PI;
        m, tiltIx = math.modf(tilt / self.fov);
        tiltIx = int(tiltIx)

        try:
            return self.sectors[panIx][tiltIx]
        except Exception:
            return None


    def map_value(self, sheep_sides, pan, tilt, color, scale=0.5, symmetry=False):
        """
        Maps the color onto panel that have some presence in the
        sector identified by the pan and tilt values. The colors
        is mapped by value (i.e. brightness) in the HSV model.
        """
        sector = self.sector_at(pan, tilt)
        if sector is None:
            return

        for name, percent in sector.iteritems():
            if name[0] == '_':
                continue

            if name[-1] == 'p':
                side = sheep_sides.party                
            else:
                side = sheep_sides.business
                # if symmetry:
                #     continue

            if symmetry:
                side = sheep_sides.both

            try:
                cell = int(name[:-1])

                c = color.copy()
                c.v = (1.0 - scale) + (c.v * percent * scale)

                side.set_cell(cell, c)
            except Exception:
                pass



FOV_10 = SectorMapper("data/sectors_fov_10.json", math.pi / 18)
