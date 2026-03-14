#pragma once

#include "Context.h"
#include "LookupTableBuilder.h"
#include "Types.h"


namespace core
{
    class LookupTableStore
    {
    public:
        std::map<std::string, std::shared_ptr<std::vector<BigInt>>> m_tables;

        LookupTableStore(LookupTableStore const&) = delete;
        LookupTableStore& operator=(LookupTableStore const&) = delete;

        static std::shared_ptr<LookupTableStore> instance();

        std::shared_ptr<std::vector<BigInt>> get_table(std::shared_ptr<LookupTableBuilder> builder);
        std::shared_ptr<std::vector<BigInt>> get_table(std::shared_ptr<Context> context);
        std::shared_ptr<std::vector<BigInt>> load(const std::string& path);
        std::shared_ptr<std::vector<BigInt>> make_table(std::shared_ptr<LookupTableBuilder> builder);
        void save(std::shared_ptr<std::vector<BigInt>> table, const std::string& path);

    private:
        LookupTableStore() {}
    };
}
