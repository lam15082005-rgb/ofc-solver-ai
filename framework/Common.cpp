#include <algorithm>
#include <chrono>
#include <cmath>
#include <stdexcept>

#include "Bit.h"
#include "Common.h"
#include "Constants.h"
#include "Mask.h"


namespace core
{
    TinyInt make_card_value(Int rank_value, Int suit_value, Int suit_count)
    {
        return rank_value * suit_count + suit_value;
    }

    TinyInt make_rank_value(Int card_value, Int suit_count)
    {
        return card_value / suit_count;
    }

    TinyInt make_suit_value(Int card_value, Int suit_count)
    {
        return card_value % suit_count;
    }

    TinyInt bit_count(BigInt value)
    {
        value = value - ((value >> 1) & 0x5555555555555555UL);
        value = (value & 0x3333333333333333UL) + ((value >> 2) & 0x3333333333333333UL);
        return static_cast<TinyInt>((((value + (value >> 4)) & 0xF0F0F0F0F0F0F0FUL) * 0x101010101010101UL) >> 56);
    }

    TinyInt get_byte(BigInt value, Int index)
    {
        return static_cast<TinyInt>((value & BYTE_MASKS[index]) >> BYTE_SHIFTS[index]);
    }

    BigInt set_byte(BigInt value, Int index, TinyInt byte)
    {
        auto bytes = reinterpret_cast<TinyInt*>(&value);

        bytes[index] = byte;

        return value;
    }

    TinyInt get_tetrade(BigInt value, Int index)
    {
        return static_cast<TinyInt>((value & TETRADE_MASKS[index]) >> TETRADE_SHIFTS[index]);
    }

    BigInt set_tetrade(BigInt value, Int index, TinyInt tetrade)
    {
        value &= ~TETRADE_MASKS[index];
        value |= BigInt(tetrade & TETRADE_MASK) << TETRADE_SHIFTS[index];

        return value;
    }

    TinyInt concatenate_tetrades(Int hi, Int lo)
    {
        return static_cast<TinyInt>((hi << TETRADE_BIT_COUNT) | lo);
    }

    TinyInt get_combination_type(BigInt strength)
    {
        return get_tetrade(strength, TOTAL_COMBINATION_CARDS * TETRADES_PER_BYTE + 1);
    }

    BigInt concatenate(Int hi, Int lo)
    {
        BigInt result = hi;

        result <<= BYTE_BIT_COUNT * sizeof(Int);
        result |= lo;

        return result;
    }

    Int get_high_dword(BigInt value)
    {
        return static_cast<Int>(value >> BYTE_BIT_COUNT * sizeof(Int));
    }

    Int get_low_dword(BigInt value)
    {
        return static_cast<Int>(value);
    }

    std::vector<Int> enumerate(Int index, Int n, Int k)
    {
        std::vector<Int> result(k);

        Int count = n_choose_k(n, k);
        if (index < count) {
            while (n > 0) {
                Int value = n_choose_k(n - 1, k);
                if (index >= value) {
                    index -= value;
                    --k;
                    result[k] = n - 1;
                }
                --n;
            }
        }

        return result;
    }

    void enumerate_bits(BigInt value, std::function<void(TinyInt, TinyInt)> callback)
    {
        TinyInt index = 0;

        while (value) {
            auto position = static_cast<TinyInt>(get_lsb_index(value));

            callback(index++, position);

            // value &= ~(BigInt(1) << position);
            auto t = value & static_cast<BigInt>(-(BigSignedInt)value);
            value ^= t;
        }
    }

    void enumerate_bits_reversed(BigInt value, std::function<void(TinyInt, TinyInt)> callback)
    {
        TinyInt count = static_cast<TinyInt>(bit_count(value));
        TinyInt index = count;

        while (value) {
            auto position = static_cast<TinyInt>(get_msb_index(value));

            callback(--index, position);

            value &= ~(BigInt(1) << position);
        }
    }

    std::vector<TinyInt> enumerate_bits(BigInt value)
    {
        auto result = reserve<TinyInt>(bit_count(value));

        enumerate_bits(
            value,
            [&](TinyInt index, TinyInt position) { result.push_back(position); }
        );

        return result;
    }

