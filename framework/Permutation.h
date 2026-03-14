#pragma once

#include <vector>

#include "Card.h"
#include "Collection.h"


namespace core
{
    class Permutation : public Collection
    {
    public:
        using Collection::Collection;

        void add(Card card);
        void add(const std::vector<Card>& cards);
        void assign(const std::vector<Card>& cards) { m_value.assign(cards.begin(), cards.end()); };
        void remove(Int count);
    };
}
