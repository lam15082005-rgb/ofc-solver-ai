#include <numeric>
#include "LookupTableBuilder.h"
#include "MixedRadixNumber.h"
#include "Parallel.h"


namespace core
{
    const Int ZERO_CODE_COUNT = 1;
    const Int JOKER_CODE_COUNT = 1;
    const Int CARD_CODE_COUNT = TOTAL_COMBINATION_CARDS;
    const Int RANK_CODE_COUNT = MAX_RANK_COUNT + ZERO_CODE_COUNT + JOKER_CODE_COUNT;
    const Int SUIT_CODE_COUNT = MAX_SUIT_COUNT + ZERO_CODE_COUNT + JOKER_CODE_COUNT;
    const Int RANK_TETRADE_INDEX = 1;
    const Int SUIT_TETRADE_INDEX = 0;

    const std::string LOOKUP_TABLE_FILE_NAME_FORMAT = "%d-ranks-%d-duplicate-suits-with-jokers.dat";


    inline TinyInt make_bit(TinyInt value)
    {
        return TinyInt(1) << value;
    }

    std::string get_table_file_name(Int rank_count, Int suit_count)
    {
        return str(
            boost::format(LOOKUP_TABLE_FILE_NAME_FORMAT)
            % rank_count
            % suit_count
        );
    }


    LookupTableBuilder::LookupTableBuilder(std::shared_ptr<Context> context)
        : m_context(std::move(context))
    {
    }

    std::vector<BigInt> LookupTableBuilder::build()
    {
        auto result = std::vector<BigInt>();

        auto strengths = build_strengths();

        Int level_count = TOTAL_COMBINATION_CARDS;
        Int offset = m_context->UNIQUE_CARD_COUNT;
        auto codes = make_codes(0);
        auto refined_codes = std::vector<BigInt>();
        std::vector<std::vector<BigInt>> levels(level_count);
        for (Int card_count = 0; card_count < level_count; card_count++) {
            auto& level = levels[card_count];

            Int code_count = static_cast<Int>(codes.size());
            Int next_card_count = card_count + 1;
            Int node_size = get_node_size(card_count);

            offset += static_cast<Int>(code_count);

            level.resize(code_count);

            if (card_count > 0) {
                // assign hand strengths to cells preceding next node
                Combination combination = reserve<Card>(card_count);
                Int table_index = card_count - 1;
                Int node_count = code_count / node_size;
                for (Int node_index = 0; node_index < node_count; node_index++) {
                    set_combination(combination, refined_codes[node_index], card_count);
                    Int joker_count = count_jokers(combination);
                    Int combination_index = n_choose_k_max_c_index(
                        m_context->CARD_COUNT,
                        combination.begin(),
                        combination.end() - joker_count,
                        MAX_DUPLICATE_COUNT
                    );

                    Int index = (node_index + 1) * node_size - 1;
                    level[index] = strengths[table_index][joker_count][combination_index];
                }
            }

            if (card_count < TOTAL_COMBINATION_CARDS) {
                Int next_node_size = get_node_size(next_card_count);

                refined_codes = refine_codes(codes);

                parallelize(
                    code_count,
                    [&](const ThreadRange<Int>& t) {
                        Combination combination = reserve<Card>(next_card_count);

                        for (Int code_index = t.begin; code_index < t.end; code_index++) {
                            BigInt code = codes[code_index];
                            if (code > 0) {
                                auto it = std::lower_bound(refined_codes.begin(), refined_codes.end(), code);
                                Int refined_code_index = static_cast<Int>(std::distance(refined_codes.begin(), it));

                                if (next_card_count < level_count) {
                                    level[code_index] = offset + next_node_size * refined_code_index;
                                }
                                else {
                                    // assign hand strengths instead of next level addresses
                                    set_combination(combination, refined_codes[refined_code_index], next_card_count);
                                    Int joker_count = count_jokers(combination);
                                    Int combination_index = n_choose_k_max_c_index(
                                        m_context->CARD_COUNT,
                                        combination.begin(),
                                        combination.end() - joker_count,
                                        MAX_DUPLICATE_COUNT
                                    );

                                    level[code_index] = strengths.back()[joker_count][combination_index];
                                }
                            }
                        }
                    },
                    MAX_CPU_UTILIZATION
                );
            }

            if (next_card_count < level_count) {
                codes = make_next_level_codes(refined_codes, next_card_count);
            }
        }

        result.resize(offset);

        auto it = result.begin() + m_context->UNIQUE_CARD_COUNT;
        std::fill(result.begin(), it, 0);
        for (Int level_index = 0; level_index < level_count; level_index++) {
            auto& level = levels[level_index];

            std::copy(level.begin(), level.end(), it);

            it += level.size();
        }

        return result;
    }

