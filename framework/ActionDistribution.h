#pragma once

#include <vector>
#include "Types.h"


namespace core
{
    class ActionDistribution
    {
    public:
        std::vector<double> m_partial_sums;

        ActionDistribution();

        void update(const std::vector<double>& distribution);
        Int get_action_index(double random_value);
    };
}
