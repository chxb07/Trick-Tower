#!/usr/bin/env python3
import random
import statistics
import math
import json
from collections import defaultdict

# =====================
# CONFIG
# =====================
NUM_FLOORS = 15
NUM_CELLS = 100
CELLS_PER_FLOOR = math.ceil(NUM_CELLS / NUM_FLOORS)
MAX_TURNS = 50

VIOLENT_THRESHOLD = 7
NONVIOLENT_THRESHOLD = 4

# =====================
# PRISONER
# =====================
class Prisoner:
    def __init__(self, pid, cell, threat):
        self.pid = pid
        self.cell = cell
        self.floor = (cell // CELLS_PER_FLOOR) + 1
        self.threat = threat
        self.believed_threat = float(threat)

# =====================
# ENGINE
# =====================
class TrickTowerEngine:
    def __init__(self, prisoners):
        self.prisoners = prisoners
        self.turn = 0
        self.heatmap = {f: [] for f in range(1, NUM_FLOORS + 1)}
        self.last_observed = -1

    # -----------------
    # FLOOR MAP
    # -----------------
    def get_floor_map(self):
        floors = defaultdict(list)
        for p in self.prisoners:
            floors[p.floor].append(p)
        return floors

    # -----------------
    # ESTIMATE THREAT
    # -----------------
    def estimate_floor_threat(self, floor):
        floors = self.get_floor_map()
        if floor not in floors:
            return 0
        return statistics.mean(p.believed_threat for p in floors[floor])

    # -----------------
    # MOVEMENT
    # -----------------
    def simulate_movement(self):
        for p in self.prisoners:
            if random.random() < 0.3:
                p.floor = random.randint(1, NUM_FLOORS)

    # -----------------
    # OBSERVE FLOOR
    # -----------------
    def choose_floor(self):
        best = -1
        best_score = -1

        for f in range(1, NUM_FLOORS + 1):
            if f == self.last_observed:
                continue

            threat = self.estimate_floor_threat(f)
            score = threat + random.random()

            if score > best_score:
                best_score = score
                best = f

        self.last_observed = best
        return best

    # -----------------
    # SWAP
    # -----------------
    def swap(self, floor):
        floors = self.get_floor_map()
        if floor not in floors:
            return

        violent = [p for p in floors[floor] if p.believed_threat >= VIOLENT_THRESHOLD]
        safe = [p for p in self.prisoners if p.believed_threat <= NONVIOLENT_THRESHOLD]

        if not violent or not safe:
            return

        v = max(violent, key=lambda x: x.believed_threat)
        s = min(safe, key=lambda x: x.believed_threat)

        v.floor, s.floor = s.floor, v.floor

    # -----------------
    # HEATMAP
    # -----------------
    def update_heatmap(self):
        floors = self.get_floor_map()
        for f in range(1, NUM_FLOORS + 1):
            if f not in floors or len(floors[f]) == 0:
                self.heatmap[f].append(0)
            else:
                density = sum(
                    1 for p in floors[f]
                    if p.believed_threat >= VIOLENT_THRESHOLD
                ) / len(floors[f])

                self.heatmap[f].append(density)

    # -----------------
    # EXPORT
    # -----------------
    def export_heatmap(self):
        data = {
            "floors": list(range(1, NUM_FLOORS + 1)),
            "turns": list(range(1, MAX_TURNS + 1)),
            "heatmap": [self.heatmap[f] for f in range(1, NUM_FLOORS + 1)]
        }

        with open("heatmap.json", "w") as f:
            json.dump(data, f)

    # -----------------
    # RUN
    # -----------------
    def run(self):
        for t in range(MAX_TURNS):
            self.turn = t

            floor = self.choose_floor()
            self.swap(floor)
            self.update_heatmap()
            self.simulate_movement()

            print(f"Turn {t+1} | Observed Floor: {floor}")

        print("Simulation complete.")
        self.export_heatmap()

# =====================
# MOCK DATA
# =====================
def generate_prisoners():
    prisoners = []
    for i in range(NUM_CELLS):
        threat = random.randint(1, 10)
        prisoners.append(Prisoner(i, i, threat))
    return prisoners

# =====================
# MAIN
# =====================
if __name__ == "__main__":
    random.seed(42)

    prisoners = generate_prisoners()
    engine = TrickTowerEngine(prisoners)

    engine.run()