from utils import iterable
from math import sqrt
from math import pi as PI
from textwrap import dedent

SOUND_VEL = 345 * 10**3  # In mm.s-1
EPSILON = .00001

class Pipe:

    def __init__(self, diam, thick):
        """Constructs a Pipe from its inner diameter and wall thickness."""
        self.diam = diam
        self.thick = thick
    
    # Corrections
    
    def end_adj(self):
        """End adjustment. The air column extends out of the pipe by a certain factor,
        roughly proportionnal to the pipe diameter."""
        return 0.8 * self.diam


# Here are defined various instruments

class VibratingPipe:

    def __init__(self, pipe, freq, emb_diam):
        """Constructs a VibratingPipe.\n
        pipe: Pipe instance\n
        freq: Target vibration frequency, in Hz\n
        emb_diam: Embouchure diameter, in mm"""
        self.pipe     = pipe
        self.emb_diam = emb_diam
        self.freq     = freq
    
    @property
    def theoric_length(self):
        """Theoric pipe length, without any correction. It's the vibrating air column
        target length."""
        return SOUND_VEL / self.freq / 2
    
    @property
    def emb_loc(self):
        """Physical embouchure location, from pipe end."""
        return self.end_pos() - self.emb_adj()

    def end_pos(self):
        """Position of flute end, from the start of the air column."""
        return self.theoric_length - self.pipe.end_adj()
    
    # Corrections

    def emb_adj(self):
        """Embouchure adjustement. The air column virtually extends out of the pipe past
        the embouchure."""
        # Complete formula (emb_adj and thick_emb) comes from Peter Kosel's Flutomat
        # source code as an alternative formula, we found it matches the Quena quite well
        diam_ratio = self.pipe.diam / self.emb_diam
        return diam_ratio**2 * self.thick_emb()

    def thick_emb(self):
        """Effective pipe thickness, due to embouchure."""
        # Here's the other part of Peter Kosel's formula
        return self.pipe.diam/2 + self.pipe.thick + 0.307*self.emb_diam
        
        # Alternative, proposed by Celso Llimpe, Jorge Moreno and Miguel Piaggio 
        # http://www.sea-acustica.es/WEB_ICA_07/fchrs/papers/mus-02-008.pdf
        # return self.pipe.thick + 0.725 * self.emb_diam


class QuenaBody(VibratingPipe):

    lips_coverage = 0.15  # Lips coverage ratio, between 0.11 and 0.25

    def __init__(self, pipe, freq, emb_size):
        """Constructs a QuenaBody.\n
        pipe: Pipe instance\n
        freq: Target vibration frequency, in Hz\n
        emb_size: Embouchure size, in mm. Must be close to pipe radius."""
        emb_diam = emb_size * sqrt(1 + PI/4)
        super().__init__(pipe, freq, emb_diam)
    
    # Corrections

    def emb_adj(self):
        """Embouchure adjustement. The air column virtually extends out of the pipe past
        the embouchure."""
        return super().emb_adj() * (1-self.lips_coverage)


class ClarinetBody(VibratingPipe):

    def __init__(self, pipe, freq):
        """Constructs a ClarinetBody.\n
        pipe: Pipe instance\n
        freq: Target vibration frequency, in Hz"""
        super().__init__(pipe, freq, emb_diam=pipe.diam)
        

