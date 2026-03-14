#pragma once

#include <vector>
#include "Card.h"
#include "Context.h"
#include "Types.h"


namespace core
{
    class Evaluator
    {
    public:
        std::shared_ptr<Context> m_context;
        BigInt* m_table;

        Evaluator();
        Evaluator(std::shared_ptr<Context> context);

        template<typename TCard>
        BigInt get_strength_template(const std::vector<TCard>& cards)
        {
            BigInt result = m_context->UNIQUE_CARD_COUNT;

            for (auto card : cards) {
                result = m_table[result + card];
            }

            if (cards.size() < TOTAL_COMBINATION_CARDS) {
                result = m_table[result + m_context->UNIQUE_CARD_COUNT];
            }

            return result;
        }

        BigInt get_strength(const std::vector<TinyInt>& cards);
        BigInt get_strength(const std::vector<Card>& cards);
    };
}