    std::vector<std::vector<std::vector<BigInt>>> LookupTableBuilder::build_strengths()
    {
        std::vector<std::vector<std::vector<BigInt>>> result(TOTAL_COMBINATION_CARDS);

        for (Int index = 0; index < TOTAL_COMBINATION_CARDS; index++) {
            Int card_count = index + 1;

            result[index].resize(card_count + 1);
            for (Int joker_count = 0; joker_count <= card_count; joker_count++) {
                Int regular_card_count = card_count - joker_count;
                Int combination_count = n_choose_k_max_c(m_context->CARD_COUNT, regular_card_count, MAX_DUPLICATE_COUNT);

                result[index][joker_count].resize(combination_count, 0);
                parallelize(
                    combination_count,
                    [&](ThreadRange<Int>& t) {
                        Permutation permutation = std::vector<Card>(card_count);
                        CombinationBreakdown breakdown = CombinationBreakdown(m_context);

                        for (Int combination_index = t.begin; combination_index < t.end; combination_index++) {
                            n_choose_k_max_c_enumerate(
                                m_context->CARD_COUNT,
                                regular_card_count,
                                MAX_DUPLICATE_COUNT,
                                combination_index,
                                [&](Int element_index, Int element_value) {
                                    permutation[element_index] = static_cast<TinyInt>(element_value);
                                }
                            );

                            if (regular_card_count <= 1) {
                                TinyInt combination_type;
                                if (card_count == 5) {
                                    combination_type = COMBINATION_TYPE_FIVE_OF_A_KIND;
                                }
                                else if (card_count == 4) {
                                    combination_type = COMBINATION_TYPE_FOUR_OF_A_KIND;
                                }
                                else if (card_count == 3) {
                                    combination_type = COMBINATION_TYPE_THREE_OF_A_KIND;
                                }
                                else if (card_count == 2) {
                                    combination_type = COMBINATION_TYPE_PAIR;
                                }
                                else {
                                    combination_type = COMBINATION_TYPE_HIGH_CARD;
                                }

                                auto rank = regular_card_count == 1 ? m_context->get_rank(permutation[0]) : Rank(m_context->RANK_A);
                                auto suit = Suit(m_context->SUIT_HIGHEST);
                                auto joker_mask = Mask();
                                for (Int joker_index = 0; joker_index < joker_count; joker_index++) {
                                    Int card_index = regular_card_count + joker_index;
                                    permutation[card_index] = m_context->get_card(rank, suit);
                                    joker_mask.set_bit(card_index);
                                }

                                breakdown.initialize(permutation, joker_mask);

                                result[index][joker_count][combination_index] = make_strength(combination_type, breakdown);
                            }
                            else {
                                for (Int joker_index = 0; joker_index < joker_count; joker_index++) {
                                    permutation[regular_card_count + joker_index] = m_context->CARD_ANY;
                                }

                                result[index][joker_count][combination_index] = evaluate_strength(permutation, breakdown);
                            }
                        }
                    },
                    MAX_CPU_UTILIZATION
                );
            }
        }

        return result;
    }

    Int LookupTableBuilder::get_node_size(Int card_count)
    {
        Int result = 1;

        if (card_count < TOTAL_COMBINATION_CARDS) {
            result += m_context->UNIQUE_CARD_COUNT;
        }

        return result;
    }

