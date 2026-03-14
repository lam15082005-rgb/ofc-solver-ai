#include "boost/format.hpp"

#include "CardParser.h"
#include "Constants.h"
#include "RankParser.h"
#include "SuitParser.h"

namespace core
{
    Card parse_card(std::shared_ptr<Context> context, const std::string& text, Int alphabet)
    {
        if (text.size() == CARD_LENGTH) {
            Rank rank = parse_rank(context, text.substr(0, RANK_LENGTH), alphabet);
            Suit suit = parse_suit(context, text.substr(RANK_LENGTH, SUIT_LENGTH), alphabet);

            return context->get_card(rank, suit);
        }

        throw std::invalid_argument(str(boost::format("Invalid card: '%s'") % text));
    }
}
