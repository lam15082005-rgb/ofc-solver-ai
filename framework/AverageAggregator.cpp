#include "AverageAggregator.h"


namespace core
{
    AverageAggregator::AverageAggregator()
        : m_sum(0), m_count(0)
    {
    }

    AverageAggregator& AverageAggregator::operator=(const AverageAggregator& rhs)
    {
        assign(rhs.m_sum, rhs.m_count);

        return *this;
    }

    AverageAggregator& AverageAggregator::operator=(double value)
    {
        assign(value, 1);

        return *this;
    }

    AverageAggregator& AverageAggregator::operator+=(const AverageAggregator& rhs)
    {
        add(rhs.m_sum, rhs.m_count);

        return *this;
    }

    AverageAggregator& AverageAggregator::operator+=(double value)
    {
        add(value, 1);

        return *this;
    }

    AverageAggregator::operator double() const
    {
        return get_value();
    }

    void AverageAggregator::add(double value, BigInt count)
    {
        m_sum += value;
        m_count += count;
    }

    void AverageAggregator::assign(double sum, BigInt count)
    {
        m_sum = sum;
        m_count = count;
    }

    double AverageAggregator::get_value() const
    {
        return m_count > 0 ? m_sum / m_count : 0;
    }

    void AverageAggregator::reset()
    {
        m_sum = 0;
        m_count = 0;
    }
}