    std::vector<BigInt> LookupTableBuilder::make_codes(BigInt code)
    {
        auto result = reserve<BigInt>(m_context->UNIQUE_CARD_COUNT);

        make_codes(result, code);

        return result;
    }

    void LookupTableBuilder::make_codes(std::vector<BigInt>& result, BigInt code)
    {
        for (Card card = 0; card < m_context->UNIQUE_CARD_COUNT; card++) {
            result.push_back(make_code(code, card));
        }
    }

    TinyInt LookupTableBuilder::count_jokers(const std::vector<Card>& cards)
    {
        return static_cast<TinyInt>(std::count_if(
            cards.begin(),
            cards.end(),
            [&](Card card) { return card >= m_context->CARD_ANY; }
        ));
    }

    std::vector<BigInt> LookupTableBuilder::make_next_level_codes(const std::vector<BigInt>& codes, Int card_count)
    {
        std::vector<BigInt> result;

        Int node_size = get_node_size(card_count);
        result.reserve(codes.size() * node_size);
        for (BigInt code : codes) {
            if (card_count < TOTAL_COMBINATION_CARDS) {
                make_codes(result, code);
            }

            if (card_count > 0) {
                result.push_back(0);
            }
        }

        return result;
    }

    std::vector<BigInt> LookupTableBuilder::refine_codes(const std::vector<BigInt>& codes)
    {
        auto result = reserve<BigInt>(codes.size());

        std::copy_if(codes.begin(), codes.end(), std::back_inserter(result), [](BigInt code) { return code > 0; });

        std::sort(result.begin(), result.end());

        auto it = std::unique(result.begin(), result.end());
        result.erase(it, result.end());

        return result;
    }

    BigInt LookupTableBuilder::make_strength(Int combination_type, const CombinationBreakdown& breakdown)
    {
        BigInt result = 0;

        bool is_top_hand_toak = breakdown.m_cards.size() == OFC_TOP_HAND_SIZE && combination_type == COMBINATION_TYPE_THREE_OF_A_KIND;

        // [t][rrrrr][sssss][n] - combination type, ranks, suits, non jokers
        // NOTE: order of ranks in rrrrr and suits in sssss will not match
        Int type_position = TOTAL_COMBINATION_CARDS * TETRADES_PER_BYTE + 1;
        Int rank_position = type_position - 1;
        Int suit_position = rank_position - TOTAL_COMBINATION_CARDS;
        Int non_joker_count_position = 0;

        if (is_top_hand_toak) {
            // [t][rrrrr][n][sssss]
            suit_position--;
            non_joker_count_position += TOTAL_COMBINATION_CARDS;
        }

        result = set_tetrade(result, type_position, combination_type);

        for (auto& rank_breakdown : breakdown.m_rank_breakdowns) {
            auto rank_code = encode(rank_breakdown.m_rank);

            auto count = rank_breakdown.get_count();

            for (Int i = 0; i < count; i++) {
                result = set_tetrade(result, rank_position--, rank_code);
            }
        }

        Int total_count = 0;
        for (Int n = 1; n <= TOTAL_COMBINATION_CARDS; n++) {
            for (auto& rank_breakdown : breakdown.m_rank_breakdowns) {
                Int count = rank_breakdown.get_count();
                if (count == n) {
                    for (auto& suit : rank_breakdown.m_suits) {
                        auto suit_code = encode(suit);

                        result = set_tetrade(result, suit_position--, suit_code);
                    }

                    total_count += count;

                    if (total_count == TOTAL_COMBINATION_CARDS) {
                        break;
                    }
                }

                if (count == 0) {
                    break;
                }
            }
        }

        TinyInt non_joker_count = static_cast<TinyInt>(breakdown.m_cards.size() - breakdown.m_joker_count);
        result = set_tetrade(result, non_joker_count_position, non_joker_count);

        return result;
    }


    TinyInt LookupTableBuilder::decode(TinyInt code)
    {
        return code - 1;
    }

    TinyInt LookupTableBuilder::encode(TinyInt value)
    {
        return value + 1;
    }

