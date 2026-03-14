#pragma once

#include <vector>
#include "Context.h"
#include "Rank.h"
#include "Types.h"


namespace core
{
    class OFCRoyaltyProvider
    {
    public:
        virtual Int get_royalty(Int hand_index, BigInt strength) = 0;
    };

    class OFCRoyaltyProviderV1 : public OFCRoyaltyProvider
    {
    public:
        Int get_royalty(Int hand_index, BigInt strength) override;
    };

    class OFCRoyaltyProviderV2 : public OFCRoyaltyProvider
    {
    public:
        Int get_royalty(Int hand_index, BigInt strength) override;
    };


    class OFCRewarder
    {
    private:
        Int m_hand_count;
        std::vector<Int> m_hand_sizes;
        std::vector<TinyInt> m_ranks;
        std::vector<std::vector<SignedInt>> m_wins;
        std::vector<std::vector<SignedInt>> m_points;

        void zero(std::vector<SignedInt>& vector);
        void zero(std::vector<std::vector<SignedInt>>& matrix);

    public:
        std::shared_ptr<Context> m_context;
        std::shared_ptr<OFCRoyaltyProvider> m_royalty_provider;

        Int m_player_count;
        std::vector<SignedInt> m_rewards;
        std::vector<SignedInt> m_special_rewards;

        OFCRewarder();
        OFCRewarder(std::shared_ptr<Context> context, const std::vector<Int>& hand_sizes, std::shared_ptr<OFCRoyaltyProvider> royalty_provider);

        void set_player_count(Int player_count);
        bool is_five_straight(BigInt strength, Rank rank);
        bool is_big_straight(const std::vector<BigInt>& strengths);
        bool is_three_flushes(const std::vector<BigInt>& strengths);
        bool is_three_straights(const std::vector<BigInt>& strengths);
        bool is_six_pairs(const std::vector<BigInt>& strengths);
        Int get_special_reward(const std::vector<BigInt>& strengths);
        std::vector<std::vector<SignedInt>>& get_points(const std::vector<std::vector<BigInt>>& players, const std::vector<TinyInt>& jokers);
        std::vector<SignedInt>& get_rewards(const std::vector<std::vector<BigInt>>& players, const std::vector<TinyInt>& jokers);
    };
}
