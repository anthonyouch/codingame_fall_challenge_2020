import sys
import math
import copy
import queue
import time
from time import perf_counter


# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.


def log(*args):
    for arg in args + ('\n',):
        print(arg, file=sys.stderr, end=' ', flush=True)


class Vector:
    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __getitem__(self, i):
        if i == 0:
            return self.a
        elif i == 1:
            return self.b
        elif i == 2:
            return self.c
        elif i == 3:
            return self.d

    def __add__(self, other):
        return Vector(self.a + other.a, self.b + other.b, self.c + other.c, self.d + other.d)

    def __str__(self):
        return "({}, {}, {}, {})".format(self.a, self.b, self.c, self.d)

    def __hash__(self):
        return hash((self.a, self.b, self.c, self.d))

    def __eq__(self, other):
        return (self.a, self.b, self.c, self.d) == (other.a, other.b, other.c, other.d)

    def is_nonneg(self):
        return self.a >= 0 and self.b >= 0 and self.c >= 0 and self.d >= 0

    def scale(self, s):
        return Vector(self.a * s, self.b * s, self.c * s, self.d * s)

    def sum(self):
        return self.a + self.b + self.c + self.d


class Potion:
    def __init__(self, idnum, delta, price):
        self.idnum = idnum
        self.delta = delta
        self.price = price

    def can_afford(self, ingreds):
        return (ingreds + self.delta).is_nonneg()


class TomeSpell:
    def __init__(self, idnum, delta, tome_index, tax_count, is_repeatable):
        self.idnum = idnum
        self.delta = delta
        self.tome_index = tome_index
        self.taxcount = tax_count
        self.is_repeatable = is_repeatable

    def get_cost(self):
        return self.tome_index


class Spell:
    def __init__(self, idnum, delta, is_castable, is_repeatable):
        self.idnum = idnum
        self.delta = delta
        self.is_castable = is_castable
        self.is_repeatable = is_repeatable

    def can_afford(self, ingreds):
        return self.is_castable and (ingreds + self.delta).is_nonneg()


def bfs(spells, inventory, max_time_ms: int, *goal_deltas):
    # start stopwatch
    t_start = perf_counter()

    # intitiate structures for bfs
    q = queue.Queue()
    closed_set = set()
    came_from = dict()

    start = (inventory, tuple(spell.is_castable for spell in spells))
    came_from[start] = (None, None)

    closed_set.add(start)
    q.put((start, 0))

    reached_goals = [None for _ in goal_deltas]

    for i, goal_delta in enumerate(goal_deltas):
        if (start[0] + goal_delta).is_nonneg():
            reached_goals[i] = start

    # begin bfs
    while not q.empty():

        if (perf_counter() - t_start) * 1000 > max_time_ms:
            log("time exceeded in bfs search proceeding to path handling")
            break

        current, dist = q.get()
        ingreds, castables = current

        # compute neightbours
        nbrs = []

        # spells:
        # deal with repeatables
        last_state, last_move = came_from[current]

        for i, spell in enumerate(spells):
            if last_state is not None and last_move == "REST" and last_state[1][i]:
                continue

            if castables[i] and (ingreds + spell.delta).is_nonneg() and (ingreds + spell.delta).sum() <= 10:
                for repeats in range(10, 0, -1):
                    if repeats > 1 and not spell.is_repeatable:
                        continue

                    final_ingreds = ingreds + spell.delta.scale(repeats)

                    if not final_ingreds.is_nonneg() or final_ingreds.sum() > 10:
                        continue

                    new_castables = list(castables[:])
                    new_castables[i] = False
                    nbrs.append(((final_ingreds, tuple(new_castables)), "CAST {} {}".format(spells[i].idnum, repeats)))

        # rest
        if not all(castables):
            nbrs.append(((ingreds, tuple(True for x in castables)), "REST"))

        for nbr, move in nbrs:
            if nbr not in closed_set:
                # goal check
                came_from[nbr] = (current, move)

                for i, goal_delta in enumerate(goal_deltas):
                    if reached_goals[i] is None and (nbr[0] + goal_delta).is_nonneg():
                        reached_goals[i] = nbr

                if all(x is not None for x in reached_goals):
                    break

                q.put((nbr, dist + 1))
                closed_set.add(nbr)

        if all(x is not None for x in reached_goals):
            break
    result = []
    for reached_goal in reached_goals:
        if reached_goal is None:
            result.append((None, None))
            continue

        path = [(reached_goal, "BREW")]
        temp_node, temp_move = came_from[reached_goal]
        while temp_node is not None:
            path.append((temp_node, temp_move))
            temp_node, temp_move = came_from[temp_node]

        path.reverse()
        result.append((len(path), path[0][1]))
    return result