    BigInt LookupTableBuilder::evaluate_strength(const std::vector<Card>& cards)
    {
        auto breakdown = CombinationBreakdown(m_context);

        return evaluate_strength(cards, breakdown);
    }

    BigInt LookupTableBuilder::evaluate_strength(const std::vector<Card>& cards, CombinationBreakdown& breakdown)
    {
        BigInt result = 0;

        auto combination = reserve<Card>(cards.size());
        Mask joker_mask = 0;
        for (Int card_index = 0; card_index < cards.size(); card_index++) {
            auto card = cards[card_index];

            combination.push_back(card);

            if (card == m_context->CARD_ANY) {
                joker_mask.set_bit(card_index);
            }
        }

        for (auto iteration = MixedRadixNumber(make_bases(cards)); iteration.m_value < iteration.m_count; iteration++) {
            for (Int card_index = 0; card_index < cards.size(); card_index++) {
                if (iteration.m_bases[card_index] == m_context->CARD_COUNT) {
                    combination[card_index] = static_cast<TinyInt>(iteration.m_digits[card_index]);
                }
            }

            breakdown.initialize(combination, joker_mask);

            BigInt strength = evaluate_strength_internal(breakdown);
            Int combination_type = get_combination_type(strength);
            if (combination_type == COMBINATION_TYPE_PAIR_FLUSH || combination_type == COMBINATION_TYPE_TWO_PAIR_FLUSH) {
                if (breakdown.m_have_joker_duplicates) {
                    // jokers are not allowed to make paired flushes
                    continue;
                }
            }

            if (strength > result) {
                result = strength;
            }
        }

        return result;
    }

    BigInt LookupTableBuilder::evaluate_strength_internal(const CombinationBreakdown& breakdown)
    {
        Int prime_product = m_context->get_prime_product(breakdown.m_cards);

        auto& ranks = breakdown.m_rank_breakdowns;
        auto& suits = breakdown.m_suit_counts;

        bool is_five_of_a_kind = ranks[0].get_count() == TOTAL_COMBINATION_CARDS;
        bool is_four_of_a_kind = ranks[0].get_count() == 4;
        bool is_full_house = ranks[0].get_count() == 3 && ranks[1].get_count() == 2;
        bool is_two_pair_flush = ranks[0].get_count() == 2 && ranks[1].get_count() == 2 && suits[0].m_count == TOTAL_COMBINATION_CARDS;
        bool is_pair_flush = ranks[0].get_count() == 2 && suits[0].m_count == TOTAL_COMBINATION_CARDS;
        bool is_flush = suits[0].m_count == TOTAL_COMBINATION_CARDS;
        bool is_straight = std::find(m_context->STRAIGHT_PRODUCTS.begin(), m_context->STRAIGHT_PRODUCTS.end(), prime_product) != m_context->STRAIGHT_PRODUCTS.end();
        bool is_three_of_a_kind = ranks[0].get_count() == 3 && ranks[1].get_count() <= 1;
        bool is_two_pairs = ranks[0].get_count() == 2 && ranks[1].get_count() == 2;
        bool is_pair = ranks[0].get_count() == 2 && ranks[1].get_count() <= 1;

        TinyInt type;

        if (is_five_of_a_kind)
            type = COMBINATION_TYPE_FIVE_OF_A_KIND;
        else if (is_flush && is_straight)
            type = COMBINATION_TYPE_STRAIGHT_FLUSH;
        else if (is_four_of_a_kind)
            type = COMBINATION_TYPE_FOUR_OF_A_KIND;
        else if (is_full_house)
            type = COMBINATION_TYPE_FULL_HOUSE;
        else if (is_two_pair_flush)
            type = COMBINATION_TYPE_TWO_PAIR_FLUSH;
        else if (is_pair_flush)
            type = COMBINATION_TYPE_PAIR_FLUSH;
        else if (is_flush)
            type = COMBINATION_TYPE_FLUSH;
        else if (is_straight)
            type = COMBINATION_TYPE_STRAIGHT;
        else if (is_three_of_a_kind)
            type = COMBINATION_TYPE_THREE_OF_A_KIND;
        else if (is_two_pairs)
            type = COMBINATION_TYPE_TWO_PAIRS;
        else if (is_pair)
            type = COMBINATION_TYPE_PAIR;
        else
            type = COMBINATION_TYPE_HIGH_CARD;

        return make_strength(type, breakdown);
    }

