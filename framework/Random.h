#pragma once

#include <random>

#include "Types.h"


namespace core
{
    class Random
    {
    private:
        BigInt m_state[2];

    public:
        Random();

        BigInt get_seed(std::random_device& rd);
        BigInt next_bigint();
        double next_double();
    };
}
