// Compliant: standard attributes and plain ISO C++ only.
#ifndef KV_RULE_4_1_1_OK_HPP
#define KV_RULE_4_1_1_OK_HPP

#include <cstdint>

namespace kv::rule_4_1_1::ok {

[[nodiscard]] inline std::uint32_t twice(std::uint32_t v) { return v << 1U; }

[[nodiscard]] inline std::uint32_t pick(std::uint32_t v) {
  std::uint32_t out = 0U;
  if (v != 0U) {
    out = twice(v);
  }
  return out;
}

}  // namespace kv::rule_4_1_1::ok

#endif  // KV_RULE_4_1_1_OK_HPP
