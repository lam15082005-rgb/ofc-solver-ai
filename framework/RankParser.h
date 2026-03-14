#pragma once

#include <string>

#include "Constants.h"
#include "Context.h"
#include "Rank.h"


namespace core
{
    Rank parse_rank(std::shared_ptr<Context> context, const std::string& text, Int alphabet = ALPHABET_WILDCARD);
}
