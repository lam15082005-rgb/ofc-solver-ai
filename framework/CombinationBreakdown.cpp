#include "CombinationBreakdown.h"


namespace core
{

    SuitCount::SuitCount()
        : SuitCount(MAX_SUIT_COUNT, 0)
    {
    }

    SuitCount::SuitCount(TinyInt suit, TinyInt count)
        : m_suit(suit), m_count(count)
    {
    }


    Int RankBreakdown::get_count() const
    {
        return static_cast<Int>(m_suits.size());
    }


    CombinationBreakdown::CombinationBreakdown()
        : CombinationBreakdown(std::make_shared<Context>())
    {
    }

    CombinationBreakdown::CombinationBreakdown(std::shared_ptr<Context> context)
        : CombinationBreakdown(std::move(context), std::vector<Card>(), Mask())
    {
    }

    CombinationBreakdown::CombinationBreakdown(std::shared_ptr<Context> context, const std::vector<Card>& cards, Mask joker_mask)
        : m_context(std::move(context)), m_duplicate_count(0), m_have_joker_duplicates(false), m_joker_count(0)
    {
        m_cards.reserve(TOTAL_COMBINATION_CARDS);
        m_rank_breakdowns.resize(m_context->RANK_COUNT);
        for (auto& rank_breakdown : m_rank_breakdowns) {
            rank_breakdown.m_suits.reserve(TOTAL_COMBINATION_CARDS);
        }
        m_suit_counts.resize(m_context->SUIT_COUNT);

        initialize(cards, joker_mask);
    }

    void CombinationBreakdown::initialize(const std::vector<Card>& cards, Mask joker_mask)
    {
        m_cards.clear();
        for (TinyInt rank = 0; rank < m_context->RANK_COUNT; rank++) {
            auto& rank_breakdown = m_rank_breakdowns[rank];

            rank_breakdown.m_rank = rank;
            rank_breakdown.m_suits.clear();
        }
        for (TinyInt suit = 0; suit < m_context->SUIT_COUNT; suit++) {
            auto& suit_count = m_suit_counts[suit];

            suit_count.m_suit = suit;
            suit_count.m_count = 0;
        }

        m_duplicate_count = 0;
        m_have_joker_duplicates = false;
        m_joker_count = 0;
        if (cards.size() == 0) {
            return;
        }

        m_joker_count = bit_count(joker_mask);

        for (Int i = 0; i < cards.size(); i++) {
            m_cards.push_back(cards[i]);

            Int duplicate_count = 0;
            for (Int j = i + 1; j < cards.size(); j++) {
                if (cards[i] == cards[j]) {
                    duplicate_count++;

                    if (joker_mask.test_bit(i) || joker_mask.test_bit(j)) {
                        m_have_joker_duplicates = true;
                    }
                }
            }

            if (duplicate_count > m_duplicate_count) {
                m_duplicate_count = duplicate_count;
            }

            auto rank = m_context->get_rank(cards[i]);
            auto suit = m_context->get_suit(cards[i]);

            auto& rank_breakdown = m_rank_breakdowns[rank];
            rank_breakdown.m_suits.push_back(suit);

            auto& suit_count = m_suit_counts[suit];
            suit_count.m_count++;
        }

        std::sort(
            m_rank_breakdowns.begin(),
            m_rank_breakdowns.end(),
            [](const RankBreakdown& a, const RankBreakdown& b) {
                Int count_a = a.get_count();
                Int count_b = b.get_count();

                if (count_a == count_b) {
                    return a.m_rank > b.m_rank;
                }

                return count_a > count_b;
            }
        );

        for (auto& rank_breakdown : m_rank_breakdowns) {
            std::sort(
                rank_breakdown.m_suits.begin(),
                rank_breakdown.m_suits.end(),
                [](TinyInt a, TinyInt b) {
                    return a > b;
                }
            );
        }

        std::sort(
            m_suit_counts.begin(),
            m_suit_counts.end(),
            [](const SuitCount& a, const SuitCount& b) {
                if (a.m_count == b.m_count) {
                    return a.m_suit > b.m_suit;
                }

                return a.m_count > b.m_count;
            }
        );
    }
}
