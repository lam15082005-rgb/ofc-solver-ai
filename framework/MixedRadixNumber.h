#pragma once

#include <vector>

#include "Object.h"
#include "Types.h"


namespace core
{
    class MixedRadixNumber : public Object<BigInt>
    {
    public:
        BigInt m_count;
        std::vector<Int> m_bases;
        std::vector<Int> m_digits;

        MixedRadixNumber();
        MixedRadixNumber(std::vector<Int> bases);
        MixedRadixNumber(BigInt value, std::vector<Int> bases);

        MixedRadixNumber& operator=(BigInt value);
        MixedRadixNumber& operator++();
        BigInt operator++(int);

        void complement(Int index);
        BigInt get_digit_value(Int index);
        Int increment(Int index = 0);
        void set(BigInt value);
        void set_bases(std::vector<Int> bases);
        void set_bases();
    };
}
