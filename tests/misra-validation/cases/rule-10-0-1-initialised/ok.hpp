// Compliant: one initialised declarator per declaration.
#ifndef KV_RULE_10_0_1_INITIALISED_OK_HPP
#define KV_RULE_10_0_1_INITIALISED_OK_HPP

#include <cstdint>

namespace kv::rule_10_0_1_initialised::ok {

struct Span {
  std::uint32_t lo = 0U;
  std::uint32_t hi = 8U;
};

inline std::uint32_t width(const Span& s) { return s.hi ^ s.lo; }

}  // namespace kv::rule_10_0_1_initialised::ok

#endif  // KV_RULE_10_0_1_INITIALISED_OK_HPP
