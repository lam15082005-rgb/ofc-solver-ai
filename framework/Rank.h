#pragma once

#include "Object.h"
#include "Types.h"


namespace core
{
    class Rank : public Object<TinyInt>
    {
    public:
        using Object::Object;
    };
}
