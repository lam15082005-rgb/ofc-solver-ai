#pragma once

#include <string>
#include <vector>

#include "CollectionParser.h"
#include "Permutation.h"
#include "Context.h"


namespace core
{
    class PermutationParser : public CollectionParser<Permutation>
    {
    public:
        using CollectionParser::CollectionParser;
    };

    Permutation parse_permutation(std::shared_ptr<Context> context, const std::string& permutation);

    std::vector<Permutation> parse_permutations(std::shared_ptr<Context> context, const std::vector<std::string>& permutations);
}
