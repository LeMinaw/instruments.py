from notes import NOTES
from instruments import Pipe, QuenaBody

pipe = Pipe(18, 3)

# notes = ['A4', 'B4', 'C5', 'D5', 'E5', 'F#5', 'G5']
# clarinet = Clarinet(
#     pipe = pipe,
#     freq = NOTES['G4'],
#     holes_freqs = [NOTES[f] for f in notes],
#     holes_diams = [10, 12, 9, 12, 12, 12, 7.5],
# )
# clarinette.show()

quena = QuenaBody(
    pipe = pipe,
    freq = NOTES['E3'],
    emb_size = 9.5,
)
print(quena.emb_loc)