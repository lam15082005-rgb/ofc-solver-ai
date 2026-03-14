#include <functional>
#include <numeric>

#include "MixedRadixNumber.h"


namespace core
{
    MixedRadixNumber::MixedRadixNumber()
        : Object(0), m_count(0)
    {
    }

    MixedRadixNumber::MixedRadixNumber(std::vector<Int> bases)
        : MixedRadixNumber()
    {
        set_bases(std::move(bases));
    }

    MixedRadixNumber::MixedRadixNumber(BigInt value, std::vector<Int> bases)
        : MixedRadixNumber(std::move(bases))
    {
        set(value);
    }

    MixedRadixNumber& MixedRadixNumber::operator=(BigInt value)
    {
        set(value);

        return *this;
    }

    MixedRadixNumber& MixedRadixNumber::operator++()
    {
        increment();

        return *this;
    }

    BigInt MixedRadixNumber::operator++(int)
    {
        increment();

        return m_value;
    }

    void MixedRadixNumber::complement(Int index)
    {
        increment(index);

        Int digit_value = 1;
        for (Int digit_index = 0; digit_index < index; digit_index++) {
            m_value -= static_cast<BigInt>(m_digits[digit_index]) * digit_value;
            m_digits[digit_index] = 0;

            digit_value *= m_bases[digit_index];
        }
    }

    BigInt MixedRadixNumber::get_digit_value(Int index)
    {
        BigInt result = 1;

        for (Int digit_index = 0; digit_index < index; digit_index++) {
            result *= m_bases[digit_index];
        }

        return result;
    }

    Int MixedRadixNumber::increment(Int index)
    {
        m_value += get_digit_value(index);

        while (index < m_bases.size()) {
            m_digits[index]++;
            if (m_digits[index] < m_bases[index]) {
                break;
            }
            else {
                m_digits[index] = 0;
                index++;
            }
        }

        return index;
    }

    void MixedRadixNumber::set(BigInt value)
    {
        m_value = value;
        for (Int index = 0; index < m_bases.size(); index++) {
            Int base = m_bases[index];
            m_digits[index] = value % base;
            value /= base;
        }
    }

    void MixedRadixNumber::set_bases(std::vector<Int> bases)
    {
        m_bases = std::move(bases);

        set_bases();
    }

    void MixedRadixNumber::set_bases()
    {
        m_digits = std::vector<Int>(m_bases.size(), 0);
        m_value = 0;
        m_count = std::accumulate(m_bases.begin(), m_bases.end(), BigInt(1), std::multiplies<BigInt>());
    }
}
