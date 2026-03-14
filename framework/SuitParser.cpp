#include <unordered_map>

#include "boost/format.hpp"

#include "SuitParser.h"


namespace core
{
    Suit parse_suit(std::shared_ptr<Context> context, const std::string& text, Int alphabet)
    {
        if (text.size() == SUIT_LENGTH) {
            auto it = context->SuitAlphabetIndexes[alphabet].find(tolower(text[0]));
            if (it != context->SuitAlphabetIndexes[alphabet].end()) {
                return Suit(it->second);
            }
        }

        throw std::invalid_argument(str(boost::format("Invalid suit: '%s'") % text));
    }
}
