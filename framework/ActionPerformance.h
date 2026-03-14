#pragma once

#include <vector>
#include "AverageAggregator.h"
#include "Types.h"


namespace core
{
    class ActionPerformance
    {
    public:
        AverageAggregator m_ev;

        ActionPerformance();

        ActionPerformance& operator+=(const ActionPerformance& rhs);
        void reset();
    };
}