class Game:
    def __init__(self):
        self.orders = []
        self.my_ingreds = None
        self.my_score = None
        self.enem_ingreds = None
        self.enem_score = None
        self.my_spells = []
        self.enem_spells = []
        self.tome = []

    def brew(self, idnum):
        print("BREW {}".format(idnum))

    def cast(self, idnum, num=1):
        print("CAST {} {}".format(idnum, num))

    def learn(self, idnum):
        print("LEARN {}".format(idnum))

    def rest(self):
        print("REST")

    def wait(self):
        print("WAIT")

    def decide(self):
        # learn spell in first 7 spell
        if turn_count <= 7:
            self.learn(self.tome[0].idnum)
            return

        # pick best one
        # target  = max(self.orders, key=lambda order: order.price, default = None)

        start_time = time.time()
        result = bfs(self.my_spells, self.my_ingreds, 46, *(potion.delta for potion in self.orders))
        finish_time = time.time()
        log("time   :", finish_time - start_time)

        log(result)

        if all(pair[0] is None for pair in result):
            # no pair found
            self.wait()
            return

        target = max((i for i in range(5) if result[i][0] is not None),
                     key=lambda i: self.orders[i].price / (1 + result[i][0]))

        dist, move = result[target]

        log("target ", self.orders[target].idnum, "dist ", dist, "move ", move)

        if dist == None:
            self.wait()
            return

        elif move == "BREW":
            self.brew(self.orders[target].idnum)
            return
        elif move == "REST":
            self.rest()
            return
        elif move.startswith("CAST"):
            _, idnum, repeats = move.split()
            self.cast(int(idnum), int(repeats))
            return

        self.wait()
        return

    # game loop


turn_count = 0
while True:

    turn_count += 1

    game = Game()

    action_count = int(input())  # the number of spells and recipes in play
    for i in range(action_count):

        action_id, action_type, delta_0, delta_1, delta_2, delta_3, price, tome_index, tax_count, castable, repeatable = input().split()
        action_id = int(action_id)
        delta_0 = int(delta_0)
        delta_1 = int(delta_1)
        delta_2 = int(delta_2)
        delta_3 = int(delta_3)
        price = int(price)
        tome_index = int(tome_index)
        tax_count = int(tax_count)
        castable = castable != "0"
        repeatable = repeatable != "0"

        delta = Vector(delta_0, delta_1, delta_2, delta_3)

        if action_type == "BREW":
            game.orders.append(Potion(action_id, delta, price))

        elif action_type == "CAST":
            game.my_spells.append(Spell(action_id, delta, castable, repeatable))

        elif action_type == "OPPONENT_CAST":
            game.enem_spells.append(Spell(action_id, delta, castable, repeatable))

        elif action_type == "LEARN":
            game.tome.append(TomeSpell(action_id, delta, tome_index, tax_count, repeatable))

    for i in range(2):
        # inv_0: tier-0 ingredients in inventory
        # score: amount of rupees
        inv_0, inv_1, inv_2, inv_3, score = [int(j) for j in input().split()]

        ingreds = Vector(inv_0, inv_1, inv_2, inv_3)

        if i == 0:
            game.my_ingreds = ingreds
            game.my_score = score
        if i == 1:
            game.enem_ingreds = ingreds
            game.enem_score = score

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    # in the first league: BREW <id> | WAIT; later: BREW <id> | CAST <id> [<times>] | LEARN <id> | REST | WAIT
    game.decide()
