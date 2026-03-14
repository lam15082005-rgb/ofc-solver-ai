#pragma once

#include <memory>
#include <string>

#include "boost/format.hpp"

#include "Card.h"
#include "CardParser.h"
#include "Context.h"
#include "Mask.h"
#include "Types.h"


namespace core
{
    template<typename TCollection>
    class CollectionParser
    {
    public:
        std::shared_ptr<Context> m_context;
        std::string m_text;

        CollectionParser(std::shared_ptr<Context> context, const std::string& text)
            : m_context(std::move(context)), m_text(text)
        {
        }

        TCollection parse()
        {
            TCollection result;

            parse(result);

            return result;
        }

        void parse(TCollection& collection)
        {
            Int i = 0;
            Mask mask;
            while (i < m_text.size()) {
                if (isspace(static_cast<unsigned char>(m_text[i]))) {
                    i++;
                    continue;
                }

                Card card;
                if (m_text.substr(i, RANK_LENGTH) == RANK_WILDCARD) {
                    // all jokers have the same value, multiple jokers are allowed
                    card = m_context->CARD_ANY;
                    i++;
                }
                else {
                    std::string card_string = m_text.substr(i, CARD_LENGTH);
                    card = parse_card(m_context, card_string);
                    i += CARD_LENGTH;
                }

                collection.add(card);
            }
        }
    };
}
