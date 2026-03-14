#include "OFCRewarder.h"

#include <map>
#include <numeric>
#include "Common.h"
#include "Constants.h"


namespace core
{
    const Int TOP_HAND_TWO_JOKERS_ROYALTY = 10;
    const Int TOP_HAND_THREE_JOKERS_ROYALTY = 20;

    const std::vector<std::vector<Int>> ROYALTIES = {
        // Top hand
        [] {
            std::vector<Int> v(COMBINATION_TYPE_COUNT, 0);

            v[COMBINATION_TYPE_HIGH_CARD] = 1;
            v[COMBINATION_TYPE_PAIR] = 1;
            v[COMBINATION_TYPE_THREE_OF_A_KIND] = 3;

            return v;
        }(),

        // Middle hand
        [] {
            std::vector<Int> v(COMBINATION_TYPE_COUNT, 0);

            v[COMBINATION_TYPE_HIGH_CARD] = 1;
            v[COMBINATION_TYPE_PAIR] = 1;
            v[COMBINATION_TYPE_TWO_PAIRS] = 1;
            v[COMBINATION_TYPE_THREE_OF_A_KIND] = 1;
            v[COMBINATION_TYPE_STRAIGHT] = 1;
            v[COMBINATION_TYPE_FLUSH] = 1;
            v[COMBINATION_TYPE_FULL_HOUSE] = 2;
            v[COMBINATION_TYPE_FOUR_OF_A_KIND] = 8;
            v[COMBINATION_TYPE_STRAIGHT_FLUSH] = 10;
            v[COMBINATION_TYPE_FIVE_OF_A_KIND] = 16;

            return v;
        }(),

        // Bottom hand
        [] {
            std::vector<Int> v(COMBINATION_TYPE_COUNT, 0);

            v[COMBINATION_TYPE_HIGH_CARD] = 1;
            v[COMBINATION_TYPE_PAIR] = 1;
            v[COMBINATION_TYPE_TWO_PAIRS] = 1;
            v[COMBINATION_TYPE_THREE_OF_A_KIND] = 1;
            v[COMBINATION_TYPE_STRAIGHT] = 1;
            v[COMBINATION_TYPE_FLUSH] = 1;
            v[COMBINATION_TYPE_FULL_HOUSE] = 1;
            v[COMBINATION_TYPE_FOUR_OF_A_KIND] = 4;
            v[COMBINATION_TYPE_STRAIGHT_FLUSH] = 5;
            v[COMBINATION_TYPE_FIVE_OF_A_KIND] = 8;

            return v;
        }(),
    };

    SignedInt get_sign(BigInt a, BigInt b = 0)
    {
        if (a > b) {
            return 1;
        }

        if (a < b) {
            return -1;
        }

        return 0;
    }


    Int get_rank_tetrade_index(Int card_index)
    {
        return card_index + TOTAL_COMBINATION_CARDS + 1;
    }

    Int get_suit_tetrade_index(Int card_index)
    {
        return card_index + 1;
    }

    TinyInt get_rank(BigInt strength, Int card_index)
    {
        auto t = get_tetrade(strength, get_rank_tetrade_index(card_index));

        return t - 1;
    }

    TinyInt get_highest_rank(BigInt strength)
    {
        return get_rank(strength, TOTAL_COMBINATION_CARDS - 1);
    }

    TinyInt get_suit(BigInt strength, Int card_index)
    {
        auto t = get_tetrade(strength, get_suit_tetrade_index(card_index));
        if (t == 0) {
            return MAX_SUIT_COUNT; // joker suit
        }

        return t - 1;
    }


    Int OFCRoyaltyProviderV1::get_royalty(Int hand_index, BigInt strength)
    {
        Int combination_type = get_combination_type(strength);

        return ROYALTIES[hand_index][combination_type];
    }


    Int OFCRoyaltyProviderV2::get_royalty(Int hand_index, BigInt strength)
    {
        Int combination_type = get_combination_type(strength);
        if (hand_index == 0 && combination_type == COMBINATION_TYPE_THREE_OF_A_KIND) {
            // strength = [t][rrr__][n][sss__]
            // where t (type), r (rank), s (suit), n (non-joker) or _ (empty) is 4 bits
            Int joker_count = OFC_TOP_HAND_SIZE - get_tetrade(strength, TOTAL_COMBINATION_CARDS);
            if (joker_count == 2) {
                return TOP_HAND_TWO_JOKERS_ROYALTY;
            }

            if (joker_count == 3) {
                return TOP_HAND_THREE_JOKERS_ROYALTY;
            }
        }

        return ROYALTIES[hand_index][combination_type];
    }


