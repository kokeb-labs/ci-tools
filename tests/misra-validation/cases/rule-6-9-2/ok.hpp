#ifndef KV_RULE_6_9_2_OK_HPP
#define KV_RULE_6_9_2_OK_HPP

// Compliant: fixed-width integer aliases.
#include <cstdint>

namespace kv::rule_6_9_2::ok {

inline std::int64_t widen(std::int32_t narrow) {
  std::uint16_t const small = 2U;
  return static_cast<std::int64_t>(narrow) + static_cast<std::int64_t>(small);
}

}  // namespace kv::rule_6_9_2::ok

#endif  // KV_RULE_6_9_2_OK_HPP
