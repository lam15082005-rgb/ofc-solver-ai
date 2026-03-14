#include "Common.h"
#include "Mask.h"


namespace core
{
    Mask::Mask()
        : Object(0)
    {
    }

    Int Mask::to_index() const
    {
        Int result = 0;

        Int n = 0;
        for (TinyInt i : enumerate_bits(m_value)) {
            result += n_choose_k(i, ++n);
        }

        return result;
    }

    Mask Mask::bits(Int count, Int padding)
    {
        Mask result;

        for (Int index = 0; index < count; index++) {
            result.set_bit(index * padding);
        }

        return result;
    }
}
