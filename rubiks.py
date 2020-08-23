from enum import Enum

from typing import List

import pdb

class Move(Enum):
    U  = 0
    U1 = 1
    U2 = 2
    D  = 3
    D1 = 4
    D2 = 5
    L2 = 6
    R2 = 7
    F2 = 8
    B2 = 9

    L  = 10
    L1 = 11
    R  = 12
    R1 = 13
    F  = 14
    F1 = 15
    B  = 16
    B1 = 17

move_strings = ['U','U1','U2','D','D1','D2','L2','R2','F2','B2',
                'L','L1','R','R1','F','F1','B','B1']
# Special optimization for 2x2x2 cubes
def restricted_move_mapping(m: int):
    # moves in range from 0 to 8
    moves = [Move.U, Move.U1, Move.U2,
             Move.L, Move.L1, Move.L2,
             Move.F, Move.F1, Move.F2]
    return moves[m]

class FaceType(Enum):
    U = 0
    D = 1
    L = 2
    R = 3
    F = 4
    B = 5

class RotType(Enum):
    CLOCK = 0
    COUNTER = 1
    FLIP = 2

def get_face(m: Move) -> FaceType:
    face_map = [FaceType.U, FaceType.U, FaceType.U,
                FaceType.D, FaceType.D, FaceType.D,
                FaceType.L, FaceType.R, FaceType.F,
                FaceType.B, FaceType.L, FaceType.L,
                FaceType.R, FaceType.R, FaceType.F,
                FaceType.F, FaceType.B, FaceType.B]
    return face_map[m.value]

def get_rot_type(m: Move) -> RotType:
    rot_map = [RotType.CLOCK, RotType.COUNTER, RotType.FLIP,
               RotType.CLOCK, RotType.COUNTER, RotType.FLIP,
               RotType.FLIP, RotType.FLIP,
               RotType.FLIP, RotType.FLIP,
               RotType.CLOCK, RotType.COUNTER,
               RotType.CLOCK, RotType.COUNTER,
               RotType.CLOCK, RotType.COUNTER,
               RotType.CLOCK, RotType.COUNTER]
    return rot_map[m.value]

def get_move(face, rot_type):
    for i in range(18):
        move = Move(i)
        if get_face(move) == face and \
                get_rot_type(move) == rot_type:
            return move
    raise Exception()

def get_rot_shift(r: RotType):
    if r == RotType.CLOCK:
        return 1
    elif r == RotType.COUNTER:
        return -1
    elif r == RotType.FLIP:
        return 2
    else:
        raise ValueError

def facemap_2(face: int, facelet: int, m: Move):
    # Takes in face, facelet, and a Move
    # Outputs (face,facelet) where that facelet gets mapped to under the Move

    rot_shift = get_rot_shift(get_rot_type(m))

    # Faces: 0:U, 1:D, 2:L, 3:R, 4:F, 5:B
    if get_face(m) == FaceType(face):
        chain = [0, 1, 3, 2]

        chain_idx = chain.index(facelet)

        return face, chain[(chain_idx + rot_shift) % len(chain)]
    else:
        U_face_chain = [FaceType.F, FaceType.L,
                        FaceType.B, FaceType.R]
        U_facelet_chain = [[0,1],[0,1],[0,1],[0,1]]
        #U_facelet_chain = [[0,1,2],[0,1,2],[0,1,2],[0,1,2]]

        D_face_chain = [FaceType.F, FaceType.R,
                        FaceType.B, FaceType.L]
        D_facelet_chain = [[2,3],[2,3],[2,3],[2,3]]
        #D_facelet_chain = [[6,7,8],[6,7,8],[6,7,8],[6,7,8]]

        L_face_chain = [FaceType.F, FaceType.D,
                        FaceType.B, FaceType.U]
        L_facelet_chain = [[0,2],[0,2],[3,1],[0,2]]
        #L_facelet_chain = [[0,3,6],[0,3,6],[8,5,2],[0,3,6]]

        R_face_chain = [FaceType.F, FaceType.U,
                        FaceType.B, FaceType.D]
        R_facelet_chain = [[1,3],[1,3],[2,0],[1,3]]
        #R_facelet_chain = [[2,5,8],[2,5,8],[6,3,0],[2,5,8]]

        F_face_chain = [FaceType.U, FaceType.R,
                        FaceType.D, FaceType.L]
        F_facelet_chain = [[2,3],[0,2],[1,0],[3,1]]
        #F_facelet_chain = [[6,7,8],[0,3,6],[2,1,0],[8,5,2]]

        B_face_chain = [FaceType.U, FaceType.L,
                        FaceType.D, FaceType.R]
        B_facelet_chain = [[0,1],[2,0],[3,2],[1,3]]
        #B_facelet_chain = [[0,1,2],[6,3,0],[8,7,6],[2,5,8]]

        face_chains = [U_face_chain, D_face_chain,
                       L_face_chain, R_face_chain,
                       F_face_chain, B_face_chain]
        facelet_chains = [U_facelet_chain, D_facelet_chain,
                          L_facelet_chain, R_facelet_chain,
                          F_facelet_chain, B_facelet_chain]

        face_chain = face_chains[get_face(m).value]
        facelet_chain = facelet_chains[get_face(m).value]

        if not FaceType(face) in face_chain:
            return face, facelet

        face_chain_idx = face_chain.index(FaceType(face))
        face_chain_idx_shifted = (face_chain_idx + rot_shift) % len(face_chain)
        next_face = face_chain[face_chain_idx_shifted]

        if not facelet in facelet_chain[face_chain_idx]:
            return face, facelet

        facelet_chain_idx = facelet_chain[face_chain_idx].index(facelet)
        next_facelet = facelet_chain[face_chain_idx_shifted][facelet_chain_idx]

        return (next_face.value, next_facelet)

