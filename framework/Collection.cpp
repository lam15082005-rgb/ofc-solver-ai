#include "Collection.h"


namespace core
{
    Mask Collection::to_mask() const
    {
        Mask result;

        for (const Card& card : m_value) {
            result |= card.to_mask();
        }

        return result;
    }
}
