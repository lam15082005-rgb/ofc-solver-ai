#include "OFCSolver.h"
#include <algorithm>
#include <cmath>
#include <numeric>
#include "Parallel.h"


namespace core
{
    std::vector<ActionPerformance> make_performances(Int action_count)
    {
        return std::vector<ActionPerformance>(action_count);
    }

    void reset_performances(std::vector<ActionPerformance>& performances)
    {
        for (auto& performance : performances) {
            performance.reset();
        }
    }


    OFCPlayer::OFCPlayer()
        : m_action_count(0)
    {
    }


    OFCSolver::OFCSolver()
        : OFCSolver(MAX_PLAYER_COUNT, REGULAR_JOKER_COUNT, REGULAR_DEAD_CARD_COUNT, std::make_shared<OFCRoyaltyProviderV1>())
    {
    }

    OFCSolver::OFCSolver(
        Int player_count,
        Int joker_count,
        Int dead_card_count,
        std::shared_ptr<OFCRoyaltyProvider> royalty_provider
    )
        : m_player_count(player_count)
        , m_joker_count(joker_count)
        , m_hole_card_count(OFC_HOLE_CARD_COUNT)
        , m_dead_card_count(dead_card_count)
        , m_action_count(OFC_ACTION_COUNT)
        , m_hand_sizes(OFC_HAND_SIZES)
        , m_hand_count(OFC_HAND_COUNT)
        , m_fixed_card_count(0)
        , m_iteration_count(0)
        , m_players(player_count)
        , m_royalty_provider(std::move(royalty_provider))
    {
        m_context = std::make_shared<Context>();
        m_evaluator = std::make_shared<OFCEvaluator>(m_context, m_hand_count);
        m_rewarder = std::make_shared<OFCRewarder>(m_context, m_hand_sizes, m_royalty_provider);

        std::random_device rd;
        m_generator = std::mt19937(rd());

        m_deck = generate_deck(m_player_count, m_joker_count);
        if (m_player_count * m_hole_card_count + m_dead_card_count > m_deck.size()) {
            throw std::invalid_argument("Not enough cards in the deck for the given number of players, jokers, and dead cards.");
        }

        m_dead_cards.resize(m_dead_card_count);

        m_hands.resize(m_hand_count);
        for (Int hand_index = 0; hand_index < m_hand_count; hand_index++) {
            m_hands[hand_index].resize(m_hand_sizes[hand_index]);
        }

        m_players_strengths.resize(m_player_count);
        m_players_joker_count.resize(m_player_count);
        for (Int player_index = 0; player_index < m_player_count; player_index++) {
            auto& player = m_players[player_index];

            player.m_hole_cards.resize(m_hole_card_count);
            player.m_regrets.resize(m_action_count);
            player.m_frequencies.resize(m_action_count);
            player.m_payoffs.resize(m_action_count);
            player.m_actions_strengths.resize(m_action_count, std::vector<BigInt>(OFC_HAND_COUNT));
            player.m_action_mask.resize(m_action_count, 1);
            player.m_action_count = m_action_count;

            m_players_strengths[player_index].resize(m_hand_count);
        }

        m_regrets.reserve(m_action_count);
        m_frequencies.resize(m_action_count);
        m_performances = make_performances(m_action_count);
    }

    void OFCSolver::act(Int player_index, Int action_index)
    {
        auto& player = m_players[player_index];
        auto& strengths = player.m_actions_strengths[action_index];

        std::copy(strengths.begin(), strengths.end(), m_players_strengths[player_index].begin());
    }

    void OFCSolver::arrange_deck(const std::vector<TinyInt>& starting_cards)
    {
        m_fixed_card_count = static_cast<Int>(starting_cards.size());

        auto sorted_cards = starting_cards;
        auto sorted_deck = m_deck;

        std::sort(sorted_cards.begin(), sorted_cards.end());
        std::sort(sorted_deck.begin(), sorted_deck.end());

        m_deck.clear();
        m_deck.insert(m_deck.end(), starting_cards.begin(), starting_cards.end());

        Int card_index = 0;
        Int deck_card_index = 0;
        while (deck_card_index < sorted_deck.size()) {
            auto deck_card = sorted_deck[deck_card_index];
            if (card_index >= sorted_cards.size() || deck_card < sorted_cards[card_index]) {
                m_deck.push_back(deck_card);
            }
            else {
                card_index++;
            }

            deck_card_index++;
        }
    }