    Int factorial(Int n)
    {
        Int result = 1;

        for (Int i = 1; i <= n; i++) {
            result *= i;
        }

        return result;
    }

    Int n_choose_k(Int n, Int k)
    {
        if (n < k) {
            return 0;
        }

        Int result = 1;

        for (Int i = 1; i <= k; ++i) {
            result *= n - (k - i);
            result /= i;
        }

        return result;
    }

    Int count_ways_to_assign_balls_to_tight_boxes(Int ball_count, const std::vector<Int>& box_sizes)
    {
        Int result = 1;

        Int remaining_ball_count = ball_count;
        for (Int box_size : box_sizes) {
            result *= n_choose_k(remaining_ball_count, box_size);
            remaining_ball_count -= box_size;
        }

        return result;
    }

    std::vector<std::vector<std::vector<Int>>> generate_ways_to_assign_balls_to_tight_boxes(Int ball_count, const std::vector<Int>& box_sizes)
    {
        Int way_count = count_ways_to_assign_balls_to_tight_boxes(ball_count, box_sizes);
        auto result = reserve<std::vector<std::vector<Int>>>(way_count);
        auto way = reserve<std::vector<Int>>(box_sizes.size());

        std::function<void(std::vector<Int>, Int)> recursive = [&](std::vector<Int> balls, Int filled_box_count) {
            Int current_ball_count = static_cast<Int>(balls.size());
            Int combination_count = n_choose_k(current_ball_count, box_sizes[filled_box_count]);
            for (Int combination_index = 0; combination_index < combination_count; combination_index++) {
                auto combination = reserve<Int>(box_sizes[filled_box_count]);
                for (Int ball_index : enumerate(combination_index, current_ball_count, box_sizes[filled_box_count])) {
                    combination.push_back(balls[ball_index]);
                }

                way.push_back(combination);

                if (filled_box_count + 1 == box_sizes.size()) {
                    result.push_back(way);
                }
                else {
                    auto remaining_balls = reserve<Int>(balls.size() - combination.size());
                    std::set_difference(balls.begin(), balls.end(), combination.begin(), combination.end(), std::back_inserter(remaining_balls));
                    recursive(remaining_balls, filled_box_count + 1);
                }

                way.pop_back();
            }
        };

        auto balls = reserve<Int>(ball_count);
        for (Int i = 0; i < ball_count; i++) {
            balls.push_back(i);
        }

        recursive(balls, 0);

        return result;
    }

    Int n_choose_k_max_c(Int n, Int k, Int c)
    {
        Int result = 0;

        Int m = n - 1;
        Int d = c + 1;

        for (Int i = 0; i <= n; i++) {
            if (k < i * d) {
                break;
            }

            Int term = n_choose_k(m + k - i * d, m);

            term *= n_choose_k(n, i);

            if (i % 2 == 0) {
                result += term;
            }
            else {
                result -= term;
            }
        }

        return result;
    }

    Int n_choose_k_max_c_index(Int n, const std::vector<Int>& items, Int c)
    {
        return n_choose_k_max_c_index(n, items.begin(), items.end(), c);
    }

    void n_choose_k_max_c_enumerate(Int n, Int k, Int c, Int index, std::function<void(Int, Int)> callback)
    {
        Int x_index = 0;

        Int a = 0;
        Int x = 0;
        for (Int i = 1; i < n; i++) {

            Int j = c + 1;
            while (j > 1) {
                if (k + 1 < a + j) {
                    j--;
                    continue;
                }

                Int count = n_choose_k_max_c(n - i, k + 1 - a - j, c);

                if (count > index) {
                    break;
                }

                index -= count;

                j--;
            }

            Int ai = j - 1;

            for (Int t = 0; t < ai; t++) {
                callback(x_index++, x);
            }

            a += ai;
            x++;
        }

        while (x_index < k) {
            callback(x_index++, x);
        }
    }

    std::vector<Int> n_choose_k_max_c_unindex(Int n, Int k, Int c, Int index)
    {
        auto result = reserve<Int>(k);

        n_choose_k_max_c_enumerate(n, k, c, index,
            [&](Int i, Int v) {
                result.push_back(v);
            }
        );

        return result;
    }
}
