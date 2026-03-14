#include <stdexcept>
#include "Permutation.h"


namespace core
{
    void Permutation::add(Card card)
    {
        m_value.push_back(card);
    }

    void Permutation::add(const std::vector<Card>& cards)
    {
        for (auto card : cards) {
            m_value.push_back(card);
        }
    }

    void Permutation::remove(Int count)
    {
        if (m_value.size() < count) {
            throw std::invalid_argument("Too many cards to remove");
        }

        m_value.resize(m_value.size() - count);
    }

}
