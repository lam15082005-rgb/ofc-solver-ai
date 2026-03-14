#include "ActionDistribution.h"

#include <numeric>
#include "Constants.h"


namespace core
{
    ActionDistribution::ActionDistribution()
        : m_partial_sums(OFC_ACTION_COUNT)
    {
    }

    void ActionDistribution::update(const std::vector<double>& distribution)
    {
        std::partial_sum(
            distribution.begin(),
            distribution.end(),
            m_partial_sums.begin()
        );
    }

    Int ActionDistribution::get_action_index(double random_value)
    {
        auto it = std::lower_bound(m_partial_sums.begin(), m_partial_sums.end(), random_value);

        return static_cast<Int>(std::distance(m_partial_sums.begin(), it));
    }
}
