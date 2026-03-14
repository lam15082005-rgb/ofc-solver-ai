#include "CombinationParser.h"


namespace core
{
    Combination parse_combination(std::shared_ptr<Context> context, const std::string& combination)
    {
        return CombinationParser(std::move(context), combination).parse();
    }

    std::vector<Combination> parse_combinations(std::shared_ptr<Context> context, const std::vector<std::string>& combinations)
    {
        std::vector<Combination> result;
        result.reserve(combinations.size());

        for (const auto& combination : combinations) {
            result.push_back(parse_combination(context, combination));
        }

        return result;
    }
}
