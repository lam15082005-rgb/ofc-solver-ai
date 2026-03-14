#pragma once

#include <string>

#include "Constants.h"
#include "Context.h"
#include "Suit.h"


namespace core
{
    Suit parse_suit(std::shared_ptr<Context> context, const std::string& text, Int alphabet = ALPHABET_WILDCARD);
}
