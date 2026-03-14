#ifdef _MSC_VER
#include <intrin.h>
#endif

#include "Types.h"


namespace core
{
#ifdef _MSC_VER
    static inline TinyInt get_lsb_index(BigInt value)
    {
        unsigned long result;

        if (_BitScanForward64(&result, value)) {
            return static_cast<TinyInt>(result);
        }

        return 32;
    }

    static inline TinyInt get_msb_index(BigInt value)
    {
        unsigned long result;

        if (_BitScanReverse64(&result, value)) {
            return static_cast<TinyInt>(result);
        }

        return 32;
    }
#else
    static inline TinyInt get_lsb_index(BigInt value)
    {
        if (value) {
            return __builtin_ctzll(value);
        }

        return sizeof(value);
    }

    static inline TinyInt get_msb_index(BigInt value)
    {
        if (value) {
            return (sizeof(value) - 1) - __builtin_clzll(value);
        }

        return sizeof(value);
    }
#endif
}