    std::string LookupTableBuilder::get_file_name()
    {
        return get_table_file_name(m_context->RANK_COUNT, m_context->SUIT_COUNT);
    }

    std::vector<Int> LookupTableBuilder::make_bases(const std::vector<Card>& cards)
    {
        auto result = reserve<Int>(cards.size());

        for (auto card : cards) {
            auto base = card < m_context->CARD_ANY ? 1 : m_context->CARD_COUNT;
            result.push_back(base);
        }

        return result;
    }

    BigInt LookupTableBuilder::make_code(BigInt code, Card card)
    {
        BigInt result = 0;

        TinyInt card_codes[CARD_CODE_COUNT] = {};
        TinyInt rank_codes[CARD_CODE_COUNT] = {};
        TinyInt suit_codes[CARD_CODE_COUNT] = {};
        TinyInt rank_counts[RANK_CODE_COUNT] = {};
        TinyInt suit_counts[SUIT_CODE_COUNT] = {};
        TinyInt card_count = 0;

        auto add_card = [&](Int c) {
            auto r = get_tetrade(c, RANK_TETRADE_INDEX);
            auto s = get_tetrade(c, SUIT_TETRADE_INDEX);

            rank_codes[card_count] = r;
            suit_codes[card_count] = s;

            rank_counts[r]++;
            suit_counts[s]++;

            card_count++;
        };

        bool is_regular_card = card < m_context->CARD_ANY;

        Int rank = is_regular_card ? make_rank_value(card, m_context->SUIT_COUNT) : m_context->RANK_ANY;
        Int suit = is_regular_card ? make_suit_value(card, m_context->SUIT_COUNT) : m_context->SUIT_ANY;

        Int rank_code = encode(rank);
        Int suit_code = encode(suit);
        Int card_code = concatenate_tetrades(rank_code, suit_code);

        Int duplicate_count = 0;
        add_card(card_code);
        for (Int byte_index = 0; byte_index < sizeof(code); byte_index++) {
            Int c = get_byte(code, byte_index);
            if (is_regular_card && c == card_code) {
                duplicate_count++;
                if (duplicate_count > 1) {
                    // more than one duplicate is not allowed
                    return 0;
                }
            }

            if (c == 0) {
                break;
            }

            add_card(c);
        }

        // this block zeros out any suits that can no longer make flushes
        Int any_rank_code = encode(m_context->RANK_ANY);
        Int any_suit_code = encode(m_context->SUIT_ANY);
        //Int remaining_card_count = TOTAL_COMBINATION_CARDS - card_count;
        //for (TinyInt suit = 0; suit < m_context->SUIT_COUNT; suit++) {
        //    Int suit_code = encode(suit);
        //    auto& suit_count = suit_counts[suit_code];
        //    if (suit_count + remaining_card_count + suit_counts[any_suit_code] < TOTAL_COMBINATION_CARDS) {
        //        // add the suit count to unspecified suit bucket and zero it out
        //        suit_counts[0] += suit_count;
        //        suit_count = 0;
        //    }
        //}

        // this block creates card codes taking new suit counts into account
        Mask suit_code_mask = 0;
        TinyInt generic_suit_counts[RANK_CODE_COUNT] = {};
        for (Int card_index = 0; card_index < card_count; card_index++) {
            auto& r = rank_codes[card_index];
            auto& s = suit_codes[card_index];

            if (r < any_rank_code) {
                // the suit is no longer relevant if its count was zeroed out above
                if (suit_counts[s] == 0) {
                    s = 0;
                }

                if (s == 0) {
                    generic_suit_counts[r]++;
                }
                else {
                    suit_code_mask |= make_bit(s);
                }
            }

            card_codes[card_index] = concatenate_tetrades(r, s);
        }

        auto fixed_suit_count = bit_count(suit_code_mask);
        for (Int card_index = 0; card_index < card_count; card_index++) {
            auto r = rank_codes[card_index];
            if (r == any_rank_code) {
                // it is allowed to have more than SUIT_COUNT jokers
                continue;
            }

            if (generic_suit_counts[r] + fixed_suit_count > m_context->SUIT_COUNT) {
                return 0;
            }
        }

        std::sort(card_codes, card_codes + card_count);

        for (Int card_index = 0; card_index < card_count; card_index++) {
            result = set_byte(result, card_index, card_codes[card_index]);
        }

        return result;
    }

