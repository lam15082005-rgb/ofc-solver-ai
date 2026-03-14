#include "Constants.h"

#include "Common.h"


namespace core
{
    const std::vector<std::vector<std::vector<Int>>> OFC_ACTIONS = generate_ways_to_assign_balls_to_tight_boxes(OFC_HOLE_CARD_COUNT, OFC_HAND_SIZES);
    const Int OFC_ACTION_COUNT = static_cast<Int>(OFC_ACTIONS.size());
}
