#define BOOST_PYTHON_STATIC_LIB
#define BOOST_NUMPY_STATIC_LIB

#include <memory>
#include <boost/python.hpp>
#include <boost/python/numpy.hpp>
#include "Evaluator.h"
#include "OFCEvaluator.h"
#include "OFCRewarder.h"
#include "OFCSolver.h"


namespace python
{
    using namespace core;
    namespace py = boost::python;
    namespace np = boost::python::numpy;

    template<typename T>
    py::list std_vector_to_py_list(const std::vector<T>& vector)
    {
        py::list list;

        for (auto it = vector.begin(); it != vector.end(); ++it) {
            list.append(*it);
        }

        return list;
    }

    template<typename T>
    py::list std_vector_2d_to_py_list_2d(const std::vector<std::vector<T>>& vector)
    {
        py::list list;

        for (auto it = vector.begin(); it != vector.end(); ++it) {
            list.append(std_vector_to_py_list<T>(*it));
        }

        return list;
    }

    template<typename T>
    np::ndarray std_vector_to_ndarray(const std::vector<T>& vector)
    {
        py::tuple shape = py::make_tuple(vector.size());
        np::dtype dtype = np::dtype::get_builtin<T>();
        np::ndarray result = np::empty(shape, dtype);

        std::copy(vector.begin(), vector.end(), reinterpret_cast<T*>(result.get_data()));

        return result;
    }

    template<typename T>
    py::list std_vector_2d_to_py_list_ndarray(const std::vector<std::vector<T>>& vector)
    {
        py::list list;

        for (auto it = vector.begin(); it != vector.end(); ++it) {
            list.append(std_vector_to_ndarray<T>(*it));
        }

        return list;
    }

    template<typename T>
    std::vector<T> py_list_to_std_vector(const py::list& list)
    {
        return std::vector<T>(py::stl_input_iterator<T>(list), py::stl_input_iterator<T>());
    }

    template<typename T>
    std::vector<std::vector<T>> py_list_2d_to_std_vector_2d(const py::list& list)
    {
        auto result = reserve<std::vector<T>>(py::len(list));

        auto len = py::len(list);
        for (Int i = 0; i < len; i++) {
            result.push_back(py_list_to_std_vector<T>(py::extract<py::list>(list[i])));
        }

        return result;
    }

    template<typename T>
    std::vector<T> py_tuple_to_std_vector(const py::tuple& tuple)
    {
        return std::vector<T>(py::stl_input_iterator<T>(tuple), py::stl_input_iterator<T>());
    }


    std::shared_ptr<OFCRoyaltyProvider> make_royalty_provider(Int version)
    {
        if (version == 2) {
            return std::make_shared<OFCRoyaltyProviderV2>();
        }

        return std::make_shared<OFCRoyaltyProviderV1>();
    }


    std::shared_ptr<OFCRewarder> ofc_rewarder_create(Int version)
    {
        return std::make_shared<OFCRewarder>(
            std::make_shared<Context>(),
            OFC_HAND_SIZES,
            make_royalty_provider(version)
        );
    }

    BigInt evaluator_get_strength(Evaluator* const that, py::list cards)
    {
        return that->get_strength(
            py_list_to_std_vector<TinyInt>(cards)
        );
    }

    py::list ofc_evaluator_get_strengths(OFCEvaluator* const that, py::list hands)
    {
        return std_vector_to_py_list(that->get_strengths(
            py_list_2d_to_std_vector_2d<TinyInt>(hands)
        ));
    }

    py::list ofc_rewarder_get_points(OFCRewarder* const that, py::list players, py::list jokers)
    {
        return std_vector_2d_to_py_list_2d(that->get_points(
            py_list_2d_to_std_vector_2d<BigInt>(players),
            py_list_to_std_vector<TinyInt>(jokers)
        ));
    }

    py::list ofc_rewarder_get_rewards(OFCRewarder* const that, py::list players, py::list jokers)
    {
        return std_vector_to_py_list(that->get_rewards(
            py_list_2d_to_std_vector_2d<BigInt>(players),
            py_list_to_std_vector<TinyInt>(jokers)
        ));
    }

    std::shared_ptr<OFCParallelSolver> ofc_solver_create(Int player_count, Int joker_count, Int dead_card_count, Int game_version)
    {
        return std::make_shared<OFCParallelSolver>(
            player_count,
            joker_count,
            dead_card_count,
            make_royalty_provider(game_version)
        );
    }

    np::ndarray ofc_solver_solve(OFCParallelSolver* const that, py::list hole_cards, py::list dead_cards, Int iteration_count, Int traversal_count)
    {
        return std_vector_to_ndarray(that->solve(
            py_list_to_std_vector<TinyInt>(hole_cards),
            py_list_to_std_vector<TinyInt>(dead_cards),
            iteration_count,
            traversal_count,
            MAX_CPU_UTILIZATION
        ));
    }

    double ofc_solver_get_ev(OFCParallelSolver* const that, Int action_index)
    {
        return that->m_performances[action_index].m_ev.get_value();
    }
}


BOOST_PYTHON_MODULE(framework)
{
    using namespace core;
    namespace py = boost::python;
    namespace np = boost::python::numpy;

    np::initialize();

    py::class_<Evaluator>("Evaluator")
        .def("get_strength", python::evaluator_get_strength)
    ;

    py::class_<OFCEvaluator>("OFCEvaluator")
        .def("get_strengths", python::ofc_evaluator_get_strengths)
    ;

    py::class_<OFCRewarder, std::shared_ptr<OFCRewarder>>("OFCRewarder")
        .def("create", python::ofc_rewarder_create).staticmethod("create")
        .def("get_points", python::ofc_rewarder_get_points)
        .def("get_rewards", python::ofc_rewarder_get_rewards)
    ;

    py::class_<OFCParallelSolver, std::shared_ptr<OFCParallelSolver>>("OFCSolver", py::no_init)
        .def("create", python::ofc_solver_create).staticmethod("create")
        .def("solve", python::ofc_solver_solve)
        .def("get_ev", python::ofc_solver_get_ev)
    ;
}