    void OFCSolver::assign_hands(std::vector<std::vector<TinyInt>>& hands, const std::vector<TinyInt>& hole_cards, Int action_index)
    {
        auto& action = OFC_ACTIONS[action_index];
        for (Int hand_index = 0; hand_index < m_hand_count; hand_index++) {
            auto& hand_action = action[hand_index];
            for (Int card_index = 0; card_index < m_hand_sizes[hand_index]; card_index++) {
                hands[hand_index][card_index] = hole_cards[hand_action[card_index]];
            }
        }
    }

    void OFCSolver::deal_cards()
    {
        std::fill(m_players_joker_count.begin(), m_players_joker_count.end(), 0);

        std::shuffle(m_deck.begin() + m_fixed_card_count, m_deck.end(), m_generator);

        std::copy(
            m_deck.begin(),
            m_deck.begin() + m_dead_card_count,
            m_dead_cards.begin()
        );

        Int from = 0;
        Int to = m_dead_card_count;

        for (Int player_index = 0; player_index < m_player_count; player_index++) {
            auto& player = m_players[player_index];
            auto& hole_cards = player.m_hole_cards;
            auto& joker_count = m_players_joker_count[player_index];

            from = to;
            to += m_hole_card_count;

            std::copy(
                m_deck.begin() + from,
                m_deck.begin() + to,
                hole_cards.begin()
            );

            for (auto card : hole_cards) {
                if (card == m_context->CARD_ANY) {
                    joker_count++;
                }
            }
        }
    }

    Int get_n_extra_players(Int n_players)
    {
        if (n_players > MAX_PLAYER_COUNT) {
            return n_players - MAX_PLAYER_COUNT;
        }

        return 0;
    }

    std::vector<TinyInt> OFCSolver::generate_deck(Int n_players, Int n_jokers)
    {
        auto n_extra_players = get_n_extra_players(n_players);
        auto n_cards = m_context->CARD_COUNT + n_extra_players * m_context->RANK_COUNT + n_jokers;
        auto result = reserve<TinyInt>(n_cards);

        for (TinyInt i_card = 0; i_card < m_context->CARD_COUNT; i_card++) {
            result.push_back(i_card);
        }

        for (TinyInt i_extra_player = 0; i_extra_player < n_extra_players; i_extra_player++) {
            for (TinyInt i_rank = 0; i_rank < m_context->RANK_COUNT; i_rank++) {
                result.push_back(i_rank * m_context->SUIT_COUNT + i_extra_player);
            }
        }

        for (TinyInt i_joker = 0; i_joker < n_jokers; i_joker++) {
            result.push_back(m_context->CARD_ANY);
        }

        return result;
    }

    std::vector<double>& OFCSolver::get_frequencies()
    {
        return m_frequencies;
    }

    double OFCSolver::get_payoff(Int player_index)
    {
        auto& rewards = m_rewarder->get_rewards(m_players_strengths, m_players_joker_count);

        return static_cast<float>(rewards[player_index]);
    }

    void OFCSolver::reset_player_actions(Int player_index)
    {
        auto& player = m_players[player_index];

        for (Int action_index = 0; action_index < m_action_count; action_index++) {
            auto& strengths = player.m_actions_strengths[action_index];
            player.m_action_mask[action_index] = strengths[0] > 0;
        }

        player.m_action_count = static_cast<Int>(std::count(player.m_action_mask.begin(), player.m_action_mask.end(), 1));
    }

    // Note: This function requires m_action_mask of the player to be set before calling.
    void OFCSolver::reset_player_frequencies(Int player_index)
    {
        auto& player = m_players[player_index];

        for (Int action_index = 0; action_index < m_action_count; action_index++) {
            if (player.m_action_mask[action_index]) {
                player.m_frequencies[action_index] = 1.0 / player.m_action_count;
            }
            else {
                player.m_frequencies[action_index] = 0.0;
            }
        }

        player.m_distribution.update(player.m_frequencies);
    }

    void OFCSolver::reset_player_payoffs_and_regrets(Int player_index)
    {
        auto& player = m_players[player_index];

        std::fill(player.m_payoffs.begin(), player.m_payoffs.end(), 0.0);
        std::fill(player.m_regrets.begin(), player.m_regrets.end(), 0.0);
    }

    void OFCSolver::reset_player_strengths(Int player_index)
    {
        auto& player = m_players[player_index];

        auto& hole_cards = player.m_hole_cards;
        for (Int action_index = 0; action_index < m_action_count; action_index++) {
            assign_hands(m_hands, hole_cards, action_index);

            auto& strengths = m_evaluator->get_strengths(m_hands);
            auto& player_strengths = player.m_actions_strengths[action_index];
            std::copy(strengths.begin(), strengths.end(), player_strengths.begin());
        }
    }

