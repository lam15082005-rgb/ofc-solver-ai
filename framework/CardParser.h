#pragma once

#include <memory>
#include <string>

#include "Card.h"
#include "Context.h"


namespace core
{
    Card parse_card(std::shared_ptr<Context> context, const std::string& text, Int alphabet = ALPHABET_WILDCARD);
}
