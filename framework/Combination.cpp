#include "Combination.h"
#include "Common.h"


namespace core
{
    void Combination::add(Card card)
    {
        m_value.insert(std::upper_bound(m_value.begin(), m_value.end(), card), card);
    }

    void Combination::add(const std::vector<Card>& cards)
    {
        add(cards.begin(), cards.end());
    }

    Int Combination::to_index() const
    {
        Int result = 0;

        Int n = 0;
        for (Card card : m_value) {
            result += n_choose_k(card, ++n);
        }

        return result;
    }
}
