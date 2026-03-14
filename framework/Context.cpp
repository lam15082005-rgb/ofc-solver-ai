#include "boost/range/adaptor/reversed.hpp"
#include "Bit.h"
#include "Common.h"
#include "Context.h"


namespace core
{
    Context::Context()
        : Context(REGULAR_RANK_COUNT, REGULAR_SUIT_COUNT)
    {
    }

    Context::Context(TinyInt ranks, TinyInt suits)
    {
        construct(ranks, suits);
    }

    void Context::enumerate_cards(Int index, Int n, Int k, std::function<void(Int, Card)> callback) const
    {
        Int count = N_CHOOSE_K[n][k];
        if (index < count) {
            while (n > 0) {
                Int value = N_CHOOSE_K[n - 1][k];
                if (index >= value) {
                    index -= value;
                    --k;

                    callback(
                        static_cast<TinyInt>(k),
                        static_cast<TinyInt>(n - 1)
                    );
                }
                --n;
            }
        }
    }

    void Context::enumerate_cards(Mask mask, std::function<void(Int, Card)> callback) const
    {
        enumerate_bits(
            mask,
            [&](TinyInt index, TinyInt position) {
                callback(index, position);
            }
        );
    }

    Card Context::get_card(const Rank& rank, const Suit& suit) const
    {
        return Card(make_card_value(rank, suit, SUIT_COUNT));
    }

    void Context::set_combination(Combination& result, Int index, Int card_count) const
    {
        result.clear();
        enumerate_cards(
            index,
            CARD_COUNT,
            card_count,
            [&](Int index, Card card) {
                result.add(card);
            }
        );
    }

    Combination Context::get_combination(Int index, Int card_count) const
    {
        Combination result;

        set_combination(result, index, card_count);

        return result;
    }

    std::string Context::get_combination_string(Int index, Int card_count) const
    {
        return get_string(get_combination(index, card_count));
    }

    Int Context::get_index(Mask mask) const
    {
        Int result = 0;

        enumerate_cards(
            mask,
            [&](TinyInt index, Card card) {
                result += N_CHOOSE_K[card][++index];
            }
        );

        return result;
    }

    Permutation Context::get_permutation(Int index, Int card_count) const
    {
        Permutation permutation = std::vector<Card>(card_count);

        set_permutation(permutation, index, card_count);

        return permutation;
    }

    void Context::set_permutation(Permutation& permutation, Int index, Int card_count) const
    {
        enumerate_cards(
            index,
            CARD_COUNT,
            card_count,
            [&](Int index, Card card) {
                permutation[index] = card;
            }
        );
    }

    Rank Context::get_rank(const Card& card) const
    {
        if (card == CARD_ANY) {
            return Rank(RANK_ANY);
        }

        return Rank(make_rank_value(card, SUIT_COUNT));
    }

    Int Context::get_prime_product(Int rank_count, std::function<Rank(Int)> callback) const
    {
        Int result = 1;

        for (Int rank_index = 0; rank_index < rank_count; rank_index++) {
            auto rank = callback(rank_index);

            result *= PRIMES[rank];
        }

        return result;
    }

    Int Context::get_prime_product(const std::vector<Card>& cards) const
    {
        auto callback = [&](Int index) {
            return get_rank(cards[index]);
        };

        return get_prime_product(static_cast<Int>(cards.size()), callback);
    }

    Int Context::get_prime_product(const std::vector<TinyInt>& cards) const
    {
        auto callback = [&](Int index) {
            return get_rank(cards[index]);
        };

        return get_prime_product(static_cast<Int>(cards.size()), callback);
    }

    Int Context::get_prime_product(const std::vector<Rank>& ranks) const
    {
        auto callback = [&](Int index) {
            return ranks[index];
        };

        return get_prime_product(static_cast<Int>(ranks.size()), callback);
    }

    std::string Context::get_string(const Card& card) const
    {
        if (card == CARD_ANY) {
            return RANK_WILDCARD;
        }

        Rank rank = get_rank(card);
        Suit suit = get_suit(card);

        return std::string({ RankAlphabets[ALPHABET_ORIGINAL][rank], SuitAlphabets[ALPHABET_ORIGINAL][suit] });
    }