def facemap_3(face: int, facelet: int, m: Move):
    # Takes in face, facelet, and a Move
    # Outputs (face,facelet) where that facelet gets mapped to under the Move

    # Center facelet never gets turned
    if facelet == 4:
        return face, facelet

    rot_shift = get_rot_shift(get_rot_type(m))

    # Faces: 0:U, 1:D, 2:L, 3:R, 4:F, 5:B
    if get_face(m) == FaceType(face):
        # 0 -> 2 -> 8 -> 6
        # 1 -> 5 -> 7 -> 3
        # 4 is constant
        chains = [[0, 2, 8, 6], [1, 5, 7, 3]]

        chain = chains[0] if (facelet in chains[0]) else chains[1]
        chain_idx = chain.index(facelet)

        return face, chain[(chain_idx + rot_shift) % len(chain)]
    else:
        U_face_chain = [FaceType.F, FaceType.L,
                        FaceType.B, FaceType.R]
        U_facelet_chain = [[0,1,2],[0,1,2],[0,1,2],[0,1,2]]

        D_face_chain = [FaceType.F, FaceType.R,
                        FaceType.B, FaceType.L]
        D_facelet_chain = [[6,7,8],[6,7,8],[6,7,8],[6,7,8]]

        L_face_chain = [FaceType.F, FaceType.D,
                        FaceType.B, FaceType.U]
        L_facelet_chain = [[0,3,6],[0,3,6],[8,5,2],[0,3,6]]

        R_face_chain = [FaceType.F, FaceType.U,
                        FaceType.B, FaceType.D]
        R_facelet_chain = [[2,5,8],[2,5,8],[6,3,0],[2,5,8]]

        F_face_chain = [FaceType.U, FaceType.R,
                        FaceType.D, FaceType.L]
        F_facelet_chain = [[6,7,8],[0,3,6],[2,1,0],[8,5,2]]

        B_face_chain = [FaceType.U, FaceType.L,
                        FaceType.D, FaceType.R]
        B_facelet_chain = [[0,1,2],[6,3,0],[8,7,6],[2,5,8]]

        face_chains = [U_face_chain, D_face_chain,
                       L_face_chain, R_face_chain,
                       F_face_chain, B_face_chain]
        facelet_chains = [U_facelet_chain, D_facelet_chain,
                          L_facelet_chain, R_facelet_chain,
                          F_facelet_chain, B_facelet_chain]

        face_chain = face_chains[get_face(m).value]
        facelet_chain = facelet_chains[get_face(m).value]

        if not FaceType(face) in face_chain:
            return face, facelet

        face_chain_idx = face_chain.index(FaceType(face))
        face_chain_idx_shifted = (face_chain_idx + rot_shift) % len(face_chain)
        next_face = face_chain[face_chain_idx_shifted]

        if not facelet in facelet_chain[face_chain_idx]:
            return face, facelet

        facelet_chain_idx = facelet_chain[face_chain_idx].index(facelet)
        next_facelet = facelet_chain[face_chain_idx_shifted][facelet_chain_idx]

        return (next_face.value, next_facelet)

facemaps = {2: facemap_2, 3: facemap_3}

# Faces: 0: U, 1: D, 2: L, 3:R, 4:F, 5:B

# Facelet colors are ints from zero to 5
FaceletColor = int
Face = List[FaceletColor]

# Facelets are such that 0 is top left
# For sides top left is obvious; for up, top left is if you flip the cube top down towards you, for bottom, top left is if you flip the cube bottom up towards you

class RubiksCube:
    N: int
    faces: List[Face] # Face and then facelet

    def __init__(self, N: int, faces: List[Face]) -> None:
        if faces == None:
            faces = []
            for i in range(6):
                faces.append([i] * (N ** 2))

        assert(len(faces) == 6)
        assert(len(faces[0]) == N ** 2)

        self.N = N
        self.faces = faces

    def do_move(self, m: Move):
        new_faces = [[0]*(self.N**2) for _ in range(6)]

        for face in range(6):
            for facelet in range(self.N ** 2):
                facemap = facemaps[self.N]
                new_face, new_facelet = facemap(face, facelet, m)
                new_faces[new_face][new_facelet] = self.faces[face][facelet]

        self.faces = new_faces
