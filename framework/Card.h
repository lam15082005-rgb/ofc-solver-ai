#pragma once

#include "Mask.h"
#include "Object.h"
#include "Types.h"


namespace core
{
    class Card : public Object<TinyInt>
    {
    public:
        using Object::Object;

        Mask to_mask() const;
    };
}
