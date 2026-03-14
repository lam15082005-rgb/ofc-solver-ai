#include "Evaluator.h"
#include "LookupTableStore.h"


namespace core
{
    Evaluator::Evaluator()
        : Evaluator(std::make_shared<Context>())
    {
    }

    Evaluator::Evaluator(std::shared_ptr<Context> context)
        : m_table(nullptr), m_context(std::move(context))
    {
        auto store = LookupTableStore::instance();
        auto table = store->get_table(m_context);

        m_table = table->data();
    }

    BigInt Evaluator::get_strength(const std::vector<TinyInt>& cards)
    {
        return get_strength_template(cards);
    }

    BigInt Evaluator::get_strength(const std::vector<Card>& cards)
    {
        return get_strength_template(cards);
    }
}
