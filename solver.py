import rubiks
from rubiks import Move, FaceType, RotType, RubiksCube

from ortools.sat.python import cp_model

from typing import List

import pdb

class RubiksSolver:
    def __init__(self, cube: RubiksCube, n_moves: int, optimize=True) -> None:
        gods = float('inf')
        if cube.N == 2:
            gods = 11
        elif cube.N == 3:
            gods = 20

        self.cube = cube
        self.model = cp_model.CpModel()
        self.n_moves = max(n_moves, gods)
        self.optimize = optimize

    def solve(self):
        self.create_vars()
        self.create_initial_constraint()
        self.create_final_constraint()
        self.create_move_constraints()
        self.create_objective()

        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = 8
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL:
            colors = self.extract_colors(solver)

            moves = []
            for move, is_solved in zip(self.moves, self.state_is_solved[1:]):
                if self.cube.N == 2 and self.optimize:
                    move = rubiks.restricted_move_mapping(solver.Value(move))
                else:
                    move = rubiks.Move(solver.Value(move))

                moves.append(move)

                if solver.Value(is_solved):
                    return moves

            return []
        else:
            raise Exception()

    def extract_colors(self, solver):
        colors = [[[solver.Value(k) for k in j]
            for j in i] for i in self.solution]
        return colors

    def create_vars(self):
        solution = [[[None for _ in range(self.cube.N ** 2)]
                           for _ in range(6)]
                           for _ in range(self.n_moves+1)]
        moves = []

        for state in range(self.n_moves+1):
            for face in range(6):
                for facelet in range(self.cube.N ** 2):
                    solution[state][face][facelet] = self.model.NewIntVar(
                            0, 5, f'{state},{face},{facelet}')

            if state != self.n_moves:
                if self.cube.N == 2 and self.optimize:
                    moves.append(self.model.NewIntVar(0, 8, f'move_{state}'))
                else:
                    moves.append(self.model.NewIntVar(0, 17, f'move_{state}'))

        self.solution = solution
        self.moves = moves

    def create_initial_constraint(self):
        for i, face in enumerate(self.cube.faces):
            for j, facelet in enumerate(face):
                self.model.Add(self.solution[0][i][j] == facelet)

    def create_final_constraint(self):
        self.state_is_solved = []

        for s, state in enumerate(self.solution):
            solved = self.model.NewBoolVar(f'{s}_is_sol')

            facelets_matching = []
            for i, face in enumerate(state):
                for j, facelet in enumerate(face):
                    facelet_matching = self.model.NewBoolVar(f'{i}{j}_matching')
                    self.model.Add(facelet == face[0]).OnlyEnforceIf(facelet_matching)
                    self.model.Add(facelet != face[0]).OnlyEnforceIf(facelet_matching.Not())

                    facelets_matching.append(facelet_matching)

            self.model.AddBoolAnd(facelets_matching).OnlyEnforceIf(solved)

            self.state_is_solved.append(solved)

        num_solved_states = self.model.NewIntVar(0, len(self.solution), 'num_solved')
        self.model.Add(num_solved_states == sum(self.state_is_solved))
        self.model.Add(num_solved_states == 1)

    def create_objective(self):
        obj = 0
        for i, is_solved in enumerate(self.state_is_solved):
            obj = obj + i * is_solved

        self.model.Minimize(obj)

    def create_move_constraints(self):
        for m, move in enumerate(self.moves):
            state_i = self.solution[m]
            state_n = self.solution[m+1]

            for move_num in range(9 if self.cube.N == 2 and self.optimize else 18):
                is_this_move = self.model.NewBoolVar(f'is_move{m},{move_num}')
                self.model.Add(move == move_num).OnlyEnforceIf(is_this_move)
                self.model.Add(move != move_num).OnlyEnforceIf(is_this_move.Not())

                literals = []
                for face in range(6):
                    for facelet in range(self.cube.N ** 2):
                        facelet_matching = self.model.NewBoolVar(f'facelet_match{m},{move_num},{face},{facelet}')
                        facemap = rubiks.facemaps[self.cube.N]
                        if self.cube.N == 2 and self.optimize:
                            next_face, next_facelet = facemap(face, facelet, rubiks.restricted_move_mapping(move_num))
                        else:
                            next_face, next_facelet = facemap(face, facelet, rubiks.Move(move_num))
                        self.model.Add(state_i[face][facelet] == state_n[next_face][next_facelet])\
                                  .OnlyEnforceIf(facelet_matching)
                        self.model.Add(state_i[face][facelet] != state_n[next_face][next_facelet])\
                                  .OnlyEnforceIf(facelet_matching.Not())

                        literals.append(facelet_matching)

                self.model.AddBoolAnd(literals).OnlyEnforceIf(is_this_move)
