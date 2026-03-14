#pragma once

#include "Object.h"
#include "Types.h"


namespace core
{
    class Suit : public Object<TinyInt>
    {
    public:
        using Object::Object;
    };
}
