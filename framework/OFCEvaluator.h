#pragma once

#include <functional>
#include <vector>
#include "Context.h"
#include "Evaluator.h"
#include "Types.h"


namespace core
{
    class OFCEvaluator
    {
    public:
        Int m_hand_count;
        std::shared_ptr<Context> m_context;
        std::shared_ptr<Evaluator> m_evaluator;
        std::vector<BigInt> m_strengths;

        OFCEvaluator();
        OFCEvaluator(std::shared_ptr<Context> context, Int hand_count);

        template<typename THand>
        std::vector<BigInt>& get_strengths_template(const std::vector<THand>& hands)
        {
            if (m_hand_count != hands.size()) {
                throw std::invalid_argument("Hand count mismatch");
            }

            for (Int hand_index = 0; hand_index < m_hand_count; hand_index++) {
                m_strengths[hand_index] = m_evaluator->get_strength(hands[hand_index]);
                if (hand_index > 0 && m_strengths[hand_index] < m_strengths[hand_index - 1]) {
                    std::fill(m_strengths.begin(), m_strengths.end(), 0);
                    break; // foul
                }
            }

            return m_strengths;
        }

        std::vector<BigInt>& get_strengths(const std::vector<std::vector<TinyInt>>& hands);
        std::vector<BigInt>& get_strengths(const std::vector<std::vector<Card>>& hands);
        std::vector<BigInt>& get_strengths(const std::vector<Combination>& hands);
    };
}
