#include "OFCEvaluator.h"


namespace core
{
    OFCEvaluator::OFCEvaluator()
        : OFCEvaluator(std::make_shared<Context>(), OFC_HAND_COUNT)
    {
    }

    OFCEvaluator::OFCEvaluator(std::shared_ptr<Context> context, Int hand_count)
        : m_hand_count(hand_count)
    {
        m_context = std::move(context);
        m_evaluator = std::make_shared<Evaluator>(m_context);
        m_strengths = std::vector<BigInt>(hand_count, 0);
    }

    std::vector<BigInt>& OFCEvaluator::get_strengths(const std::vector<std::vector<TinyInt>>& hands)
    {
        return get_strengths_template(hands);
    }

    std::vector<BigInt>& OFCEvaluator::get_strengths(const std::vector<std::vector<Card>>& hands)
    {
        return get_strengths_template(hands);
    }

    std::vector<BigInt>& OFCEvaluator::get_strengths(const std::vector<Combination>& hands)
    {
        return get_strengths_template(hands);
    }
}
