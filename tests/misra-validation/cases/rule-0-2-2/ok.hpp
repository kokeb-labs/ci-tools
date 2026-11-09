// Compliant: every named parameter is read; the one the body does not need has no name.
#ifndef KV_RULE_0_2_2_OK_HPP
#define KV_RULE_0_2_2_OK_HPP

#include <cstdint>

namespace kv::rule_0_2_2::ok {

inline std::uint32_t select(std::uint32_t value, std::uint32_t mask) { return value & mask; }

inline std::uint32_t keep(std::uint32_t value, std::uint32_t /*unused*/) { return value; }

}  // namespace kv::rule_0_2_2::ok

#endif  // KV_RULE_0_2_2_OK_HPP