    void LookupTableBuilder::set_combination(Combination& result, BigInt code, Int card_count)
    {
        result.clear();

        TinyInt rank_codes[CARD_CODE_COUNT] = {};
        TinyInt suit_codes[CARD_CODE_COUNT] = {};

        TinyInt rank_code_counts[RANK_CODE_COUNT] = {};

        TinyInt fixed_suit_mask = 0;
        TinyInt suit_masks[RANK_CODE_COUNT] = {};
        TinyInt suit_counts[MAX_SUIT_COUNT] = {};
        Int remaining_card_count = TOTAL_COMBINATION_CARDS - card_count;

        TinyInt any_rank_code = encode(m_context->RANK_ANY);
        TinyInt any_suit_code = encode(m_context->SUIT_ANY);

        Int joker_count = 0;
        for (Int byte_index = 0; byte_index < card_count; byte_index++) {
            auto card_code = get_byte(code, byte_index);

            auto rank_code = get_tetrade(card_code, RANK_TETRADE_INDEX);
            auto suit_code = get_tetrade(card_code, SUIT_TETRADE_INDEX);

            if (rank_code == any_rank_code) {
                joker_count++;
            }

            if (0 < suit_code && suit_code < any_suit_code) {
                auto suit = decode(suit_code);
                fixed_suit_mask |= make_bit(suit);
            }

            rank_code_counts[rank_code]++;

            rank_codes[byte_index] = rank_code;
            suit_codes[byte_index] = suit_code;
        }

        // max_irrelevant_suit_count is the number of suits that can no longer make flushes
        Int max_irrelevant_suit_count;
        if (card_count - joker_count <= 1)
        {
            // we're free to have as many suits as we want since we have too many jokers
            max_irrelevant_suit_count = TOTAL_COMBINATION_CARDS;
        }
        else {
            max_irrelevant_suit_count = TOTAL_COMBINATION_CARDS - 1 - joker_count;
        }
        Int max_suit_count = max_irrelevant_suit_count - remaining_card_count;

        for (Int iteration_index = 0; iteration_index < card_count; iteration_index++) {
            auto it = std::max_element(std::begin(rank_code_counts), std::end(rank_code_counts));
            if (*it == 0) {
                break;
            }

            auto rank_code = static_cast<TinyInt>(std::distance(rank_code_counts, it));
            if (rank_code == any_rank_code) {
                for (Int card_index = 0; card_index < card_count; card_index++) {
                    if (rank_codes[card_index] == rank_code) {
                        result.add(m_context->CARD_ANY);
                    }
                }
            }
            else {
                Rank rank = decode(rank_code);
                Suit suit;

                for (Int card_index = 0; card_index < card_count; card_index++) {
                    if (rank_codes[card_index] == rank_code) {
                        auto suit_code = suit_codes[card_index];
                        if (suit_code > 0) {
                            suit = decode(suit_code);
                        }
                        else {
                            auto suit_mask = fixed_suit_mask | suit_masks[rank];
                            for (suit = 0; suit < m_context->SUIT_COUNT; suit++) {
                                if ((suit_mask & make_bit(suit)) == 0) {
                                    if (suit_counts[suit] < max_suit_count) {
                                        suit_counts[suit]++;
                                        break;
                                    }
                                }
                            }
                        }
                        suit_masks[rank] |= make_bit(suit);

                        auto card = m_context->get_card(rank, suit);

                        result.add(card);
                    }
                }
            }

            *it = 0;
        }
    }
}
