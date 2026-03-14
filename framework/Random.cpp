#include "Random.h"


namespace core
{
    inline BigInt rotl(const BigInt x, int k) {
        return (x << k) | (x >> (64 - k));
    }

    inline double to_double(BigInt x) {
        union {
            BigInt i;
            double d;
        } u{ UINT64_C(0x3FF) << 52 | x >> 12 };
        return u.d - 1.0;
    }

    Random::Random()
    {
        std::random_device rd;

        m_state[0] = get_seed(rd);
        m_state[1] = get_seed(rd);
    }

    BigInt Random::get_seed(std::random_device& rd)
    {
        if (sizeof(BigInt) > sizeof(std::random_device::result_type)) {
            return rd() | (BigInt(rd()) << 32);
        }
        else {
            return rd();
        }
    }

    BigInt Random::next_bigint()
    {
        BigInt s0 = m_state[0];
        BigInt s1 = m_state[1];

        BigInt result = s0 + s1;

        s1 ^= s0;
        m_state[0] = rotl(s0, 24) ^ s1 ^ (s1 << 16); // a, b
        m_state[1] = rotl(s1, 37); // c

        return result;
    }

    double Random::next_double()
    {
        return to_double(next_bigint());
    }
}
