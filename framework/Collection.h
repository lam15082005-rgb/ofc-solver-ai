#pragma once

#include <algorithm>
#include <vector>
#include "Card.h"
#include "Mask.h"
#include "Object.h"
#include "Types.h"


namespace core
{
    class Collection : public Object<std::vector<Card>>
    {
    public:
        Collection() {}
        Collection(std::size_t size) { resize(size); }
        Collection(std::vector<Card> cards) { m_value = std::move(cards); }

        bool operator==(const Collection& other) { return m_value == other.m_value; }

        const Card& operator[](Int index) const { return m_value[index]; }
        Card& operator[](Int index) { return m_value[index]; }

        std::vector<Card>::const_iterator begin() const { return m_value.begin(); }
        std::vector<Card>::const_iterator end() const { return m_value.end(); }
        std::vector<Card>::iterator begin() { return m_value.begin(); }
        std::vector<Card>::iterator end() { return m_value.end(); }
        std::size_t capacity() { return m_value.capacity(); }
        void clear() { return m_value.clear(); }
        void copy(const std::vector<Card>& cards, Int offset) { std::copy(cards.begin(), cards.end(), m_value.begin() + offset); };
        void resize(std::size_t size) { return m_value.resize(size); }
        void reserve(std::size_t capacity) { return m_value.reserve(capacity); }
        std::size_t size() const { return m_value.size(); }
        void sort() { std::sort(m_value.begin(), m_value.end()); }

        Mask to_mask() const;
    };
}
