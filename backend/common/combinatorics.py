from itertools import combinations
from math import comb


def comb_index(combination):
    result = 0

    n = 0
    for item in combination:
        n += 1
        result += comb(item, n)

    return result


def sorted_combinations(iterable, r):
    return sorted(combinations(iterable, r), key=comb_index)


def count_ways_to_assign_balls_to_tight_boxes(num_balls, box_sizes):
    if num_balls < sum(box_sizes):
        raise ValueError("Total number of balls must be greater than or equal to sum of box sizes")

    result = 1

    num_remaining_balls = num_balls
    for box_size in box_sizes:
        result *= comb(num_remaining_balls, box_size)
        num_remaining_balls -= box_size

    return result


def generate_ways_to_assign_balls_to_tight_boxes(num_balls, box_sizes, flatten=False):
    """
        Generate all possible ways to assign balls to tight boxes
    """
    if num_balls < sum(box_sizes):
        raise ValueError("Total number of balls must be greater than or equal to sum of box sizes")

    def recursive(balls, boxes, way):
        for combination in sorted_combinations(balls, boxes[0]):
            way.append(combination)
            if len(boxes) == 1:
                if flatten:
                    yield tuple([ball for box in way for ball in box])
                else:
                    yield tuple(way)
            else:
                remaining_balls = balls - set(combination)
                yield from recursive(remaining_balls, boxes[1:], way)
            way.remove(combination)

    yield from recursive(set(range(num_balls)), box_sizes, [])
