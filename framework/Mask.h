#pragma once

#include "Object.h"
#include "Types.h"


namespace core
{
    class Mask : public Object<BigInt>
    {
    public:
        using Object::Object;

        Mask();

        void clear_bit(Int index) { m_value &= ~(BigInt(1) << index); }
        void set_bit(Int index) { m_value |= BigInt(1) << index; }
        void set_bits(Int count) { m_value |= bits(count, 1); }
        bool test_bit(Int index) { return m_value & (BigInt(1) << index); }

        Int to_index() const;

        static Mask bits(Int count, Int padding);
        static Mask bits(Int count) { return bits(count, 1); }
    };
}
