import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

# game loop
value = 0
start_count = False


def can_do_spell(spell, inven):
    addition = []
    for i in range(len(inven)):
        addition.append(spell[i] + inven[i])

    if all(j >= 0 for j in addition) and sum(addition) <= 10:
        return True
    return False


def good_spell(spell, inven):
    smallest_index_list = []
    smallest_value = min(inven)

    for i in range(len(inven)):
        if inven[i] == smallest_value:
            smallest_index_list.append(i)

    for index in smallest_index_list:
        if spell[index] > 0:
            return True

    return False


def is_it_worth(tome_spells, inven):
    # tier 0: 1
    # tier 1: 3
    # tier 2: 2
    # tier 3: 4
    # 4th index = tome_count
    # 5th index = tax_count

    worth = False
    calc = tome_spells[0] + tome_spells[1] * 3 + tome_spells[2] * 2 + tome_spells[3] * 4
    if (calc + tome_spells[-1] - tome_spells[-2]) >= 2:
        worth = True

    if not worth:
        return 0

    if inven[0] >= tome_spells[-2]:
        return (calc + tome_spells[-1] - tome_spells[-2])

    return 0


def goes_towards(spell, potion, inven):
    array = []
    for i in range(len(inven)):
        array.append(abs(potion[i]) - inven[i])
    for i in range(len(spell)):
        if spell[i] > 0 and array[i] > 0:
            return True
    return False


def find_smallest_difference(potion, inven):
    smallest_difference = 1000
    pot_index = []
    pot_smallest = []
    for pot in potion:
        dif_array = []
        for i in range(len(inven)):
            if inven[i] < abs(pot[i]):
                dif_array.append(abs(pot[i]) - inven[i])
            else:
                dif_array.append(0)

        if sum(dif_array) < smallest_difference:
            smallest_difference = sum(dif_array)
            pot_smallest = pot

    pot_index.append(pot_smallest)

    for pot in potion:
        dif_array = []
        for i in range(len(inven)):
            if inven[i] < abs(pot[i]):
                dif_array.append(abs(pot[i]) - inven[i])
            else:
                dif_array.append(0)

        if sum(dif_array) == smallest_difference:
            pot_index.append(pot)

    return pot_index


def check_sabotage(spell, potion, inven):
    potion = [abs(i) for i in potion]

    inven_pot = []

    for i in range(len(inven)):
        if inven[i] < potion[i]:
            inven_pot.append(potion[i] - inven[i])
        else:
            inven_pot.append(0)
    inven_pot_sum = sum(inven_pot)

    inven_after_spell = []
    for i in range(len(inven)):
        inven_after_spell.append(inven[i] + spell[i])
    # check sum of inven_after_spell
    inven_after_spell_pot = []
    for i in range(len(inven)):
        if inven_after_spell[i] < potion[i]:
            inven_after_spell_pot.append(potion[i] - inven_after_spell[i])
        else:
            inven_after_spell_pot.append(0)

    inven_after_spell_pot_sum = sum(inven_after_spell_pot)

    if inven_after_spell_pot_sum <= inven_pot_sum:
        different = inven_pot_sum - inven_after_spell_pot_sum
        return different

    return -1


