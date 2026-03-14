#pragma once

#include <vector>
#include "Card.h"
#include "Collection.h"
#include "Types.h"


namespace core
{
    class Combination : public Collection
    {
    public:
        Combination() : Collection() {}
        Combination(std::size_t size) : Collection(size) {}
        Combination(std::vector<Card> cards) : Collection(std::move(cards)) { sort(); }

        template<typename Iter>
        Combination(Iter begin, Iter end) : Collection() { add(begin, end); }

        void add(Card card);
        void add(const std::vector<Card>& cards);
        void assign(const std::vector<Card>& cards) { m_value.assign(cards.begin(), cards.end()); sort(); };

        template<typename Iter>
        void add(Iter begin, Iter end)
        {
            reserve(size() + std::distance(begin, end));

            while (begin != end) {
                m_value.push_back(*begin);

                ++begin;
            }

            sort();
        }


        Int to_index() const;
    };
}
