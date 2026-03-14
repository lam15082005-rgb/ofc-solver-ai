#include "PermutationParser.h"


namespace core
{
    Permutation parse_permutation(std::shared_ptr<Context> context, const std::string& permutation)
    {
        return PermutationParser(std::move(context), permutation).parse();
    }

    std::vector<Permutation> parse_permutations(std::shared_ptr<Context> context, const std::vector<std::string>& permutations)
    {
        std::vector<Permutation> result;
        result.reserve(permutations.size());

        for (const auto& permutation : permutations) {
            result.push_back(parse_permutation(context, permutation));
        }

        return result;
    }
}
