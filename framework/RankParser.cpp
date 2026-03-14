#include <unordered_map>

#include "boost/format.hpp"

#include "RankParser.h"


namespace core
{
    Rank parse_rank(std::shared_ptr<Context> context, const std::string& text, Int alphabet)
    {
        if (text.size() == RANK_LENGTH) {
            auto it = context->RankAlphabetIndexes[alphabet].find(toupper(text[0]));
            if (it != context->RankAlphabetIndexes[alphabet].end()) {
                return Rank(it->second);
            }
        }

        throw std::invalid_argument(str(boost::format("Invalid rank: '%s'") % text));
    }
}