    std::string Context::get_string(const Combination& combination) const
    {
        std::string result;
        result.reserve(CARD_LENGTH * combination.size());

        for (const Card& card : combination.m_value | boost::adaptors::reversed) {
            result += get_string(card);
        }

        return result;
    }

    std::string Context::get_string(const Permutation& permutation) const
    {
        std::string result;
        result.reserve(CARD_LENGTH * permutation.size());

        for (auto card : permutation) {
            result += get_string(card);
        }

        return result;
    }

    std::string Context::get_string(const Rank& rank, Int alphabet) const
    {
        return std::string({ RankAlphabets[alphabet][rank] });
    }

    std::string Context::get_string(const Suit& suit, Int alphabet) const
    {
        return std::string({ SuitAlphabets[alphabet][suit] });
    }

    Suit Context::get_suit(const Card& card) const
    {
        if (card == CARD_ANY) {
            return Suit(SUIT_ANY);
        }

        return Suit(make_suit_value(card, SUIT_COUNT));
    }

    void Context::initialize(std::vector<std::reference_wrapper<TinyInt>>& refs, TinyInt count, TinyInt& total_count)
    {
        for (TinyInt i = 0; i < refs.size(); i++) {
            TinyInt index = static_cast<TinyInt>(refs.size() - i - 1);
            if (count > 0) {
                count--;
                total_count--;
                refs[index].get() = total_count;
            }
            else {
                refs[index].get() = ~count;
            }
        }
    }

