#include "ActionPerformance.h"


namespace core
{
    ActionPerformance::ActionPerformance()
    {
    }

    ActionPerformance& ActionPerformance::operator+=(const ActionPerformance& rhs)
    {
        m_ev += rhs.m_ev;

        return *this;
    }

    void ActionPerformance::reset()
    {
        m_ev.reset();
    }
}
