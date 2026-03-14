#pragma once

#include "Context.h"
#include "CombinationBreakdown.h"


namespace core
{
    class LookupTableBuilder
    {
    public:
        std::shared_ptr<Context> m_context;

        LookupTableBuilder(std::shared_ptr<Context> context);

        std::vector<BigInt> build();
        std::vector<std::vector<std::vector<BigInt>>> build_strengths();
        BigInt evaluate_strength(const std::vector<Card>& cards);
        BigInt evaluate_strength(const std::vector<Card>& cards, CombinationBreakdown& breakdown);
        std::string get_file_name();
        Int get_node_size(Int card_count);
        BigInt make_code(BigInt code, Card card);
        std::vector<BigInt> make_codes(BigInt code);
        void make_codes(std::vector<BigInt>& result, BigInt code);
        void set_combination(Combination& result, BigInt code, Int card_count);
        TinyInt count_jokers(const std::vector<Card>& cards);
        std::vector<BigInt> make_next_level_codes(const std::vector<BigInt>& codes, Int card_count);
        std::vector<BigInt> refine_codes(const std::vector<BigInt>& codes);
        BigInt make_strength(Int combination_type, const CombinationBreakdown& breakdown);
        TinyInt decode(TinyInt code);
        TinyInt encode(TinyInt value);
        BigInt evaluate_strength_internal(const CombinationBreakdown& breakdown);
        std::vector<Int> make_bases(const std::vector<Card>& cards);
    };
}
