// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_2_UNCAUGHT_EXCEPTION_OK_NEAR_HPP
#define KV_RULE_4_1_2_UNCAUGHT_EXCEPTION_OK_NEAR_HPP

#include <exception>

namespace kv::rule_4_1_2_uncaught_exception::near {

// std::uncaught_exceptions (plural, a count) replaces the removed function.
inline bool unwinding() { return std::uncaught_exceptions() > 0; }

}  // namespace kv::rule_4_1_2_uncaught_exception::near

#endif  // KV_RULE_4_1_2_UNCAUGHT_EXCEPTION_OK_NEAR_HPP
