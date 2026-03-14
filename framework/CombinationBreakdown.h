#pragma once

#include <memory>
#include <vector>
#include "Context.h"
#include "Mask.h"
#include "Types.h"


namespace core
{
    class SuitCount
    {
    public:
        TinyInt m_suit;
        TinyInt m_count;

        SuitCount();
        SuitCount(TinyInt suit, TinyInt count);
    };


    class RankBreakdown
    {
    public:
        TinyInt m_rank;
        std::vector<TinyInt> m_suits;

        Int get_count() const;
    };


    class CombinationBreakdown
    {
    public:
        std::shared_ptr<Context> m_context;
        std::vector<TinyInt> m_cards;
        std::vector<RankBreakdown> m_rank_breakdowns;
        std::vector<SuitCount> m_suit_counts;
        TinyInt m_duplicate_count;
        bool m_have_joker_duplicates;
        TinyInt m_joker_count;

        CombinationBreakdown();
        CombinationBreakdown(std::shared_ptr<Context> context);
        CombinationBreakdown(std::shared_ptr<Context> context, const std::vector<Card>& cards, Mask joker_mask);

        void initialize(const std::vector<Card>& cards, Mask joker_mask);
    };
}
