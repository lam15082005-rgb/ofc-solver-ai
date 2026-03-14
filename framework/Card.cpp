#include "Card.h"


namespace core
{
    Mask core::Card::to_mask() const
    {
        return Mask(BigInt(1) << m_value);
    }
}
