#pragma once

#include <string>
#include <vector>

#include "Types.h"


namespace core
{
    const TinyInt TETRADE_BIT_COUNT = 4;
    const TinyInt TETRADE_MASK = 0x0F;
    const BigInt TETRADE_0_MASK = TETRADE_MASK;
    const BigInt TETRADE_1_MASK = TETRADE_0_MASK << TETRADE_BIT_COUNT;
    const BigInt TETRADE_2_MASK = TETRADE_1_MASK << TETRADE_BIT_COUNT;
    const BigInt TETRADE_3_MASK = TETRADE_2_MASK << TETRADE_BIT_COUNT;
    const BigInt TETRADE_4_MASK = TETRADE_3_MASK << TETRADE_BIT_COUNT;
    const BigInt TETRADE_5_MASK = TETRADE_4_MASK << TETRADE_BIT_COUNT;
    const BigInt TETRADE_6_MASK = TETRADE_5_MASK << TETRADE_BIT_COUNT;
    const BigInt TETRADE_7_MASK = TETRADE_6_MASK << TETRADE_BIT_COUNT;
    const BigInt TETRADE_8_MASK = TETRADE_7_MASK << TETRADE_BIT_COUNT;
    const BigInt TETRADE_9_MASK = TETRADE_8_MASK << TETRADE_BIT_COUNT;
    const BigInt TETRADE_A_MASK = TETRADE_9_MASK << TETRADE_BIT_COUNT;
    const BigInt TETRADE_B_MASK = TETRADE_A_MASK << TETRADE_BIT_COUNT;
    const BigInt TETRADE_C_MASK = TETRADE_B_MASK << TETRADE_BIT_COUNT;
    const BigInt TETRADE_D_MASK = TETRADE_C_MASK << TETRADE_BIT_COUNT;
    const BigInt TETRADE_E_MASK = TETRADE_D_MASK << TETRADE_BIT_COUNT;
    const BigInt TETRADE_F_MASK = TETRADE_E_MASK << TETRADE_BIT_COUNT;
    const std::vector<TinyInt> TETRADE_SHIFTS = {
        TETRADE_BIT_COUNT * 0x0,
        TETRADE_BIT_COUNT * 0x1,
        TETRADE_BIT_COUNT * 0x2,
        TETRADE_BIT_COUNT * 0x3,
        TETRADE_BIT_COUNT * 0x4,
        TETRADE_BIT_COUNT * 0x5,
        TETRADE_BIT_COUNT * 0x6,
        TETRADE_BIT_COUNT * 0x7,
        TETRADE_BIT_COUNT * 0x8,
        TETRADE_BIT_COUNT * 0x9,
        TETRADE_BIT_COUNT * 0xA,
        TETRADE_BIT_COUNT * 0xB,
        TETRADE_BIT_COUNT * 0xC,
        TETRADE_BIT_COUNT * 0xD,
        TETRADE_BIT_COUNT * 0xE,
        TETRADE_BIT_COUNT * 0xF,
    };
    const std::vector<BigInt> TETRADE_MASKS = {
        TETRADE_0_MASK,
        TETRADE_1_MASK,
        TETRADE_2_MASK,
        TETRADE_3_MASK,
        TETRADE_4_MASK,
        TETRADE_5_MASK,
        TETRADE_6_MASK,
        TETRADE_7_MASK,
        TETRADE_8_MASK,
        TETRADE_9_MASK,
        TETRADE_A_MASK,
        TETRADE_B_MASK,
        TETRADE_C_MASK,
        TETRADE_D_MASK,
        TETRADE_E_MASK,
        TETRADE_F_MASK,
    };

    const TinyInt BYTE_BIT_COUNT = 8;
    const TinyInt BYTE_MASK = TinyInt(~0);
    const BigInt BYTE_0_MASK = BYTE_MASK;
    const BigInt BYTE_1_MASK = BYTE_0_MASK << BYTE_BIT_COUNT;
    const BigInt BYTE_2_MASK = BYTE_1_MASK << BYTE_BIT_COUNT;
    const BigInt BYTE_3_MASK = BYTE_2_MASK << BYTE_BIT_COUNT;
    const BigInt BYTE_4_MASK = BYTE_3_MASK << BYTE_BIT_COUNT;
    const BigInt BYTE_5_MASK = BYTE_4_MASK << BYTE_BIT_COUNT;
    const BigInt BYTE_6_MASK = BYTE_5_MASK << BYTE_BIT_COUNT;
    const BigInt BYTE_7_MASK = BYTE_6_MASK << BYTE_BIT_COUNT;
    const std::vector<TinyInt> BYTE_SHIFTS = {
        BYTE_BIT_COUNT * 0,
        BYTE_BIT_COUNT * 1,
        BYTE_BIT_COUNT * 2,
        BYTE_BIT_COUNT * 3,
        BYTE_BIT_COUNT * 4,
        BYTE_BIT_COUNT * 5,
        BYTE_BIT_COUNT * 6,
        BYTE_BIT_COUNT * 7,
    };
    const std::vector<BigInt> BYTE_MASKS = {
        BYTE_0_MASK,
        BYTE_1_MASK,
        BYTE_2_MASK,
        BYTE_3_MASK,
        BYTE_4_MASK,
        BYTE_5_MASK,
        BYTE_6_MASK,
        BYTE_7_MASK,
    };
    const TinyInt TETRADES_PER_BYTE = BYTE_BIT_COUNT / TETRADE_BIT_COUNT;

