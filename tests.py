from pytest import fixture, approx, raises
from instruments import Pipe, QuenaBody, ClarinetBody, Quena
from notes import NOTES

# FIXTURES

@fixture
def water_pipe():
    return Pipe(18, 3.5)

@fixture
def quena_G4(water_pipe):
    return Quena(
        pipe = water_pipe,
        freq = NOTES['G4'],
        holes_freqs = [NOTES[f] for f in ['A4', 'B4', 'C5', 'D5', 'E5', 'F#5', 'G5']],
        holes_diams = [10, 12, 9, 12, 12, 12, 7.5],
        emb_size = 9.5, 
        ring = True
    )

# REAL WORLD MEASURES CONFORMATION

def test_quena_body_emb_pos(water_pipe):
    measures = {  # fq:loc
        317.66:499,  
        259.41:619.5,
        358.08:435.5,
        363.16:433,
        402.16:384,
        403.91:382.5,
        362.66:435,
        405.16:382, 
        426.58:361.5
    }
    for fq, pos in measures.items():
        quena = QuenaBody(water_pipe, fq, 9.5)
        assert quena.emb_loc == approx(pos, .01)

def test_clarinet_body_emb_pos(water_pipe):
    clarinet = ClarinetBody(water_pipe, NOTES['G4'])
    assert clarinet.emb_loc == approx(407.63, .001) #TODO: Check experimental data

def test_quena_emb_pos(water_pipe): #TODO: Provide a TC with more holes
    quena = Quena(
        pipe = water_pipe,
        freq = 362.67,
        holes_freqs = [400],
        holes_diams = 10,
        emb_size = 9.5
    )
    assert quena.emb_loc == approx(435, .01)

def test_quena_ringed_emb_pos(quena_G4):
    assert quena_G4.emb_loc == approx(385-9, .01) #TODO: Check experimental data

def test_quena_holes_pos(): #TODO: Provide a TC
    assert False

def test_quena_ringed_holes_pos(quena_G4):
    measures = [48, 85, 108, 141, 171, 200, 215] #TODO: Check experimental data
    assert quena_G4.holes_loc == approx(measures, .01)

# OTHER TESTS

def test_impossible_quena(water_pipe):
    impossible = Quena(
        pipe = water_pipe,
        freq = 380,
        holes_freqs = [450, 650, 780],
        holes_diams = 4,
        emb_size = 9.5,
    )
    with raises(ValueError):
        impossible.holes_loc

def test_quena_display(quena_G4):
    quena_G4.show()