    std::vector<double>& OFCSolver::solve(
        const std::vector<TinyInt>& hole_cards,
        const std::vector<TinyInt>& dead_cards,
        Int iteration_count,
        Int traversal_count
    )
    {
        solve_begin(hole_cards, dead_cards);

        solve_continue(iteration_count, traversal_count);

        return get_frequencies();
    }

    void OFCSolver::solve_begin(const std::vector<TinyInt>& hole_cards, const std::vector<TinyInt>& dead_cards)
    {
        if (hole_cards.size() != m_hole_card_count) {
            throw std::invalid_argument("Invalid hole cards size");
        }

        if (dead_cards.size() != m_dead_card_count) {
            throw std::invalid_argument("Invalid dead cards size");
        }

        auto n_hole_jokers = std::count_if(hole_cards.begin(), hole_cards.end(), [&](TinyInt card) { return card == m_context->CARD_ANY; });
        auto n_dead_jokers = std::count_if(dead_cards.begin(), dead_cards.end(), [&](TinyInt card) { return card == m_context->CARD_ANY; });
        if (n_hole_jokers + n_dead_jokers > m_joker_count) {
            throw std::invalid_argument("Input cards contain too many jokers");
        }

        std::fill(m_frequencies.begin(), m_frequencies.end(), 0.0);

        reset_performances(m_performances);

        auto starting_cards = reserve<TinyInt>(hole_cards.size() + dead_cards.size());

        starting_cards.insert(starting_cards.end(), dead_cards.begin(), dead_cards.end());
        starting_cards.insert(starting_cards.end(), hole_cards.begin(), hole_cards.end());

        arrange_deck(starting_cards);

        m_iteration_count = 0;
    }

    void OFCSolver::solve_continue(Int iteration_count, Int traversal_count)
    {
        for (Int iteration_index = 0; iteration_index < iteration_count; iteration_index++) {
            deal_cards();

            for (Int player_index = 0; player_index < m_player_count; player_index++) {
                // reset for everyone on the first iteration, reset only for opponents after that
                if (m_iteration_count == 0 || player_index > 0) {
                    reset_player_payoffs_and_regrets(player_index);
                    reset_player_strengths(player_index);
                }
                reset_player_actions(player_index);
                reset_player_frequencies(player_index);
            }

            solve_one(traversal_count);

            m_iteration_count++;
        }
    }

    void OFCSolver::solve_one(Int traversal_count)
    {
        const double DISCARD_FREQUENCY = 0.1;
        const double DISCARD_VOLUME = 0.5;
        const Int MIN_ACTION_COUNT = 1000;

        double discard_interval = traversal_count * DISCARD_FREQUENCY;
        double discard_progress = discard_interval;

        for (Int traversal_index = 0; traversal_index < traversal_count; traversal_index++) {
            for (Int player_index = 0; player_index < m_player_count; player_index++) {
                auto& player = m_players[player_index];
                for (Int other_player_index = 0; other_player_index < m_player_count; other_player_index++) {
                    if (other_player_index == player_index) {
                        continue;
                    }

                    auto& other_player = m_players[other_player_index];

                    auto random_value = m_random(m_generator);
                    auto action_index = other_player.m_distribution.get_action_index(random_value);

                    act(other_player_index, action_index);
                }

                for (Int action_index = 0; action_index < m_action_count; action_index++) {
                    if (!player.m_action_mask[action_index]) {
                        continue;
                    }

                    act(player_index, action_index);

                    player.m_payoffs[action_index] = get_payoff(player_index);
                }

                if (player_index == HERO_INDEX && traversal_index + 1 == traversal_count) {
                    for (Int action_index = 0; action_index < m_action_count; action_index++) {
                        if (!player.m_action_mask[action_index]) {
                            // calculate payoffs for the actions skipped in the above loop
                            act(player_index, action_index);

                            player.m_payoffs[action_index] = get_payoff(player_index);
                        }

                        m_performances[action_index].m_ev += player.m_payoffs[action_index];
                    }
                }

                double utility = std::inner_product(
                    player.m_payoffs.begin(),
                    player.m_payoffs.end(),
                    player.m_frequencies.begin(),
                    0.0
                );

                for (Int action_index = 0; action_index < m_action_count; action_index++) {
                    if (!player.m_action_mask[action_index]) {
                        continue;
                    }

                    auto payoff = player.m_payoffs[action_index];
                    auto regret = payoff - utility;
                    player.m_regrets[action_index] += regret;
                }

                double total_regret = 0;
                for (auto regret : player.m_regrets) {
                    if (regret > 0.0) {
                        total_regret += regret;
                    }
                }

                if (total_regret > 0) {
                    for (Int action_index = 0; action_index < m_action_count; action_index++) {
                        if (!player.m_action_mask[action_index]) {
                            continue;
                        }

                        auto regret = player.m_regrets[action_index];
                        if (regret > 0.0) {
                            player.m_frequencies[action_index] = regret / total_regret;
                        }
                        else {
                            player.m_frequencies[action_index] = 0.0;
                        }
                    }

                    if ((traversal_index + 1) >= discard_progress && player.m_action_count > MIN_ACTION_COUNT) {
                        m_regrets.clear();

                        for (Int action_index = 0; action_index < m_action_count; action_index++) {
                            if (!player.m_action_mask[action_index]) {
                                continue;
                            }

                            m_regrets.push_back(player.m_regrets[action_index]);
                        }

                        std::sort(m_regrets.rbegin(), m_regrets.rend());

                        Int discard_count = static_cast<Int>(std::ceil(player.m_action_count * DISCARD_VOLUME));
                        Int keep_count = player.m_action_count - discard_count;
                        double threshold = std::min(m_regrets[keep_count - 1], 0.0);
                        for (Int action_index = 0; action_index < m_action_count; action_index++) {
                            if (!player.m_action_mask[action_index]) {
                                continue;
                            }

                            auto regret = player.m_regrets[action_index];
                            if (regret < threshold) {
                                player.m_action_mask[action_index] = 0;
                                player.m_regrets[action_index] = 0.0;
                                player.m_payoffs[action_index] = 0.0;
                                player.m_frequencies[action_index] = 0.0;
                                player.m_action_count--;
                            }
                        }
                    }
                }
                else {
                    reset_player_frequencies(player_index);
                }

                if (player_index == HERO_INDEX) {
                    auto& a = m_frequencies;
                    auto& b = player.m_frequencies;
                    std::transform(
                        a.begin(),
                        a.end(),
                        b.begin(),
                        a.begin(),
                        std::plus<double>()
                    );
                }

                player.m_distribution.update(player.m_frequencies);
            }

            if ((traversal_index + 1) >= discard_progress) {
                discard_progress += discard_interval;
            }
        }
    }