    void OFCRewarder::zero(std::vector<SignedInt>& vector)
    {
        std::fill(vector.begin(), vector.end(), 0);
    }

    void OFCRewarder::zero(std::vector<std::vector<SignedInt>>& matrix)
    {
        for (auto& vector : matrix) {
            std::fill(vector.begin(), vector.end(), 0);
        }
    }

    OFCRewarder::OFCRewarder()
        : OFCRewarder(std::make_shared<Context>(), OFC_HAND_SIZES, std::make_shared<OFCRoyaltyProviderV1>())
    {
    }

    OFCRewarder::OFCRewarder(std::shared_ptr<Context> context, const std::vector<Int>& hand_sizes, std::shared_ptr<OFCRoyaltyProvider> royalty_provider)
        : m_context(std::move(context))
        , m_royalty_provider(std::move(royalty_provider))
        , m_hand_count(static_cast<Int>(hand_sizes.size()))
        , m_hand_sizes(hand_sizes)
        , m_player_count(0)
        , m_ranks(hand_sizes.size())
    {
    }

    void OFCRewarder::set_player_count(Int player_count)
    {
        m_player_count = player_count;
        m_rewards = std::vector<SignedInt>(player_count);
        m_special_rewards = std::vector<SignedInt>(player_count);
        m_wins = std::vector<std::vector<SignedInt>>(player_count, std::vector<SignedInt>(player_count));
        m_points = std::vector<std::vector<SignedInt>>(player_count, std::vector<SignedInt>(player_count));
    }

    bool OFCRewarder::is_five_straight(BigInt strength, Rank rank)
    {
        auto t = get_combination_type(strength);
        if (t != COMBINATION_TYPE_STRAIGHT) {
            return false;
        }

        auto r = get_highest_rank(strength);
        if (r != rank) {
            return false;
        }

        return true;
    }

    bool OFCRewarder::is_big_straight(const std::vector<BigInt>& strengths)
    {
        if (!is_five_straight(strengths[2], m_context->RANK_A)) {
            return false;
        }

        if (!is_five_straight(strengths[1], m_context->RANK_9)) {
            return false;
        }

        Int card_index = TOTAL_COMBINATION_CARDS - 1;
        if (get_rank(strengths[0], card_index) != m_context->RANK_4) {
            return false;
        }

        card_index--;
        if (get_rank(strengths[0], card_index) != m_context->RANK_3) {
            return false;
        }

        card_index--;
        if (get_rank(strengths[0], card_index) != m_context->RANK_2) {
            return false;
        }

        return true;
    }

    bool OFCRewarder::is_three_flushes(const std::vector<BigInt>& strengths)
    {
        TinyInt t;

        t = get_combination_type(strengths[2]);
        if (t != COMBINATION_TYPE_FLUSH) {
            return false;
        }

        t = get_combination_type(strengths[1]);
        if (t != COMBINATION_TYPE_FLUSH) {
            return false;
        }

        t = get_combination_type(strengths[0]);
        if (t != COMBINATION_TYPE_HIGH_CARD) {
            return false;
        }

        Int card_index = TOTAL_COMBINATION_CARDS - 1;
        TinyInt s = get_suit(strengths[0], card_index);

        card_index--;
        if (get_suit(strengths[0], card_index) != s) {
            return false;
        }

        card_index--;
        if (get_suit(strengths[0], card_index) != s) {
            return false;
        }

        return true;
    }

    bool OFCRewarder::is_three_straights(const std::vector<BigInt>& strengths)
    {
        TinyInt t;

        t = get_combination_type(strengths[2]);
        if (t != COMBINATION_TYPE_STRAIGHT && t != COMBINATION_TYPE_STRAIGHT_FLUSH) {
            return false;
        }

        t = get_combination_type(strengths[1]);
        if (t != COMBINATION_TYPE_STRAIGHT && t != COMBINATION_TYPE_STRAIGHT_FLUSH) {
            return false;
        }


        Int card_index = TOTAL_COMBINATION_CARDS - 1;
        TinyInt r = get_rank(strengths[0], card_index);

        r -= 1;
        card_index -= 1;
        if (get_rank(strengths[0], card_index) != r) {
            return false;
        }

        r -= 1;
        card_index -= 1;
        if (get_rank(strengths[0], card_index) != r) {
            return false;
        }

        return true;
    }