    const Int MIN_CPU_UTILIZATION = 1;
    const Int MAX_CPU_UTILIZATION = 0;

    const TinyInt MIN_RANK_COUNT = 5;
    const TinyInt MAX_RANK_COUNT = 13;

    const TinyInt MIN_SUIT_COUNT = 1;
    const TinyInt MAX_SUIT_COUNT = 4;

    const TinyInt MAX_CARD_COUNT = MAX_RANK_COUNT * MAX_SUIT_COUNT;
    const TinyInt MAX_DUPLICATE_COUNT = 2;

    const TinyInt SHORT_DECK_RANK_COUNT = 9;
    const TinyInt SHORT_DECK_SUIT_COUNT = 4;
    const TinyInt REGULAR_RANK_COUNT = 13;
    const TinyInt REGULAR_SUIT_COUNT = 4;
    const TinyInt REGULAR_JOKER_COUNT = 4;
    const TinyInt REGULAR_DEAD_CARD_COUNT = 4;

    const TinyInt TOTAL_COMBINATION_CARDS = 5;

    const Int OFC_TOP_HAND_SIZE = 3;
    const Int OFC_MIDDLE_HAND_SIZE = TOTAL_COMBINATION_CARDS;
    const Int OFC_BOTTOM_HAND_SIZE = TOTAL_COMBINATION_CARDS;
    const Int OFC_HOLE_CARD_COUNT = OFC_TOP_HAND_SIZE + OFC_MIDDLE_HAND_SIZE + OFC_BOTTOM_HAND_SIZE;
    const std::vector<Int> OFC_HAND_SIZES = { OFC_TOP_HAND_SIZE, OFC_MIDDLE_HAND_SIZE, OFC_BOTTOM_HAND_SIZE };
    const Int OFC_HAND_COUNT = static_cast<Int>(OFC_HAND_SIZES.size());
    extern const std::vector<std::vector<std::vector<Int>>> OFC_ACTIONS;
    extern const Int OFC_ACTION_COUNT;

    const TinyInt MIN_PLAYER_COUNT = 2;
    const TinyInt MAX_PLAYER_COUNT = 4;

    const Int HERO_INDEX = 0;
    const Int HERO_COUNT = 1;

    // Parser
    const std::string RANKS = "23456789TJQKA";
    const std::string RANK_WILDCARD = "*";
    const std::string SUITS = "dchs";
    const std::string SUIT_WILDCARD = "#";

    const TinyInt RANK_WILDCARD_COUNT = 1;
    const TinyInt SUIT_WILDCARD_COUNT = 1;

    const TinyInt RANK_LENGTH = 1;
    const TinyInt SUIT_LENGTH = 1;
    const TinyInt CARD_LENGTH = 2;

    const TinyInt MAX_PERCENTAGE = 100;
    const double MAX_PERCENTAGE_DOUBLE = MAX_PERCENTAGE;

    // Evaluator
    const TinyInt PRIMES[MAX_RANK_COUNT] = { 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, };

    enum {
        COMBINATION_TYPE_NONE,
        COMBINATION_TYPE_HIGH_CARD,
        COMBINATION_TYPE_PAIR,
        COMBINATION_TYPE_TWO_PAIRS,
        COMBINATION_TYPE_THREE_OF_A_KIND,
        COMBINATION_TYPE_STRAIGHT,
        COMBINATION_TYPE_FLUSH,
        COMBINATION_TYPE_PAIR_FLUSH,
        COMBINATION_TYPE_TWO_PAIR_FLUSH,
        COMBINATION_TYPE_FULL_HOUSE,
        COMBINATION_TYPE_FOUR_OF_A_KIND,
        COMBINATION_TYPE_STRAIGHT_FLUSH,
        COMBINATION_TYPE_FIVE_OF_A_KIND,
        COMBINATION_TYPE_COUNT,
    };

    enum {
        ALPHABET_ORIGINAL,
        ALPHABET_WILDCARD,
        ALPHABET_COUNT,
    };
}
