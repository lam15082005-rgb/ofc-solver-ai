#pragma once

#include <utility>


namespace core
{
    template<typename T>
    class Object
    {
    public:
        T m_value;

        Object() : m_value() {}
        Object(const T& value) : m_value(value) {}
        Object(T&& value) : m_value(std::move(value)) {}

        operator T&() { return m_value; }
        operator const T&() const { return m_value; }
    };
}
