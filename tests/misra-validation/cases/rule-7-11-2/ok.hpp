#ifndef KV_RULE_7_11_2_OK_HPP
#define KV_RULE_7_11_2_OK_HPP

// Compliant: the sequence is passed as a span over a std::array, which keeps its length.
#include <array>
#include <cstdint>
#include <span>

namespace kv::rule_7_11_2::ok {

inline std::int32_t first(std::span<std::int32_t const> values) {
  return values.empty() ? 0 : values.front();
}

inline std::int32_t use() {
  std::array<std::int32_t, 3> const samples{1, 2, 3};
  return first(samples);
}

}  // namespace kv::rule_7_11_2::ok

#endif  // KV_RULE_7_11_2_OK_HPP
