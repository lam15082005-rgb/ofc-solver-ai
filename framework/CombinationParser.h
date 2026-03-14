#pragma once

#include <memory>
#include <string>
#include <vector>

#include "CollectionParser.h"
#include "Combination.h"
#include "Context.h"


namespace core
{
    class CombinationParser : public CollectionParser<Combination>
    {
    public:
        using CollectionParser::CollectionParser;
    };

    Combination parse_combination(std::shared_ptr<Context> context, const std::string& combination);

    std::vector<Combination> parse_combinations(std::shared_ptr<Context> context, const std::vector<std::string>& combinations);
}
