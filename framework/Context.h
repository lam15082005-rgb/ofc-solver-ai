#pragma once

#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

#include "Card.h"
#include "Common.h"
#include "Combination.h"
#include "Constants.h"
#include "Permutation.h"
#include "Rank.h"
#include "Suit.h"
#include "Types.h"


namespace core
{
    class Context
    {
    public:

        Context();
        Context(TinyInt ranks, TinyInt suits);

        void enumerate_cards(Int index, Int n, Int k, std::function<void(Int, Card)> callback) const;
        void enumerate_cards(Mask mask, std::function<void(Int, Card)> callback) const;
        Card get_card(const Rank& rank, const Suit& suit) const;
        void set_combination(Combination& result, Int index, Int card_count) const;
        Combination get_combination(Int index, Int card_count) const;
        std::string get_combination_string(Int index, Int card_count) const;
        Int get_index(Mask mask) const;
        Permutation get_permutation(Int index, Int card_count) const;
        void set_permutation(Permutation& permutation, Int index, Int card_count) const;
        Rank get_rank(const Card& card) const;
        Int get_prime_product(Int rank_count, std::function<Rank(Int)> callback) const;
        Int get_prime_product(const std::vector<Card>& cards) const;
        Int get_prime_product(const std::vector<TinyInt>& cards) const;
        Int get_prime_product(const std::vector<Rank>& ranks) const;
        std::string get_string(const Card& card) const;
        std::string get_string(const Combination& combination) const;
        std::string get_string(const Permutation& permutation) const;
        std::string get_string(const Rank& rank, Int alphabet = ALPHABET_ORIGINAL) const;
        std::string get_string(const Suit& suit, Int alphabet = ALPHABET_ORIGINAL) const;
        Suit get_suit(const Card& card) const;

        template<typename Iter>
        Int get_index(Iter begin, Iter end) const
        {
            Int result = 0;

            Int n = 0;
            while (begin != end) {
                result += N_CHOOSE_K[*begin][++n];

                ++begin;
            }

            return result;
        }

        TinyInt RANK_LOWEST;
        TinyInt RANK_HIGHEST;
        TinyInt RANK_2;
        TinyInt RANK_3;
        TinyInt RANK_4;
        TinyInt RANK_5;
        TinyInt RANK_6;
        TinyInt RANK_7;
        TinyInt RANK_8;
        TinyInt RANK_9;
        TinyInt RANK_T;
        TinyInt RANK_J;
        TinyInt RANK_Q;
        TinyInt RANK_K;
        TinyInt RANK_A;
        TinyInt RANK_COUNT;
        TinyInt RANK_ANY;
        std::string RankAlphabets[ALPHABET_COUNT];
        std::unordered_map<char, TinyInt> RankAlphabetIndexes[ALPHABET_COUNT];

        std::vector<Int> STRAIGHT_PRODUCTS;

        TinyInt SUIT_LOWEST;
        TinyInt SUIT_HIGHEST;
        TinyInt SUIT_D;
        TinyInt SUIT_C;
        TinyInt SUIT_H;
        TinyInt SUIT_S;
        TinyInt SUIT_COUNT;
        TinyInt SUIT_ANY;
        std::string SuitAlphabets[ALPHABET_COUNT];
        std::unordered_map<char, TinyInt> SuitAlphabetIndexes[ALPHABET_COUNT];

        TinyInt CARD_2D;
        TinyInt CARD_2C;
        TinyInt CARD_2H;
        TinyInt CARD_2S;
        TinyInt CARD_3D;
        TinyInt CARD_3C;
        TinyInt CARD_3H;
        TinyInt CARD_3S;
        TinyInt CARD_4D;
        TinyInt CARD_4C;
        TinyInt CARD_4H;
        TinyInt CARD_4S;
        TinyInt CARD_5D;
        TinyInt CARD_5C;
        TinyInt CARD_5H;
        TinyInt CARD_5S;
        TinyInt CARD_6D;
        TinyInt CARD_6C;
        TinyInt CARD_6H;
        TinyInt CARD_6S;
        TinyInt CARD_7D;
        TinyInt CARD_7C;
        TinyInt CARD_7H;
        TinyInt CARD_7S;
        TinyInt CARD_8D;
        TinyInt CARD_8C;
        TinyInt CARD_8H;
        TinyInt CARD_8S;
        TinyInt CARD_9D;
        TinyInt CARD_9C;
        TinyInt CARD_9H;
        TinyInt CARD_9S;
        TinyInt CARD_TD;
        TinyInt CARD_TC;
        TinyInt CARD_TH;
        TinyInt CARD_TS;
        TinyInt CARD_JD;
        TinyInt CARD_JC;
        TinyInt CARD_JH;
        TinyInt CARD_JS;
        TinyInt CARD_QD;
        TinyInt CARD_QC;
        TinyInt CARD_QH;
        TinyInt CARD_QS;
        TinyInt CARD_KD;
        TinyInt CARD_KC;
        TinyInt CARD_KH;
        TinyInt CARD_KS;
        TinyInt CARD_AD;
        TinyInt CARD_AC;
        TinyInt CARD_AH;
        TinyInt CARD_AS;
        TinyInt CARD_COUNT;
        TinyInt CARD_ANY;

        TinyInt UNIQUE_CARD_COUNT;

        std::vector<std::vector<Int>> N_CHOOSE_K;
    private:
        void construct(TinyInt ranks, TinyInt suits);
        void initialize(std::vector<std::reference_wrapper<TinyInt>>& refs, TinyInt count, TinyInt& value);
    };
}
