#pragma once

#include <memory>
#include <random>
#include <vector>
#include "ActionDistribution.h"
#include "ActionPerformance.h"
#include "Context.h"
#include "OFCEvaluator.h"
#include "OFCRewarder.h"
#include "Types.h"


namespace core
{
    class OFCPlayer
    {
    public:
        std::vector<TinyInt> m_hole_cards;
        std::vector<double> m_regrets;
        std::vector<double> m_frequencies;
        std::vector<double> m_payoffs;
        ActionDistribution m_distribution;
        std::vector<std::vector<BigInt>> m_actions_strengths;
        std::vector<TinyInt> m_action_mask;
        Int m_action_count;

        OFCPlayer();
    };


    class OFCSolver
    {
    public:
        std::shared_ptr<Context> m_context;
        std::shared_ptr<OFCEvaluator> m_evaluator;
        std::shared_ptr<OFCRewarder> m_rewarder;
        std::shared_ptr<OFCRoyaltyProvider> m_royalty_provider;

        Int m_player_count;
        Int m_joker_count;
        Int m_hole_card_count;
        Int m_dead_card_count;
        Int m_action_count;
        Int m_hand_count;
        Int m_fixed_card_count;
        Int m_iteration_count;
        std::vector<TinyInt> m_deck;
        std::vector<Int> m_hand_sizes;
        std::vector<TinyInt> m_dead_cards;
        std::vector<std::vector<TinyInt>> m_hands;
        std::vector<OFCPlayer> m_players;
        std::vector<std::vector<BigInt>> m_players_strengths;
        std::vector<TinyInt> m_players_joker_count;
        std::mt19937 m_generator;
        std::uniform_real_distribution<double> m_random;

        std::vector<double> m_regrets;
        std::vector<double> m_frequencies;
        std::vector<ActionPerformance> m_performances;

        OFCSolver();
        OFCSolver(
            Int player_count,
            Int joker_count,
            Int dead_card_count,
            std::shared_ptr<OFCRoyaltyProvider> royalty_provider
        );

        void act(Int player_index, Int action_index);
        void arrange_deck(const std::vector<TinyInt>& starting_cards);
        void assign_hands(std::vector<std::vector<TinyInt>>& hands, const std::vector<TinyInt>& hole_cards, Int action_index);
        void deal_cards();
        std::vector<TinyInt> generate_deck(Int player_count, Int joker_count);
        std::vector<double>& get_frequencies();
        double get_payoff(Int player_index);
        void reset_player_actions(Int player_index);
        void reset_player_frequencies(Int player_index);
        void reset_player_payoffs_and_regrets(Int player_index);
        void reset_player_strengths(Int player_index);

        std::vector<double>& solve(
            const std::vector<TinyInt>& hole_cards,
            const std::vector<TinyInt>& dead_cards,
            Int iteration_count,
            Int traversal_count
        );
        void solve_begin(
            const std::vector<TinyInt>& hole_cards,
            const std::vector<TinyInt>& dead_cards
        );
        void solve_continue(
            Int iteration_count,
            Int traversal_count
        );

        void solve_one(Int traversal_count);
    };


    class OFCParallelSolver
    {
    public:
        Int m_player_count;
        Int m_joker_count;
        Int m_dead_card_count;
        std::shared_ptr<OFCRoyaltyProvider> m_royalty_provider;
        std::vector<ActionPerformance> m_performances;

        OFCParallelSolver();
        OFCParallelSolver(
            Int player_count,
            Int joker_count,
            Int dead_card_count,
            std::shared_ptr<OFCRoyaltyProvider> royalty_provider
        );

        std::vector<double> solve(
            const std::vector<TinyInt>& hole_cards,
            const std::vector<TinyInt>& dead_cards,
            Int iteration_count,
            Int traversal_count,
            Int thread_count
        );
    };
}
