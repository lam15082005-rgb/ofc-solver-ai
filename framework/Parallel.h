#pragma once

#include <atomic>
#include <cmath>
#include <functional>
#include <thread>
#include <vector>

#include "Constants.h"
#include "Types.h"


namespace core
{
    Int resolve_thread_count(Int thread_count);
    std::vector<std::thread> spawn_threads(std::function<std::thread(Int)> spawn, Int count);

    template<typename TInteger>
    struct ThreadElement
    {
        Int thread_index;
        Int thread_count;
        TInteger index;
    };

    void parallelize(Int count, std::function<void(ThreadElement<Int>&)> function, Int thread_count);
    void parallelize(BigInt count, std::function<void(ThreadElement<BigInt>&)> function, Int thread_count);

    template<typename TInteger>
    struct ThreadRange
    {
        std::atomic<TInteger>* iteration_index;
        Int thread_index;
        Int thread_count;
        TInteger begin;
        TInteger end;
        TInteger index;
        TInteger count;
        TInteger iteration_count;

        TInteger get_percentage()
        {
            return MAX_PERCENTAGE * (index - begin) / count;
        }

        bool next()
        {
            TInteger original_percentage;

            if (begin <= index && index < end) {
                original_percentage = get_percentage();
                index++;
            }
            else {
                original_percentage = 0;
                index = begin;
            }

            TInteger current_percentage = get_percentage();
            if (original_percentage < current_percentage) {
                *iteration_index += iteration_count;
                iteration_count = 0;
            }

            iteration_count++;

            return index < end;
        }
    };

    void parallelize(Int count, std::function<void(ThreadRange<Int>&)> function, Int thread_count);
    void parallelize(BigInt count, std::function<void(ThreadRange<BigInt>&)> function, Int thread_count);
}