    OFCParallelSolver::OFCParallelSolver()
        : OFCParallelSolver(MAX_PLAYER_COUNT, REGULAR_JOKER_COUNT, REGULAR_DEAD_CARD_COUNT, std::make_shared<OFCRoyaltyProviderV1>())
    {
    }

    OFCParallelSolver::OFCParallelSolver(
        Int player_count,
        Int joker_count,
        Int dead_card_count,
        std::shared_ptr<OFCRoyaltyProvider> royalty_provider
    )
        : m_player_count(player_count)
        , m_joker_count(joker_count)
        , m_dead_card_count(dead_card_count)
        , m_royalty_provider(std::move(royalty_provider))
    {
        m_performances = make_performances(OFC_ACTION_COUNT);
    }

    std::vector<double> OFCParallelSolver::solve(
        const std::vector<TinyInt>& hole_cards,
        const std::vector<TinyInt>& dead_cards,
        Int iteration_count,
        Int traversal_count,
        Int thread_count
    )
    {
        reset_performances(m_performances);

        Int solver_count = resolve_thread_count(thread_count);

        auto solvers = reserve<OFCSolver>(solver_count);
        for (Int solver_index = 0; solver_index < solver_count; solver_index++) {
            solvers.emplace_back(
                m_player_count,
                m_joker_count,
                m_dead_card_count,
                m_royalty_provider
            );

            solvers.back().solve_begin(hole_cards, dead_cards);
        }

        parallelize(
            iteration_count,
            [&](ThreadElement<Int>& te) {
                solvers[te.thread_index].solve_continue(1, traversal_count);
            },
            solver_count
        );

        Int action_count = solvers.front().m_action_count;
        auto result = std::vector<double>(action_count);

        for (Int solver_index = 0; solver_index < solver_count; solver_index++) {
            auto& solver = solvers[solver_index];
            auto& frequencies = solver.get_frequencies();
            for (Int action_index = 0; action_index < action_count; action_index++) {
                result[action_index] += frequencies[action_index];
            }
        }

        auto total = std::accumulate(result.begin(), result.end(), 0.0);
        if (total > 0) {
            for (auto& frequency : result) {
                frequency /= total;
            }
        }

        for (auto& solver : solvers) {
            auto& performances = solver.m_performances;
            for (Int action_index = 0; action_index < action_count; action_index++) {
                m_performances[action_index] += performances[action_index];
            }
        }

        return result;
    }
}