class Quena(QuenaBody):

    ring_offset = 23.58  # mm

    def __init__(self, pipe, freq, holes_freqs, emb_size, holes_diams=5, ring=False):
        """Constructs a Quena.\n
        pipe: Pipe instance in wich the Quena will be cut\n
        freq: The frequence of the flute when all holes are closed\n
        hole_freqs: An iterable containing holes frequencies\n
        emb_size: Embouchure size, in mm\n
        hole_diams: An iterable containing hole diameters. If a numeric value
        is provided, it will be used for all holes.
        ring: Bool, True if the Quena used a ring to close part of its open end."""
        self.ring = ring
        self.holes_freqs = sorted(holes_freqs)
        
        if iterable(holes_diams):
            if len(holes_diams) != len(holes_freqs):
                raise IndexError(
                    "holes_diams and holes_freqs parameters must be of same length")
            self.holes_diams = [d for f, d in sorted(zip(holes_freqs, holes_diams))]
        else:
            self.holes_diams = [holes_diams] * len(holes_freqs)
        
        super().__init__(pipe, freq, emb_size)
    
    @property
    def holes_nb(self):
        return len(self.holes_freqs)
    
    @property
    def holes_loc(self):
        """Physical holes locations, relative to flute end."""
        return [self.end_pos() - pos for pos in self.holes_pos()]
    
    def show(self):
        """Prints a nice diagram of the Quena to the console!"""
        diagram = dedent(f"""
            ALL UNITS ARE MILIMETERS
            ┌┬─┬┐
            │└─┘│<-- {self.emb_loc:3.1f}
            │   │
            │   │""")
        for loc, diam in zip(reversed(self.holes_loc), reversed(self.holes_diams)):
            diagram += dedent(f"""
                │ O │<-- {loc:3.1f} (Ø{diam:3.1f})
                │   │""")
        diagram += dedent("""
            │   │
            └───┘<-- 0.00""")
        print(diagram)



    def end_pos(self):
        """Position of flute end, from the start of the air column."""
        return super().end_pos() - self.ring_adj() - self.cum_closed_adj(0)
    
    def theoric_hole_pos(self, n):
        """Theoric position of hole n."""
        return SOUND_VEL / self.holes_freqs[n] / 2
    
    def holes_pos(self):
        """Find the locations of all finger holes.\n
        This procedure uses Benade equations in an iterative manner."""
        holes_pos = []
        for n in range(self.holes_nb):
            holes_pos.append(0)
            old_pos = 1
            while abs(holes_pos[n] - old_pos) > EPSILON:
                old_pos = holes_pos[n]

                # Open hole correction
                try:
                    if n == 0:  # First hole is lower
                        ratio = self.holes_diams[0] / self.pipe.diam
                        dist = self.end_pos() - holes_pos[0]
                        open_adj = (
                            self.thick_hole(0) / (ratio**2 + self.thick_hole(0) / dist)
                        )
                    else:
                        ratio = self.pipe.diam / self.holes_diams[n]
                        dist = holes_pos[n-1] - holes_pos[n]
                        open_adj = ( dist / 2
                            * (sqrt(1 + 4*(self.thick_hole(n) / dist*ratio**2)) - 1)
                        )
                except ValueError:
                    raise ValueError("Failed to compute open hole correction for hole "
                        f"{n}. Is it too small?")

                holes_pos[n] = self.theoric_hole_pos(n) - open_adj
                if n < self.holes_nb-1:
                    holes_pos[n] -= self.cum_closed_adj(n+1)

        return holes_pos
    
    # Corrections

    def ring_adj(self):
        """Ring adjustment. Certain Quenas have a ring partially covering their open
        end, producing a reduction of the physical pipe length."""
        if self.ring:
            return self.ring_offset
        return 0
    
    def cum_closed_adj(self, a, b=None):
        """Cumulated closed hole adjustment from hole a up to hole b, where b is the last
        closed hole. The length of the vibrating air column is effectively increased by
        each closed tone hole which exists above the first open tone hole."""
        b = b or self.holes_nb
        return sum([self.closed_adj(i) for i in range(a, b)])
    
    def closed_adj(self, n):
        """Closed hole adjustment for tone hole n. Part of any hole covered by a finger
        remains free, reducing physical pipe length."""
        free_thick = self.pipe.thick / 10
        return free_thick * (self.holes_diams[n]/self.pipe.diam)**2
    
    def thick_hole(self, n):
        """Effective pipe thickness, due to open tonal hole n. Air column extends out past
        end of hole 3/4 of the hole diameter."""
        return self.pipe.thick + 0.75*self.holes_diams[n]