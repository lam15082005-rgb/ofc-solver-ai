#pragma once

#include "Types.h"


namespace core
{
    class AverageAggregator
    {
    public:
        double m_sum;
        BigInt m_count;

        AverageAggregator();

        AverageAggregator& operator=(const AverageAggregator& rhs);
        AverageAggregator& operator=(double value);
        AverageAggregator& operator+=(const AverageAggregator& rhs);
        AverageAggregator& operator+=(double value);
        operator double() const;

        void add(double value, BigInt count);
        void assign(double sum, BigInt count);
        double get_value() const;
        void reset();
    };
}