    bool OFCRewarder::is_six_pairs(const std::vector<BigInt>& strengths)
    {
        for (Int hand_index = 0; hand_index < m_hand_count; hand_index++) {
            TinyInt t = get_combination_type(strengths[hand_index]);

            if (hand_index == 0) {
                if (t != COMBINATION_TYPE_THREE_OF_A_KIND && t != COMBINATION_TYPE_PAIR) {
                    return false;
                }
            }
            else {
                if (t != COMBINATION_TYPE_FOUR_OF_A_KIND && t != COMBINATION_TYPE_FULL_HOUSE && t != COMBINATION_TYPE_TWO_PAIRS) {
                    return false;
                }
            }

            Int rank_index = t != COMBINATION_TYPE_FULL_HOUSE ? TOTAL_COMBINATION_CARDS - m_hand_sizes[hand_index] : TOTAL_COMBINATION_CARDS - 1;

            m_ranks[hand_index] = get_rank(strengths[hand_index], rank_index);
        }

        for (Int i = 0; i < m_hand_count; i++) {
            for (Int j = i + 1; j < m_hand_count; j++) {
                if (m_ranks[i] == m_ranks[j]) {
                    return true;
                }
            }
        }

        return false;
    }

    Int OFCRewarder::get_special_reward(const std::vector<BigInt>& strengths)
    {
        if (is_big_straight(strengths)) {
            return 15;
        }
        else if (is_three_flushes(strengths)) {
            return 3;
        }
        else if (is_three_straights(strengths)) {
            return 3;
        }
        else if (is_six_pairs(strengths)) {
            return 3;
        }

        return 0;
    }

    std::vector<std::vector<SignedInt>>& OFCRewarder::get_points(const std::vector<std::vector<BigInt>>& players, const std::vector<TinyInt>& jokers)
    {
        if (players.size() != m_player_count) {
            set_player_count(static_cast<Int>(players.size()));
        }

        zero(m_wins);
        zero(m_points);
        zero(m_rewards);
        zero(m_special_rewards);

        for (Int i = 0; i < players.size(); i++) {
            if (jokers[i] == 0) {
                m_special_rewards[i] = get_special_reward(players[i]);
            }
        }

        if (std::any_of(m_special_rewards.begin(), m_special_rewards.end(), [](SignedInt x) { return x > 0; })) {
            for (Int i = 0; i < m_special_rewards.size(); i++) {
                for (Int j = 0; j < m_special_rewards.size(); j++) {
                    auto reward = m_special_rewards[i] - m_special_rewards[j];

                    m_points[i][j] = reward;
                    m_wins[i][j] = get_sign(reward) * m_hand_count;
                }
            }
        }

        for (Int i = 0; i < players.size(); i++) {
            for (Int j = i + 1; j < players.size(); j++) {
                if (m_special_rewards[i] == 0 && m_special_rewards[j] == 0) {
                    for (Int h = 0; h < m_hand_count; h++) {
                        auto sign = get_sign(players[i][h], players[j][h]);

                        m_wins[i][j] += sign;

                        if (sign > 0) {
                            m_points[i][j] += m_royalty_provider->get_royalty(h, players[i][h]);
                        }

                        if (sign < 0) {
                            m_points[i][j] -= m_royalty_provider->get_royalty(h, players[j][h]);
                        }
                    }
                }

                if (abs(m_wins[i][j]) == m_hand_count) {
                    m_points[i][j] *= 2;
                }

                m_wins[j][i] = -m_wins[i][j];
                m_points[j][i] = -m_points[i][j];
            }
        }

        if (m_player_count > MIN_PLAYER_COUNT) {
            for (Int i = 0; i < m_player_count; i++) {
                if (m_special_rewards[i] > 0) {
                    continue;
                }

                auto sum = std::accumulate(m_wins[i].begin(), m_wins[i].end(), 0);
                Int matchup_count = (m_player_count - 1) * m_hand_count;
                if (sum == matchup_count) {
                    for (Int j = 0; j < m_player_count; j++) {
                        m_points[i][j] *= 2;
                        m_points[j][i] *= 2;
                    }
                }
            }
        }

        return m_points;
    }

    std::vector<SignedInt>& OFCRewarder::get_rewards(const std::vector<std::vector<BigInt>>& players, const std::vector<TinyInt>& jokers)
    {
        auto& points = get_points(players, jokers);

        for (Int i = 0; i < m_player_count; i++) {
            m_rewards[i] = std::accumulate(points[i].begin(), points[i].end(), 0);
        }

        return m_rewards;
    }
}