    void Context::construct(TinyInt ranks, TinyInt suits)
    {
        TinyInt total_count;

        total_count = ranks + RANK_WILDCARD_COUNT;
        std::vector<std::reference_wrapper<TinyInt>> rank_refs = {
            std::ref(RANK_2),
            std::ref(RANK_3),
            std::ref(RANK_4),
            std::ref(RANK_5),
            std::ref(RANK_6),
            std::ref(RANK_7),
            std::ref(RANK_8),
            std::ref(RANK_9),
            std::ref(RANK_T),
            std::ref(RANK_J),
            std::ref(RANK_Q),
            std::ref(RANK_K),
            std::ref(RANK_A),
            std::ref(RANK_COUNT),
        };
        initialize(rank_refs, total_count, total_count);
        RANK_LOWEST = 0;
        RANK_HIGHEST = RANK_COUNT - 1;
        RANK_ANY = RANK_COUNT;

        RankAlphabets[ALPHABET_ORIGINAL] = RANKS.substr(MAX_RANK_COUNT - RANK_COUNT);
        RankAlphabets[ALPHABET_WILDCARD] = RankAlphabets[ALPHABET_ORIGINAL] + RANK_WILDCARD;
        for (Int alphabet = 0; alphabet < ALPHABET_COUNT; alphabet++) {
            for (TinyInt i = 0; i < RankAlphabets[alphabet].size(); i++) {
                RankAlphabetIndexes[alphabet][RankAlphabets[alphabet][i]] = i;
            }
        }


        total_count = suits + SUIT_WILDCARD_COUNT;
        std::vector<std::reference_wrapper<TinyInt>> suit_refs = {
            std::ref(SUIT_D),
            std::ref(SUIT_C),
            std::ref(SUIT_H),
            std::ref(SUIT_S),
            std::ref(SUIT_COUNT),
        };
        initialize(suit_refs, total_count, total_count);
        SUIT_LOWEST = 0;
        SUIT_HIGHEST = SUIT_COUNT - 1;
        SUIT_ANY = SUIT_COUNT;

        SuitAlphabets[ALPHABET_ORIGINAL] = SUITS.substr(MAX_SUIT_COUNT - SUIT_COUNT);
        SuitAlphabets[ALPHABET_WILDCARD] = SuitAlphabets[ALPHABET_ORIGINAL] + SUIT_WILDCARD;
        for (Int alphabet = 0; alphabet < ALPHABET_COUNT; alphabet++) {
            for (TinyInt i = 0; i < SuitAlphabets[alphabet].size(); i++) {
                SuitAlphabetIndexes[alphabet][SuitAlphabets[alphabet][i]] = i;
            }
        }


        CARD_COUNT = CARD_ANY = ranks * suits;
        UNIQUE_CARD_COUNT = CARD_COUNT + 1; // +1 for indistinguishable jokers
        std::vector<std::vector<std::reference_wrapper<TinyInt>>> card_refs = {
            {
                std::ref(CARD_2D),
                std::ref(CARD_2C),
                std::ref(CARD_2H),
                std::ref(CARD_2S),
            },
            {
                std::ref(CARD_3D),
                std::ref(CARD_3C),
                std::ref(CARD_3H),
                std::ref(CARD_3S),
            },
            {
                std::ref(CARD_4D),
                std::ref(CARD_4C),
                std::ref(CARD_4H),
                std::ref(CARD_4S),
            },
            {
                std::ref(CARD_5D),
                std::ref(CARD_5C),
                std::ref(CARD_5H),
                std::ref(CARD_5S),
            },
            {
                std::ref(CARD_6D),
                std::ref(CARD_6C),
                std::ref(CARD_6H),
                std::ref(CARD_6S),
            },
            {
                std::ref(CARD_7D),
                std::ref(CARD_7C),
                std::ref(CARD_7H),
                std::ref(CARD_7S),
            },
            {
                std::ref(CARD_8D),
                std::ref(CARD_8C),
                std::ref(CARD_8H),
                std::ref(CARD_8S),
            },
            {
                std::ref(CARD_9D),
                std::ref(CARD_9C),
                std::ref(CARD_9H),
                std::ref(CARD_9S),
            },
            {
                std::ref(CARD_TD),
                std::ref(CARD_TC),
                std::ref(CARD_TH),
                std::ref(CARD_TS),
            },
            {
                std::ref(CARD_JD),
                std::ref(CARD_JC),
                std::ref(CARD_JH),
                std::ref(CARD_JS),
            },
            {
                std::ref(CARD_QD),
                std::ref(CARD_QC),
                std::ref(CARD_QH),
                std::ref(CARD_QS),
            },
            {
                std::ref(CARD_KD),
                std::ref(CARD_KC),
                std::ref(CARD_KH),
                std::ref(CARD_KS),
            },
            {
                std::ref(CARD_AD),
                std::ref(CARD_AC),
                std::ref(CARD_AH),
                std::ref(CARD_AS),
            },
        };

        total_count = CARD_COUNT;
        for (Int i = 0; i < ranks; i++) {
            Int index = static_cast<Int>(card_refs.size() - 1 - i);
            initialize(card_refs[index], SUIT_COUNT, total_count);
        }

        if (RANK_COUNT >= TOTAL_COMBINATION_CARDS) {
            if (RANK_COUNT > TOTAL_COMBINATION_CARDS) {
                Int wheel_straight_product = PRIMES[RANK_A];
                for (Int i = 0; i < TOTAL_COMBINATION_CARDS - 1; i++) {
                    wheel_straight_product *= PRIMES[i];
                }

                STRAIGHT_PRODUCTS.push_back(wheel_straight_product);
            }

            Int total_straights = RANK_COUNT + 1 - TOTAL_COMBINATION_CARDS;
            for (Int i = 0; i < total_straights; i++) {
                Int product = 1;
                for (Int j = 0; j < TOTAL_COMBINATION_CARDS; j++) {
                    product *= PRIMES[i + j];
                }

                STRAIGHT_PRODUCTS.push_back(product);
            }
        }

        N_CHOOSE_K.clear();
        N_CHOOSE_K.resize(CARD_COUNT + 1, std::vector<Int>(CARD_COUNT + 1));
        for (Int i = 0; i <= CARD_COUNT; i++) {
            for (Int j = 0; j <= CARD_COUNT; j++) {
                N_CHOOSE_K[i][j] = n_choose_k(i, j);
            }
        }
    }
}
