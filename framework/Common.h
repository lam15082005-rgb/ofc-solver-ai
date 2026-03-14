#pragma once

#include <functional>
#include <map>
#include <string>
#include <vector>

#include "boost/algorithm/string/join.hpp"
#include "boost/format.hpp"
#include "boost/range/adaptor/transformed.hpp"

#include "Constants.h"
#include "Types.h"


namespace core
{
    template<typename T>
    class CollectionAdapter
    {
    public:
        virtual Int size() const = 0;
        virtual T operator[](Int index) const = 0;
    };

    template<typename V, typename T>
    class VectorAdapter : public CollectionAdapter<T>
    {
    public:
        const std::vector<V>& m_vector;

        VectorAdapter(const std::vector<V>& vector) : m_vector(vector) {}

        Int size() const override { return static_cast<Int>(m_vector.size()); }
        T operator[](Int index) const override { return static_cast<T>(m_vector[index]); }
    };

    template<typename T>
    std::vector<T> reserve(std::size_t capacity)
    {
        std::vector<T> result;

        result.reserve(capacity);

        return result;
    }

    template<typename T>
    bool are_equal(const std::vector<T>& values)
    {
        if (values.size() == 0) {
            return true;
        }

        T value = values.front();

        Int count = static_cast<Int>(std::count_if(
            values.begin(),
            values.end(),
            [&](T current_value) { return current_value == value; }
        ));

        return count == values.size();
    }


    TinyInt make_card_value(Int rank_value, Int suit_value, Int suit_count);
    TinyInt make_rank_value(Int card_value, Int suit_count);
    TinyInt make_suit_value(Int card_value, Int suit_count);

    TinyInt bit_count(BigInt value);

    TinyInt get_byte(BigInt value, Int index);
    BigInt set_byte(BigInt value, Int index, TinyInt byte);

    TinyInt get_tetrade(BigInt value, Int index);
    BigInt set_tetrade(BigInt value, Int index, TinyInt tetrade);
    TinyInt concatenate_tetrades(Int hi, Int lo);
    TinyInt get_combination_type(BigInt strength);

    BigInt concatenate(Int hi, Int lo);
    Int get_high_dword(BigInt value);
    Int get_low_dword(BigInt value);

    std::vector<Int> enumerate(Int index, Int n, Int k);

    void enumerate_bits(BigInt value, std::function<void(TinyInt, TinyInt)> callback);
    void enumerate_bits_reversed(BigInt value, std::function<void(TinyInt, TinyInt)> callback);
    std::vector<TinyInt> enumerate_bits(BigInt value);

    Int factorial(Int n);
    Int n_choose_k(Int n, Int k);
    Int count_ways_to_assign_balls_to_tight_boxes(Int ball_count, const std::vector<Int>& box_sizes);
    std::vector<std::vector<std::vector<Int>>> generate_ways_to_assign_balls_to_tight_boxes(Int ball_count, const std::vector<Int>& box_sizes);

    Int n_choose_k_max_c(Int n, Int k, Int c);

    template<typename It>
    Int n_choose_k_max_c_index(Int n, It begin, It end, Int c)
    {
        Int result = 0;

        Int k = static_cast<Int>(std::distance(begin, end));
        It p = begin;
        Int x = 0;
        Int a = 0;

        for (Int i = 1; i < n; i++) {
            Int ai = 0;
            while (p < end && *p == x) {
                ai++;
                ++p;
            }

            for (Int j = ai + 1; j <= c; j++) {
                if (k < a + j) {
                    break;
                }

                result += n_choose_k_max_c(n - i, k - a - j, c);
            }

            a += ai;
            x++;
        }

        return result;
    }

    Int n_choose_k_max_c_index(Int n, const std::vector<Int>& items, Int c);
    void n_choose_k_max_c_enumerate(Int n, Int k, Int c, Int index, std::function<void(Int, Int)> callback);
    std::vector<Int> n_choose_k_max_c_unindex(Int n, Int k, Int c, Int index);
}
