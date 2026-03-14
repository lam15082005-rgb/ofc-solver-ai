#include <algorithm>
#include <chrono>
#include <numeric>

#include "Parallel.h"


namespace core
{
    std::vector<Int> get_processor_counts()
    {
        std::vector<Int> result;

        result.push_back(std::thread::hardware_concurrency());

        return result;
    }

    Int get_processor_count()
    {
        auto counts = get_processor_counts();

        return std::accumulate(counts.begin(), counts.end(), 0);
    }

    Int resolve_thread_count(Int thread_count)
    {
        if (thread_count == MAX_CPU_UTILIZATION) {
            thread_count = get_processor_count();

            if (thread_count == 0) {
                thread_count = 1;
            }
        }

        return thread_count;
    }

    std::vector<std::thread> spawn_threads(std::function<std::thread(Int)> spawn, Int count)
    {
        std::vector<std::thread> result(count);

        for (Int index = 0; index < count; index++) {
            result[index] = spawn(index);
        }

        return result;
    }

    template<typename TInteger>
    void parallelize_template(std::atomic<TInteger>& index, TInteger count, std::function<void(Int, Int)> function, Int thread_count)
    {
        using namespace std::chrono_literals;

        thread_count = resolve_thread_count(thread_count);
        if (thread_count > count) {
            thread_count = static_cast<Int>(count);
        }

        if (thread_count > MIN_CPU_UTILIZATION) {
            std::vector<std::thread> threads = spawn_threads(
                [&](Int thread_index) {
                    return std::thread(function, thread_index, thread_count);
                },
                thread_count
            );

            for (auto& thread : threads) {
                thread.join();
            }
        }
        else {
            function(0, thread_count);
        }
    }

    template<typename TInteger>
    void parallelize_thread_element_template(TInteger count, std::function<void(ThreadElement<TInteger>&)> function, Int thread_count)
    {
        std::atomic<TInteger> index = 0;

        parallelize_template(
            index,
            count,
            [&](Int thread_index, Int thread_count) {
                ThreadElement<TInteger> t{ thread_index, thread_count, 0 };
                while ((t.index = index++) < count) {
                    function(t);
                }
            },
            thread_count
        );
    }

    template<typename TInteger>
    void parallelize_thread_range_template(TInteger count, std::function<void(ThreadRange<TInteger>&)> function, Int thread_count)
    {
        std::atomic<TInteger> index = 0;

        parallelize_template(
            index,
            count,
            [&](Int thread_index, Int thread_count) {
                double volume = static_cast<double>(count) / thread_count;
                double begin = thread_index * volume;
                double end = (thread_index + 1) * volume;

                TInteger thread_begin = static_cast<TInteger>(round(begin));
                TInteger thread_end = static_cast<TInteger>(round(end));

                ThreadRange<TInteger> tr{ &index, thread_index, thread_count, thread_begin, thread_end, thread_end, thread_end - thread_begin, 0 };

                function(tr);
            },
            thread_count
        );
    }

    void parallelize(Int count, std::function<void(ThreadElement<Int>&)> function, Int thread_count)
    {
        parallelize_thread_element_template(count, function, thread_count);
    }

    void parallelize(BigInt count, std::function<void(ThreadElement<BigInt>&)> function, Int thread_count)
    {
        parallelize_thread_element_template(count, function, thread_count);
    }

    void parallelize(Int count, std::function<void(ThreadRange<Int>&)> function, Int thread_count)
    {
        parallelize_thread_range_template(count, function, thread_count);
    }

    void parallelize(BigInt count, std::function<void(ThreadRange<BigInt>&)> function, Int thread_count)
    {
        parallelize_thread_range_template(count, function, thread_count);
    }
}