while True:
    spell = []
    best_price = 0
    brew_id = 0
    cast_id = 0
    potions = []
    tome_spells = []
    castable_lst = []

    action_count = int(input())  # the number of spells and recipes in play
    for i in range(action_count):
        # action_id: the unique ID of this spell or recipe
        # action_type: in the first league: BREW; later: CAST, OPPONENT_CAST, LEARN, BREW
        # delta_0: tier-0 ingredient change
        # delta_1: tier-1 ingredient change
        # delta_2: tier-2 ingredient change
        # delta_3: tier-3 ingredient change
        # price: the price in rupees if this is a potion
        # tome_index: in the first two leagues: always 0; later: the index in the tome if this is a tome spell, equal to the read-ahead tax; For brews, this is the value of the current urgency bonus
        # tax_count: in the first two leagues: always 0; later: the amount of taxed tier-0 ingredients you gain from learning this spell; For brews, this is how many times you can still gain an urgency bonus
        # castable: in the first league: always 0; later: 1 if this is a castable player spell
        # repeatable: for the first two leagues: always 0; later: 1 if this is a repeatable player spell
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

        if action_type == 'BREW':
            potions.append([delta_0, delta_1, delta_2, delta_3, price, action_id])

        if action_type == 'CAST':
            castable_lst.append(castable)

        if action_type == 'CAST' and castable == 1:
            spell.append([delta_0, delta_1, delta_2, delta_3, castable, action_id])

        if action_type == 'LEARN':
            tome_spells.append([delta_0, delta_1, delta_2, delta_3, tome_index, tax_count, action_id])

    my_space = 0

    for i in range(2):
        # inv_0: tier-0 ingredients in inventory
        # score: amount of rupees
        inv_0, inv_1, inv_2, inv_3, score = [int(j) for j in input().split()]

        if i == 0:
            invent = [inv_0, inv_1, inv_2, inv_3, score]
            my_space += (inv_0 + inv_1 + inv_2 + inv_3)

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    # in the first league: BREW <id> | WAIT; later: BREW <id> | CAST <id> [<times>] | LEARN <id> | REST | WAIT

    # try to brew
    keep_going = True

    best_potion_id = 0
    best_potion_price = 0
    for each in potions:
        if can_do_spell(each[:-2], invent[:-1]):
            potion_price = each[-2]
            if potion_price > best_potion_price:
                best_potion_id = each[-1]
                best_potion_price = potion_price

    if best_potion_id != 0:
        print("BREW " + str(best_potion_id))
        keep_going = False

    if keep_going:
        max_id = 0
        max_value = 0

        for each in tome_spells:
            worth_it_value = is_it_worth(each[:-1], invent[:-1])
            if worth_it_value and len(castable_lst) < 8:

                if worth_it_value > max_value:
                    max_value = worth_it_value
                    max_id = each[-1]

        if max_id != 0:
            print("LEARN " + str(max_id))
            keep_going = False
            if start_count:
                value += 1
        else:
            start_count = True

    # cast
    if keep_going:
        closest_potion = []
        highest_value = 0
        for pot in find_smallest_difference(potions, invent[:-1]):
            if pot[-2] > highest_value:
                closest_potion = pot
                highest_value = pot[-2]
        sys.stderr.write(str(closest_potion[-1]))
        # closest_potion = find_smallest_difference(potions, invent[:-1])

    """
    if keep_going: 
        max_spell_value = -10000
        max_spell_id = 0

        for each in spell:
            if can_do_spell(each[:-1], invent[:-1]):
                #if good_spell(each[:-1], invent[:-1]):
                    if goes_towards(each[:-1], closest_potion, invent[:-1]):

                        if sum(each[:-1]) > max_spell_value:
                            max_spell_value = sum(each[:-1])
                            max_spell_id = each[-1]

        if max_spell_id != 0:
            sys.stderr.write('hii')    
            print("CAST " + str(max_spell_id))
            keep_going = False

    """
    # without checking for go_towards

    if keep_going:
        max_spell_value = -10000
        max_spell_id = 0

        for each in spell:
            if can_do_spell(each[:-1], invent[:-1]):
                # if good_spell(each[:-1], invent[:-1]):
                if check_sabotage(each[:-1], closest_potion, invent[:-1]) >= 0:
                    sys.stderr.write('  ' + str(check_sabotage(each[:-1], closest_potion, invent[:-1])) + '  ')

                    if check_sabotage(each[:-1], closest_potion, invent[:-1]) > max_spell_value:
                        if check_sabotage(each[:-1], closest_potion, invent[:-1]) == 0:
                            # also check if it's "good move"
                            if good_spell(each[:-1], invent[:-1]):
                                sys.stderr.write('hiiii')
                                max_spell_value = check_sabotage(each[:-1], closest_potion, invent[:-1])
                                max_spell_id = each[-1]
                        else:
                            max_spell_value = check_sabotage(each[:-1], closest_potion, invent[:-1])
                            max_spell_id = each[-1]

                    """if sum(each[:-1]) > max_spell_value:
                        max_spell_value = sum(each[:-1])
                        max_spell_id = each[-1]
                    """

        if max_spell_id != 0:
            print("CAST " + str(max_spell_id))
            keep_going = False

    """
    if keep_going: 
        max_spell_value = -10000
        max_spell_id = 0

        for each in spell:
            if can_do_spell(each[:-1], invent[:-1]):
                if good_spell(each[:-1], invent[:-1]):
                    if sum(each[:-1]) > max_spell_value:
                        max_spell_value = sum(each[:-1])
                        max_spell_id = each[-1]

        if max_spell_id != 0:    
            print("CAST " + str(max_spell_id))
            keep_going = False


    if keep_going:
        for each in spell:
            if can_do_spell(each[:-1], invent[:-1]):
                print("CAST " + str(each[-1]))
                keep_going = False
                break
    """

    if keep_going:
        if not all(k == 1 for k in castable_lst):
            print("REST")
        else:
            print("LEARN " + str(tome_spells[0][-1]))







