#include <filesystem>
#include <fstream>
#include <mutex>
#include "LookupTableBuilder.h"
#include "LookupTableStore.h"


namespace core
{
    const std::string ROOT_DIRECTORY = "lookup";


    std::shared_ptr<LookupTableStore> LookupTableStore::instance()
    {
        static std::shared_ptr<LookupTableStore> store{ new LookupTableStore() };

        return store;
    }

    std::shared_ptr<std::vector<BigInt>> LookupTableStore::get_table(std::shared_ptr<LookupTableBuilder> builder)
    {
        std::shared_ptr<std::vector<BigInt>> result;

        static std::mutex mutex;
        {
            std::lock_guard<std::mutex> lock(mutex);

            auto path = builder->get_file_name();

            auto it = m_tables.find(path);
            if (it != m_tables.end()) {
                return it->second;
            }

            result = make_table(builder);

            m_tables[path] = result;
        }

        return result;
    }

    std::shared_ptr<std::vector<BigInt>> LookupTableStore::get_table(std::shared_ptr<Context> context)
    {
        return get_table(std::make_shared<LookupTableBuilder>(context));
    }

    std::shared_ptr<std::vector<BigInt>> LookupTableStore::load(const std::string& path)
    {
        auto result = std::make_shared<std::vector<BigInt>>();

        BigInt size = static_cast<BigInt>(std::filesystem::file_size(path));
        BigInt count = size / sizeof(BigInt);

        result->resize(count);

        std::ifstream input(path, std::ios::in | std::ios::binary);
        input.read(reinterpret_cast<char*>(result->data()), size);

        return result;
    }

    std::shared_ptr<std::vector<BigInt>> LookupTableStore::make_table(std::shared_ptr<LookupTableBuilder> builder)
    {
        std::shared_ptr<std::vector<BigInt>> result;

        auto path = std::filesystem::path(ROOT_DIRECTORY);
        if (!std::filesystem::exists(path)) {
            std::filesystem::create_directories(path);
        }

        path /= builder->get_file_name();

        if (std::filesystem::exists(path)) {
            result = load(path.string());
        }
        else {
            result = std::make_shared<std::vector<BigInt>>(builder->build());
            save(result, path.string());
        }

        return result;
    }

    void LookupTableStore::save(std::shared_ptr<std::vector<BigInt>> table, const std::string& path)
    {
        std::ofstream output(path, std::ios::out | std::ios::binary | std::ios::trunc);
        if (output.is_open()) {
            output.write(reinterpret_cast<const char*>(table->data()), table->size() * sizeof(BigInt));
        }
    }
}
