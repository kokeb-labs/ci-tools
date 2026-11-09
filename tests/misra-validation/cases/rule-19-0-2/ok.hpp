#ifndef KV_RULE_19_0_2_OK_HPP
#define KV_RULE_19_0_2_OK_HPP

// Compliant: a constexpr function replaces the macro.
#include <cstdint>

namespace kv::rule_19_0_2::ok {

constexpr std::uint32_t square(std::uint32_t x) { return x * x; }

inline std::uint32_t area(std::uint32_t side) { return square(side); }

}  // namespace kv::rule_19_0_2::ok

#endif  // KV_RULE_19_0_2_OK_HPP
